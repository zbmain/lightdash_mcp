# Contributing to lightdash-mcp

Thank you for your interest in contributing!

## Development Setup

```bash
# Clone the repo
git clone https://github.com/zbmain/lightdash_mcp.git
cd lightdash_mcp

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Install dev dependencies
uv add --dev ruff pytest
```

## Code Style

We use **Ruff** for linting and formatting:

```bash
# Check code
just check

# Auto-fix linting issues
just fix

# Format code
just fmt
```

## Running Tests

```bash
just test
```

## Adding a New Tool

1. Create a new file in `lightdash_mcp/tools/` (e.g., `my_new_tool.py`)
2. Define `TOOL_DEFINITION` and `run()` function
3. Add entry to `lightdash_mcp/tools_registry.yml` with `enabled: true`
4. Restart the server — the tool is auto-registered

See the full guide in `README.md`.

## Submitting Changes

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make your changes and run `just check` and `just test`
4. Commit with a clear message
5. Open a Pull Request

## Reporting Issues

Please open a GitHub Issue with:
- A clear description of the problem
- Steps to reproduce
- Your environment (Python version, Lightdash version, etc.)
