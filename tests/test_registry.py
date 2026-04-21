"""Tool registry validation tests."""
from __future__ import annotations

from lightdash_mcp.tools import tool_registry, validate_registry


def test_tool_registry_not_empty():
    """Verify that at least one tool is registered."""
    assert len(tool_registry) > 0, "No tools registered — check tools_registry.yml"


def test_tool_registry_contains_expected_tools():
    """Verify core discovery tools are present."""
    expected = {"list-projects", "list-spaces", "list-dashboards"}
    missing = expected - set(tool_registry.keys())
    assert not missing, f"Expected tools not found: {missing}"


def test_validate_registry_passes():
    """Run the registry validation and ensure it completes without errors."""
    # validate_registry prints to stdout; just ensure it doesn't raise
    validate_registry()
