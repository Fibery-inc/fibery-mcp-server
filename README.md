# Fibery MCP Server

This MCP (Model Context Protocol) server provides integration between Fibery and any LLM provider supporting the MCP protocol (e.g., Claude for Desktop), allowing you to interact with your Fibery workspace using natural language.

## ✨ Features
- Query Fibery entities using natural language
- Get information about your Fibery databases and their fields
- Create and update Fibery entities through conversational interfaces

## 📦 Installation

### Prerequisites

- A Fibery account with an API token
- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv)

```bash
uv tool install fibery-mcp-server
```

## 🔌 MCP Integration
Add this configuration to your MCP client config file. 

In Claude Desktop, you can access the config in **Settings → Developer → Edit Config**:
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