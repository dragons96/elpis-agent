import asyncio
import os
import hashlib
from typing import Literal

import click
from dotenv import load_dotenv

from elpis import constants, i18n, tools
from elpis.factories import model_factory
from elpis.langgraph_agent import LangGraphElpisAgent
from elpis import mcp_servers


async def multi_line_run(agent, lang):
    question = input("[You]: ")
    content = ''
    while question.lower() not in ['q', 'quit']:
        if not question.strip():
            if content:
                await agent.ask(content)
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


async def run(agent, lang):
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
        await agent.ask(question)
        question = input("[You]: ")


async def _main(
        env_file: str | None = None,
        lang: Literal['en', 'zh'] = 'en',
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

    print(f"[{constants.AI_AGENT_NAME}] Using LangGraph implementation", flush=True)
    # Generate session_id based on current directory path MD5
    current_dir = os.getcwd()
    session_id = hashlib.md5(current_dir.encode('utf-8')).hexdigest()

    mcp_file_path = os.getenv('MCP_FILE_PATH', default=os.path.join(os.getcwd(), 'mcp.json'))
    mcp_tools = None
    if os.path.exists(mcp_file_path):
        mcp_tools = await mcp_servers.get_mcp_tools(mcp_file_path)

    chat_model = model_factory.new_model(
        os.getenv('CHAT_MODEL_KEY_PREFIX')
    )

    agent = LangGraphElpisAgent(
        chat_model=chat_model,
        session_id=session_id,
        lang=lang,
        mcp_tools=mcp_tools
    )

    if multi_mode:
        await multi_line_run(agent, lang)
    else:
        await run(agent, lang)


@click.command(help=constants.USAGE)
@click.option('--env_file', default=None, help='Path to a .env file')
@click.option('--lang', default='en', type=click.Choice(['en', 'zh']),
              help='Language to use for the tool. Default is "en"')
@click.option('--multi_mode', is_flag=True, default=False, help='Enable multi-line-mode (default: False)')
@click.help_option('-h', '--help')
def main(
        env_file: str | None = None,
        lang: Literal['en', 'zh'] = 'en',
        multi_mode: bool = False
):
    asyncio.run(_main(env_file, lang, multi_mode))


if __name__ == '__main__':
    main()
