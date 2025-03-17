from typing import List, Dict, Any

import mcp

from fibery_mcp_server.utils import prettify_fields, PrettyField
from fibery_mcp_server.fibery_client import FiberyClient, Schema, Database, Field

database_tool_name = "describe_database"


def database_tool() -> mcp.types.Tool:
    return mcp.types.Tool(
        name=database_tool_name,
        description="Get list of all fields (in format of 'Title [name]: type') in the selected Fibery database and for all related databases.",
        inputSchema={
            "type": "object",
            "properties": {
                "database_name": {
                    "type": "string",
                    "description": "Database name as defined in Fibery schema",
                }
            },
            "required": ["database_name"],
        },
    )


def describe_database(database: str, fields: List[PrettyField]) -> str:
    content = f"Database {database}:\n"
    for field in fields:
        content += f"    {field.title} [{field.name}]: {field.type}\n"
    return content + "\n"


async def handle_database(fibery_client: FiberyClient, arguments: Dict[str, Any]) -> List[mcp.types.TextContent]:
    schema: Schema = await fibery_client.get_schema()

    database_name: str = arguments.get("database_name")
    if not database_name:
        return [mcp.types.TextContent(type="text", text="Error: database_name is not provided.")]

    database: Database | None = schema.databases_by_name().get(database_name, None)
    if not database:
        return [mcp.types.TextContent(type="text", text=f"Error: database {database_name} was not found.")]

    db_fields: List[Field] = database.fields

    if not db_fields:
        return [mcp.types.TextContent(type="text", text="There are no fields found in this Fibery database.")]

    prettified_fields, external_databases = await prettify_fields(
        fibery_client, schema, database, collect_external_databases=True
    )
    external_prettified_databases = [
        (db.name, (await prettify_fields(fibery_client, schema, db))[0]) for db in external_databases
    ]

    content = ""
    for db, fields in [(database.name, prettified_fields)] + external_prettified_databases:
        content += describe_database(db, fields)
    return [mcp.types.TextContent(type="text", text=content)]
