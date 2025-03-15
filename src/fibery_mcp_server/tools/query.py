from typing import Dict, Any, List

import mcp

from fibery_mcp_server.fibery_client import FiberyClient

query_tool_name = "query_database"
query_tool = mcp.types.Tool(
    name=query_tool_name,
    description="Run any Fibery API command. This gives tremendous flexibility, but requires a bit of experience with the low-level Fibery API. In case query succeeded, return value contains a list of records with fields you specified in select. If request failed, will return detailed error message.",
    inputSchema={
        "type": "object",
        "properties": {
            "q_from": {
                "type": "string",
                "description": 'Specifies the entity type in "Space/Type" format (e.g., "Product Management/feature", "Product Management/Insight")'
            },
            "q_select": {
                "type": "object",
                "description": "\n".join([
                    'Defines what fields to retrieve. Can include:',
                    '  - Primitive fields using format {"AliasName": "FieldName"} (i.e. {"Name": "Product Management/Name"})',
                    '  - Related entity fields using format {"AliasName": ["Related entity", "related entity field"]} (i.e. {"Secret": ["Product Management/Description", "Collaboration~Documents/secret"]}). Careful, does not work with 1-* connection!',
                    'To work with 1-* relationships, you can use sub-querying: {"AliasName": {"q/from": "Related type", "q/select": {"AliasName 2": "fibery/id"}, "q/limit": 50}}',
                    'AliasName can be of any arbitrary value.',
                ])
            },
            "q_where": {
                "type": "object",
                "description": "\n".join([
                    'Filter conditions in format [operator, [field_path], value] or ["q/and"|"q/or", ...conditions]. Common usages:',
                    '- Simple comparison: ["=", ["field", "path"], "$param"]. You cannot pass value of $param directly in where clause. Use params object instead. Pay really close attention to it as it is not common practice, but that\'s how it works in our case!',
                    '- Logical combinations: ["q/and", ["<", ["field1"], "$param1"], ["=", ["field2"], "$param2"]]',
                    '- Available operators: =, !=, <, <=, >, >=, q/contains, q/not-contains, q/in, q/not-in',
                ])
            },
            "q_orderby": {
                "type": "object",
                "description": 'List of sorting criteria in format [[["field1"], "q/asc"], [["field2"], "q/desc"]]',
            },
            "q_limit": {
                "type": "int",
                "description": 'Number of results per page (defaults to 50). Maximum allowed value is 1000',
            },
            "q_offset": {
                "type": "int",
                "description": 'Number of results to skip. Mainly used in combination with limit and orderBy for pagination.',
            },
            "q_params": {
                "type": "object",
                "description": 'Dictionary of parameter values referenced in where using "$param" syntax. For example, {$fromDate: "2025-01-01"}',
            }
        },
        "required": ["q_from", "q_select"],
    },
)


async def handle_query(fibery_client: FiberyClient, arguments: Dict[str, Any]) -> List[mcp.types.TextContent]:
    base = {
        "q/from": arguments["q_from"],
        "q/select": arguments["q_select"],
        "q/limit": arguments.get("q_limit", 50),
    }
    optional = {k: v for k, v in {
        "q/where": arguments.get("q_where", None),
        "q/order-by": arguments.get("q_order_by", None),
        "q/offset": arguments.get("q_offset", None)
    }.items() if v is not None}
    query = base | optional

    commandResult = await fibery_client.execute_command(
        "fibery.entity/query",
        {
            "query": query,
            "params": arguments.get("params", None)
        })
    return [mcp.types.TextContent(type="text", text=str(commandResult))]
