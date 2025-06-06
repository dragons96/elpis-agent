import hashlib
import os
from typing import Annotated, Sequence, TypedDict

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.types import interrupt, Command

from elpis import tools, constants, prompts
from elpis.factories import model_factory, checkpointer_factory
from elpis.i18n import en


class AgentState(TypedDict):
    """The state of the agent."""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    pending_tool_calls: list | None  # 待确认的工具调用
    user_confirmation: str | None    # 用户确认结果


class LangGraphElpisAgent:
    """LangGraph implementation of ElpisAgent with the same interface."""
    __name__ = constants.AI_AGENT_NAME
    
    # 需要用户确认的危险操作工具
    DANGEROUS_TOOLS = {
        'create_file',
        'delete_file', 
        'edit_file',
        'run_terminal_cmd'
    }

    def __init__(self, chat_model: BaseChatModel = None,
                 session_id: str = None,
                 lang = en):
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

        # Initialize checkpointer
        self._memory = checkpointer_factory.new_checkpointer(
            os.getenv('CHECKPOINTER')
        )

        # Build the graph
        self._graph = self._build_graph()
        self._lang = lang

    def _build_graph(self):
        """Build the LangGraph workflow."""
        # Create the tool node
        tool_node = ToolNode(tools.TOOLS)

        # Define the graph
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("agent", self._agent_node)
        workflow.add_node("user_confirmation_node", self._user_confirmation_node)
        workflow.add_node("tools", tool_node)

        # Set entry point
        workflow.set_entry_point("agent")

        # Add conditional edges
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "user_confirmation_node",
                "end": END,
            }
        )
        
        # Add conditional edges from user confirmation
        workflow.add_conditional_edges(
            "user_confirmation_node",
            self._handle_confirmation,
            {
                "approved": "tools",
                "no_confirmation_needed": "tools",
                "rejected": "agent",
            }
        )

        # Add edge from tools back to agent
        workflow.add_edge("tools", "agent")

        # Compile with checkpointer for memory
        return workflow.compile(checkpointer=self._memory)

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

    def _user_confirmation_node(self, state: AgentState):
        """用户确认节点，检查是否需要用户确认危险操作"""
        messages = state["messages"]
        last_message = messages[-1]
        
        if not (hasattr(last_message, 'tool_calls') and last_message.tool_calls):
            return {"pending_tool_calls": None, "user_confirmation": None}
        
        # 检查是否有需要确认的危险操作
        dangerous_calls = []
        for tool_call in last_message.tool_calls:
            if tool_call['name'] in self.DANGEROUS_TOOLS:
                dangerous_calls.append(tool_call)
        
        if not dangerous_calls:
            return {"pending_tool_calls": None, "user_confirmation": None}
        
        # 对每个危险操作单独进行确认
        confirmed_calls = []
        cancelled_calls = []
        
        for tool_call in dangerous_calls:
            tool_name = tool_call['name']

            explanation = tool_call.get('args', {}).get('explanation', '')

            # 使用 interrupt 暂停执行，等待用户输入
            confirmation = interrupt({
                "message": f"""{explanation}
{self._lang.HUMAN_OPERATION_ALLOW_MESSAGE.format(tool_name)}""",
                "tool_call": tool_call,
            })
            
            # 处理用户确认结果
            if confirmation and confirmation.lower().strip() in ['y', 'yes', '是', '确认']:
                confirmed_calls.append(tool_call)
            else:
                cancelled_calls.append(tool_call)
        
        # 如果有被取消的操作，创建取消消息
        if cancelled_calls:
            cancelled_messages = []
            for tool_call in cancelled_calls:
                tool_message = ToolMessage(
                    content=f"operation cancelled: {tool_call['name']}",
                    tool_call_id=tool_call['id']
                )
                cancelled_messages.append(tool_message)
            
            # 更新消息列表，移除被取消的工具调用
            updated_last_message = last_message
            if hasattr(updated_last_message, 'tool_calls'):
                # 只保留确认的工具调用
                confirmed_tool_call_ids = {call['id'] for call in confirmed_calls}
                updated_tool_calls = [call for call in updated_last_message.tool_calls 
                                    if call['id'] in confirmed_tool_call_ids or call['name'] not in self.DANGEROUS_TOOLS]
                updated_last_message.tool_calls = updated_tool_calls
            
            return {
                "messages": cancelled_messages,
                "pending_tool_calls": confirmed_calls if confirmed_calls else None,
                "user_confirmation": "partial" if confirmed_calls else "all_rejected"
            }
        
        return {
            "pending_tool_calls": confirmed_calls,
            "user_confirmation": "approved"
        }
    
    def _handle_confirmation(self, state: AgentState):
        """处理用户确认结果"""
        pending_calls = state.get("pending_tool_calls")
        confirmation = state.get("user_confirmation")
        
        # 如果没有待确认的操作，直接执行工具
        if not pending_calls:
            return "no_confirmation_needed"
        
        # 处理用户确认结果
        if confirmation in ("approved", "partial"):
            return "approved"
        else:
            return "rejected"
    
    def _should_continue(self, state: AgentState):
        """Determine whether to continue or end the conversation."""
        messages = state["messages"]
        last_message = messages[-1]

        # If there are tool calls, continue to user confirmation
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

        initial_messages = self._system_messages + [user_message]

        # Run the graph with checkpointing
        result = self._graph.invoke({"messages": initial_messages}, config=config)
        
        # 处理中断情况（用户确认）
        if '__interrupt__' in result:
            interrupts = result['__interrupt__']
            for interrupt_info in interrupts:
                if interrupt_info.resumable:
                    interrupt_data = interrupt_info.value
                    message = interrupt_data.get('message', '请确认操作 (y/n): ')
                    
                    # 获取用户输入
                    try:
                        user_input = input(f'[{self.__name__}]: {message}').strip()
                        # 使用 Command 恢复执行
                        result = self._graph.invoke(Command(resume=user_input), config=config)
                        
                        # 如果还有中断，继续处理（支持多个工具的单独确认）
                        while '__interrupt__' in result:
                            interrupt_info = result['__interrupt__'][0]
                            if interrupt_info.resumable:
                                interrupt_data = interrupt_info.value
                                message = interrupt_data.get('message', '请确认操作 (y/n): ')
                                user_input = input(f'[{self.__name__}]: {message}').strip()
                                result = self._graph.invoke(Command(resume=user_input), config=config)
                            else:
                                break
                    except KeyboardInterrupt:
                        return
                    except Exception as e:
                        return

    def _output_stream(self, message: BaseMessage, start: bool = False):
        """Output streaming content - maintains the same interface as ElpisAgent."""
        if message.content != END:
            if start:
                print(f"[{self.__name__}]: ", end="", flush=True)
            if message.content:
                print(message.content, end="", flush=True)

    def _output(self, message: BaseMessage):
        """Output complete message - maintains the same interface as ElpisAgent."""
        if message.content and message.content != END:
            print(f"[{self.__name__}]: {message.content}", flush=True)

    @property
    def graph(self):
        return self._graph
