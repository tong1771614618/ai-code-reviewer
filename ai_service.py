"""
AI 代码审查服务 — 核心业务逻辑

两个入口函数：
- review_stream(): 流式输出（Generator），用于 SSE 实时推送
- review():        非流式输出（一次性返回完整结果）
"""

import time
from typing import Optional, Generator
from llm_client import client
from logger import agent_log
from config import settings
from prompts import SYSTEM_PROMPT

log = agent_log("CodeReview")


def review_stream(
    code: str,
    language: Optional[str] = None,
    focus: Optional[str] = None,
) -> Generator[str, None, None]:
    """
    流式代码审查 — 核心函数

    使用 stream=True 让 LLM 边生成边返回：
    - 每个 chunk 包含 LLM 新生成的一小段文本（delta）
    - yield 把文本立即推给 FastAPI → 前端实时显示
    - 用户 0.5 秒就能看到第一行输出
    """
    t0 = time.time()
    log.request(f"代码审查 ({language or '自动检测'}, {len(code)} 字符)")

    # ─── 构建用户消息 ──────────────────────────────────────────
    user_message = "请审查以下代码：\n\n"

    if language:
        user_message += f"编程语言：{language}\n\n"
    if focus:
        focus_map = {
            "security": "请重点关注安全问题（SQL注入、XSS、权限等）",
            "performance": "请重点关注性能问题（N+1查询、内存、循环等）",
            "style": "请重点关注代码规范和可维护性",
        }
        user_message += f"{focus_map.get(focus, '')}\n\n"

    user_message += f"```{language or ''}\n{code}\n```"

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    # ─── 流式调用 LLM ──────────────────────────────────────────
    stream = client.chat.completions.create(
        model=settings.QWEN_MODEL,
        messages=messages,
        temperature=0.3,
        stream=True,
    )

    total_chars = 0

    for chunk in stream:
        if not chunk.choices:
            continue
        delta = chunk.choices[0].delta
        if delta.content:
            total_chars += len(delta.content)
            yield delta.content

    elapsed = time.time() - t0
    log.complete(rounds=1, time_s=elapsed)
    log.answer(round=1, usage=None, preview=f"[streaming] {total_chars} chars in {elapsed:.1f}s")


def review(code: str, language: Optional[str] = None, focus: Optional[str] = None) -> dict:
    """
    非流式代码审查 — 一次性返回完整结果

    内部复用 review_stream()，把所有 chunk 拼成完整字符串。
    """
    chunks = list(review_stream(code, language, focus))
    return {"review": "".join(chunks)}
