from typing import Dict, Any

import mcp

from ..fibery_client import FiberyClient
from fibery_mcp_server.tools.schema import schema_tool_name, schema_tool, handle_schema


def handle_list_tools():
    return [schema_tool]


async def handle_tool_call(fibery_client: FiberyClient, name: str, arguments: Dict[str, Any]):
    if name == schema_tool_name:
        return await handle_schema(fibery_client)
    else:
        return [mcp.types.TextContent(type="text", text=f"Error: Unknown tool {name}")]


__all__ = [
    "handle_list_tools",
    "handle_tool_call",
]