import sys
import logging
import asyncio
from typing import List

import mcp
import click
from pydantic import AnyUrl
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions

from .fibery_client import FiberyClient
from .resources import list_all_resources, handle_resource


async def serve(fibery_host: str, fibery_api_token: str) -> Server:
    server = Server("fibery-mcp-server")
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    logger = logging.getLogger("fibery-mcp-server")
    fibery_client = FiberyClient(fibery_host, fibery_api_token)

    @server.list_resources()
    async def list_resources() -> List[mcp.types.Resource]:
        return list_all_resources()

    @server.read_resource()
    async def read_resource(uri: AnyUrl) -> str:
        logger.info(f'Requested resource with uri: {uri}')
        return await handle_resource(fibery_client, uri)

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
