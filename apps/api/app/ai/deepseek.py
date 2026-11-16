from collections.abc import Sequence
from dataclasses import asdict

import httpx

from app.ai.provider import AIProvider, ChatMessage
from app.core.config import settings


class DeepSeekProvider(AIProvider):
    async def complete(
        self,
        messages: Sequence[ChatMessage],
        *,
        response_format: dict | None = None,
    ) -> str:
        if not settings.deepseek_api_key:
            raise RuntimeError("DEEPSEEK_API_KEY is not configured")

        payload: dict = {
            "model": "deepseek-chat",
            "messages": [asdict(message) for message in messages],
        }
        if response_format:
            payload["response_format"] = response_format

        async with httpx.AsyncClient(base_url=settings.deepseek_base_url, timeout=60) as client:
            response = await client.post(
                "/chat/completions",
                headers={"Authorization": f"Bearer {settings.deepseek_api_key}"},
                json=payload,
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
