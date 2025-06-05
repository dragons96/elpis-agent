import click
from dotenv import load_dotenv

from elpis.agent import ElpisAgent
from elpis import constants


@click.command(help=constants.USAGE)
@click.option('--env_file', default=None, help='Path to a .env file')
@click.option('--lang', default='en', type=click.Choice(['en', 'zh']), help='Language to use for the tool. Default is "en"')
@click.help_option('-h', '--help')
def main(
        env_file: str | None = None,
        lang: str = 'en',
):
    print(constants.BANNER, flush=True)
    if lang == 'en':
        print(constants.WELCOME_INFO, flush=True)
    elif lang == 'zh':
        print(constants.WELCOME_INFO_ZH, flush=True)
    if env_file:
        load_dotenv(env_file)
    else:
        load_dotenv()

    agent = ElpisAgent()
    question = input("[You]: ")

    while question.lower() not in ['q', 'quit']:
        if question:
            agent.ask(question)
        question = input("[You]: ")


if __name__ == '__main__':
    main()
