import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    Uuid,
    func,
)
from sqlalchemy import (
    Enum as SAEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class VerificationStatus(str, Enum):
    unverified = "unverified"
    pass_ = "pass"
    issue = "issue"


class IssueType(str, Enum):
    unsupported_claim = "unsupported_claim"
    exaggeration = "exaggeration"
    absolute_wording = "absolute_wording"
    price_mismatch = "price_mismatch"
    missing_restriction = "missing_restriction"
    source_missing = "source_missing"


class IssueSeverity(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"


_VERIFICATION_STATUS = SAEnum(
    VerificationStatus,
    name="verification_status",
    native_enum=False,
    length=16,
    values_callable=lambda enum: [member.value for member in enum],
)
def _values(enum):
    return [member.value for member in enum]


_ISSUE_TYPE = SAEnum(
    IssueType, name="issue_type", native_enum=False, length=24, values_callable=_values
)
_ISSUE_SEVERITY = SAEnum(
    IssueSeverity, name="issue_severity", native_enum=False, length=16, values_callable=_values
)


class ScriptVerification(Base):
    __tablename__ = "script_verifications"
    __table_args__ = (Index("ix_verifications_script_id", "script_id"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    script_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("scripts.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[VerificationStatus] = mapped_column(
        _VERIFICATION_STATUS, nullable=False, default=VerificationStatus.unverified
    )
    summary: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    issues: Mapped[list["VerificationIssue"]] = relationship(
        back_populates="verification", cascade="all, delete-orphan", lazy="selectin"
    )


class VerificationIssue(Base):
    __tablename__ = "verification_issues"
    __table_args__ = (Index("ix_issues_verification_id", "verification_id"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    verification_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("script_verifications.id", ondelete="CASCADE"), nullable=False
    )
    section_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("script_sections.id", ondelete="SET NULL"), nullable=True
    )
    type: Mapped[IssueType] = mapped_column(
        _ISSUE_TYPE, nullable=False, default=IssueType.unsupported_claim
    )
    severity: Mapped[IssueSeverity] = mapped_column(
        _ISSUE_SEVERITY, nullable=False, default=IssueSeverity.medium
    )
    message: Mapped[str] = mapped_column(Text, nullable=False, default="")
    quote: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggestion: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Source material this finding is checked against, when available.
    source_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    origin: Mapped[str] = mapped_column(String(16), nullable=False, default="ai")

    verification: Mapped[ScriptVerification] = relationship(back_populates="issues")
