# ============================================================
# Stage 1: Build wheel
# ============================================================
FROM python:3.11-slim AS builder

# Install uv (用于构建)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# 只复制构建所需文件
COPY pyproject.toml .
COPY uv.lock .

# 构建 wheel（仅生产依赖，不含 dev）
RUN uv build --wheel

# ============================================================
# Stage 2: Production runtime
# ============================================================
FROM python:3.11-slim

# 安装 uv 用于运行时包管理
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# 从 builder 复制 wheel 并安装
COPY --from=builder /app/dist/*.whl .
RUN uv pip install --system --no-cache *.whl

# 非 root 用户运行
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# 默认环境变量
ENV LIGHTDASH_MCP_HTTP_HOST=0.0.0.0
ENV LIGHTDASH_MCP_HTTP_PORT=8082

EXPOSE 8082

ENTRYPOINT ["lightdash-mcp", "http"]
