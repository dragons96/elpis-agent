import click
from dotenv import load_dotenv

from elpis.agent import ElpisAgent


@click.command()
@click.option('--env_file', default=None, help='Path to a .env file')
def main(
        env_file: str | None = None,
):
    if env_file:
        load_dotenv(env_file)
    else:
        load_dotenv()

    agent = ElpisAgent()
    question = input("[You]: ")

    while question.lower() not in ['q', 'quit']:
        agent.ask(question)
        question = input("[You]: ")


if __name__ == '__main__':
    main()
