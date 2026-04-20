# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.2] — 2026-04-20

### Added
- `list-table-field-values` tool: search for unique field values in a specific table column (with v2 API fallback to v1 runQuery)
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
- Bumped minimum Python version to 3.11

### Security
- Removed hardcoded IAP service account default
- Added comprehensive `.gitignore`
- Added `.env` and other sensitive files to `.gitignore`

### Documentation
- Added `CONTRIBUTING.md`, `CHANGELOG.md`, `SECURITY.md`
- Added `.editorconfig` for consistent formatting
- Added GitHub Actions CI workflow
- Added ruff configuration to `pyproject.toml`
