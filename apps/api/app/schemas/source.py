from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SourceTextOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product_id: UUID
    name: str
    reference: str | None = None
    page_count: int | None = None
    text: str
    created_at: datetime | None = None
