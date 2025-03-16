from datetime import datetime
from typing import List

import mcp

current_date_tool_name = "current_date"


def current_date_tool() -> mcp.types.Tool:
    return mcp.types.Tool(
        name=current_date_tool_name,
        description="Get today's date in ISO 8601 format (YYYY-mm-dd.HH:MM:SS.000Z)",
        inputSchema={"type": "object"},
    )


async def handle_current_date() -> List[mcp.types.TextContent]:
    date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")
    return [mcp.types.TextContent(type="text", text=date)]
