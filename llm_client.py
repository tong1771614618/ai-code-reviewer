"""
OpenAI 客户端初始化

使用 OpenAI SDK 连接任何兼容接口的 LLM。
修改 .env 中的 QWEN_BASE_URL 即可切换不同的 LLM 提供商。
"""

from openai import OpenAI
from config import settings

client = OpenAI(
    api_key=settings.QWEN_API_KEY,
    base_url=settings.QWEN_BASE_URL,
)
