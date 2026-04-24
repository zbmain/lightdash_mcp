"""
run_question_annotation tool - Call cpvmatch annotation API for natural language question annotation.
"""

from __future__ import annotations

import os
from typing import Any

import httpx

from .base_tool import ToolDefinition

BASE_URL = "https://ml-jsonrpc.banmahui.cn/cpvmatch"
_API_VERSION = "v2"
_TIMEOUT = 30

TOOL_DEFINITION = ToolDefinition(
    name="run-question-annotation",
    description="""Annotate a natural language question for CPV entities (NER).

Extracts entity objects from user questions to identify dimensions, metrics, and context.

Entity types:
  time: 时间 (e.g., 今年, 近一年, 2025年1月)
  group: 集团 (e.g., 元气森林, 农夫山泉, 可口可乐, 康师傅)
  brand: 品牌 (e.g., 元气森林, 外星人, 农夫山泉, 东方树叶, 可口可乐, 雪碧, 冰露)
  metric: 指标 metrics (e.g., 销售额, 销量, 市占率)
  attributes: 属性 (e.g., 包装, 口味, 含糖情况)

Tips: This endpoint uses exhaustive annotation. Results may contain errors for nested
or ambiguous entities. Review annotations before using them for downstream analysis.
""",
    inputSchema={
        "properties": {
            "question": {
                "type": "string",
                "description": "Natural language question to annotate",
            },
            "full_mode": {
                "type": "boolean",
                "description": "Enable full annotation mode (default True)",
            },
            "attribute_categories": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional list of attribute categories to restrict scope, e.g. 饮料,食品",
            },
        },
        "required": ["question"],
    },
)


def run(
    question: str,
    full_mode: bool = True,
    attribute_categories: list[str] | None = None,
) -> dict[str, Any]:
    """Call cpvmatch annotation endpoint."""
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
    """Get cpvmatch APIKEY from environment variable."""
    apikey = os.getenv("CPVMATCH_APIKEY", "").strip()
    if not apikey:
        raise ValueError(
            "CPVMATCH_APIKEY environment variable not set. "
            "Set it before calling run-question-annotation tool."
        )
    return apikey
