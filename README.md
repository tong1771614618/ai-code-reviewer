<div align="center">

# 📝 AI Code Reviewer

**基于 LLM + SSE 流式输出的多维度 AI 代码审查工具**

粘贴代码 → 实时逐字输出审查报告，0.5 秒看到第一行结果

`FastAPI` · `Streaming / SSE` · `OpenAI 兼容 API` · `原生 JS`

</div>

---

## ✨ 为什么做这个

传统调用 LLM 是「等它全部生成完再一次性返回」——一段代码审查报告通常 500~2000 字，用户要干等 5~10 秒，很容易以为卡死了。

本项目用 **SSE（Server-Sent Events）流式输出** 解决这个问题：LLM 边生成、后端边推、前端边渲染，用户 0.5 秒就能看到第一行文字，体验和 ChatGPT 一样丝滑。

这既是一个可用的代码审查工具，也是一个 **Streaming 技术的完整学习范例**（从 LLM `stream=True` 到前端 `ReadableStream` 的全链路）。

## 🎯 功能特性

- **多维度审查** — 安全、逻辑、性能、代码规范、可维护性 5 个维度，按优先级排序
- **严重度分级** — 🔴 严重 / 🟡 警告 / 🔵 建议，每个问题都给出具体修复代码
- **流式输出** — SSE 实时推送，打字机效果，带耗时统计
- **多语言支持** — PHP / Python / JavaScript / Java / Go / Rust / SQL 等，自动识别或手动指定
- **聚焦模式** — 可指定只重点看 `security` / `performance` / `style`
- **内置示例** — 前端自带 4 个典型反面教材（PHP SQL 注入、Python 性能、JS 异步、Laravel N+1），一键载入

## 🛠 技术栈

| 层 | 技术 | 说明 |
|----|------|------|
| 后端 | FastAPI + Uvicorn | 异步 Web 框架，原生支持 SSE |
| LLM | OpenAI SDK | 兼容任意 OpenAI 格式接口（默认阿里云 Qwen） |
| 前端 | 原生 HTML/CSS/JS | `fetch + ReadableStream` 消费流式响应 |
| 校验 | Pydantic | 自动请求体校验 + 生成 API 文档 |

## 🚀 快速开始

### 1. 安装依赖

```bash
cd ai-code-reviewer
pip install -r requirements.txt
```

### 2. 配置 API Key

```bash
cp .env.example .env
```

编辑 `.env`，填入你的 API Key。默认使用阿里云 Qwen，切换到其他 LLM 只需改 `QWEN_BASE_URL` 和 `QWEN_MODEL`：

| 提供商 | `QWEN_BASE_URL` | `QWEN_MODEL` 示例 |
|--------|-----------------|-------------------|
| 阿里云 Qwen | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-plus` |
| OpenAI | `https://api.openai.com/v1` | `gpt-4o-mini` |
| DeepSeek | `https://api.deepseek.com/v1` | `deepseek-chat` |
| Ollama（本地） | `http://localhost:11434/v1` | `qwen2.5-coder` |

### 3. 启动服务

```bash
python -m uvicorn main:app --host 127.0.0.1 --port 8001 --reload
```

### 4. 打开浏览器

- 🖥 前端页面: http://127.0.0.1:8001/
- 📖 API 文档（Swagger）: http://127.0.0.1:8001/docs

## 📡 API 接口

### `POST /review` — 非流式审查

一次性返回完整 JSON，适合后端调用 / API 集成。

```bash
curl -X POST http://127.0.0.1:8001/review \
  -H "Content-Type: application/json" \
  -d '{"code": "eval(input())", "language": "python", "focus": "security"}'
```

响应：

```json
{ "review": "### 📋 审查概览\n\n- **语言**: Python\n..." }
```

### `POST /review-stream` — 流式审查（SSE）

LLM 边生成边推送，适合前端实时展示。

```bash
curl -N -X POST http://127.0.0.1:8001/review-stream \
  -H "Content-Type: application/json" \
  -d '{"code": "eval(input())", "language": "python"}'
```

### 请求参数

| 字段 | 类型 | 必填 | 说明 |
|------|------|:----:|------|
| `code` | string | ✅ | 待审查的代码 |
| `language` | string | ❌ | 编程语言，不传则 LLM 自动识别 |
| `focus` | string | ❌ | 重点方向：`security` / `performance` / `style` |

## 🔬 核心原理：SSE 流式输出全链路

```
LLM (stream=True)
   │  每次返回几个字的 delta
   ▼
Python Generator (yield)
   │  review_stream() 逐 chunk yield
   ▼
FastAPI StreamingResponse
   │  media_type="text/event-stream"
   ▼
前端 fetch + ReadableStream
      reader.read() 循环读取 → 实时渲染 Markdown
```

**关键点 1 — LLM 流式调用：**

```python
stream = client.chat.completions.create(model=..., messages=..., stream=True)
for chunk in stream:
    if not chunk.choices:      # 防御空 chunk（首个可能只含元数据）
        continue
    if chunk.choices[0].delta.content:
        yield chunk.choices[0].delta.content   # 立即推送增量文本
```

**关键点 2 — 为什么用 `fetch` 而不是 `EventSource`？**

浏览器内置的 `EventSource` 只支持 **GET** 请求。代码审查必须用 **POST**（代码可能很长，塞不进 URL），所以前端改用 `fetch + ReadableStream` 手动消费 SSE 流。

**关键点 3 — Nginx 缓冲陷阱：**

生产环境若经过 Nginx，需加响应头 `X-Accel-Buffering: no`，否则 Nginx 会缓冲整个响应，流式效果失效。

## 📁 项目结构

```
ai-code-reviewer/
├── main.py           # FastAPI 入口 + 静态文件服务
├── routes.py         # API 路由（/review, /review-stream）
├── ai_service.py     # 核心逻辑（流式 + 非流式审查）
├── prompts.py        # LLM Prompt（多维度审查模板）
├── schemas.py        # Pydantic 请求模型
├── config.py         # 配置管理（读取 .env）
├── llm_client.py     # OpenAI 客户端初始化
├── logger.py         # 终端彩色日志 + 文件记录
├── static/
│   └── index.html    # 前端页面（暗色主题 + 打字机效果）
├── .env.example      # 环境变量模板
└── requirements.txt  # Python 依赖
```

## 📝 License

MIT
