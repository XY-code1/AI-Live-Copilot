import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
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

if TYPE_CHECKING:
    from app.models.product import Product


class ComparisonStatus(str, Enum):
    pending = "pending"
    ready = "ready"
    failed = "failed"


class EvidenceType(str, Enum):
    source = "source"
    inferred = "inferred"
    speculative = "speculative"


class AdvantageSide(str, Enum):
    ours = "ours"
    theirs = "theirs"
    neutral = "neutral"


_COMPARISON_STATUS = SAEnum(
    ComparisonStatus, name="comparison_status", native_enum=False, length=16
)
_EVIDENCE_TYPE = SAEnum(EvidenceType, name="evidence_type", native_enum=False, length=16)
_ADVANTAGE_SIDE = SAEnum(AdvantageSide, name="advantage_side", native_enum=False, length=16)


class Competitor(Base):
    __tablename__ = "competitors"
    __table_args__ = (Index("ix_competitors_workspace_id", "workspace_id"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    brand: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    price: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    comparisons: Mapped[list["Comparison"]] = relationship(
        back_populates="competitor", cascade="all, delete-orphan"
    )


class Comparison(Base):
    __tablename__ = "comparisons"
    __table_args__ = (
        Index("ix_comparisons_product_id", "product_id"),
        Index("ix_comparisons_competitor_id", "competitor_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    product_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    competitor_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("competitors.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[ComparisonStatus] = mapped_column(
        _COMPARISON_STATUS, nullable=False, default=ComparisonStatus.pending
    )
    missing_info: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    product: Mapped["Product"] = relationship(back_populates="comparisons")
    competitor: Mapped[Competitor] = relationship(back_populates="comparisons")
    differences: Mapped[list["ComparisonDifference"]] = relationship(
        back_populates="comparison", cascade="all, delete-orphan", lazy="selectin"
    )


class ComparisonDifference(Base):
    __tablename__ = "comparison_differences"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    comparison_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("comparisons.id", ondelete="CASCADE"), nullable=False
    )
    field: Mapped[str] = mapped_column(String(120), nullable=False)
    ours: Mapped[str] = mapped_column(Text, nullable=False, default="")
    theirs: Mapped[str] = mapped_column(Text, nullable=False, default="")
    evidence_type: Mapped[EvidenceType] = mapped_column(
        _EVIDENCE_TYPE, nullable=False, default=EvidenceType.source
    )
    side: Mapped[AdvantageSide] = mapped_column(
        _ADVANTAGE_SIDE, nullable=False, default=AdvantageSide.neutral
    )
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    comparison: Mapped[Comparison] = relationship(back_populates="differences")
