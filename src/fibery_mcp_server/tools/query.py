import os
from copy import deepcopy
from typing import Dict, Any, List, Tuple

import mcp

from fibery_mcp_server.fibery_client import FiberyClient, Schema, Database

query_tool_name = "query_database"


def query_tool() -> mcp.types.Tool:
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "descriptions", "query"), "r") as file:
        description = file.read()

    return mcp.types.Tool(
        name=query_tool_name,
        description=description,
        inputSchema={
            "type": "object",
            "properties": {
                "q_from": {
                    "type": "string",
                    "description": 'Specifies the entity type in "Space/Type" format (e.g., "Product Management/feature", "Product Management/Insight")',
                },
                "q_select": {
                    "type": "object",
                    "description": "\n".join(
                        [
                            "Defines what fields to retrieve. Can include:",
                            '  - Primitive fields using format {"AliasName": "FieldName"} (i.e. {"Name": "Product Management/Name"})',
                            '  - Related entity fields using format {"AliasName": ["Related entity", "related entity field"]} (i.e. {"Secret": ["Product Management/Description", "Collaboration~Documents/secret"]}). Careful, does not work with 1-* connection!',
                            'To work with 1-* relationships, you can use sub-querying: {"AliasName": {"q/from": "Related type", "q/select": {"AliasName 2": "fibery/id"}, "q/limit": 50}}',
                            "AliasName can be of any arbitrary value.",
                        ]
                    ),
                },
                "q_where": {
                    "type": "object",
                    "description": "\n".join(
                        [
                            'Filter conditions in format [operator, [field_path], value] or ["q/and"|"q/or", ...conditions]. Common usages:',
                            '- Simple comparison: ["=", ["field", "path"], "$param"]. You cannot pass value of $param directly in where clause. Use params object instead. Pay really close attention to it as it is not common practice, but that\'s how it works in our case!',
                            '- Logical combinations: ["q/and", ["<", ["field1"], "$param1"], ["=", ["field2"], "$param2"]]',
                            "- Available operators: =, !=, <, <=, >, >=, q/contains, q/not-contains, q/in, q/not-in",
                        ]
                    ),
                },
                "q_order_by": {
                    "type": "object",
                    "description": 'List of sorting criteria in format {"field1": "q/asc", "field2": "q/desc"}',
                },
                "q_limit": {
                    "type": "integer",
                    "description": "Number of results per page (defaults to 50). Maximum allowed value is 1000",
                },
                "q_offset": {
                    "type": "integer",
                    "description": "Number of results to skip. Mainly used in combination with limit and orderBy for pagination.",
                },
                "q_params": {
                    "type": "object",
                    "description": 'Dictionary of parameter values referenced in where using "$param" syntax. For example, {$fromDate: "2025-01-01"}',
                },
            },
            "required": ["q_from", "q_select"],
        },
    )


def parse_q_order_by(q_order_by: Dict[str, str] | None) -> List[Tuple[List[str], str]] | None:
    if not q_order_by:
        return None
    return [([field], q_order) for field, q_order in q_order_by.items()]


def get_rich_text_fields(q_select: Dict[str, Any], database: Database) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    rich_text_fields = []
    safe_q_select = deepcopy(q_select)
    for field_alias, field_name in safe_q_select.items():
        if not isinstance(field_name, str):
            if isinstance(field_name, list):
                field_name = field_name[0]
        if database.fields_by_name().get(field_name, None).is_rich_text():
            rich_text_fields.append({"alias": field_alias, "name": field_name})
            safe_q_select[field_alias] = [field_name, "Collaboration~Documents/secret"]
    return rich_text_fields, safe_q_select


async def handle_query(fibery_client: FiberyClient, arguments: Dict[str, Any]) -> List[mcp.types.TextContent]:
    q_from, q_select = arguments["q_from"], arguments["q_select"]

    schema: Schema = await fibery_client.get_schema()
    database = schema.databases_by_name()[arguments["q_from"]]
    rich_text_fields, safe_q_select = get_rich_text_fields(q_select, database)

    base = {
        "q/from": q_from,
        "q/select": safe_q_select,
        "q/limit": arguments.get("q_limit", 50),
    }
    optional = {
        k: v
        for k, v in {
            "q/where": arguments.get("q_where", None),
            "q/order-by": parse_q_order_by(arguments.get("q_order_by", None)),
            "q/offset": arguments.get("q_offset", None),
        }.items()
        if v is not None
    }
    query = base | optional

    commandResult = await fibery_client.query(query, arguments.get("q_params", None))

    if not commandResult.success:
        return [mcp.types.TextContent(type="text", text=str(commandResult))]

    for i, entity in enumerate(commandResult.result):
        for field in rich_text_fields:
            secret = entity.get(field["alias"], None)
            if not secret:
                return [
                    mcp.types.TextContent(
                        type="text", text=f"Unable to get document content for entity {entity}. Field: {field}"
                    )
                ]
            entity[field["alias"]] = await fibery_client.get_document_content(secret)
    return [mcp.types.TextContent(type="text", text=str(commandResult))]
