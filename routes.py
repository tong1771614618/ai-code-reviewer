"""
FastAPI 路由 — 两个审查接口

- POST /review        非流式（一次性返回 JSON）
- POST /review-stream 流式 SSE（实时推送）
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from schemas import CodeReviewRequest
import ai_service

router = APIRouter()


@router.post("/review")
async def review(request: CodeReviewRequest):
    """非流式代码审查 — 等 LLM 生成完一次性返回"""
    try:
        return ai_service.review(request.code, request.language, request.focus)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"代码审查失败: {str(e)}")


@router.post("/review-stream")
async def review_stream(request: CodeReviewRequest):
    """流式代码审查 — SSE (Server-Sent Events) 实时推送"""
    try:
        generator = ai_service.review_stream(
            request.code, request.language, request.focus
        )
        return StreamingResponse(
            generator,
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"流式审查失败: {str(e)}")
