# Fibery MCP Server
[![smithery badge](https://smithery.ai/badge/@Fibery-inc/fibery-mcp-server)](https://smithery.ai/server/@Fibery-inc/fibery-mcp-server)

This MCP (Model Context Protocol) server provides integration between Fibery and any LLM provider supporting the MCP protocol (e.g., Claude for Desktop), allowing you to interact with your Fibery workspace using natural language.

<a href="https://glama.ai/mcp/servers/@Fibery-inc/fibery-mcp-server">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@Fibery-inc/fibery-mcp-server/badge" alt="Fibery Server MCP server" />
</a>

## ✨ Features
- Query Fibery entities using natural language
- Get information about your Fibery databases and their fields
- Create and update Fibery entities through conversational interfaces

## 📦 Installation

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
        "arxiv-mcp-server": {
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

## 🚀 Available Tools

#### 1. List Databases (`list_databases`)

Retrieves a list of all databases available in your Fibery workspace.

#### 2. Describe Database (`describe_database`)

Provides a detailed breakdown of a specific database's structure, showing all fields with their titles, names, and types.

#### 3. Query Database (`query_database`)

Offers powerful, flexible access to your Fibery data through the Fibery API.

#### 4. Create Entity (`create_entity`)

Creates new entities in your Fibery workspace with specified field values.

#### 5. Update Entity (`update_entity`) 

Updates existing entities in your Fibery workspace with new field values.