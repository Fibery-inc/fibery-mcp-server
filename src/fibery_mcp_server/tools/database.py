from typing import List, Dict, Any

import mcp

from fibery_mcp_server.fibery_client import FiberyClient
from fibery_mcp_server.utils import get_database_by_name, process_fields

database_tool_name = "describe_database"
database_tool = mcp.types.Tool(
    name=database_tool_name,
    description="Get list of all fields (in format of 'Title [name]: type') in the selected Fibery database",
    inputSchema={
        "type": "object",
        "properties": {
            "database_name": {
                "type": "string",
                "description": "Database name as defined in Fibery schema"
            }
        }
    },
)


async def handle_database(fibery_client: FiberyClient, arguments: Dict[str, Any]) -> List[mcp.types.TextContent]:
    schema = await fibery_client.get_schema()

    database_name = arguments.get("database_name")
    if not database_name:
        return [mcp.types.TextContent(type="text", text=f"Error: database_name is not provided.")]

    database = get_database_by_name(schema["fibery/types"], database_name)
    if not database:
        return [mcp.types.TextContent(type="text", text=f"Error: database {database_name} was not found.")]


    db_fields = database["fibery/fields"]

    # Format the output nicely
    if not db_fields:
        return [mcp.types.TextContent(type="text", text=f"There are no fields found in this Fibery database.")]

    prettified_fields = process_fields(schema["fibery/types"], db_fields)

    content = f"Fields in {database_name}:\n\n"
    for field in prettified_fields:
        content += f"{field['title']} [{field['name']}]: {field['type']}\n"

    return [mcp.types.TextContent(type="text", text=content)]
