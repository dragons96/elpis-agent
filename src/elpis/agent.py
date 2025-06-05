import os

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage

from elpis import tools, constants, prompts, model_factory


class ElpisAgent:
    __name__ = constants.AI_AGENT_NAME

    def __init__(self,
                 chat_model: BaseChatModel = None,
                 ):
        self._tool_selector = {tool.name: tool for tool in tools.TOOLS}
        if chat_model:
            self._chat_model = chat_model.bind_tools(tools.TOOLS)
        else:
            self._chat_model = model_factory.new_model(
                os.getenv('CHAT_MODEL_KEY_PREFIX')
            ).bind_tools(tools.TOOLS)

        self._messages: list[BaseMessage] = [
            SystemMessage(prompts.ElpisPrompt),
            SystemMessage(prompts.DonePrompt),
        ]

        # add system prompt
        system_prompt = os.getenv('SYSTEM_PROMPT', default=constants.SYSTEM_PROMPT)
        if system_prompt:
            self._messages.append(SystemMessage(system_prompt))

    def _model_invoke(self):
        next_message = None
        start = True
        for chunk in self._chat_model.stream(self._messages):
            self._output_stream(chunk, start=start)
            start = False
            if next_message is None:
                next_message = chunk
            else:
                next_message += chunk
        print()
        self._messages.append(next_message)
        return next_message

    def ask(self, question: str):
        self._messages.append(HumanMessage(question))
        next_message = self._model_invoke()

        while next_message.content != prompts.DONE:

            for tool_call in next_message.tool_calls:
                tool = self._tool_selector[tool_call["name"].lower()]
                tool_msg = tool.invoke(tool_call)
                self._messages.append(tool_msg)

            self._messages.append(HumanMessage(prompts.NextStepPrompt))
            next_message = self._model_invoke()

    def _output_stream(self, message: BaseMessage, start: bool = False):
        if message.content and message.content != prompts.DONE:
            if start:
                print(f"[{self.__name__}]: ", end="", flush=True)
            print(message.content, end="", flush=True)

    def _output(self, message: BaseMessage):
        if message.content and message.content != prompts.DONE:
            print(f"[{self.__name__}]: {message.content}", flush=True)
