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
   uv add "mcp[cli]"
   ```
