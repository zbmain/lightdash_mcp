"""
Lightdash MCP Server

支持两种传输模式：
  - STDIO（默认）：`lightdash-mcp` 或 `lightdash-mcp stdio`
  - HTTP：        `lightdash-mcp http`

HTTP 模式需要安装额外依赖：`pip install lightdash-mcp[http]`
JWT 认证由 LIGHTDASH_MCP_HTTP_APIKEY 环境变量配置（必填）。
HTTP 客户端通过请求头传入凭证覆盖服务端环境变量：
  Authorization: Bearer <jwt>                        # JWT 认证（必填）
  X-Lightdash-Url: https://xxx.lightdash.cloud      # 可选：覆盖 LIGHTDASH_URL
  X-Lightdash-Token: ldt_xxx                        # 可选：覆盖 LIGHTDASH_TOKEN
  X-Lightdash-Project-Uuid: xxx                    # 可选：覆盖 LIGHTDASH_PROJECT_UUID
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
import time
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route
from starlette.types import ASGIApp, Receive, Scope, Send

from . import lightdash_client as _lc
from .tools import tool_registry

app = Server("lightdash")


# ── MCP 工具处理 ──────────────────────────────────────────────────────────


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    tool_definitions = []
    for _tool_name, tool_module in tool_registry.items():
        tool_def = tool_module.TOOL_DEFINITION
        tool_definitions.append(
            Tool(
                name=tool_def.name,
                description=tool_def.description,
                inputSchema=tool_def.input_schema.dict(by_alias=True),
            )
        )
    return tool_definitions


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls."""
    try:
        if name not in tool_registry:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

        tool_module = tool_registry[name]
        result = tool_module.run(**arguments)

        if isinstance(result, (dict, list)):
            result_text = json.dumps(result, indent=2)
        else:
            result_text = str(result)

        return [TextContent(type="text", text=result_text)]

    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


# ── STDIO 模式 ────────────────────────────────────────────────────────────


