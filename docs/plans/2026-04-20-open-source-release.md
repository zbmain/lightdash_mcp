# Open Source Release Preparation — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` to implement this plan task-by-task.

**Goal:** Polish the `lightdash_mcp` project for open-source release — fix critical security and metadata issues, improve code quality, add missing open-source files, and ensure the README accurately reflects the codebase.

**Architecture:** Single-package Python project using Hatchling build system, MCP protocol, requests/httpx for API calls. The release prep focuses on: (1) security fixes (gitignore, .env removal), (2) metadata correctness (version sync, LICENSE, pyproject.toml), (3) documentation completeness (README accuracy, CONTRIBUTING, CHANGELOG), (4) code quality (deduplication, lint, ruff config), and (5) CI/CD infrastructure (GitHub Actions).

**Tech Stack:** Python 3.11+, Hatchling, Ruff, Pytest, requests, MCP (StreamableHTTP/STDIO), GitHub Actions, uv

---

## Task 1: Fix `.gitignore` — Complete and Remove Sensitive Files

**Files:**
- Modify: `.gitignore`
- Action: `git rm --cached .env .venv/ uv.lock .idea/ skills-lock.json .mcp.json 2>/dev/null || true`

**Step 1: Write the complete `.gitignore`**

```gitignore
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Distribution / packaging
build/
dist/
*.egg-info/
*.egg

# Environments
.env
.env.local
.env.*.local
.venv/
venv/
ENV/
env/

# IDE
.idea/
.vscode/
*.swp
*.swo
*~

# Testing
.pytest_cache/
.coverage
htmlcov/
*.cover

# Lint & type check
.ruff_cache/
.mypy_cache/

# Claude Code
.mcp.json
skills-lock.json

# uv lock (optional — some projects commit it, some don't)
uv.lock

# OS
.DS_Store
Thumbs.db

# Logs
*.log
```

**Step 2: Write the complete `.gitignore`**

Run: `cat > .gitignore << 'EOF'\n...\nEOF` (see content above)

**Step 3: Remove already-tracked sensitive files from git index**

Run: `git rm --cached .env .venv/ uv.lock .idea/ skills-lock.json .mcp.json 2>/dev/null; echo "done"`
Expected: No error

**Step 4: Commit**

```bash
git add .gitignore
git rm --cached .env .venv/ uv.lock .idea/ skills-lock.json .mcp.json
git commit -m "security: add comprehensive .gitignore and remove sensitive files from index"
```

---

## Task 2: Sync Version — `pyproject.toml` ↔ `__init__.py`

**Files:**
- Modify: `pyproject.toml`
- Modify: `lightdash_mcp/__init__.py`

**Step 1: Read current values**

Run: `grep "^version" pyproject.toml; grep "__version__" lightdash_mcp/__init__.py`
Expected: Shows `0.1.2` in pyproject.toml and `0.1.0` in __init__.py

**Step 2: Update both to `0.1.2` (keep pyproject.toml as source of truth, update __init__.py)**

In `pyproject.toml`:
```toml
[tool.hatch.version]
path = "lightdash_mcp/__init__.py"
```

In `lightdash_mcp/__init__.py`:
```python
__version__ = "0.1.2"
```

Or simply remove `[tool.hatch.version]` and keep `__version__` in `__init__.py` as the single source.

**Step 3: Commit**

```bash
git add pyproject.toml lightdash_mcp/__init__.py
git commit -m "chore: sync version to 0.1.2 in pyproject.toml and __init__.py"
```

---

## Task 3: Fix `pyproject.toml` — URLs, Authors, Keywords, Classifiers

**Files:**
- Modify: `pyproject.toml`

**Step 1: Read current content**

Run: `cat pyproject.toml`
Expected: Shows current content with wrong URLs

**Step 2: Update URLs section**

Change `poddubnyoleg/lightdash_mcp` → `zbmain/lightdash_mcp` in all URL fields.

**Step 3: Add missing fields**

Add `authors`, `keywords`, and `classifiers`:
```toml
authors = [{name = "zbmain", email = "zbmain@example.com"}]
keywords = ["lightdash", "mcp", "model-context-protocol", "analytics", "bi"]
classifiers = [
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Operating System :: OS Independent",
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Topic :: Scientific/Engineering :: Information Analysis",
]
```

Also add `license = {text = "MIT"}` if not already present, and add `anyio` to `http` extra deps.

**Step 4: Commit**

```bash
git add pyproject.toml
git commit -m "chore: add authors, keywords, classifiers to pyproject.toml and fix URLs"
```

---

## Task 4: Fix `LICENSE` Copyright Header

