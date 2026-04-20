"""
CLI entry point for lightdash-mcp.
"""

from __future__ import annotations

import sys

from lightdash_mcp.server import run


def main() -> None:
    """CLI entry point."""
    mode = sys.argv[1] if len(sys.argv) > 1 else "stdio"
    run(mode=mode)


if __name__ == "__main__":
    main()
