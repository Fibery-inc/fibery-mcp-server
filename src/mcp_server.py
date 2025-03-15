import logging
import sys
logging.basicConfig(level=logging.INFO, stream=sys.stderr)

import mcp
from pydantic import AnyUrl
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import click
import asyncio
from typing import List
from fibery_service import FiberyClient
from utils import databases_from_schema


async def serve(fibery_host: str, fibery_api_token: str) -> Server:
    server = Server("Fibery")
    logger = logging.getLogger(__name__)
    fibery_client = FiberyClient(fibery_host, fibery_api_token)

    @server.list_resources()
    async def list_resources() -> List[mcp.types.Resource]:
        return [
            mcp.types.Resource(
                uri=AnyUrl("fibery://databases"),
                name="Fibery Databases",
                description="List of all databases (their names) in the Fibery workspace"
            )
        ]

    @server.read_resource()
    async def read_resource(uri: AnyUrl) -> str:
        logger.info(f'Requested resource with uri: {uri}')
        if str(uri) == "fibery://databases":
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
        else:
            raise ValueError(f"No resource '{uri}' found.")

    return server


@click.command()
@click.option(
    "--fibery-host",
    envvar="FIBERY_HOST",
    required=True,
    help="Fibery host (your-account.fibery.io)",
)
@click.option(
    "--fibery-api-token",
    envvar="FIBERY_API_TOKEN",
    required=True,
    help="Fibery API Token",
)
def main(fibery_host: str, fibery_api_token: str):
    async def _run():
        async with mcp.stdio_server() as (read_stream, write_stream):
            server = await serve(fibery_host, fibery_api_token)
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="Fibery MCP",
                    server_version="0.0.1",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )

    asyncio.run(_run())


if __name__ == '__main__':
    asyncio.run(main())