**Files:**
- Modify: `LICENSE`

**Step 1: Read current content**

Run: `head -3 LICENSE`
Expected: `Copyright (c) 2025 pd`

**Step 2: Update copyright line**

Change: `Copyright (c) 2025 pd` → `Copyright (c) 2025 zbmain`

**Step 3: Commit**

```bash
git add LICENSE
git commit -m "chore: update LICENSE copyright to zbmain"
```

---

## Task 5: Fix IAP Hardcoded Default Service Account

**Files:**
- Modify: `lightdash_mcp/lightdash_client.py`

**Step 1: Read the IAP section**

Run: `grep -n "wallet-data\|IAP_SA\|default" lightdash_mcp/lightdash_client.py`
Expected: Shows hardcoded `lightdash-cli-iap@wallet-data-483412.iam.gserviceaccount.com`

**Step 2: Remove hardcoded default**

Change:
```python
sa_email = os.getenv(
    "IAP_SA",
    "lightdash-cli-iap@wallet-data-483412.iam.gserviceaccount.com",
)
```
To:
```python
sa_email = os.getenv("IAP_SA", "")
```
And add a check that raises a clear error if `sa_email` is empty when IAP is enabled.

**Step 3: Commit**

```bash
git add lightdash_mcp/lightdash_client.py
git commit -m "security: remove hardcoded IAP service account default"
```

---

## Task 6: Enable Disabled Tools OR Fix README to Match Reality

**Files:**
- Modify: `lightdash_mcp/tools_registry.yml`
- Modify: `README.md`
- Modify: `README_CN.md`

**Decision point:** Enabling 11 tools that haven't been tested may introduce bugs. The safer choice is to update the README to only list enabled tools (the current reality), making the documentation accurate.

**Step 1: Identify disabled tools from registry**

Run: `grep -A1 "enabled: false" lightdash_mcp/tools_registry.yml | grep "name:"`
Expected: List of disabled tool names

**Step 2: Remove disabled tools from README tool tables**

In both `README.md` and `README_CN.md`, remove rows for:
- `create-space`, `delete-space`
- `create-chart`, `update-chart`, `delete-chart`
- `create-dashboard`, `duplicate-dashboard`
- `create-dashboard-tile`, `update-dashboard-tile`, `rename-dashboard-tile`, `delete-dashboard-tile`
- `update-dashboard-filters`

**Step 3: Commit**

```bash
git add README.md README_CN.md
git commit -m "docs: sync README tool tables with enabled tools in registry"
```

---

## Task 7: Fix README — Remove Duplicate Section and Add Missing HTTP HOST Row

**Files:**
- Modify: `README.md`
- Modify: `README_CN.md`

**Step 1: Find duplicate section in README.md**

Run: `grep -n "Adding a New Tool" README.md`
Expected: Two line numbers (lines ~280 and ~332)

**Step 2: Remove the first duplicate (keep the one in "Tool Registry" section)**

Remove lines ~279-309 (the first "Adding a New Tool" section in the "Development" chapter).

**Step 3: Add missing HTTP HOST row to README.md**

In the "HTTP Mode Configuration" table, add:
```
| `LIGHTDASH_MCP_HTTP_HOST` | ❌ | HTTP server bind address (default: `0.0.0.0`) | `127.0.0.1` |
```

**Step 4: Mirror all changes to README_CN.md**

**Step 5: Commit**

```bash
git add README.md README_CN.md
git commit -m "docs: fix README duplicate section and add missing HTTP_HOST row"
```

---

## Task 8: Add `CONTRIBUTING.md`

**Files:**
- Create: `CONTRIBUTING.md`

**Step 1: Write the file**

```markdown
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
```

**Step 2: Commit**

```bash
git add CONTRIBUTING.md
git commit -m "docs: add CONTRIBUTING.md"
```

---

## Task 9: Add `CHANGELOG.md`

**Files:**
- Create: `CHANGELOG.md`

**Step 1: Write the file**

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.2] — YYYY-MM-DD

### Added
- `list-table-field-values` tool: search for unique field values in a table column
- `list-projects`, `get-project`, `list-explores`, `get-explore-schema`, `get-custom-metrics` discovery tools
- `list-charts`, `search-charts`, `get-chart-details`, `run-chart-query` chart tools
- `list-dashboards`, `get-dashboard-tiles`, `get-dashboard-tile-chart-config`, `get-dashboard-code`, `run-dashboard-tiles` dashboard tools
- `run-raw-query` for ad-hoc metric queries
- HTTP transport mode (StreamableHTTP with JWT auth)
- Google Cloud IAP authentication support
- Cloudflare Access authentication support

