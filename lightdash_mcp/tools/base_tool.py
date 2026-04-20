from typing import Any

from pydantic import BaseModel, Field


class ToolParameter(BaseModel):
    """工具参数定义（非必选，已保留兼容现有工具导入）。"""

    type: str
    description: str


class InputSchema(BaseModel):
    """工具输入 schema（MCP 协议用），properties 每个值接受 dict 或 ToolParameter。"""

    type: str = "object"
    properties: dict[str, Any] = Field(default_factory=dict)
    required: list[str] = Field(default_factory=list)


class ToolDefinition(BaseModel):
    name: str
    description: str
    input_schema: InputSchema = Field(alias="inputSchema")

    class Config:
        populate_by_name = True
