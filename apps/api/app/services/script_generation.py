import asyncio
import json
import re
import uuid

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.ai import get_provider
from app.ai.prompts import SCRIPT_SYSTEM_PROMPT
from app.ai.provider import ChatMessage
from app.models.comparison import Comparison
from app.models.product import Product
from app.models.script import Script, ScriptSection, ScriptStatus
from app.schemas.script import ScriptGenerateRequest, ScriptSectionInput

MAX_CHARS = 20_000


class GeneratedScript(BaseModel):
    sections: list[ScriptSectionInput] = []


def _clean_json(raw: str) -> dict:
    text = raw.strip()
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        text = match.group(0)
    return json.loads(text)


def build_user_message(
    product: Product,
    comparison: Comparison | None,
    request: ScriptGenerateRequest,
) -> str:
    lines = [f"商品：{product.name}"]
    if product.price is not None:
        lines.append(f"价格：{product.price} {product.currency}")
    if product.summary:
        lines.append(f"简介：{product.summary}")

    confirmed = [
        f"{attribute.label}：{attribute.value}（{attribute.status.value}）"
        for attribute in product.attributes
    ]
    if confirmed:
        lines.append("属性：" + "；".join(confirmed))

    if comparison is not None:
        lines.append(f"竞品：{comparison.competitor.name}")
        for difference in comparison.differences:
            lines.append(
                f"差异[{difference.field}] 我方={difference.ours} "
                f"对方={difference.theirs} 依据={difference.evidence_type.value} "
                f"优劣={difference.side.value}"
            )
        if comparison.missing_info:
            lines.append("资料不足：" + "、".join(comparison.missing_info))

    lines.append(
        f"直播场景：{request.scenario}；目标人群：{request.audience}；话术风格：{request.style}"
    )
    return "\n".join(lines)[:MAX_CHARS]


def generate_script(
    db: Session,
    product: Product,
    request: ScriptGenerateRequest,
    comparison: Comparison | None = None,
    *,
    max_retries: int = 2,
) -> Script:
    messages = [
        ChatMessage(role="system", content=SCRIPT_SYSTEM_PROMPT),
        ChatMessage(
            role="user",
            content=build_user_message(product, comparison, request),
        ),
    ]

    parsed: GeneratedScript | None = None
    last_error: Exception | None = None
    for _ in range(max_retries):
        try:
            provider = get_provider()
            raw = asyncio.run(provider.complete(messages, response_format={"type": "json_object"}))
            parsed = GeneratedScript.model_validate(_clean_json(raw))
            break
        except Exception as exc:  # noqa: BLE001 - surfaced to the caller
            last_error = exc

    if parsed is None:
        raise RuntimeError(f"AI 生成失败：{last_error}")

    script = Script(
        series_id=uuid.uuid4(),
        product_id=product.id,
        comparison_id=comparison.id if comparison else None,
        version=1,
        title=request.title or f"{product.name} · 直播话术",
        scenario=request.scenario,
        audience=request.audience,
        style=request.style,
        status=ScriptStatus.draft,
    )
    db.add(script)
    db.flush()

    for position, item in enumerate(parsed.sections):
        db.add(
            ScriptSection(
                script_id=script.id,
                kind=item.kind,
                title=item.title,
                content=item.content,
                position=position,
                origin="ai",
            )
        )
    db.commit()
    db.refresh(script)
    return script
