# Fibery MCP Server

This MCP (Model Context Protocol) server provides integration between Fibery and any LLM provider support MCP protocol (i.e., Claude for Desktop), allowing you to interact with your Fibery workspace using natural language.

## Features
- Query Fibery entities using natural language
- Get information about your Fibery databases and their fields

## Installation

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- A Fibery account with an API token

### Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/Fibery-inc/fibery-mcp-server.git
   cd fibery-mcp-server
   ```

2. Set up the virtual environment:
   ```bash
   uv init
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   uv sync
   ```
   
### 🔌 MCP Integration

Add this configuration to your MCP client config file:

```json
{
    "mcpServers": {
        "fibery-mcp-server": {
            "command": "/Users/max/.local/bin/uv",
            "args": [
                "--directory",
                "path/to/your/fibery-mcp-server",
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

### Available Tools

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