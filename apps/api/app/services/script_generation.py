import asyncio
import uuid

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.ai import get_provider
from app.ai.json_utils import parse_json_object
from app.ai.prompts import SCRIPT_SYSTEM_PROMPT
from app.ai.provider import ChatMessage
from app.models.comparison import Comparison
from app.models.product import Product, ProductSource
from app.models.script import Script, ScriptSection, ScriptStatus
from app.schemas.script import ScriptGenerateRequest, ScriptSectionInput

MAX_MATERIAL_CHARS = 16_000


class GeneratedScript(BaseModel):
    sections: list[ScriptSectionInput] = Field(default_factory=list)


def build_user_message(
    product: Product,
    comparison: Comparison | None,
    request: ScriptGenerateRequest,
) -> str:
    # User directives come first so truncation can never drop them.
    lines = [
        f"直播场景：{request.scenario}；目标人群：{request.audience}；话术风格：{request.style}"
    ]
    lines.append(f"商品：{product.name}")
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

    material = "\n".join(lines[1:])
    return f"{lines[0]}\n{material[:MAX_MATERIAL_CHARS]}"


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
    for _ in range(1 + max_retries):
        try:
            provider = get_provider()
            raw = asyncio.run(
                provider.complete(messages, response_format={"type": "json_object"})
            )
            candidate = GeneratedScript.model_validate(parse_json_object(raw))
            if not candidate.sections:
                raise ValueError("AI 未生成任何段落")
            if not any(item.kind.value == "risk" for item in candidate.sections):
                raise ValueError("AI 未包含风险提示段落")
            parsed = candidate
            break
        except Exception as exc:  # noqa: BLE001 - surfaced to the caller
            last_error = exc

    if parsed is None:
        raise RuntimeError(f"AI 生成失败：{last_error}")

    primary_source: ProductSource | None = next(
        (source for source in product.sources if source.content_text), None
    )
    script = Script(
        series_id=uuid.uuid4(),
        workspace_id=product.workspace_id,
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
                source_reference=primary_source.reference if primary_source else None,
            )
        )
    db.commit()
    db.refresh(script)
    return script
