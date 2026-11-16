import asyncio
import re

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.ai import get_provider
from app.ai.json_utils import parse_json_object
from app.ai.prompts import VERIFICATION_SYSTEM_PROMPT
from app.ai.provider import ChatMessage
from app.crud import product as product_crud
from app.models.script import Script, ScriptSection
from app.models.verification import (
    IssueSeverity,
    IssueType,
    ScriptVerification,
    VerificationIssue,
    VerificationStatus,
)
from app.schemas.verification import VerificationIssueInput

MAX_MATERIAL_CHARS = 16_000

# Advertising-compliance sensitive wording (deterministic rules).
ABSOLUTE_WORDS = [
    "全网最低",
    "全网最便宜",
    "第一品牌",
    "史上最",
    "最便宜",
    "第一选择",
    "绝对",
    "100%",
    "保证",
    "包治",
    "永久",
]

MAX_MESSAGE = 1000
MAX_QUOTE = 2000
MAX_SUGGESTION = 2000


class VerificationResult(BaseModel):
    issues: list[VerificationIssueInput] = Field(default_factory=list)
    summary: str = ""


def scan_absolute_wording(sections: list[ScriptSection]) -> list[VerificationIssueInput]:
    """Deterministic rule scan over section titles and content."""
    ordered = sorted(sections, key=lambda item: item.position)
    issues: list[VerificationIssueInput] = []
    for index, section in enumerate(ordered):
        text = f"{section.title or ''}\n{section.content or ''}"
        occupied: list[tuple[int, int]] = []
        for word in sorted(ABSOLUTE_WORDS, key=len, reverse=True):
            for match in re.finditer(re.escape(word), text):
                start, end = match.span()
                if any(not (end <= seen_start or start >= seen_end) for seen_start, seen_end in occupied):
                    continue
                occupied.append((start, end))
                context_start = max(0, start - 12)
                context_end = min(len(text), end + 12)
                issues.append(
                    VerificationIssueInput(
                        section_index=index,
                        type=IssueType.absolute_wording,
                        severity=IssueSeverity.high,
                        message=f"出现绝对化/违规表述「{word}」",
                        quote=text[context_start:context_end],
                        suggestion="删除或改为可核验的客观表述。",
                    )
                )
    return issues


def _truncate(value: str | None, limit: int) -> str | None:
    if value is None:
        return None
    return value[:limit]


def build_user_message(script: Script, material: str) -> str:
    product = script.product
    lines = [f"商品：{product.name if product else script.title}"]
    if product is not None:
        if product.price is not None:
            lines.append(f"价格：{product.price} {product.currency}")
        if product.summary:
            lines.append(f"简介：{product.summary}")
        confirmed = [
            f"{attribute.label}：{attribute.value}"
            for attribute in product.attributes
            if attribute.status.value == "confirmed"
        ]
        if confirmed:
            lines.append("已确认属性：" + "；".join(confirmed))
    if material:
        truncated = len(material) > MAX_MATERIAL_CHARS
        lines.append("原始资料：")
        lines.append(material[:MAX_MATERIAL_CHARS] + ("\n（资料过长已截断）" if truncated else ""))
    else:
        lines.append("原始资料：无（请据此判断缺少来源的内容）")
    lines.append("待核验话术：")
    for index, section in enumerate(sorted(script.sections, key=lambda item: item.position)):
        lines.append(f"[{index}] {section.title or section.kind.value}：{section.content}")
    return "\n".join(lines)


def verify_script(
    db: Session, script: Script, *, max_retries: int = 2
) -> ScriptVerification:
    product = product_crud.get_product(db, script.product_id)
    material = ""
    if product is not None:
        material = "\n\n".join(
            source.content_text or "" for source in product.sources if source.content_text
        )

    sections = sorted(script.sections, key=lambda item: item.position)
    messages = [
        ChatMessage(role="system", content=VERIFICATION_SYSTEM_PROMPT),
        ChatMessage(role="user", content=build_user_message(script, material)),
    ]

    ai_issues: list[VerificationIssueInput] = []
    summary = ""
    last_error: Exception | None = None
    for _ in range(1 + max_retries):
        try:
            provider = get_provider()
            raw = asyncio.run(
                provider.complete(messages, response_format={"type": "json_object"})
            )
            parsed = VerificationResult.model_validate(parse_json_object(raw))
            ai_issues = [
                VerificationIssueInput(
                    section_index=item.section_index,
                    type=item.type,
                    severity=item.severity,
                    message=_truncate(item.message, MAX_MESSAGE) or "",
                    quote=_truncate(item.quote, MAX_QUOTE),
                    suggestion=_truncate(item.suggestion, MAX_SUGGESTION),
                    source_reference=_truncate(item.source_reference, 255),
                )
                for item in parsed.issues
            ]
            summary = parsed.summary
            break
        except Exception as exc:  # noqa: BLE001 - surfaced to the caller
            last_error = exc

    rule_issues = scan_absolute_wording(sections)

    # De-duplicate: rule findings win over AI findings for the same section+type.
    rule_keys = {(item.section_index, item.type) for item in rule_issues}
    ai_issues = [
        item for item in ai_issues if (item.section_index, item.type) not in rule_keys
    ]

    all_issues: list[tuple[VerificationIssueInput, str]] = [
        (item, "rule") for item in rule_issues
    ] + [(item, "ai") for item in ai_issues]

    ai_failed = last_error is not None and not ai_issues
    if all_issues:
        status = VerificationStatus.issue
    elif ai_failed:
        status = VerificationStatus.unverified
    else:
        status = VerificationStatus.pass_

    if rule_issues and not ai_issues:
        summary = f"AI 未发现问题，但规则命中 {len(rule_issues)} 处绝对化/违规表述。"
    elif not summary:
        if status == VerificationStatus.unverified:
            summary = f"AI 核验未完成（{last_error}），且规则未命中，暂记为未核验。"
        elif all_issues:
            summary = "发现待处理问题。"
        else:
            summary = "未发现明显问题。"

    primary_reference = next(
        (source.reference for source in product.sources if source.content_text),
        None,
    ) if product is not None else None

    verification = ScriptVerification(
        script_id=script.id, status=status, summary=summary
    )
    db.add(verification)
    db.flush()

    for item, origin in all_issues:
        section_id = None
        if item.section_index is not None and 0 <= item.section_index < len(sections):
            section = sections[item.section_index]
            quote = item.quote or ""
            if not quote or quote in section.content or quote in (section.title or ""):
                section_id = section.id
        db.add(
            VerificationIssue(
                verification_id=verification.id,
                section_id=section_id,
                type=item.type,
                severity=item.severity,
                message=item.message,
                quote=item.quote,
                suggestion=item.suggestion,
                source_reference=primary_reference,
                origin=origin,
            )
        )

    script.verification_status = status.value
    db.commit()
    db.refresh(verification)
    return verification
