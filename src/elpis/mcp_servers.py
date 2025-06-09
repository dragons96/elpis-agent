import json

from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient
from pydantic import BaseModel


class McpServer(BaseModel):
    command: str
    args: list[str]
    transport: str = 'stdio'


async def get_mcp_tools(mcp_file_path: str) -> list[BaseTool] | None:
    with open(mcp_file_path, 'r') as f:
        mcp_config = f.read()
    try:
        mcp_servers = json.loads(mcp_config)['mcpServers']
        # 参数校验与预处理
        mcp_servers = {name: McpServer(**config).model_dump() for name, config in mcp_servers.items()}
        mcp_client = MultiServerMCPClient(mcp_servers)
        return await mcp_client.get_tools()
    except Exception as e:
        return None
