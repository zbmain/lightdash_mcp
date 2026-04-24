# Justfile - Common shortcuts for lightdash_mcp development
# See https://just.systems for documentation

# 自动加载 .env 文件并导出环境变量
set dotenv-load := true
set export := true

# 锁定并同步依赖
sync:
    uv sync

# 安装依赖
install:
    uv sync

# 添加依赖 (use: just add httpx)
add PKG:
    uv add {{PKG}}

# 添加开发依赖 (use: just add-dev pytest)
add-dev PKG:
    uv add --dev {{PKG}}

# 移除依赖 (use: just remove httpx)
remove PKG:
    uv remove {{PKG}}

# 代码格式检查
check:
    uv run ruff check lightdash_mcp/

# 自动修复代码问题
fix:
    uv run ruff check --fix lightdash_mcp/

# 格式化代码
fmt:
    uv run ruff format lightdash_mcp/

# 检查 + 格式化 (CI 用)
lint: check fmt

# 运行测试
test:
    uv run pytest

# 带覆盖率运行测试
test-cov:
    uv run pytest --cov=lightdash_mcp --cov-report=term-missing

# 启动 MCP 服务器 (需要设置环境变量)
run:
    uv run lightdash-mcp

# 启动 MCP HTTP 服务器 (需要设置 LIGHTDASH_MCP_HTTP_APIKEY)
run-http:
    uv run lightdash-mcp http

# 清理构建产物
clean:
    rm -rf dist/ build/ *.egg-info/ .pytest_cache/ .ruff_cache/ .coverage htmlcov/

# 仅构建包
build: clean
    uv build

# 发布到 PyPI
publish:
    uv publish

image:
    #!/bin/bash
    TAG=$(date +%Y%m%d)$(git rev-parse refs/remotes/origin/master^{commit} | cut -c 1-4)
    docker buildx build --build-arg UV_INDEX=https://mirrors.aliyun.com/pypi/simple/ -f deploy/Dockerfile -t registry.cn-hangzhou.aliyuncs.com/winwin/tool:lightdash-mcp-$TAG .

# 进入 uv 虚拟环境
shell:
    uv run python

# 列出所有可用工具
list-tools:
    uv run python -c "from lightdash_mcp.tools import tool_registry; print('Registered tools:', len(tool_registry)); [print(f'  - {name}') for name in sorted(tool_registry)]"

# 验证 YAML 配置
validate-registry:
    uv run python -c "from lightdash_mcp.tools import validate_registry; validate_registry()"

# ── GitHub Actions (本地运行) ───────────────────────────────────────────────
# 需要安装 act: https://github.com/nektos/act
# macOS: brew install act
# Linux: curl -s https://raw.githubusercontent.com/nektos/act/master/install.sh | bash
#
# 注意: act 容器在某些网络环境下可能无法下载 uv/依赖（Docker 网络限制）。
# 在 GitHub Actions 上运行完全正常。本地测试建议使用 `just check` / `just test`。

# 检查 act 是否安装
check-act:
    @which act > /dev/null 2>&1 && echo "✅ act installed" || echo "❌ act not found. Install: brew install act"

# 运行 CI workflow (lint + test + build) — 串行运行避免并行网络竞争
ci:
    @which act > /dev/null 2>&1 || { echo "❌ act not installed. Run: brew install act"; exit 1; }
    act -W .github/workflows/ci.yml --pull=false -j lint && \
    act -W .github/workflows/ci.yml --pull=false -j test && \
    act -W .github/workflows/ci.yml --pull=false -j build

# 运行 CI workflow (dry-run, 不执行实际命令)
ci-dry:
    @which act > /dev/null 2>&1 || { echo "❌ act not installed. Run: brew install act"; exit 1; }
    act -W .github/workflows/ci.yml --pull=false -j lint --dry-run && \
    act -W .github/workflows/ci.yml --pull=false -j test --dry-run && \
    act -W .github/workflows/ci.yml --pull=false -j build --dry-run

# 运行 self-check workflow (repo-health + pre-commit + dependency-audit)
self-check:
    @which act > /dev/null 2>&1 || { echo "❌ act not installed. Run: brew install act"; exit 1; }
    act -W .github/workflows/self-check.yml --pull=false -j repo-health && \
    act -W .github/workflows/self-check.yml --pull=false -j pre-commit && \
    act -W .github/workflows/self-check.yml --pull=false -j dependency-audit

# 运行所有 GitHub workflows (CI + self-check)
github-actions: self-check ci
