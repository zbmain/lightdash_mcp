from typing import Any

from .. import lightdash_client as _lc
from .base_tool import ToolDefinition

TOOL_DEFINITION = ToolDefinition(
    name="get-project",
    description="""Get detailed information about a specific project.

Returns comprehensive project details including:
- Project configuration and settings
- Warehouse connection information
- dbt integration details
- Project metadata

**When to use:** When you need detailed configuration information about a specific project, such as its warehouse connection, dbt settings, or other metadata.

**Parameters:**
- project_uuid: Optional. If not provided, uses the current/default project.""",
    inputSchema={
        "properties": {
            "project_uuid": {
                "type": "string",
                "description": "Optional: UUID of the project. If not provided, uses current project from LIGHTDASH_PROJECT_UUID env var or first available project.",
            }
        },
    },
)


def get_project_uuid() -> str:
    """Get project UUID from context (HTTP client override) or env var, or fallback to first project."""
    # 优先使用 context 中的覆盖值（HTTP 模式下由中间件写入），否则用环境变量
    project_uuid = _lc._effective_project_uuid()
    if project_uuid:
        return project_uuid

    response = _lc.get("/api/v1/org/projects")
    projects = response.get("results", [])
    if not projects:
        raise ValueError("No projects found in this Lightdash instance.")

    return projects[0]["projectUuid"]


def run(project_uuid: str | None = None) -> dict[str, Any]:
    """Run the get project tool"""
    if not project_uuid:
        project_uuid = get_project_uuid()

    response = _lc.get(f"/api/v1/projects/{project_uuid}")
    return response.get("results", {})
