from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SegmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    source_id: UUID
    kind: str
    page_no: int | None = None
    position: int
    content: str
    structured: dict | list | None = None
    created_at: datetime
