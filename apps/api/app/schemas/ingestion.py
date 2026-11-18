from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class IngestionRunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product_id: UUID | None = None
    source_id: UUID | None = None
    type: str
    status: str
    parser: str | None = None
    content_hash: str | None = None
    snapshot_path: str | None = None
    final_url: str | None = None
    redirect_chain: list[str] = []
    requested_url: str | None = None
    fetch_duration_ms: int | None = None
    raw_size_bytes: int | None = None
    cleaned_text_length: int | None = None
    error: str | None = None
    started_at: datetime
    finished_at: datetime | None = None
