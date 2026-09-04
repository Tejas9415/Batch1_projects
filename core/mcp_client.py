"""
mcp_client.py
-------------
LangGraph nodes NORMAL (sync) functions hote hain, MCP protocol ASYNC hai.
Yeh file dono ke beech ka pul hai.
"""

import asyncio
import json
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_SCRIPT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mcp_server", "company_info_server.py")


async def _call_tool_async(tool_name: str, arguments: dict) -> str:
    # sys.executable = EXACT wahi Python jo abhi chal raha hai - hardcoded
    # "python" string kai systems par fail hoti hai (sirf "python3" hota hai)
    server_params = StdioServerParameters(command=sys.executable, args=[SERVER_SCRIPT])
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)
            return result.content[0].text


def call_mcp_tool(tool_name: str, arguments: dict) -> dict:
    raw_text = asyncio.run(_call_tool_async(tool_name, arguments))
    return json.loads(raw_text)