# ⚠️ Deprecated

This local MCP server is deprecated and no longer receives updates. Use the Fibery remote MCP server instead:

- **Claude**: install the [Fibery connector](https://claude.ai/directory/fibery) from the Claude directory.
- **ChatGPT**: install the [Fibery app](https://chatgpt.com/plugins/plugin_asdk_app_6a2ab6b4009c8191b74cb3b2c70025e3) in ChatGPT.
- **Cursor**: add `{"mcpServers": {"fibery": {"url": "https://mcp.fibery.io/mcp"}}}` to `~/.cursor/mcp.json`.
- **Claude Code**: `claude mcp add --transport http fibery https://mcp.fibery.io/mcp`

For other clients, see [Connecting to Fibery MCP](https://developers.fibery.com/guides/mcp/connecting#connecting-to-fibery-mcp).

---

## Legacy (unsupported)

These instructions are kept for reference only. This server no longer receives fixes or updates.

### Prerequisites
- A Fibery account with an API token
- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv)

### Installation
1. Install the tool using uv:
```bash
uv tool install fibery-mcp-server
```

2. Then, add this configuration to your MCP client config file. In Claude Desktop, you can access the config in **Settings → Developer → Edit Config**:
```json
{
    "mcpServers": {
        "fibery-mcp-server": {
            "command": "uv",
            "args": [
                 "tool",
                 "run",
                 "fibery-mcp-server",
                 "--fibery-host",
                 "your-domain.fibery.io",
                 "--fibery-api-token",
                 "your-api-token"
            ]
        }
    }
}
```
Note: If "uv" command does not work, try absolute path (i.e. /Users/username/.local/bin/uv)

**For Development:**

```json
{
    "mcpServers": {
        "fibery-mcp-server": {
            "command": "uv",
            "args": [
                "--directory",
                "path/to/cloned/fibery-mcp-server",
                "run",
                "fibery-mcp-server",
                "--fibery-host",
                 "your-domain.fibery.io",
                 "--fibery-api-token",
                 "your-api-token"
            ]
        }
    }
}
```
