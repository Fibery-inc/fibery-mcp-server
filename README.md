## Deprecated
This local MCP server is **deprecated**. We support **Remote MCP Server** now, which can be connected via this url: **https://mcp.fibery.io/mcp**.

See the [Fibery MCP Server guide](https://the.fibery.io/@public/User_Guide/Guide/Fibery-MCP-Server-401) for setup instructions.

This repository will no longer receive feature updates. Please migrate to the remote server.

## Installation

If you still want to use this server...

### Installing via Smithery

To install Fibery MCP Server for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@Fibery-inc/fibery-mcp-server):

```bash
npx -y @smithery/cli install @Fibery-inc/fibery-mcp-server --client claude
```

### Installing via UV
#### Pre-requisites:
- A Fibery account with an API token
- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv)

#### Installation Steps:
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
