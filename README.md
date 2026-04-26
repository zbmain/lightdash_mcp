# Lightdash MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-compatible-green.svg)](https://modelcontextprotocol.io/)
[![PyPI](https://img.shields.io/pypi/v/lightdash-mcp.svg)](https://pypi.org/project/lightdash-mcp/)
[![GitHub stars](https://img.shields.io/github/stars/zbmain/lightdash_mcp)](https://github.com/zbmain/lightdash_mcp/stargazers)

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

*   Python 3.11+
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
git clone https://github.com/zbmain/lightdash_mcp.git
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

### HTTP Mode Configuration

HTTP mode requires additional environment variables:

| Variable | Required | Description | Example |
| :--- | :---: | :--- | :--- |
| `LIGHTDASH_MCP_HTTP_APIKEY` | ✅ | Fixed API key for HTTP endpoint authentication | `mashangying` |
| `LIGHTDASH_MCP_HTTP_HOST` | ❌ | HTTP server bind address (default: `0.0.0.0`) | `127.0.0.1` |
| `LIGHTDASH_MCP_HTTP_PORT` | ❌ | HTTP server port (default: `8080`) | `9000` |

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

### Usage with MCP Clients via HTTP (Remote Deployment)

For remote/multi-client deployments, run the server in HTTP mode:

```bash
# Install with HTTP dependencies
pip install lightdash-mcp[http]

# Start HTTP server (requires LIGHTDASH_MCP_HTTP_APIKEY env var)
LIGHTDASH_MCP_HTTP_APIKEY="your-apikey" \
LIGHTDASH_URL="https://app.lightdash.cloud" \
LIGHTDASH_TOKEN="ldt_your_token_here" \
lightdash-mcp http
```

HTTP clients connect with:

```
HTTP endpoint: http://host:port/mcp/   (GET  — SSE event stream)
HTTP endpoint: http://host:port/mcp/   (POST — client messages)
HTTP endpoint: http://host:port/messages/  (POST — client messages, alternative)
HTTP endpoint: http://host:port/health    (GET  — health check, no auth)
```

All MCP endpoints require `APIKEY: <your-apikey>` header (fixed plaintext, not JWT).

**Client credential override**: HTTP clients can override server-side Lightdash credentials per-request:

```
APIKEY: <your-apikey>                        # API key auth (required)
X-Lightdash-Url: https://custom.lightdash.cloud  # Override LIGHTDASH_URL
X-Lightdash-Token: ldt_client_token         # Override LIGHTDASH_TOKEN
X-Lightdash-Project-Uuid: project-uuid      # Override LIGHTDASH_PROJECT_UUID
```

Unset headers fall back to the server's environment variables.

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
| `list-table-field-values` | Search for unique field values in a specific table column |

### 📈 Chart Management

| Tool | Description |
| :--- | :--- |
| `list-charts` | List all saved charts, optionally filtered by name |
| `search-charts` | Search for charts by name or description |
| `get-chart-details` | Get complete configuration of a specific chart |
| `run-chart-query` | Execute a chart's query and retrieve the data |

### 📋 Dashboard Management

| Tool | Description |
| :--- | :--- |
| `list-dashboards` | List all dashboards in the project |
| `get-dashboard-tiles` | Get all tiles from a dashboard with optional full config |
| `get-dashboard-tile-chart-config` | Get complete chart configuration for a specific dashboard tile |
| `get-dashboard-code` | Get the complete dashboard configuration as code |
| `run-dashboard-tiles` | Execute one, multiple, or all tiles on a dashboard concurrently |

### 🔍 Query Execution

| Tool | Description |
| :--- | :--- |
| `run-chart-query` | Execute a saved chart's query and return data |
| `run-dashboard-tiles` | Run queries for dashboard tiles (supports bulk execution) |
| `run-raw-query` | Execute an ad-hoc metric query against any explore |

### 🗂 Query Results

| Tool | Description |
| :--- | :--- |
| `run-chart-query` | Execute a saved chart's query and return data |
| `run-dashboard-tiles` | Run queries for dashboard tiles (supports bulk execution) |
| `run-raw-query` | Execute an ad-hoc metric query against any explore |

### 🌐 External APIs

| Tool | Description |
| :--- | :--- |
| `run-question-annotation` | Annotate a natural language question for CPV entities (NER). Extracts time, group, brand, metric, and attribute entities from user questions. Requires `CPVMATCH_APIKEY` environment variable. |

## Project Structure

```
.
├── Justfile                     # Just commands for common development tasks
├── pyproject.toml               # Package configuration
├── lightdash_mcp/               # Main package
│   ├── __init__.py              # Package init
│   ├── server.py                # MCP server entry point
│   ├── lightdash_client.py      # Lightdash API client
│   ├── tools_registry.yml       # Tool registry configuration (YAML)
│   └── tools/                   # Tool implementations
│       ├── __init__.py          # Auto-discovery and tool registry (YAML filtered)
│       ├── base_tool.py         # Base tool interface
│       └── *.py                 # Individual tool implementations
├── deploy/                      # Docker deployment
│   ├── Dockerfile               # Multi-stage production Dockerfile
│   └── docker-compose.yml       # Container orchestration
├── README.md
└── LICENSE
```

## Development

Tools are automatically discovered and filtered via two mechanisms:

1. **Auto-discovery**: `tools/__init__.py` scans the `tools/` directory for Python modules
2. **YAML filtering**: Only tools with `enabled: true` in `tools_registry.yml` are registered

### tools_registry.yml

A centralized YAML configuration (`lightdash_mcp/tools_registry.yml`) controls which tools are active.

```yaml
tools:
  - name: list-projects
    category: discovery
    enabled: true   # ← only enabled tools are registered

  - name: list-explores
    category: discovery
    enabled: true
    defaults:        # ← optional parameter defaults (merged before tool call)
      tags:
        - "msy150"
```

Key features:
- **Enable/disable**: `enabled: true/false` controls registration
- **Categories**: group tools into logical categories (discovery, chart, dashboard, query, resource, external)
- **Parameter defaults**: `defaults` field injects default values into tool arguments (user values take precedence)

### Adding a New Tool

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

3.  **Register in YAML**: Add the tool entry to `tools_registry.yml` with `enabled: true`

4.  **Restart the server** — the tool will be automatically registered

### Validating the Registry

```bash
# Check that YAML config and discovered tools are in sync
just validate-registry
```

### Building a Docker Image

```bash
# Build and push image to Aliyun registry (linux/amd64)
just image
```

Image tag format: `registry.cn-hangzhou.aliyuncs.com/winwin/tool:lightdash-mcp-YYYYMMDDGIT`
Example: `registry.cn-hangzhou.aliyuncs.com/winwin/tool:lightdash-mcp-20260425f646`

Requires `docker buildx`. The build uses `uv sync` (not wheel) and requires internet access to PyPI. The `--no-cache` flag is used to ensure the latest dependency index is fetched. Override the PyPI mirror with `UV_INDEX_URL` if needed:

```bash
docker buildx build --build-arg UV_INDEX_URL=https://pypi.org/simple/ -f deploy/Dockerfile --load .
```

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
*   Verify your `LIGHTDASH_TOKEN` is correct and starts with `ldt_/ldpat_`
*   Check that the token hasn't expired
*   Ensure you have the necessary permissions in Lightdash

### Connection Errors

If you see connection errors:
*   Verify `LIGHTDASH_URL` is correct
*   For Lightdash Cloud: use `https://app.lightdash.cloud`
*   For self-hosted: use `https://your-domain.com`
*   If behind Cloudflare Access, ensure `CF_ACCESS_CLIENT_ID` and `CF_ACCESS_CLIENT_SECRET` are set
*   If behind Google Cloud IAP, ensure `IAP_ENABLED=true` is set, install with `pip install lightdash-mcp[iap]`, and verify the service account has `serviceAccountTokenCreator` on itself

### HTTP Mode Errors

If you see `401 Unauthorized` in HTTP mode:
*   Verify `LIGHTDASH_MCP_HTTP_APIKEY` is set on the server
*   Ensure the client sends `APIKEY: <your-apikey>` header (not JWT Bearer)
*   Check the apikey matches the server-side `LIGHTDASH_MCP_HTTP_APIKEY` value

If you see `500 MCP error`:
*   Check server logs for detailed error messages
*   Verify Lightdash credentials (URL and token) are correct

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

## Acknowledgments

* [poddubnyoleg/lightdash_mcp](https://github.com/poddubnyoleg/lightdash_mcp) - Original project this fork is based on.

## Support

For issues and questions:
*   [Lightdash Documentation](https://docs.lightdash.com/)
*   [Lightdash Community Slack](https://join.slack.com/t/lightdash-community/shared_invite/)
*   [MCP Documentation](https://modelcontextprotocol.io/)
