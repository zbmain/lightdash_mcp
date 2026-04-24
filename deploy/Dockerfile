# ============================================================
# Stage 1: Build wheel
# ============================================================
FROM registry.cn-hangzhou.aliyuncs.com/winwin/tool:python-uv-3.11-slim AS builder

WORKDIR /app

# 清除镜像内 pip/uv 内网源配置
RUN rm -f /etc/pip.conf /root/.pip/pip.conf /root/.config/pip/pip.conf 2>/dev/null || true

# 安装构建工具 build + hatchling（公网源）
RUN --mount=type=cache,target=/root/.cache/uv \
    UV_INDEX_URL=https://pypi.org/simple/ \
    uv pip install --system build hatchling

# 复制源码
COPY lightdash_mcp/ ./lightdash_mcp/
COPY pyproject.toml ./
COPY README.md .
COPY CHANGELOG.md .
COPY LICENSE .
COPY uv.lock .

# 构建 wheel（python -m build 直接用已安装的 hatchling）
RUN python -m build --wheel --outdir /dist

# ============================================================
# Stage 2: Production runtime
# ============================================================
FROM registry.cn-hangzhou.aliyuncs.com/winwin/tool:python-3.11-slim

WORKDIR /app

# 复制 wheel 并用 pip 安装（该镜像有 pip 但可能无 uv）
COPY --from=builder /dist /dist
RUN pip install --no-cache-dir /dist/*.whl

EXPOSE 8080

CMD ["lightdash-mcp", "http"]
