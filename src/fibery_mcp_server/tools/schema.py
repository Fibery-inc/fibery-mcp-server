from typing import List

import mcp

from fibery_mcp_server.fibery_client import FiberyClient, Schema, Database

schema_tool_name = "list_databases"


def schema_tool() -> mcp.types.Tool:
    return mcp.types.Tool(
        name=schema_tool_name,
        description="Get list of all databases (their names) in user's Fibery workspace (schema)",
        inputSchema={"type": "object"},
    )


async def handle_schema(fibery_client: FiberyClient) -> List[mcp.types.TextContent]:
    schema: Schema = await fibery_client.get_schema()
    db_list: List[Database] = schema.include_databases_from_schema()

    if not db_list:
        content = "No databases found in this Fibery workspace."
    else:
        content = "Databases in Fibery workspace:\n\n"
        for i, db in enumerate(db_list, 1):
            content += f"{i}. {db.name}\n"

    return [mcp.types.TextContent(type="text", text=content)]
