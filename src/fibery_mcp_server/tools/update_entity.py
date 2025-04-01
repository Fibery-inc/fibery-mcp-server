import os
from copy import deepcopy
from typing import List, Dict, Any, Tuple

import mcp

from fibery_mcp_server.fibery_client import FiberyClient, Schema, Database
from fibery_mcp_server.utils import str_to_bool

update_entity_tool_name = "update_entity"


def update_entity_tool() -> mcp.types.Tool:
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "descriptions", "update_entity"), "r") as file:
        description = file.read()

    return mcp.types.Tool(
        name=update_entity_tool_name,
        description=description,
        inputSchema={
            "type": "object",
            "properties": {
                "database": {
                    "type": "string",
                    "description": "Fibery Database where to update an entity.",
                },
                "entity": {
                    "type": "object",
                    "description": "\n".join(
                        [
                            'Dictionary that defines what fields to set in format {"FieldName": value} (i.e. {"Product Management/Name": "My new entity"}).',
                            'Exception are document fields. For them you must specify append (boolean, whether to append to current content) and content itself: {"Product Management/Description": {"append": true, "content": "Additional info"}}',
                        ]
                    ),
                },
            },
            "required": ["database", "entity"],
        },
    )


async def process_fields(
    fibery_client: FiberyClient, schema: Schema, database: Database, fields: Dict[str, Any]
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    rich_text_fields = []
    safe_fields = deepcopy(fields)
    for field_name, field_value in fields.items():
        # process rich-text fields
        if database.fields_by_name().get(field_name, None).is_rich_text():
            rich_text_fields.append(
                {"name": field_name, "append": str_to_bool(field_value["append"]), "value": field_value["content"]}
            )
            safe_fields.pop(field_name)

        # process enum fields
        field_type = database.fields_by_name().get(field_name, None).type
        if schema.databases_by_name()[field_type].is_enum():
            enum_values_response = await fibery_client.get_enum_values(field_type)
            enum_values = enum_values_response.result
            safe_fields[field_name] = {"fibery/id": next(filter(lambda e: e["Name"] == field_value, enum_values))["Id"]}

    return rich_text_fields, safe_fields


async def handle_update_entity(fibery_client: FiberyClient, arguments: Dict[str, Any]) -> List[mcp.types.TextContent]:
    database_name: str = arguments.get("database")
    entity: Dict[str, Any] = arguments.get("entity")

    if not database_name:
        return [mcp.types.TextContent(type="text", text="Error: database is not provided.")]

    if not entity:
        return [mcp.types.TextContent(type="text", text="Error: entity is not provided.")]

    if not entity["fibery/id"]:
        return [
            mcp.types.TextContent(
                type="text", text="Error: entity id is not provided. Use 'fibery/id' field to set it."
            )
        ]

    schema = await fibery_client.get_schema()
    database = schema.databases_by_name()[database_name]
    if not database:
        return [mcp.types.TextContent(type="text", text=f"Error: database {database_name} was not found.")]
    rich_text_fields, safe_entity = await process_fields(fibery_client, schema, database, entity)

    update_result = await fibery_client.update_entity(database_name, safe_entity)

    if not update_result.success:
        return [mcp.types.TextContent(type="text", text=str(update_result))]

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
            doc_result = await fibery_client.create_or_update_document(secret, field["value"], append=field["append"])
            if not doc_result.success:
                return [mcp.types.TextContent(type="text", text=str(doc_result))]

    public_id = await fibery_client.get_public_id_by_id(database_name, safe_entity["fibery/id"])
    url = fibery_client.compose_url(database_name.split("/")[0], database_name.split("/")[1], public_id)
    return [mcp.types.TextContent(type="text", text=str(f"Entity updated successfully. URL: {url}"))]
