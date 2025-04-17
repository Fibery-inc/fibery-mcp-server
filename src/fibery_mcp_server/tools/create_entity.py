import os
from uuid import uuid4
from typing import List, Dict, Any

import mcp

from fibery_mcp_server.fibery_client import FiberyClient
from fibery_mcp_server.utils import create_entity_process_fields

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
                    "description": 'Dictionary that defines what fields to set in format {"FieldName": value} (i.e. {"Product Management/Name": "My new entity"}).',
                },
            },
            "required": ["database", "entity"],
        },
    )


async def handle_create_entity(fibery_client: FiberyClient, arguments: Dict[str, Any]) -> List[mcp.types.TextContent]:
    database_name: str = arguments.get("database")
    entity: Dict[str, Any] = arguments.get("entity")

    if not database_name:
        return [mcp.types.TextContent(type="text", text="Error: database is not provided.")]

    if not entity:
        return [mcp.types.TextContent(type="text", text="Error: entity is not provided.")]

    schema = await fibery_client.get_schema()
    database = schema.databases_by_name()[database_name]
    if not database:
        return [mcp.types.TextContent(type="text", text=f"Error: database {database_name} was not found.")]
    rich_text_fields, safe_entity = await create_entity_process_fields(fibery_client, schema, database, entity)

    safe_entity["fibery/id"] = str(uuid4())
    creation_result = await fibery_client.create_entity(database_name, safe_entity)

    if not creation_result.success:
        return [mcp.types.TextContent(type="text", text=str(creation_result))]

    if len(rich_text_fields) > 0:
        secrets_response = await fibery_client.query(
            {
                "q/from": database_name,
                "q/select": {
                    field["name"]: [field["name"], "Collaboration~Documents/secret"] for field in rich_text_fields
                },
                "q/limit": 1,
                "q/where": ["=", ["fibery/id"], "$id"],
            },
            {"$id": safe_entity["fibery/id"]},
        )

        for field, secret_response in zip(rich_text_fields, secrets_response.result):
            secret = secret_response.get(field["name"], None)
            if not secret:
                return [
                    mcp.types.TextContent(
                        type="text", text=f"Error: entity created, but could you populate document {field['name']}"
                    )
                ]
            doc_result = await fibery_client.create_or_update_document(secret, field["value"])
            if not doc_result.success:
                return [mcp.types.TextContent(type="text", text=str(doc_result))]

    public_id = creation_result.result["fibery/public-id"]
    url = fibery_client.compose_url(database_name.split("/")[0], database_name.split("/")[1], public_id)
    return [
        mcp.types.TextContent(
            type="text", text=str(f'Entity created successfully. fibery/id: "{safe_entity["fibery/id"]}" URL: "{url}"')
        )
    ]
