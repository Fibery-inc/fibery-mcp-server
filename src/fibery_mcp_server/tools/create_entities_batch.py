import os
from uuid import uuid4
from typing import List, Dict, Any

import mcp

from fibery_mcp_server.fibery_client import FiberyClient, CommandResponse
from fibery_mcp_server.utils import create_entity_process_fields

create_entities_batch_tool_name = "create_entities_batch"


def create_entities_batch_tool() -> mcp.types.Tool:
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "descriptions", "create_entities_batch"), "r") as file:
        description = file.read()

    return mcp.types.Tool(
        name=create_entities_batch_tool_name,
        description=description,
        inputSchema={
            "type": "object",
            "properties": {
                "database": {
                    "type": "string",
                    "description": "Fibery Database where entities will be created.",
                },
                "entities": {
                    "type": "object",
                    "description": 'List of dictionaries that define what fields to set in format [{"FieldName": value}] (i.e. [{"Product Management/Name": "My new entity"}]).',
                },
            },
            "required": ["database", "entities"],
        },
    )


async def handle_create_entities_batch(fibery_client: FiberyClient, arguments: Dict[str, Any]) -> List[mcp.types.TextContent]:
    database_name: str = arguments.get("database")
    entities: List[Dict[str, Any]] = arguments.get("entities")

    if not database_name:
        return [mcp.types.TextContent(type="text", text="Error: database is not provided.")]

    if not entities or len(entities) == 0:
        return [mcp.types.TextContent(type="text", text="Error: entities is not provided.")]

    schema = await fibery_client.get_schema()
    database = schema.databases_by_name()[database_name]
    if not database:
        return [mcp.types.TextContent(type="text", text=f"Error: database {database_name} was not found.")]

    safe_entities = []
    rich_text_fields_map = {}
    for entity in entities:
        rich_text_fields, safe_entity = await create_entity_process_fields(fibery_client, schema, database, entity)
        safe_entity["fibery/id"] = str(uuid4())
        rich_text_fields_map[safe_entity["fibery/id"]] = rich_text_fields
        safe_entities.append(safe_entity)
    creation_batch_result = await fibery_client.create_entities_batch(database_name, safe_entities)

    if not creation_batch_result.success:
        return [mcp.types.TextContent(type="text", text=str(creation_batch_result))]

    entities_info = []
    for creation_result in creation_batch_result.result:
        creation_result_command = CommandResponse(creation_result["success"], creation_result["result"])
        rich_text_fields = rich_text_fields_map.get(creation_result_command.result["fibery/id"])
        if len(rich_text_fields_map.get(creation_result_command.result["fibery/id"])) > 0:
            secrets_response = await fibery_client.query(
                {
                    "q/from": database_name,
                    "q/select": {
                        field["name"]: [field["name"], "Collaboration~Documents/secret"] for field in rich_text_fields
                    },
                    "q/limit": 1,
                    "q/where": ["=", ["fibery/id"], "$id"],
                },
                {"$id": creation_result_command.result["fibery/id"]},
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

        public_id = creation_result_command.result["fibery/public-id"]
        url = fibery_client.compose_url(database_name.split("/")[0], database_name.split("/")[1], public_id)
        entities_info.append({"id": creation_result_command.result["fibery/id"], "public_id": public_id, "url": url})
    entities_info_str = list(map(lambda ent: f'\nfibery/id: "{ent["id"]}" URL: "{ent["url"]}"', entities_info))
    return [
        mcp.types.TextContent(
            type="text", text=str(f'{len(creation_batch_result.result)} entities created successfully.List of created entities:{entities_info_str}')
        )
    ]
