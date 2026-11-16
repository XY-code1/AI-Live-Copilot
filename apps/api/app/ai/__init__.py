from app.ai.deepseek import DeepSeekProvider
from app.ai.provider import AIProvider, ChatMessage
from app.core.config import settings


def get_provider() -> AIProvider:
    if settings.ai_provider == "deepseek":
        return DeepSeekProvider()
    raise ValueError(f"未知的 AI provider: {settings.ai_provider}")


__all__ = ["AIProvider", "ChatMessage", "get_provider"]
