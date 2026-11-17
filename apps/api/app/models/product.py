import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
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
    from app.models.ingestion import IngestionRun
    from app.models.script import Script
    from app.models.segment import SourceSegment

if TYPE_CHECKING:
    from app.models.comparison import Comparison


class ProductStatus(str, Enum):
    draft = "draft"
    ready = "ready"
    archived = "archived"


class ProductSourceType(str, Enum):
    pdf = "pdf"
    image = "image"
    url = "url"
    manual = "manual"


class ProductSourceStatus(str, Enum):
    ready = "ready"
    processing = "processing"
    failed = "failed"


class ConfirmationStatus(str, Enum):
    unconfirmed = "unconfirmed"
    confirmed = "confirmed"
    doubtful = "doubtful"


_PRODUCT_STATUS = SAEnum(ProductStatus, name="product_status", native_enum=False, length=32)
_SOURCE_TYPE = SAEnum(ProductSourceType, name="product_source_type", native_enum=False, length=16)
_SOURCE_STATUS = SAEnum(
    ProductSourceStatus, name="product_source_status", native_enum=False, length=16
)
_CONFIRMATION_STATUS = SAEnum(
    ConfirmationStatus, name="confirmation_status", native_enum=False, length=16
)


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        Index("ix_products_workspace_id", "workspace_id"),
        Index("ix_products_status", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    # Reserved for multi-tenant isolation; enforced in P6.
    workspace_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    summary: Mapped[str] = mapped_column(Text, nullable=False, default="")
    price: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(8), nullable=False, default="CNY")
    status: Mapped[ProductStatus] = mapped_column(
        _PRODUCT_STATUS, nullable=False, default=ProductStatus.draft
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

    sources: Mapped[list["ProductSource"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    attributes: Mapped[list["ProductAttribute"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    scripts: Mapped[list["Script"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )
    comparisons: Mapped[list["Comparison"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class ProductSource(Base):
    __tablename__ = "product_sources"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[ProductSourceType] = mapped_column(
        _SOURCE_TYPE, nullable=False, default=ProductSourceType.manual
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    # Page / fragment reference for traceability, e.g. "第 2 页 · 行程安排".
    reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # Local path or remote URL. Storage policy is local disk for the MVP.
    storage_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Text extracted from the file (PDF) so it can be traced and searched later.
    content_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    page_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    run_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("ingestion_runs.id", ondelete="SET NULL"), nullable=True
    )
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    parser: Mapped[str | None] = mapped_column(String(120), nullable=True)
    # sufficient | insufficient | restricted
    sufficiency: Mapped[str] = mapped_column(String(16), nullable=False, default="sufficient")
    status: Mapped[ProductSourceStatus] = mapped_column(
        _SOURCE_STATUS, nullable=False, default=ProductSourceStatus.ready
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    product: Mapped[Product] = relationship(back_populates="sources")
    run: Mapped["IngestionRun | None"] = relationship(
        "IngestionRun", foreign_keys="[ProductSource.run_id]", uselist=False
    )
    attributes: Mapped[list["ProductAttribute"]] = relationship(
        back_populates="source", lazy="selectin"
    )
    segments: Mapped[list["SourceSegment"]] = relationship(
        cascade="all, delete-orphan", lazy="selectin"
    )


class ProductAttribute(Base):
    __tablename__ = "product_attributes"
    __table_args__ = (Index("ix_attributes_product_id", "product_id"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    product_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    # Source this value was extracted from; kept nullable for manual values.
    source_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("product_sources.id", ondelete="SET NULL"), nullable=True
    )
    label: Mapped[str] = mapped_column(String(120), nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[ConfirmationStatus] = mapped_column(
        _CONFIRMATION_STATUS, nullable=False, default=ConfirmationStatus.unconfirmed
    )
    # "ai" for model-extracted values, "manual" otherwise.
    origin: Mapped[str] = mapped_column(String(16), nullable=False, default="manual")
    # Page / fragment reference copied from the source for traceability.
    source_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    product: Mapped[Product] = relationship(back_populates="attributes")
    source: Mapped[ProductSource | None] = relationship(back_populates="attributes")
