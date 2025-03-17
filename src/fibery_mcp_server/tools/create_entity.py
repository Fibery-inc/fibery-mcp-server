import os
from uuid import uuid4
from typing import List, Dict, Any

import mcp

from fibery_mcp_server.fibery_client import FiberyClient

create_entity_tool_name = "create_entity"


def create_entity_tool() -> mcp.types.Tool:
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "descriptions", "create_entity"), "r") as file:
        description = file.read()

    return mcp.types.Tool(
        name=create_entity_tool_name,
        description=description,
        inputSchema={
            "type": "object",
            "properties": {
                "database": {
                    "type": "string",
                    "description": "Fibery Database where to create an entity.",
                },
                "entity": {
                    "type": "object",
                    "description": 'Defines what fields to set in format {"FieldName": value} (i.e. {"Product Management/Name": "My new entity"}). Can include:',
                },
            },
        },
    )


async def handle_create_entity(fibery_client: FiberyClient, arguments: Dict[str, Any]) -> List[mcp.types.TextContent]:
    database_name: str = arguments.get("database")
    if not database_name:
        return [mcp.types.TextContent(type="text", text="Error: database is not provided.")]

    entity: Dict[str, Any] = arguments.get("entity")
    if not entity:
        return [mcp.types.TextContent(type="text", text="Error: entity is not provided.")]
    entity["fibery/id"] = str(uuid4())
    result = await fibery_client.create_entity(database_name, entity)
    return [mcp.types.TextContent(type="text", text=str(result))]