### Changed
- Updated README URLs to reflect fork repository
- Enabled STDIO and HTTP dual-transport mode

### Security
- Removed hardcoded IAP service account default
- Added comprehensive `.gitignore`
```

**Step 2: Commit**

```bash
git add CHANGELOG.md
git commit -m "docs: add CHANGELOG.md"
```

---

## Task 10: Add `SECURITY.md`

**Files:**
- Create: `SECURITY.md`

**Step 1: Write the file**

```markdown
# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability, please do **not** open a public GitHub Issue.

Instead, please contact the maintainers directly by email or through GitHub's private vulnerability reporting.

Please include:
- A description of the vulnerability
- Steps to reproduce
- Potential impact
- Any suggested fixes (optional)

We aim to respond within 48 hours and will work with you to disclose and fix the issue responsibly.
```

**Step 2: Commit**

```bash
git add SECURITY.md
git commit -m "docs: add SECURITY.md"
```

---

## Task 11: Add GitHub Actions CI Workflow

**Files:**
- Create: `.github/workflows/ci.yml`

**Step 1: Write the CI workflow**

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    name: Lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4
        with:
          enable-cache: true

      - name: Install dependencies
        run: uv sync --dev

      - name: Run ruff check
        run: uv run ruff check .

  test:
    name: Test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4
        with:
          enable-cache: true

      - name: Install dependencies
        run: uv sync --dev

      - name: Run tests
        run: uv run pytest -v

  build:
    name: Build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4
        with:
          enable-cache: true

      - name: Install dependencies
        run: uv sync

      - name: Build package
        run: uv run python -m build
```

**Step 2: Create directory and write file**

Run: `mkdir -p .github/workflows`

**Step 3: Commit**

```bash
git add .github/workflows/ci.yml
git commit -m "ci: add GitHub Actions CI workflow"
```

---

## Task 12: Add `[tool.ruff]` Configuration to `pyproject.toml`

**Files:**
- Modify: `pyproject.toml`

**Step 1: Read current pyproject.toml tool section**

Run: `grep -n "tool\." pyproject.toml`
Expected: Shows existing tool sections

**Step 2: Add ruff configuration**

Append to `pyproject.toml`:
```toml
[tool.ruff]
target-version = "py311"
line-length = 88

[tool.ruff.lint]
select = [
  "E",     # pycodestyle errors
  "W",     # pycodestyle warnings
  "F",     # Pyflakes
  "I",     # isort
  "B",     # flake8-bugbear
  "C4",    # flake8-comprehensions
  "UP",    # pyupgrade
]
ignore = [
  "E501",  # line too long (handled by formatter)
]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
line-ending = "auto"
```

**Step 3: Commit**

```bash
git add pyproject.toml
git commit -m "chore: add ruff configuration to pyproject.toml"
```

---

## Task 13: Add `.editorconfig`

**Files:**
- Create: `.editorconfig`

**Step 1: Write the file**

```ini
# EditorConfig is awesome: https://EditorConfig.org

root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true

[*.py]
indent_style = space
indent_size = 4

[*.{yml,yaml,json,md,rst}]
indent_style = space
indent_size = 2

[Makefile]
indent_style = tab
```

**Step 2: Commit**

```bash
git add .editorconfig
git commit -m "chore: add .editorconfig for consistent formatting"
```

---

## Task 14: Extract Duplicated `get_chart` Helper Functions

**Files:**
- Modify: `lightdash_mcp/tools/get_chart_details.py`
- Modify: `lightdash_mcp/tools/get_dashboard_tile_chart_config.py`
- Modify: `lightdash_mcp/tools/dashboard_utils.py`
- Modify: `lightdash_mcp/tools/get_dashboard_tiles.py`
- Modify: `lightdash_mcp/tools/utils.py`

**Step 1: Read the three get_chart implementations**

Run: `grep -n "def get_chart" lightdash_mcp/tools/get_chart_details.py lightdash_mcp/tools/get_dashboard_tile_chart_config.py lightdash_mcp/tools/dashboard_utils.py`
Expected: Three definitions of `get_chart` (likely very similar)

**Step 2: Read get_dashboard implementations**

Run: `grep -n "def get_dashboard" lightdash_mcp/tools/get_dashboard_tiles.py lightdash_mcp/tools/dashboard_utils.py`
Expected: Two definitions of `get_dashboard`

**Step 3: Choose the best implementation and add to utils.py**

Move the canonical `get_chart` and `get_dashboard` functions to `lightdash_mcp/tools/utils.py`.

**Step 4: Update all files that import the helpers**

Update imports in all dependent files to use `from .utils import get_chart, get_dashboard`.

