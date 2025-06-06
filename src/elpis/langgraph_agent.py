import os
import hashlib
import sqlite3
from pathlib import Path
from typing import Annotated, Sequence, TypedDict

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages

from elpis import tools, constants, prompts, model_factory


class AgentState(TypedDict):
    """The state of the agent."""
    messages: Annotated[Sequence[BaseMessage], add_messages]


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
            SystemMessage(prompts.ElpisPrompt),
        ]

        # Add custom system prompt if provided
        system_prompt = os.getenv('SYSTEM_PROMPT', default=constants.SYSTEM_PROMPT)
        if system_prompt:
            self._system_messages.append(SystemMessage(system_prompt))

        # Initialize session ID and SQLite memory
        self._session_id = session_id or self._generate_session_id()
        self._memory = self._init_sqlite_memory()

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

        # Add edge from tools back to agent
        workflow.add_edge("tools", "agent")

        # Compile with checkpointer for memory
        return workflow.compile(checkpointer=self._memory)

    def _init_sqlite_memory(self) -> SqliteSaver:
        """Initialize SQLite database for memory storage."""
        # Create .elpis directory if it doesn't exist
        elpis_dir = Path(os.getcwd()) / ".elpis"
        elpis_dir.mkdir(exist_ok=True)

        # Create SQLite database file path
        db_path = elpis_dir / "memory.db"

        # Create SQLite connection
        # check_same_thread=False is OK as SqliteSaver uses locks for thread safety
        conn = sqlite3.connect(str(db_path), check_same_thread=False)

        # Initialize and return SqliteSaver
        return SqliteSaver(conn)

    def _generate_session_id(self) -> str:
        """Generate a unique session ID based on timestamp."""
        import time
        timestamp = str(int(time.time()))
        random_hash = hashlib.md5(timestamp.encode()).hexdigest()[:8]
        return f"session_{random_hash}"

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

        return {
            "messages": [next_message],
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
        # Create user message
        user_message = HumanMessage(question)

        # Prepare config with thread_id for checkpointing
        config = RunnableConfig(**{"configurable": {"thread_id": self._session_id}})

        # Get current state to include system messages if this is the first message
        try:
            current_state = self._graph.get_state(config)
            if not current_state.values.get("messages"):
                # First message - include system messages
                initial_messages = self._system_messages + [user_message]
            else:
                # Subsequent messages - just add the user message
                initial_messages = [user_message]
        except Exception as e:
            # Fallback - include system messages
            initial_messages = self._system_messages + [user_message]

        # Run the graph with checkpointing
        self._graph.invoke({"messages": initial_messages}, config=config)

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
