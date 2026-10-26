"""
Pydantic 数据模型 — 请求校验

FastAPI 自动把 JSON 请求体解析为这些模型，
不需要手写参数校验代码。
"""

from typing import Optional
from pydantic import BaseModel


class CodeReviewRequest(BaseModel):
    """
    代码审查请求

    - code: 必填，待审查的代码
    - language: 可选，编程语言（不传则 LLM 自动识别）
    - focus: 可选，重点方向 security / performance / style
    """
    code: str
    language: Optional[str] = None
    focus: Optional[str] = None
