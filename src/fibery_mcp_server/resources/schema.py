import mcp
from pydantic import AnyUrl

from ..fibery_client import FiberyClient
from ..utils import databases_from_schema


schema_uri = "fibery://databases"
schema_resource = mcp.types.Resource(
    uri=AnyUrl(schema_uri),
    name="Fibery Databases",
    description="List of all databases (their names) in the Fibery workspace"
)


async def handle_schema(fibery_client: FiberyClient):
    """Handler for reading resource data"""
    try:
        schema = await fibery_client.get_schema()
        db_list = databases_from_schema(schema)

        # Format the output nicely
        if not db_list:
            content = "No databases found in this Fibery workspace."
        else:
            content = "Databases in Fibery workspace:\n\n"
            for i, db in enumerate(db_list, 1):
                content += f"{i}. {db}\n"

        return content
    except Exception as e:
        return f"Error retrieving databases: {str(e)}"
