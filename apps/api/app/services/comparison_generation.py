import asyncio
import json
import re

from sqlalchemy.orm import Session

from app.ai import get_provider
from app.ai.prompts import COMPARISON_SYSTEM_PROMPT
from app.ai.provider import ChatMessage
from app.models.comparison import Comparison, ComparisonDifference
from app.schemas.comparison import ComparisonGenerationOutput

MAX_CHARS = 20_000


def _clean_json(raw: str) -> dict:
    text = raw.strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        text = match.group(0)
    return json.loads(text)


def generate_comparison_differences(
    db: Session, comparison: Comparison, *, max_retries: int = 2
) -> list[ComparisonDifference]:
    """Generate differences from our product material and competitor material.

    AI-generated differences replace previous AI-generated ones; manually added
    differences are preserved. ``missing_info`` is updated on the comparison.
    """
    product = comparison.product
    competitor = comparison.competitor

    ours = (
        "\n\n".join(source.content_text or "" for source in product.sources if source.content_text)
        or product.summary
    )
    theirs = competitor.material or ""

    if not (ours or "").strip() and not theirs.strip():
        raise ValueError("资料不足：请先为商品上传资料，并填写竞品资料")

    user_message = (
        f"【我方商品】{product.name}\n{(ours or '')[:MAX_CHARS]}\n\n"
        f"【竞品】{competitor.name}（{competitor.brand}）\n{theirs[:MAX_CHARS]}"
    )
    messages = [
        ChatMessage(role="system", content=COMPARISON_SYSTEM_PROMPT),
        ChatMessage(role="user", content=user_message),
    ]

    parsed: ComparisonGenerationOutput | None = None
    last_error: Exception | None = None
    for _ in range(max_retries):
        try:
            provider = get_provider()
            raw = asyncio.run(provider.complete(messages, response_format={"type": "json_object"}))
            parsed = ComparisonGenerationOutput.model_validate(_clean_json(raw))
            break
        except Exception as exc:  # noqa: BLE001 - surfaced to the caller
            last_error = exc

    if parsed is None:
        raise RuntimeError(f"AI 生成失败：{last_error}")

    for difference in list(comparison.differences):
        if difference.origin == "ai":
            db.delete(difference)
    db.flush()

    our_source = next((source for source in product.sources if source.content_text), None)
    source_reference = our_source.reference if our_source else None

    created: list[ComparisonDifference] = []
    for item in parsed.differences:
        difference = ComparisonDifference(
            comparison_id=comparison.id,
            field=item.field,
            ours=item.ours,
            theirs=item.theirs,
            evidence_type=item.evidence_type,
            side=item.side,
            note=item.note,
            origin="ai",
            source_reference=source_reference,
        )
        db.add(difference)
        created.append(difference)

    comparison.missing_info = parsed.missing_info
    comparison.status = "ready"
    db.commit()
    return created
