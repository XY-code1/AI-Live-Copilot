import asyncio
import json
import re

from sqlalchemy.orm import Session

from app.ai import get_provider
from app.ai.prompts import REWRITE_SYSTEM_PROMPT
from app.ai.provider import ChatMessage
from app.models.script import Script, ScriptSection


def _clean_json(raw: str) -> dict:
    text = raw.strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        text = match.group(0)
    return json.loads(text)


def rewrite_section(
    db: Session,
    script: Script,
    section: ScriptSection,
    instruction: str,
    *,
    max_retries: int = 2,
) -> str:
    """Return a rewritten version of one section. Nothing is persisted here."""
    user_message = (
        f"商品：{script.title}\n"
        f"场景：{script.scenario}；人群：{script.audience}；风格：{script.style}\n"
        f"段落类型：{section.title or section.kind}\n"
        f"原文：{section.content}\n"
        f"改写要求：{instruction}"
    )
    messages = [
        ChatMessage(role="system", content=REWRITE_SYSTEM_PROMPT),
        ChatMessage(role="user", content=user_message),
    ]

    last_error: Exception | None = None
    for _ in range(max_retries):
        try:
            provider = get_provider()
            raw = asyncio.run(provider.complete(messages, response_format={"type": "json_object"}))
            content = str(_clean_json(raw)["content"]).strip()
            if content:
                return content
            raise ValueError("模型返回空内容")
        except Exception as exc:  # noqa: BLE001 - surfaced to the caller
            last_error = exc

    raise RuntimeError(f"AI 改写失败：{last_error}")
