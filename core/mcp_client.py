import asyncio
import json 
import os
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

Server_script = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "mcp_server",
    "company_info_server.py"
)

async def _call_tool_async(
        tool_name: str,
        arguments: dict
) -> str:
    
    server_params = StdioServerParameters(
        command= sys.executable,
        args = [Server_script]
    )

    #start mcp server subprocess
    async with stdio_client(server_params) as (read,write):

        async with ClientSession(read, write) as session:

            await session.initialize()

            result = await session.call_tool(
                tool_name,
                arguments= arguments
            )

            if not result.content:
                return ""
            
            outputs = []
            for item in result.content:
                if hasattr(item, "text"):
                    outputs.append(item.text)
                else:
                    outputs.append(str(item))
            return "\n".join(outputs)

def call_mcp_tool(
        tool_name: str,
        arguments: dict
) -> dict:
    
    """Synchronus wrapper around asynchronus MCP call"""

    raw_text = asyncio.run(
        _call_tool_async(
            tool_name,
            arguments
        )
    )

    return json.loads(raw_text)