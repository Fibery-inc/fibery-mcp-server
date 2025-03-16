import sys
import logging
import asyncio
from typing import List, Dict, Any

import mcp
import click
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions

from .fibery_client import FiberyClient
from .tools import handle_list_tools, handle_tool_call


async def serve(fibery_host: str, fibery_api_token: str) -> Server:
    server = Server("fibery-mcp-server")
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    logger = logging.getLogger("fibery-mcp-server")
    fibery_client = FiberyClient(fibery_host, fibery_api_token)

    @server.list_tools()
    async def list_tools() -> List[mcp.types.Tool]:
        return handle_list_tools()

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> List[mcp.types.TextContent]:
        logger.info(f"Requested tool with uri: {name}")
        try:
            return await handle_tool_call(fibery_client, name, arguments)
        except Exception as e:
            logger.error(f"Tool error: {str(e)}")
            return [mcp.types.TextContent(type="text", text=f"Error: {str(e)}")]

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
def main(fibery_host: str, fibery_api_token: str) -> None:
    async def _run() -> None:
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
