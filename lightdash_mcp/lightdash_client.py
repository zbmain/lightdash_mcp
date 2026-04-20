"""
Lightdash API 客户端。

支持两种模式：
- STDIO 模式：使用服务端环境变量（LIGHTDASH_URL、LIGHTDASH_TOKEN 等）
- HTTP 模式：通过 contextvar 支持每个请求的凭证覆盖
  （客户端通过 X-Lightdash-* 请求头传入，优先级高于环境变量）
"""

import json
import os
import sys
import time
from contextvars import ContextVar
from typing import Any

import requests

# ── 服务端默认凭证（环境变量，模块加载时读取） ──────────────────────────────

LIGHTDASH_URL = os.getenv("LIGHTDASH_URL", "")
LIGHTDASH_TOKEN = os.getenv("LIGHTDASH_TOKEN", "")
LIGHTDASH_PROJECT_UUID = os.getenv("LIGHTDASH_PROJECT_UUID", "")
CF_ACCESS_CLIENT_ID = os.getenv("CF_ACCESS_CLIENT_ID", "")
CF_ACCESS_CLIENT_SECRET = os.getenv("CF_ACCESS_CLIENT_SECRET", "")
IAP_ENABLED = os.getenv("IAP_ENABLED", "").lower() in ("1", "true", "yes")

# ── 请求级凭证覆盖（HTTP 模式下由服务端中间件写入） ────────────────────────

# 每个 HTTP 请求的凭证覆盖（STDIO 模式下始终为空）
_request_context: ContextVar[dict[str, str | None] | None] = ContextVar(
    "request_context", default=None
)


def set_request_context(headers: dict[str, str]) -> None:
    """
    从 HTTP 请求头中提取客户端凭证并写入 context。

    HTTP 客户端可传入以下请求头（均为可选）：
      X-Lightdash-Url:        覆盖 LIGHTDASH_URL
      X-Lightdash-Token:      覆盖 LIGHTDASH_TOKEN
      X-Lightdash-Project-Uuid: 覆盖 LIGHTDASH_PROJECT_UUID

    未传入的头将 fallback 到环境变量。
    """
    ctx = {
        "LIGHTDASH_URL": headers.get("X-Lightdash-Url"),
        "LIGHTDASH_TOKEN": headers.get("X-Lightdash-Token"),
        "LIGHTDASH_PROJECT_UUID": headers.get("X-Lightdash-Project-Uuid"),
    }
    _request_context.set(ctx)


def clear_request_context() -> None:
    """清除当前请求的凭证覆盖（请求结束时调用）。"""
    _request_context.set(None)


def _get_effective(key: str) -> str:
    """获取实际生效的凭证值：优先 context 覆盖，否则回退到环境变量。"""
    ctx = _request_context.get()
    if ctx is not None:
        override = ctx.get(key)
        if override:
            return override
    return globals()[key]  # 环境变量值


def _effective_url() -> str:
    return _get_effective("LIGHTDASH_URL")


def _effective_token() -> str:
    return _get_effective("LIGHTDASH_TOKEN")


def _effective_project_uuid() -> str:
    return _get_effective("LIGHTDASH_PROJECT_UUID")


# ── 全局 requests.Session（用于服务端默认凭证） ────────────────────────────

session = requests.Session()
session.headers.update(
    {
        "Authorization": f"ApiKey {LIGHTDASH_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
)

if CF_ACCESS_CLIENT_ID and CF_ACCESS_CLIENT_SECRET:
    session.headers.update(
        {
            "CF-Access-Client-Id": CF_ACCESS_CLIENT_ID,
            "CF-Access-Client-Secret": CF_ACCESS_CLIENT_SECRET,
        }
    )

_iap_jwt_cache: dict = {}


def _attach_iap_token() -> None:
    """Sign a JWT and attach it as Proxy-Authorization for Cloud Run IAP."""
    try:
        import google.auth
        import google.auth.iam
        import google.auth.jwt
        import google.auth.transport.requests
    except ImportError:
        raise RuntimeError(
            "google-auth is required for IAP support. "
            "Install with: pip install lightdash-mcp[iap]"
        ) from None

    now = int(time.time())
    cached = _iap_jwt_cache.get("token")
    if cached and _iap_jwt_cache.get("exp", 0) > now + 300:
        session.headers["Proxy-Authorization"] = f"Bearer {cached}"
        return

    try:
        credentials, _ = google.auth.default()
        request = google.auth.transport.requests.Request()
        credentials.refresh(request)

        sa_email = os.getenv("IAP_SA", "")
        if not sa_email:
            raise RuntimeError(
                "IAP_SA environment variable is required when IAP_ENABLED=true. "
                "Set IAP_SA to the service account email used for IAP authentication."
            )

        signer = google.auth.iam.Signer(request, credentials, sa_email)

        exp = now + 3600
        payload = {
            "iss": sa_email,
            "sub": sa_email,
            "aud": f"{_effective_url()}/*",
            "iat": now,
            "exp": exp,
        }

        token = google.auth.jwt.encode(signer, payload)
        if isinstance(token, bytes):
            token = token.decode("utf-8")

        _iap_jwt_cache["token"] = token
        _iap_jwt_cache["exp"] = exp
        session.headers["Proxy-Authorization"] = f"Bearer {token}"
        print(f"[IAP] JWT signed for {sa_email}, valid until {exp}", file=sys.stderr)
    except Exception as e:
        print(f"[IAP] Failed to sign JWT: {e}", file=sys.stderr)


def _handle_request(method: str, path: str, **kwargs) -> dict[str, Any]:
    """
    向 Lightdash API 发起请求。

    HTTP 模式下：优先使用请求上下文中的凭证覆盖，服务端环境变量作为默认值兜底。
    STDIO 模式下：始终使用服务端环境变量。
    """
    url = f"{_effective_url()}{path}"

    # 构建请求头：全局 session headers + 当前 context 覆盖
    ctx = _request_context.get()
    headers = {}
    if ctx is not None:
        # 仅当 context 提供了有效覆盖时才修改 Authorization 头
        token = ctx.get("LIGHTDASH_TOKEN")
        if token:
            headers["Authorization"] = f"ApiKey {token}"

    if IAP_ENABLED:
        _attach_iap_token()

    try:
        r = session.request(method, url, headers=headers or None, **kwargs)
        r.raise_for_status()
        try:
            return r.json()
        except ValueError:
            # 非 JSON 响应（如 HTML 错误页、text/plain 等）
            raise Exception(
                f"Lightdash API returned non-JSON response ({r.headers.get('Content-Type', 'unknown')}): {r.text[:500]}"
            ) from None
    except requests.exceptions.HTTPError as e:
        try:
            error_details = r.json()
        except Exception:
            error_details = r.text

        raise Exception(
            f"Lightdash API Error: {e} - Details: {json.dumps(error_details) if isinstance(error_details, dict) else error_details}"
        ) from e


def get(path: str) -> dict[str, Any]:
    """Make a GET request to the Lightdash API."""
    return _handle_request("GET", path)


def patch(path: str, data: dict[str, Any]) -> dict[str, Any]:
    """Make a PATCH request to the Lightdash API."""
    return _handle_request("PATCH", path, json=data)


def post(path: str, data: dict[str, Any]) -> dict[str, Any]:
    """Make a POST request to the Lightdash API."""
    return _handle_request("POST", path, json=data)


def delete(path: str) -> dict[str, Any]:
    """Make a DELETE request to the Lightdash API."""
    return _handle_request("DELETE", path)
