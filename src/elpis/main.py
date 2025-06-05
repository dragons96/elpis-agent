import os
from typing import Literal

import click
from dotenv import load_dotenv

from elpis.agent import ElpisAgent
from elpis import constants, i18n, tools, codebase


@click.command(help=constants.USAGE)
@click.option('--env_file', default=None, help='Path to a .env file')
@click.option('--lang', default='en', type=click.Choice(['en', 'zh']), help='Language to use for the tool. Default is "en"')
@click.help_option('-h', '--help')
def main(
        env_file: str | None = None,
        lang: Literal['en', 'zh'] = 'en',
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

    agent = ElpisAgent()
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


if __name__ == '__main__':
    main()
