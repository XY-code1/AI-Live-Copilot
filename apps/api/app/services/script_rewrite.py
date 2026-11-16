import asyncio

from sqlalchemy.orm import Session

from app.ai import get_provider
from app.ai.json_utils import parse_json_object
from app.ai.prompts import REWRITE_SYSTEM_PROMPT
from app.ai.provider import ChatMessage
from app.models.product import Product
from app.models.script import Script, ScriptSection


def rewrite_section(
    db: Session,
    script: Script,
    section: ScriptSection,
    instruction: str,
    product: Product | None = None,
    *,
    max_retries: int = 2,
) -> str:
    """Return a rewritten version of one section. Nothing is persisted here."""
    product_line = (
        f"商品：{product.name}" if product is not None else f"话术：{script.title}"
    )
    user_message = (
        f"{product_line}\n"
        f"场景：{script.scenario}；人群：{script.audience}；风格：{script.style}\n"
        f"段落类型：{section.title or section.kind.value}\n"
        f"原文：{section.content}\n"
        f"改写要求：{instruction}"
    )
    messages = [
        ChatMessage(role="system", content=REWRITE_SYSTEM_PROMPT),
        ChatMessage(role="user", content=user_message),
    ]

    last_error: Exception | None = None
    for _ in range(1 + max_retries):
        try:
            provider = get_provider()
            raw = asyncio.run(
                provider.complete(messages, response_format={"type": "json_object"})
            )
            content = parse_json_object(raw).get("content")
            if not isinstance(content, str) or not content.strip():
                raise ValueError("模型返回内容无效")
            return content.strip()
        except Exception as exc:  # noqa: BLE001 - surfaced to the caller
            last_error = exc

    raise RuntimeError(f"AI 改写失败：{last_error}")
