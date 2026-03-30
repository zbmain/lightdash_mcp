# Lightdash MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-compatible-green.svg)](https://modelcontextprotocol.io/)
[![PyPI](https://img.shields.io/pypi/v/lightdash-mcp.svg)](https://pypi.org/project/lightdash-mcp/)
[![GitHub stars](https://img.shields.io/github/stars/poddubnyoleg/lightdash_mcp)](https://github.com/poddubnyoleg/lightdash_mcp/stargazers)

> Connect Claude, Cursor, and other AI assistants to your Lightdash analytics using the Model Context Protocol (MCP).

A Model Context Protocol (MCP) server for interacting with [Lightdash](https://www.lightdash.com/), enabling LLMs to discover data, create charts, and manage dashboards programmatically.

## Features

This MCP server provides a comprehensive set of tools for the full data analytics workflow:

*   **Discovery**: Explore data catalogs, find tables/explores, and understand schemas
*   **Querying**: Execute queries with full filter, metric, and aggregation support
*   **Chart Management**: Create, read, update, and delete charts with complex visualizations
*   **Dashboard Management**: Build and manage dashboards with tiles, filters, and layouts
*   **Resource Organization**: Create and manage spaces for content organization

## Installation

### Prerequisites

*   Python 3.10+
*   A Lightdash instance (Cloud or self-hosted)
*   Lightdash Personal Access Token (obtain from your Lightdash profile settings)

### Quick Start with pip (Recommended)

```bash
pip install lightdash-mcp
```

### Quick Start with uvx

```bash
uvx lightdash-mcp
```

### Quick Start with pipx

```bash
pipx run lightdash-mcp
```

### Install from Source

```bash
git clone https://github.com/poddubnyoleg/lightdash_mcp.git
cd lightdash_mcp
pip install .
```

### Google Cloud IAP Support

If your Lightdash instance is behind [Google Cloud Identity-Aware Proxy](https://cloud.google.com/iap) (e.g. Cloud Run with `--iap`), install with the `iap` extra:

```bash
pip install lightdash-mcp[iap]
# or from source
pip install .[iap]
```

Set `IAP_ENABLED=true`. The server will sign a JWT (audience `{LIGHTDASH_URL}/*`) via the IAM Credentials API and attach it as `Proxy-Authorization: Bearer <jwt>` on every request. The `Authorization: ApiKey` header is preserved for Lightdash.

Both service account credentials and user credentials (Application Default Credentials / ADC) are supported:

**Service account credentials** (default in Cloud Run, GCE, etc.):
- The runtime service account needs `roles/iam.serviceAccountTokenCreator` on itself
- The runtime service account needs `roles/iap.httpsResourceAccessor` on the Cloud Run service

**User credentials (ADC)** (e.g. `gcloud auth application-default login`):
- Set `IAP_SA` to the service account email to impersonate for signing the JWT
- The user needs `roles/iam.serviceAccountTokenCreator` on the target service account
- The target service account needs `roles/iap.httpsResourceAccessor` on the Cloud Run service

## Configuration

### Environment Variables

The server requires the following environment variables:

| Variable | Required | Description | Example |
| :--- | :---: | :--- | :--- |
| `LIGHTDASH_TOKEN` | ✅ | Your Lightdash Personal Access Token | `ldt_abc123...` |
| `LIGHTDASH_URL` | ✅ | Base URL of your Lightdash Instance | `https://app.lightdash.cloud` |
| `CF_ACCESS_CLIENT_ID` | ❌ | Cloudflare Access Client ID (if behind CF Access) | - |
| `CF_ACCESS_CLIENT_SECRET` | ❌ | Cloudflare Access Client Secret (if behind CF Access) | - |
| `LIGHTDASH_PROJECT_UUID` | ❌ | Default project UUID (falls back to first available project) | `3fc2835f-...` |
| `IAP_ENABLED` | ❌ | Enable Google Cloud IAP authentication (`true`/`1`) | `true` |
| `IAP_SA` | ❌ | Service account email for IAP when using user credentials (ADC) | `sa@project.iam.gserviceaccount.com` |

### Getting Your Lightdash Token

1. Log into your Lightdash instance
2. Go to **Settings** → **Personal Access Tokens**
3. Click **Generate new token**
4. Copy the token (starts with `ldt_`)

### Usage with Claude Desktop

Add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "lightdash": {
      "command": "uvx",
      "args": ["lightdash-mcp"],
      "env": {
        "LIGHTDASH_TOKEN": "ldt_your_token_here",
        "LIGHTDASH_URL": "https://app.lightdash.cloud",
        "LIGHTDASH_PROJECT_UUID": "your-project-uuid"
      }
    }
  }
}
```
### Usage with Claude Code (CLI)

Create or edit `.mcp.json` in your project root:

```json
{
  "mcpServers": {
    "lightdash": {
      "type": "stdio",
      "command": "lightdash-mcp",
      "env": {
        "LIGHTDASH_URL": "https://your-lightdash-instance.com",
        "LIGHTDASH_TOKEN": "ldt_your_token_here",
        "LIGHTDASH_PROJECT_UUID": "your-project-uuid"
      }
    }
  }
}
```

Restart Claude Code and run `/mcp` to verify the server shows as connected.

> **Note**: Don't commit `.mcp.json` if it contains secrets — add it to `.gitignore`.

### Usage with Other MCP Clients

Export the environment variables before running:

```bash
export LIGHTDASH_TOKEN="ldt_your_token_here"
export LIGHTDASH_URL="https://app.lightdash.cloud"
lightdash-mcp
```

## Available Tools

### 📊 Discovery & Metadata

| Tool | Description |
| :--- | :--- |
| `list-projects` | List all available Lightdash projects |
| `get-project` | Get detailed information about a specific project |
| `list-explores` | List all available explores/tables in a project |
| `get-explore-schema` | Get detailed schema for a specific explore (dimensions, metrics, joins) |
| `list-spaces` | List all spaces (folders) in the project |
| `get-custom-metrics` | Get custom metrics defined in the project |

### 📈 Chart Management

| Tool | Description |
| :--- | :--- |
| `list-charts` | List all saved charts, optionally filtered by name |
| `search-charts` | Search for charts by name or description |
| `get-chart-details` | Get complete configuration of a specific chart |
| `create-chart` | Create a new saved chart with metric query and visualization config |
| `update-chart` | Update an existing chart's configuration (name, description, queries, visualization) |
| `run-chart-query` | Execute a chart's query and retrieve the data |
| `delete-chart` | Delete a saved chart |

### 📋 Dashboard Management

| Tool | Description |
| :--- | :--- |
| `list-dashboards` | List all dashboards in the project |
| `create-dashboard` | Create a new dashboard (empty or with tiles) |
| `duplicate-dashboard` | Clone an existing dashboard with a new name |
| `get-dashboard-tiles` | Get all tiles from a dashboard with optional full config |
| `get-dashboard-tile-chart-config` | Get complete chart configuration for a specific dashboard tile |
| `get-dashboard-code` | Get the complete dashboard configuration as code |
| `create-dashboard-tile` | Add a new tile (chart, markdown, or loom) to a dashboard |
| `update-dashboard-tile` | Update tile properties (position, size, content) |
| `rename-dashboard-tile` | Rename a dashboard tile |
| `delete-dashboard-tile` | Remove a tile from a dashboard |
| `update-dashboard-filters` | Update dashboard-level filters |
| `run-dashboard-tiles` | Execute one, multiple, or all tiles on a dashboard concurrently |

### 🔍 Query Execution

| Tool | Description |
| :--- | :--- |
| `run-chart-query` | Execute a saved chart's query and return data |
| `run-dashboard-tiles` | Run queries for dashboard tiles (supports bulk execution) |
| `run-raw-query` | Execute an ad-hoc metric query against any explore |

### 🗂️ Resource Management

| Tool | Description |
| :--- | :--- |
| `create-space` | Create a new space to organize charts and dashboards |
| `delete-space` | Delete an empty space |

## Project Structure

```
.
├── pyproject.toml              # Package configuration
├── lightdash_mcp/              # Main package
│   ├── __init__.py             # Package init
│   ├── server.py               # MCP server entry point
│   ├── lightdash_client.py     # Lightdash API client
│   └── tools/                  # Tool implementations
│       ├── __init__.py         # Auto-discovery and tool registry
│       ├── base_tool.py        # Base tool interface
│       └── *.py                # Individual tool implementations
├── README.md
└── LICENSE
```

## Development

### Adding a New Tool

The server automatically discovers and registers tools from the `tools/` directory. To add a new tool:

1.  **Create a new file** in `lightdash_mcp/tools/` (e.g., `my_new_tool.py`)

2.  **Define the tool**:
    ```python
    from pydantic import BaseModel, Field
    from .base_tool import ToolDefinition
    from .. import lightdash_client as client
    
    class MyToolInput(BaseModel):
        param1: str = Field(..., description="Description of param1")
    
    TOOL_DEFINITION = ToolDefinition(
        name="my-new-tool",
        description="Description of what this tool does",
        input_schema=MyToolInput
    )
    
    def run(param1: str) -> dict:
        """Execute the tool logic"""
        result = client.get(f"/api/v1/some/endpoint/{param1}")
        return result
    ```

3.  **Restart the server** - the tool will be automatically registered

### Tool Registry

Tools are automatically discovered via `tools/__init__.py`, which:
*   Scans the `tools/` directory for Python modules
*   Imports each module (excluding utility modules)
*   Registers tools by their `TOOL_DEFINITION.name`

### Testing

You can test individual tools by importing them:

```python
from tools import tool_registry

# List all registered tools
print(tool_registry.keys())

# Test a specific tool
result = tool_registry['list-projects'].run()
print(result)
```

## Troubleshooting

### Authentication Errors

If you see `401 Unauthorized` errors:
*   Verify your `LIGHTDASH_TOKEN` is correct and starts with `ldt_`
*   Check that the token hasn't expired
*   Ensure you have the necessary permissions in Lightdash

### Connection Errors

If you see connection errors:
*   Verify `LIGHTDASH_URL` is correct
*   For Lightdash Cloud: use `https://app.lightdash.cloud`
*   For self-hosted: use `https://your-domain.com`
*   If behind Cloudflare Access, ensure `CF_ACCESS_CLIENT_ID` and `CF_ACCESS_CLIENT_SECRET` are set
*   If behind Google Cloud IAP, ensure `IAP_ENABLED=true` is set, install with `pip install lightdash-mcp[iap]`, and verify the service account has `serviceAccountTokenCreator` on itself

### Tool Not Found

If a tool isn't showing up:
*   Check that the file is in the `tools/` directory
*   Ensure the file has a `TOOL_DEFINITION` variable
*   Verify the file isn't in the exclusion list in `tools/__init__.py`
*   Restart the MCP server

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add your changes with appropriate tests
4. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues and questions:
*   [Lightdash Documentation](https://docs.lightdash.com/)
*   [Lightdash Community Slack](https://join.slack.com/t/lightdash-community/shared_invite/)
*   [MCP Documentation](https://modelcontextprotocol.io/)
