import asyncio
import json
import re

from sqlalchemy.orm import Session

from app.ai import get_provider
from app.ai.prompts import EXTRACTION_SYSTEM_PROMPT
from app.ai.provider import ChatMessage
from app.models.product import Product, ProductAttribute
from app.schemas.extraction import ExtractionOutput

MAX_SOURCE_CHARS = 20_000


def _clean_json(raw: str) -> dict:
    text = raw.strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        text = match.group(0)
    return json.loads(text)


def extract_product_attributes(
    db: Session, product: Product, *, max_retries: int = 2
) -> list[ProductAttribute]:
    """Extract structured attributes from the product's source text.

    AI-generated attributes replace previous AI-generated ones; manually added
    attributes are preserved.
    """
    sources = [source for source in product.sources if source.content_text]
    if not sources:
        raise ValueError("没有可提取的资料文本，请先上传资料")

    source_text = "\n\n".join(source.content_text or "" for source in sources)
    source_text = source_text[:MAX_SOURCE_CHARS]

    messages = [
        ChatMessage(role="system", content=EXTRACTION_SYSTEM_PROMPT),
        ChatMessage(role="user", content=source_text),
    ]

    parsed: ExtractionOutput | None = None
    last_error: Exception | None = None
    for _ in range(max_retries):
        try:
            provider = get_provider()
            raw = asyncio.run(provider.complete(messages, response_format={"type": "json_object"}))
            parsed = ExtractionOutput.model_validate(_clean_json(raw))
            break
        except Exception as exc:  # noqa: BLE001 - surfaced to the caller
            last_error = exc

    if parsed is None:
        raise RuntimeError(f"AI 提取失败：{last_error}")

    for attribute in list(product.attributes):
        if attribute.origin == "ai":
            db.delete(attribute)
    db.flush()

    primary_source_id = sources[0].id
    created: list[ProductAttribute] = []
    for item in parsed.attributes:
        attribute = ProductAttribute(
            product_id=product.id,
            source_id=primary_source_id,
            label=item.label,
            value=item.value,
            status=item.status,
            origin="ai",
        )
        db.add(attribute)
        created.append(attribute)
    db.commit()
    return created
