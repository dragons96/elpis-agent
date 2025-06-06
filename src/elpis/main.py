import os
import hashlib
from typing import Literal

import click
from dotenv import load_dotenv

from elpis.agent import ElpisAgent
from elpis.langgraph_agent import LangGraphElpisAgent
from elpis import constants, i18n, tools


def multi_line_run(agent, lang):
    question = input("[You]: ")
    content = ''
    while question.lower() not in ['q', 'quit']:
        if not question.strip():
            if content:
                agent.ask(content)
                content = ''
            question = input("[You]: ")
            continue
        if question.lower() in ('i', 'index'):
            if not tools.codebase:
                print(lang.NO_CODEBASE_INDEXED)
                question = input("[You]: ")
                continue
            tools.codebase.index_codebase()
            question = input("[You]: ")
            continue
        content += question + '\n'
        question = input("[You]: ")


@click.command(help=constants.USAGE)
@click.option('--env_file', default=None, help='Path to a .env file')
@click.option('--lang', default='en', type=click.Choice(['en', 'zh']),
              help='Language to use for the tool. Default is "en"')
@click.option('--use_langgraph', is_flag=True, default=False,
              help='Use LangGraph implementation instead of the original agent')
@click.option('--multi_mode', is_flag=True, default=False, help='Enable multi-line-mode (default: False)')
@click.help_option('-h', '--help')
def main(
        env_file: str | None = None,
        lang: Literal['en', 'zh'] = 'en',
        use_langgraph: bool = False,
        multi_mode: bool = False
):
    os.environ['LANG'] = lang
    print(constants.BANNER, flush=True)
    if env_file:
        load_dotenv(env_file)
    else:
        load_dotenv()

    lang = i18n.select_lang(lang)
    print(lang.WELCOME_INFO, flush=True)

    # initialize codebase
    if os.getenv('EMBEDDING_MODEL_KEY_PREFIX'):
        tools.init_codebase(os.getcwd())

    # Choose agent implementation based on flag or environment variable
    use_langgraph_impl = use_langgraph or os.getenv('USE_LANGGRAPH', '').lower() in ('true', '1', 'yes')

    if use_langgraph_impl:
        print(f"[{constants.AI_AGENT_NAME}] Using LangGraph implementation", flush=True)
        # Generate session_id based on current directory path MD5
        current_dir = os.getcwd()
        session_id = hashlib.md5(current_dir.encode('utf-8')).hexdigest()
        agent = LangGraphElpisAgent(session_id=session_id, lang=lang)
    else:
        print(f"[{constants.AI_AGENT_NAME}] Using original implementation", flush=True)
        agent = ElpisAgent()

    if multi_mode:
        multi_line_run(agent, lang)
    else:
        question = input("[You]: ")
        while question.lower() not in ['q', 'quit']:
            if not question.strip():
                question = input("[You]: ")
                continue
            if question.lower() in ('i', 'index'):
                if not tools.codebase:
                    print(lang.NO_CODEBASE_INDEXED)
                    question = input("[You]: ")
                    continue
                tools.codebase.index_codebase()
                question = input("[You]: ")
                continue
            agent.ask(question)
            question = input("[You]: ")


if __name__ == '__main__':
    main()
