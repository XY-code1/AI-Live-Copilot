from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.product import (
    ConfirmationStatus,
    ProductSourceStatus,
    ProductSourceType,
    ProductStatus,
)


class ProductAttributeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    label: str
    value: str
    status: ConfirmationStatus
    origin: str
    source_id: UUID | None = None
    source_reference: str | None = None


class ProductSourceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    type: ProductSourceType
    name: str
    reference: str | None = None
    status: ProductSourceStatus
    page_count: int | None = None
    created_at: datetime


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID | None = None
    name: str
    category: str
    summary: str
    price: float | None = None
    currency: str
    status: ProductStatus
    sources: list[ProductSourceOut] = []
    attributes: list[ProductAttributeOut] = []
    created_at: datetime
    updated_at: datetime


class ProductCreate(BaseModel):
    name: str
    category: str = ""
    summary: str = ""
    price: float | None = None
    currency: str = "CNY"


class ProductUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    summary: str | None = None
    price: float | None = None
    currency: str | None = None
    status: ProductStatus | None = None


class AttributeCreate(BaseModel):
    label: str
    value: str = ""
    status: ConfirmationStatus = ConfirmationStatus.unconfirmed
