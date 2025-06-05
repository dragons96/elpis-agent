import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Annotated, Sequence, TypedDict, List

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from elpis import tools, constants, prompts, model_factory


class AgentState(TypedDict):
    """The state of the agent."""
    messages: Annotated[Sequence[BaseMessage], "The messages in the conversation"]


class LangGraphElpisAgent:
    """LangGraph implementation of ElpisAgent with the same interface."""
    __name__ = constants.AI_AGENT_NAME

    def __init__(self, chat_model: BaseChatModel = None, session_id: str = None):
        self._tool_selector = {tool.name: tool for tool in tools.TOOLS}
        
        if chat_model:
            self._chat_model = chat_model.bind_tools(tools.TOOLS)
        else:
            self._chat_model = model_factory.new_model(
                os.getenv('CHAT_MODEL_KEY_PREFIX')
            ).bind_tools(tools.TOOLS)

        # Initialize system messages
        self._system_messages = [
            SystemMessage("You are a helpful AI coding assistant. Use the available tools to help users with their coding tasks."),
        ]
        
        # Add custom system prompt if provided
        system_prompt = os.getenv('SYSTEM_PROMPT', default=constants.SYSTEM_PROMPT)
        if system_prompt:
            self._system_messages.append(SystemMessage(system_prompt))

        # Initialize memory storage
        self._session_id = session_id or self._generate_session_id()
        self._memory_dir = Path.home() / '.elpis' / 'memory'
        self._memory_dir.mkdir(parents=True, exist_ok=True)
        self._memory_file = self._memory_dir / f'{self._session_id}.json'
        
        # Load conversation history
        self._conversation_history: List[BaseMessage] = self._load_memory()

        # Build the graph
        self._graph = self._build_graph()

    def _build_graph(self):
        """Build the LangGraph workflow."""
        # Create the tool node
        tool_node = ToolNode(tools.TOOLS)
        
        # Define the graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("agent", self._agent_node)
        workflow.add_node("tools", tool_node)
        workflow.add_node("add_next_step", self._add_next_step_node)
        
        # Set entry point
        workflow.set_entry_point("agent")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "tools",
                "end": END,
            }
        )
        
        # Add edge from tools to add_next_step, then back to agent
        workflow.add_edge("tools", "add_next_step")
        workflow.add_edge("add_next_step", "agent")
        
        return workflow.compile()

    def _generate_session_id(self) -> str:
        """Generate a unique session ID based on timestamp."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        random_hash = hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()[:8]
        return f"session_{timestamp}_{random_hash}"

    def _message_to_dict(self, message: BaseMessage) -> dict:
        """Convert a message to a dictionary for JSON serialization."""
        message_dict = {
            'type': message.__class__.__name__,
            'content': message.content,
            'timestamp': datetime.now().isoformat()
        }
        
        # Handle additional attributes for different message types
        if hasattr(message, 'tool_calls') and message.tool_calls:
            message_dict['tool_calls'] = message.tool_calls
        if hasattr(message, 'tool_call_id'):
            message_dict['tool_call_id'] = message.tool_call_id
        if hasattr(message, 'name'):
            message_dict['name'] = message.name
            
        return message_dict

    def _dict_to_message(self, message_dict: dict) -> BaseMessage:
        """Convert a dictionary back to a message object."""
        message_type = message_dict['type']
        content = message_dict['content']
        
        if message_type == 'HumanMessage':
            return HumanMessage(content=content)
        elif message_type == 'AIMessage':
            message = AIMessage(content=content)
            if 'tool_calls' in message_dict:
                message.tool_calls = message_dict['tool_calls']
            return message
        elif message_type == 'SystemMessage':
            return SystemMessage(content=content)
        elif message_type == 'ToolMessage':
            return ToolMessage(
                content=content,
                tool_call_id=message_dict.get('tool_call_id', ''),
                name=message_dict.get('name', '')
            )
        else:
            # Fallback to HumanMessage for unknown types
            return HumanMessage(content=content)

    def _load_memory(self) -> List[BaseMessage]:
        """Load conversation history from the memory file."""
        if not self._memory_file.exists():
            return []
        
        try:
            with open(self._memory_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                messages = []
                for msg_dict in data.get('messages', []):
                    try:
                        message = self._dict_to_message(msg_dict)
                        messages.append(message)
                    except Exception as e:
                        print(f"Warning: Failed to load message: {e}")
                        continue
                return messages
        except Exception as e:
            print(f"Warning: Failed to load memory from {self._memory_file}: {e}")
            return []

    def _save_memory(self):
        """Save conversation history to the memory file."""
        try:
            data = {
                'session_id': self._session_id,
                'created_at': datetime.now().isoformat(),
                'messages': [self._message_to_dict(msg) for msg in self._conversation_history]
            }
            
            with open(self._memory_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save memory to {self._memory_file}: {e}")

    def clear_memory(self):
        """Clear the conversation history and delete the memory file."""
        self._conversation_history.clear()
        if self._memory_file.exists():
            self._memory_file.unlink()
        print(f"Memory cleared for session: {self._session_id}")

    def get_session_id(self) -> str:
        """Get the current session ID."""
        return self._session_id

    def _agent_node(self, state: AgentState):
        """The agent node that calls the model."""
        messages = state["messages"]
        
        # Stream the response and collect it
        next_message = None
        start = True
        
        for chunk in self._chat_model.stream(messages):
            self._output_stream(chunk, start=start)
            start = False
            if next_message is None:
                next_message = chunk
            else:
                next_message += chunk
        
        print()  # Add newline after streaming
        
        # Add the AI message to conversation history
        if hasattr(self, '_conversation_history') and next_message:
            self._conversation_history.append(next_message)
        
        return {
            "messages": [next_message]
        }

    def _add_next_step_node(self, state: AgentState):
        """Add NextStepPrompt after tool calls to maintain proper message sequence."""
        return {
            "messages": [HumanMessage(prompts.NextStepPrompt)]
        }

    def _should_continue(self, state: AgentState):
        """Determine whether to continue or end the conversation."""
        messages = state["messages"]
        last_message = messages[-1]
        
        # If there are tool calls, continue to tools
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "continue"
        
        # Otherwise, end
        return "end"

    def ask(self, question: str):
        """Ask a question to the agent - maintains the same interface as ElpisAgent."""
        # Add the new user question to conversation history
        user_message = HumanMessage(question)
        self._conversation_history.append(user_message)
        
        # Prepare initial state with system messages and full conversation history
        initial_messages = self._system_messages + self._conversation_history
        
        # Run the graph - it will automatically handle tool calls and state transitions
        result = self._graph.invoke({"messages": initial_messages})
        
        # Extract and save the new messages from the result
        if result and "messages" in result:
            new_messages = result["messages"]
            # Add new AI and tool messages to conversation history
            for msg in new_messages:
                if not isinstance(msg, (SystemMessage,)) and msg not in self._conversation_history:
                    self._conversation_history.append(msg)
        
        # Save the updated conversation history
        self._save_memory()

    def _output_stream(self, message: BaseMessage, start: bool = False):
        """Output streaming content - maintains the same interface as ElpisAgent."""
        if message.content and message.content != END:
            if start:
                print(f"[{self.__name__}]: ", end="", flush=True)
            print(message.content, end="", flush=True)

    def _output(self, message: BaseMessage):
        """Output complete message - maintains the same interface as ElpisAgent."""
        if message.content and message.content != END:
            print(f"[{self.__name__}]: {message.content}", flush=True)