async def main_stdio() -> None:
    """Run in STDIO mode (默认)."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


# ── HTTP 模式 ─────────────────────────────────────────────────────────────


def _get_jwt_secret() -> str:
    """获取 JWT 对称密钥，未设置则退出。"""
    secret = os.getenv("LIGHTDASH_MCP_HTTP_APIKEY", "").strip()
    if not secret:
        sys.exit(
            "[HTTP] LIGHTDASH_MCP_HTTP_APIKEY environment variable is required for HTTP mode.\n"
            "Example: LIGHTDASH_MCP_HTTP_APIKEY=your-256-bit-secret lightdash-mcp http"
        )
    return secret


def _verify_jwt(token: str) -> dict[str, Any]:
    """验证 JWT 并返回 payload，失败则抛出 PermissionError。"""
    import jwt  # 延迟导入，仅 HTTP 模式需要

    try:
        payload = jwt.decode(token, _get_jwt_secret(), algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise PermissionError("JWT token has expired") from None
    except jwt.InvalidTokenError as e:
        raise PermissionError(f"Invalid JWT token: {e}") from e


def _extract_bearer(scope: Scope) -> str | None:
    """从 ASGI scope headers 中提取 Bearer token。"""
    for key, value in scope.get("headers", []):
        if key == b"authorization":
            val = value.decode()
            if val.startswith("Bearer "):
                return val[7:]
    return None


def _headers_to_str_dict(scope: Scope) -> dict[str, str]:
    """将 ASGI headers bytes 转为 str->str dict。"""
    return {k.decode(): v.decode() for k, v in scope.get("headers", [])}


# ── MCP HTTP 会话管理器 ───────────────────────────────────────────────────

_http_manager = None  # 全局单例
_http_asgi_app = None  # 全局 ASGI 包装


def _get_session_manager() -> Any:
    """获取或创建 StreamableHTTPSessionManager 单例。"""
    global _http_manager
    if _http_manager is None:
        from mcp.server.streamable_http_manager import StreamableHTTPSessionManager

        _http_manager = StreamableHTTPSessionManager(
            app,
            stateless=True,
            json_response=True,
        )
    return _http_manager


def _get_mcp_asgi_app() -> Any:
    """获取 ASGI 包装后的 MCP 应用（供 Starlette Mount 使用）。"""
    global _http_asgi_app
    if _http_asgi_app is None:
        manager = _get_session_manager()

        class MCPASGIApp:
            """将 StreamableHTTPSessionManager 包装为 ASGI 应用。"""

            def __init__(self, mgr: Any) -> None:
                self.mgr = mgr

            async def __call__(
                self, scope: Scope, receive: Receive, send: Send
            ) -> None:
                await self.mgr.handle_request(scope, receive, send)

        _http_asgi_app = MCPASGIApp(manager)
    return _http_asgi_app


# ── JWT 认证 + 凭证注入中间件 ─────────────────────────────────────────────


class JWTAuthMiddleware:
    """
    ASGI 中间件：对 /mcp/* 和 /messages/* 进行 JWT 认证，
    验证通过后注入 Lightdash 凭证上下文。
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")

        # 所有 MCP 端点需要 JWT 认证
        if path.startswith("/mcp") or path.startswith("/messages"):
            token = _extract_bearer(scope)
            if not token:
                await self._error(send, 401, "Missing or invalid Authorization header")
                return
            try:
                _verify_jwt(token)
            except PermissionError as e:
                await self._error(send, 401, str(e))
                return

            # JWT 验证通过，注入凭证到 Lightdash 请求上下文
            headers = _headers_to_str_dict(scope)
            _lc.set_request_context(headers)
            try:
                await self.app(scope, receive, send)
            except Exception as e:
                await self._error(send, 500, f"MCP error: {e}")
            finally:
                _lc.clear_request_context()
            return

        # 其他路径透传
        await self.app(scope, receive, send)

    async def _error(self, send: Send, status: int, message: str) -> None:
        body = json.dumps({"error": message}).encode()
        await send(
            {
                "type": "http.response.start",
                "status": status,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"access-control-allow-origin", b"*"),
                    (b"cache-control", b"no-store"),
                ],
            }
        )
        await send({"type": "http.response.body", "body": body})


# ── 健康检查端点 ──────────────────────────────────────────────────────────


async def health_endpoint(request: Any) -> JSONResponse:
    """健康检查，无需认证。"""
    return JSONResponse(
        {
            "status": "ok",
            "server": "lightdash-mcp",
            "transport": "http",
            "registered_tools": len(tool_registry),
            "uptime": time.time(),
        }
    )


# ── HTTP 服务器入口 ───────────────────────────────────────────────────────


def main_http() -> None:
    """
    Run in HTTP mode.

    HTTP 端点：
      GET  /mcp/        — MCP SSE 事件流（JWT 认证）
      POST /messages/  — 客户端消息（JWT 认证）
      GET  /health     — 健康检查（无需认证）
    """
    print("Starting lightdash-mcp server...")
    try:
        import anyio
        import uvicorn
    except ImportError as e:
        sys.exit(
            "[HTTP] Missing dependencies. Install with:\n"
            "  pip install lightdash-mcp[http]\n"
            "Or:\n"
            "  uv add --optional http starlette uvicorn\n"
            f"Original error: {e}"
        )

    host = os.getenv("LIGHTDASH_MCP_HTTP_HOST", "0.0.0.0")
    port = int(os.getenv("LIGHTDASH_MCP_HTTP_PORT", "8080"))
    secret = os.getenv("LIGHTDASH_MCP_HTTP_APIKEY", "")

    if secret:
        print(f"[HTTP] JWT secret configured ({len(secret)} chars)", file=sys.stderr)
    else:
        print(
            "[HTTP] WARNING: LIGHTDASH_MCP_HTTP_APIKEY not set - JWT auth will fail on /mcp",
            file=sys.stderr,
        )
    print(f"Lightdash Host: {os.getenv('LIGHTDASH_URL')}\n", file=sys.stderr)
    print(f"[HTTP] Starting server on {host}:{port}", file=sys.stderr)
    print(f"[HTTP] MCP endpoint: http://{host}:{port}/mcp/", file=sys.stderr)
    print(f"[HTTP] Health check: http://{host}:{port}/health", file=sys.stderr)

    manager = _get_session_manager()
    mcp_app = _get_mcp_asgi_app()

    # 构建 Starlette 应用
    starlette_app = Starlette(
        debug=False,
        routes=[
            Route("/health", health_endpoint),
            Mount("/mcp", app=JWTAuthMiddleware(mcp_app)),
            Mount("/messages", app=JWTAuthMiddleware(mcp_app)),
        ],
    )

    async def run() -> None:
        """在 anyio 中管理 session manager 生命周期，同时运行 uvicorn。"""
        async with manager.run():
            config = uvicorn.Config(
                starlette_app,
                host=host,
                port=port,
                lifespan="off",
                log_level="info",
            )
            srv = uvicorn.Server(config)
            await srv.serve()

    # ── CLI 入口 ──────────────────────────────────────────────────────────────

    anyio.run(run)


# ── CLI 入口 ──────────────────────────────────────────────────────────────


def run(mode: str = "stdio") -> None:
    """
    服务器启动入口。

    Args:
        mode: 传输模式，"stdio"（默认）或 "http"。
    """
    print(f"Current mode: {mode}")
    if mode == "http":
        main_http()
    elif mode == "stdio":
        asyncio.run(main_stdio())
    else:
        sys.exit(f"Unknown mode: {mode}. Use 'stdio' or 'http'.")


if __name__ == "__main__":
    _mode = sys.argv[1] if len(sys.argv) > 1 else "stdio"
    run(mode=_mode)
