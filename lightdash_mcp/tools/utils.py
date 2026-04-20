import csv
import json
from io import StringIO
from typing import Any


def flatten_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Flattens Lightdash query results from:
    [{"field_id": {"value": {"raw": 123, "formatted": "123"}}}]
    to:
    [{"field_id": 123}]
    """
    flattened = []
    for row in rows:
        flat_row = {}
        for key, value in row.items():
            if isinstance(value, dict) and "value" in value and "raw" in value["value"]:
                flat_row[key] = value["value"]["raw"]
            else:
                flat_row[key] = value
        flattened.append(flat_row)
    return flattened


def format_as_csv(
    rows: list[dict[str, Any]], metadata: dict[str, Any] | None = None
) -> str:
    """
    Formats query results as CSV string.

    Args:
        rows: List of dictionaries (query results)
        metadata: Optional metadata to include as JSON comment at top

    Returns:
        CSV-formatted string with optional metadata header
    """
    if not rows:
        if metadata:
            return f"# Metadata: {json.dumps(metadata, separators=(',', ':'))}\n# No data rows\n"
        return "# No data rows\n"

    output = StringIO()

    # Add metadata as comment if provided
    if metadata:
        output.write(f"# Metadata: {json.dumps(metadata, separators=(',', ':'))}\n")

    # Write CSV data
    fieldnames = list(rows[0].keys())
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

    return output.getvalue()
