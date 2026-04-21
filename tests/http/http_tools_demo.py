"""
HTTP 模式下 MCP 只读工具测试。

前置条件：启动 MCP HTTP 服务器
    just run-http

运行：
    uv run python tests/http/http_tools_demo.py
"""
from __future__ import annotations

import os
import sys

import jwt


def _load_env():
    """从 .env 加载环境变量。"""
    env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip())


_load_env()

# ── 配置 ────────────────────────────────────────────────────────────────────

HTTP_HOST = os.getenv("LIGHTDASH_MCP_HTTP_HOST", "0.0.0.0")
HTTP_PORT = int(os.getenv("LIGHTDASH_MCP_HTTP_PORT", "8080"))
HTTP_APIKEY = os.getenv("LIGHTDASH_MCP_HTTP_APIKEY", "")

MCP_ENDPOINT = f"http://{HTTP_HOST}:{HTTP_PORT}/mcp/"


def main():
    import asyncio
    from mcp.client.streamable_http import streamablehttp_client
    from mcp import ClientSession

    auth_token = jwt.encode(
        {"sub": "test", "exp": 9999999999}, HTTP_APIKEY, algorithm="HS256"
    )

    print(f"Connecting to {MCP_ENDPOINT}...")

    async def run_tests():
        async with streamablehttp_client(
                MCP_ENDPOINT,
                headers={"Authorization": f"Bearer {auth_token}"},
                timeout=60.0,
        ) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                print("MCP initialized.\n")

                tools = [
                    ("list-projects", {"name": "POS DB"}),
                    ("list-spaces", {}),
                    ("list-dashboards", {}),
                    ("list-charts", {}),
                    ("list-explores", {"database_name": "zhidou_bi"}),
                    ("get-project", {}),
                    ("search-charts", {"search_term": "test"}),
                ]

                passed = 0
                failed = 0
                for name, args in tools:
                    try:
                        result = await session.call_tool(name, args)
                        text = str(result)
                        print(f"  ok {name}: {len(text)} chars")
                        print(f"  result: {result}\n")
                        passed += 1
                    except Exception as e:
                        print(f"  FAIL {name}: {e}\n")
                        failed += 1

                print(f"Results: {passed} passed, {failed} failed")
                return failed == 0

    ok = asyncio.run(run_tests())
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
