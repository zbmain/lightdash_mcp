"""
question_annotation tool - 调用 cpvmatch annotate API 做自然语言问题标注。
"""

from __future__ import annotations

import os
from typing import Any

import httpx

from .base_tool import ToolDefinition, ToolParameter

BASE_URL = "https://ml-jsonrpc.banmahui.cn/cpvmatch"
_API_VERSION = "v2"
_TIMEOUT = 30.0

TOOL_DEFINITION = ToolDefinition(
    name="question-annotation",
    description="Annotate a natural language question for CPV entities.",
    inputSchema={
        "properties": {
            "question": ToolParameter(
                type="string",
                description="Natural language question to annotate",
            ),
            "full_mode": ToolParameter(
                type="boolean",
                description="Enable full annotation mode (default True)",
            ),
            "attribute_categories": ToolParameter(
                type="array",
                items={"type": "string"},
                description="Optional list of attribute categories, e.g. 饮料,食品",
            ),
        },
        "required": ["question"],
    },
)


def run(
    question: str,
    full_mode: bool = True,
    attribute_categories: list[str] | None = None,
) -> dict[str, Any]:
    """
    Call cpvmatch annotation endpoint.

    Returns:
        Annotation result as a dict.
    """
    categories_value: str | list[str] | None
    if attribute_categories is not None:
        categories_value = attribute_categories
    else:
        categories_value = "auto"

    apikey = _get_apikey()

    with httpx.Client(
        base_url=BASE_URL,
        headers={"apikey": apikey, "content-type": "application/json"},
        timeout=_TIMEOUT,
    ) as client:
        resp = client.post(
            f"/{_API_VERSION}/annotation",
            json={
                "question": question,
                "full_mode": full_mode,
                "attribute_categories": categories_value,
            },
        )
        resp.raise_for_status()
        return resp.json()


def _get_apikey() -> str:
    """从环境变量获取 cpvmatch APIKEY。"""
    apikey = os.getenv("CPVMATCH_APIKEY", "").strip()
    if not apikey:
        raise ValueError(
            "CPVMATCH_APIKEY environment variable not set. "
            "Set it before calling question-annotation tool."
        )
    return apikey
