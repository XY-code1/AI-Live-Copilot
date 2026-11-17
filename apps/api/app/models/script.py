import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
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


class ScriptStatus(str, Enum):
    draft = "draft"
    verified = "verified"
    issue = "issue"


class ScriptSectionKind(str, Enum):
    opening = "opening"
    intro = "intro"
    selling_points = "selling_points"
    differentiation = "differentiation"
    interaction = "interaction"
    closing = "closing"
    risk = "risk"


SCRIPT_STATUS = SAEnum(ScriptStatus, name="script_status", native_enum=False, length=16)
SECTION_KIND = SAEnum(ScriptSectionKind, name="script_section_kind", native_enum=False, length=24)


class Script(Base):
    __tablename__ = "scripts"
    __table_args__ = (
        Index("ix_scripts_series_id", "series_id"),
        Index("ix_scripts_product_id", "product_id"),
        UniqueConstraint("series_id", "version", name="uq_scripts_series_version"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    series_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, default=uuid.uuid4)
    workspace_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    product_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    comparison_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("comparisons.id", ondelete="SET NULL"), nullable=True
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    scenario: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    audience: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    style: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    status: Mapped[ScriptStatus] = mapped_column(
        SCRIPT_STATUS, nullable=False, default=ScriptStatus.draft
    )
    verification_status: Mapped[str] = mapped_column(
        String(16), nullable=False, default="unverified"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    product: Mapped["Product"] = relationship(back_populates="scripts")
    sections: Mapped[list["ScriptSection"]] = relationship(
        back_populates="script", cascade="all, delete-orphan", lazy="selectin"
    )


class ScriptSection(Base):
    __tablename__ = "script_sections"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    script_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("scripts.id", ondelete="CASCADE"), nullable=False
    )
    kind: Mapped[ScriptSectionKind] = mapped_column(
        SECTION_KIND, nullable=False, default=ScriptSectionKind.intro
    )
    title: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    content: Mapped[str] = mapped_column(Text, nullable=False, default="")
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    origin: Mapped[str] = mapped_column(String(16), nullable=False, default="ai")
    # Page / fragment reference copied from the source material (P5 traceability).
    source_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)

    script: Mapped[Script] = relationship(back_populates="sections")
