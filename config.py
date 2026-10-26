"""
配置管理 — 从 .env 文件读取

使用 python-dotenv 加载项目根目录的 .env 文件。
只需配置 LLM 相关参数，不需要数据库配置。

支持任何 OpenAI 兼容接口：
- 阿里云 Qwen（本项目默认）
- OpenAI GPT
- DeepSeek
- Ollama（本地部署）
"""

import os
from dotenv import load_dotenv

# 加载项目根目录的 .env
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))


class Settings:
    QWEN_API_KEY: str = os.getenv("QWEN_API_KEY", "")
    QWEN_MODEL: str = os.getenv("QWEN_MODEL", "qwen3.7-plus")
    QWEN_BASE_URL: str = os.getenv(
        "QWEN_BASE_URL",
        "https://token-plan.cn-beijing.maas.aliyuncs.com/compatible-mode/v1"
    )


settings = Settings()