**Step 5: Commit**

```bash
git add lightdash_mcp/tools/utils.py lightdash_mcp/tools/get_chart_details.py lightdash_mcp/tools/get_dashboard_tile_chart_config.py lightdash_mcp/tools/dashboard_utils.py lightdash_mcp/tools/get_dashboard_tiles.py
git commit -m "refactor: extract duplicated get_chart/get_dashboard to utils.py"
```

---

## Task 15: Fix Docstring Language Inconsistency

**Files:**
- Modify: `lightdash_mcp/server.py` (file-level docstring)
- Modify: `lightdash_mcp/lightdash_client.py` (file-level docstring)
- Modify: `lightdash_mcp/tools/base_tool.py` (add missing docstrings)
- Modify: `lightdash_mcp/tools/__init__.py` (file-level docstring)

**Step 1: Convert server.py file-level docstring to English**

Change the Chinese file-level docstring to English while keeping all function-level English docstrings.

**Step 2: Convert lightdash_client.py file-level docstring to English**

**Step 3: Add docstrings to base_tool.py classes**

**Step 4: Commit**

```bash
git add lightdash_mcp/server.py lightdash_mcp/lightdash_client.py lightdash_mcp/tools/base_tool.py lightdash_mcp/tools/__init__.py
git commit -m "chore: standardize docstrings to English across codebase"
```

---

## Task 16: Refactor HTTP Test to Proper Pytest Format

**Files:**
- Modify: `tests/http/test_http_tools.py`

**Step 1: Read current test**

Run: `cat tests/http/test_http_tools.py`
Expected: Current implementation with `_load_env()` and manual assertions

**Step 2: Refactor to use pytest fixtures**

```python
import os
import pytest
from mcp.client import ClientSession
from mcp_streamable_http import StreamableHTTPServerParams, create_sse_client

@pytest.fixture
def lightdash_env():
    """Load env vars from .env for testing (requires real credentials)."""
    from dotenv import load_dotenv
    load_dotenv()
    return {
        "url": os.getenv("LIGHTDASH_URL"),
        "token": os.getenv("LIGHTDASH_TOKEN"),
        "project_uuid": os.getenv("LIGHTDASH_PROJECT_UUID"),
    }

@pytest.fixture
def skip_without_env(lightdash_env):
    """Skip test if LIGHTDASH_URL is not set."""
    if not lightdash_env["url"]:
        pytest.skip("LIGHTDASH_URL not set")

def test_list_projects(skip_without_env, lightdash_env):
    """Test that list-projects returns a non-empty list."""
    # Integration test — requires real Lightdash credentials
    # Set LIGHTDASH_URL, LIGHTDASH_TOKEN in .env to run
    import requests
    r = requests.get(
        f"{lightdash_env['url']}/api/v1/org/projects",
        headers={"Authorization": f"ApiKey {lightdash_env['token']}"},
    )
    assert r.status_code == 200
    results = r.json().get("results", [])
    assert isinstance(results, list)
```

**Step 3: Add pytest.mark.skipif for integration tests**

```python
# Skip all integration tests unless LIGHTDASH_URL is set
requires_lightdash = pytest.mark.skipif(
    os.getenv("LIGHTDASH_URL") is None,
    reason="Requires LIGHTDASH_URL environment variable",
)
```

**Step 4: Commit**

```bash
git add tests/http/test_http_tools.py
git commit -m "test: refactor HTTP integration tests to pytest with skip conditions"
```

---

## Task 17: Final Cleanup — Remove Dead Code `InputSchema` in `base_tool.py`

**Files:**
- Modify: `lightdash_mcp/tools/base_tool.py`

**Step 1: Check if InputSchema is used anywhere**

Run: `grep -r "InputSchema" lightdash_mcp/`
Expected: Only the definition in base_tool.py

**Step 2: Remove InputSchema class**

Delete the `InputSchema` class from `base_tool.py` since it's dead code.

**Step 3: Commit**

```bash
git add lightdash_mcp/tools/base_tool.py
git commit -m "refactor: remove unused InputSchema class from base_tool.py"
```

---

## Task 18: Final Verification

**Files:**
- Action: Run all verification commands

**Step 1: Run lint**

Run: `just check`
Expected: All checks pass

**Step 2: Run tests**

Run: `just test`
Expected: All tests pass (or skipped if no env)

**Step 3: Check git status**

Run: `git status`
Expected: Only expected files modified

**Step 4: Build package**

Run: `just build`
Expected: Package builds successfully

**Step 5: Commit any remaining changes**

```bash
git add -A
git commit -m "chore: final open-source release prep cleanup"
```
