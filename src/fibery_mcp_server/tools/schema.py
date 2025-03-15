from typing import List

import mcp

from fibery_mcp_server.fibery_client import FiberyClient
from fibery_mcp_server.utils import databases_from_schema

schema_tool_name = "list_databases"
schema_tool = mcp.types.Tool(
    name=schema_tool_name,
    description="Get list of all databases (their names) in user's Fibery workspace (schema)",
    inputSchema={"type": "object"},
)


async def handle_schema(fibery_client: FiberyClient) -> List[mcp.types.TextContent]:
    schema = await fibery_client.get_schema()
    db_list = databases_from_schema(schema)

    # Format the output nicely
    if not db_list:
        content = "No databases found in this Fibery workspace."
    else:
        content = "Databases in Fibery workspace:\n\n"
        for i, db in enumerate(db_list, 1):
            content += f"{i}. {db}\n"

    return [mcp.types.TextContent(type="text", text=content)]
