# ============================================================
# Stage 1: Build dependencies and sync project
# ============================================================
FROM registry.cn-hangzhou.aliyuncs.com/winwin/tool:python-uv-3.11-slim AS builder

WORKDIR /app

# 允许通过 --build-arg UV_INDEX_URL 覆盖镜像源，默认使用阿里云公网镜像
ARG UV_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/

# 取消镜像内置的 UV_INDEX_URL 和 UV_DEFAULT_INDEX（指向无法访问的内网镜像）
ENV UV_INDEX_URL=${UV_INDEX_URL}
ENV UV_DEFAULT_INDEX=${UV_INDEX_URL}
ENV PIP_INDEX_URL=${UV_INDEX_URL}
#ENV PIP_EXTRA_INDEX_URL=

# 清除镜像内 pip/uv 内网源配置
RUN rm -rf /etc/pip.conf /root/.pip /root/.config/pip /etc/uv /root/.config/uv 2>/dev/null || true

# Install build dependencies (hatchling needed for project sync)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system --index-url ${UV_INDEX_URL} build hatchling

# Install dependencies (without syncing the project)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-editable --index-url ${UV_INDEX_URL}

# Copy source and sync project into the venv
COPY lightdash_mcp/ ./lightdash_mcp/
COPY pyproject.toml ./
COPY README.md .
COPY CHANGELOG.md .
COPY LICENSE .
COPY uv.lock .
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-editable --index-url ${UV_INDEX_URL}

# ============================================================
# Stage 2: Production runtime
# ============================================================
FROM registry.cn-hangzhou.aliyuncs.com/winwin/tool:python-3.11-slim

WORKDIR /app

COPY --from=builder /app /app

EXPOSE 8080

CMD ["/app/.venv/bin/lightdash-mcp", "http"]
