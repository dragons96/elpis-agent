import os

from langchain_core.language_models import BaseChatModel
from . import tools, constants, prompts
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from langchain.chat_models import init_chat_model


class ElpisAgent:
    __name__ = constants.AI_AGENT_NAME

    def __init__(self, agent_model: BaseChatModel = None):
        self._tool_selector = {tool.name: tool for tool in tools.TOOLS}
        if agent_model:
            self._agent_model = agent_model.bind_tools(tools.TOOLS)
        else:
            self._agent_model = init_chat_model(
                model=os.getenv("MODEL"),
                model_provider="openai",
                base_url=os.getenv("OPENAI_BASE_URL"),
                temperature=float(os.getenv("TEMPERATURE", default="0.3"))
            ).bind_tools(tools.TOOLS)

        self._messages: list[BaseMessage] = [
            SystemMessage(prompts.ElpisPrompt),
            SystemMessage(prompts.DonePrompt),
        ]
        # add system prompt
        system_prompt = os.getenv('SYSTEM_PROMPT', default=constants.SYSTEM_PROMPT)
        if system_prompt:
            self._messages.append(SystemMessage(system_prompt))

    def ask(self, question: str):
        self._messages.append(HumanMessage(question))
        next_message = self._agent_model.invoke(self._messages)

        self._output(next_message)
        self._messages.append(next_message)
        while next_message.content != prompts.DONE:

            for tool_call in next_message.tool_calls:
                tool = self._tool_selector[tool_call["name"].lower()]
                tool_msg = tool.invoke(tool_call)
                self._messages.append(tool_msg)

            self._messages.append(HumanMessage(prompts.NextStepPrompt))

            next_message = self._agent_model.invoke(self._messages)

            self._output(next_message)
            self._messages.append(next_message)

    def _output(self, message: BaseMessage):
        if message.content and message.content != prompts.DONE:
            print(f"[{self.__name__}]: {message.content}")
