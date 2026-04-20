from fnmatch import fnmatch
from inspect import signature
from typing import Any

import humps

from .. import lightdash_client
from .base_tool import ToolDefinition
from .get_project import get_project_uuid

TOOL_DEFINITION = ToolDefinition(
    name="list-explores",
    description="""List all available explores/tables in the project catalog.

Returns a catalog of all tables/explores organized by project and dataset:
- Explore/table names
- Table descriptions
- SQL table references

**When to use:**
- To discover what tables/explores are available in the project
- To browse the data catalog and find relevant tables by description
- Before using get-explore-schema to get detailed field information

**Best practice:** Use this for initial discovery to find table names, then use get-explore-schema for detailed dimensions, metrics, and joins.

**Note:** This can return large amounts of data for projects with many explores.""",
    inputSchema={
        "properties": {
            "project_uuid": {
                "type": "string",
                "description": "Optional: UUID of the project. If not provided, uses current project.",
            },
            "database_name": {
                "type": "string",
                "description": "Optional: Filter explores by database name. Case-insensitive exact match.",
            },
            "tags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional: Filter explores that contain all of the specified tags.",
            },
            "schema_name": {
                "type": "string",
                "description": "Optional: Filter explores by schema name. Case-insensitive exact match.",
            },
            "group_label": {
                "type": "string",
                "description": "Optional: Filter explores by group label. Case-insensitive exact match.",
            },
            "name": {
                "type": "string",
                "description": "Optional: Filter explores by name. Supports wildcard '*' for partial matching (e.g., 'ads_*'). Case-insensitive.",
            },
        },
    },
)


def run(
    project_uuid: str | None = None,
    database_name: str | None = None,
    tags: list[str] | None = None,
    schema_name: str | None = None,
    group_label: str | None = None,
    name: str | None = None,
) -> dict[str, Any]:
    """Run the list explores tool with optional filtering."""
    if not project_uuid:
        project_uuid = get_project_uuid()

    response = lightdash_client.get(f"/api/v1/projects/{project_uuid}/explores")
    # 兼容不同响应格式
    if isinstance(response, str):
        raise Exception(f"Lightdash API returned non-JSON response: {response[:200]}")
    if not isinstance(response, (dict, list)):
        raise Exception(
            f"Lightdash API returned unexpected type: {type(response).__name__}"
        )
    results: list[dict[str, Any]] = (
        response.get("results", []) if isinstance(response, dict) else response
    )

    # Auto-build filters from function parameters (excluding project_uuid)
    for param in signature(run).parameters:
        if param == "project_uuid":
            continue
        val = locals()[param]
        if val:
            if param == "tags":
                # 支持列表：仅保留包含所有指定 tag 的记录（tag 字段缺失则排除）
                results = [
                    r
                    for r in results
                    if all(
                        t.lower()
                        in [
                            tag.lower()
                            for tag in (humps.decamelize(r).get("tags") or [])
                        ]
                        for t in val
                    )
                ]
            elif param == "name":
                # 支持*通配符：字段缺失或为空则排除
                results = [
                    r
                    for r in results
                    if fnmatch(
                        (humps.decamelize(r).get("name") or "").lower(), val.lower()
                    )
                ]
            else:
                # 普通相等：字段缺失或为空则排除
                results = [
                    r
                    for r in results
                    if (humps.decamelize(r).get(param) or "").lower() == val.lower()
                ]

    return {"status": "ok", "results": results}
