import asyncio
import hashlib
import os

from dotenv import load_dotenv
from elpis import mcp_servers

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

mcp_file_path = os.getenv('MCP_FILE_PATH', default=os.path.join(os.getcwd(), 'mcp.json'))
mcp_tools = None
if os.path.exists(mcp_file_path):
    mcp_tools = asyncio.run(mcp_servers.get_mcp_tools(mcp_file_path))

agent = LangGraphElpisAgent(session_id=session_id, lang=lang,
                            mcp_tools=mcp_tools)

graph = agent.graph
