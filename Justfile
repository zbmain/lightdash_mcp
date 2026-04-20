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

# 仅构建包
build:
    uv build

# 发布到 PyPI
publish:
    uv publish

# 清理构建产物
clean:
    rm -rf dist/ build/ *.egg-info/ .pytest_cache/ .ruff_cache/ .coverage htmlcov/

# 进入 uv 虚拟环境
shell:
    uv run python

# 列出所有可用工具
list-tools:
    uv run python -c "from lightdash_mcp.tools import tool_registry; print('Registered tools:', len(tool_registry)); [print(f'  - {name}') for name in sorted(tool_registry)]"

# 验证 YAML 配置
validate-registry:
    uv run python -c "from lightdash_mcp.tools import validate_registry; validate_registry()"