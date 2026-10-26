"""
AI 代码审查器 — FastAPI 入口

启动方式：
    python -m uvicorn main:app --host 127.0.0.1 --port 8001 --reload

启动后访问：
    前端页面: http://127.0.0.1:8001/
    API 文档: http://127.0.0.1:8001/docs
    健康检查: http://127.0.0.1:8001/health
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from routes import router

app = FastAPI(
    title="AI Code Reviewer",
    description="AI 代码审查器 — 支持流式输出 (SSE) 的多维度代码分析",
    version="1.0.0",
)


# ─── 健康检查 ───────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "service": "ai-code-reviewer", "version": "1.0.0"}


# ─── 注册路由 ───────────────────────────────────────────────
app.include_router(router)


# ─── 静态文件（前端页面）────────────────────────────────────
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def index():
    """返回前端页面"""
    return FileResponse("static/index.html")
