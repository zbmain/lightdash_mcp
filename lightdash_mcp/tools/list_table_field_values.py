from typing import Any

from .. import lightdash_client as _lc
from .base_tool import ToolDefinition, ToolParameter
from .get_project import get_project_uuid

TOOL_DEFINITION = ToolDefinition(
    name="list-table-field-values",
    description="""Search for unique field values in a specific table column.

Returns distinct values for a given field, useful for:
- Populating filter dropdown options
- Validating filter values
- Understanding field cardinality

**Parameters:**
- table: The table/explore name (e.g. 'ads_yy_msy150_cube_brand_sales_m_view')
- field_id: The field ID (e.g. 'brand_name', will be expanded to 'table_brand_name')
- search: Optional search prefix to filter results (case-insensitive)
- limit: Optional max number of values to return (default: 500)

**Tip:** Use get-explore-schema first to find the correct field IDs for a table.""",
    inputSchema={
        "type": "object",
        "properties": {
            "table": ToolParameter(
                type="string",
                description="The table/explore name. Example: 'ads_yy_msy150_cube_brand_sales_m_view'",
            ),
            "field_id": ToolParameter(
                type="string",
                description="The field ID to get distinct values for. Example: 'brand_name', 'status', 'user_id'. This will be prefixed with the table name automatically.",
            ),
            "search": ToolParameter(
                type="string",
                description="Optional search prefix to filter values (case-insensitive). Returns values starting with this prefix.",
            ),
            "limit": ToolParameter(
                type="integer",
                description="Optional max number of values to return. Default: 50.",
            ),
        },
        "required": ["table", "field_id"],
    },
)


def _try_v2_field_values(
    project_uuid: str, table: str, field_id: str, search: str | None, limit: int
) -> dict[str, Any] | None:
    """Try the v2 field-values endpoint. Returns None if not available (404)."""
    payload: dict[str, Any] = {
        "table": table,
        "fieldId": field_id,
        "limit": limit,
    }
    if search:
        payload["search"] = search

    try:
        response = _lc.post(
            f"/api/v2/projects/{project_uuid}/query/field-values",
            data=payload,
        )
        return response
    except Exception as e:
        if "404" in str(e):
            return None  # v2 not available, fall back to v1
        raise


def _v1_field_values(
    project_uuid: str, table: str, field_id: str, search: str | None, limit: int
) -> dict[str, Any]:
    """Use v1 runQuery to get field values via single-dimension query."""
    # Build the full field ID: table_fieldname
    full_field_id = f"{table}_{field_id}"

    query_config: dict[str, Any] = {
        "exploreName": table,
        "dimensions": [full_field_id],
        "metrics": [],
        "limit": limit,
        "sorts": [{"fieldId": full_field_id, "descending": False}],
        "tableCalculations": [],
        "filters": {"dimensions": {"id": "root", "and": []}},
    }
    if search:
        # Apply prefix filter on the field
        query_config["filters"] = {
            "dimensions": {
                "id": "root",
                "and": [
                    {
                        "id": "search_filter",
                        "target": {"fieldId": full_field_id},
                        "operator": "startsWith",
                        "values": [f"{search}%"],
                    }
                ],
            }
        }

    response = _lc.post(
        f"/api/v1/projects/{project_uuid}/explores/{table}/runQuery",
        data=query_config,
    )

    rows = response.get("results", {}).get("rows", [])
    values = []
    for row in rows:
        cell = row.get(full_field_id, {})
        raw = cell.get("value", {}).get("raw")
        formatted = cell.get("value", {}).get("formatted")
        if raw is not None:
            values.append({"raw": raw, "formatted": formatted or raw})

    return {"status": "ok", "results": values, "count": len(values)}


def run(
    table: str,
    field_id: str,
    search: str | None = None,
    limit: int = 50,
) -> dict[str, Any]:
    """Run the list table field values tool.

    First tries the v2 /api/v2/projects/{uuid}/query/field-values endpoint.
    Falls back to v1 runQuery if v2 is not available (404).
    """
    project_uuid = get_project_uuid()

    # Try v2 first
    v2_result = _try_v2_field_values(project_uuid, table, field_id, search, limit)
    if v2_result is not None:
        return v2_result

    # Fall back to v1
    return _v1_field_values(project_uuid, table, field_id, search, limit)
