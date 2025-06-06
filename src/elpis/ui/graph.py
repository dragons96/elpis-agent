import hashlib
import os

from dotenv import load_dotenv

if os.getenv('ELPIS_ENV_FILE'):
    load_dotenv(os.getenv('ELPIS_ENV_FILE'))
else:
    load_dotenv()

from elpis import constants, i18n, tools
from elpis.langgraph_agent import LangGraphElpisAgent


lang = os.getenv('LANG')
if not lang:
    lang = 'en'

print(constants.BANNER, flush=True)

lang = i18n.select_lang(lang)
print(lang.WELCOME_INFO, flush=True)

# initialize codebase
if os.getenv('EMBEDDING_MODEL_KEY_PREFIX'):
    tools.init_codebase(os.getcwd())

print(f"[{constants.AI_AGENT_NAME}] Using LangGraph implementation", flush=True)
# Generate session_id based on current directory path MD5
current_dir = os.getcwd()
session_id = hashlib.md5(current_dir.encode('utf-8')).hexdigest()
agent = LangGraphElpisAgent(session_id=session_id, lang=lang)

graph = agent.graph
