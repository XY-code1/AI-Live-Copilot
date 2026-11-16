import asyncio

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

# Deterministic rule: advertising-compliance sensitive wording.
ABSOLUTE_WORDS = [
    "全网最低",
    "全网最便宜",
    "第一品牌",
    "绝对",
    "100%",
    "史上最",
    "最便宜",
    "最强",
    "第一选择",
    "保证",
    "包治",
    "永久",
]


class VerificationResult(BaseModel):
    issues: list[VerificationIssueInput] = Field(default_factory=list)
    summary: str = ""


def scan_absolute_wording(sections: list[ScriptSection]) -> list[VerificationIssueInput]:
    issues: list[VerificationIssueInput] = []
    for section in sections:
        for word in ABSOLUTE_WORDS:
            position = section.content.find(word)
            if position < 0:
                continue
            start = max(0, position - 12)
            end = min(len(section.content), position + len(word) + 12)
            issues.append(
                VerificationIssueInput(
                    section_index=section.position,
                    type=IssueType.absolute_wording,
                    severity=IssueSeverity.high,
                    message=f"出现绝对化/违规表述「{word}」",
                    quote=section.content[start:end],
                    suggestion="删除或改为可核验的客观表述。",
                )
            )
    return issues


def build_user_message(script: Script, material: str) -> str:
    lines = [f"商品：{script.title}"]
    if material:
        lines.append("原始资料：")
        lines.append(material[:MAX_MATERIAL_CHARS])
    else:
        lines.append("原始资料：无（请据此判断缺少来源的内容）")
    lines.append("待核验话术：")
    for section in sorted(script.sections, key=lambda item: item.position):
        lines.append(f"[{section.position}] {section.title or section.kind.value}：{section.content}")
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
            ai_issues = parsed.issues
            summary = parsed.summary
            break
        except Exception as exc:  # noqa: BLE001 - surfaced to the caller
            last_error = exc

    if ai_issues and not summary:
        summary = "AI 核验发现问题，详见下方列表。"

    rule_issues = scan_absolute_wording(sections)
    all_issues: list[tuple[VerificationIssueInput, str]] = [
        (item, "rule") for item in rule_issues
    ] + [(item, "ai") for item in ai_issues]
    status = VerificationStatus.issue if all_issues else VerificationStatus.pass_

    if not summary:
        summary = "未发现明显问题。" if not all_issues else "发现待处理问题。"
    if last_error is not None and not ai_issues:
        summary = f"AI 核验未完成（{last_error}），仅应用规则核验结果。"

    verification = ScriptVerification(
        script_id=script.id, status=status, summary=summary
    )
    db.add(verification)
    db.flush()

    for item, origin in all_issues:
        section_id = None
        if item.section_index is not None and 0 <= item.section_index < len(sections):
            section_id = sections[item.section_index].id
        db.add(
            VerificationIssue(
                verification_id=verification.id,
                section_id=section_id,
                type=item.type,
                severity=item.severity,
                message=item.message,
                quote=item.quote,
                suggestion=item.suggestion,
                origin=origin,
            )
        )

    script.verification_status = status.value
    db.commit()
    db.refresh(verification)
    return verification
