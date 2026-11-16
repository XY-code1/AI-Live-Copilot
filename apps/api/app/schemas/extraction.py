from pydantic import BaseModel, Field

from app.models.product import ConfirmationStatus


class ExtractionAttribute(BaseModel):
    label: str = Field(min_length=1, max_length=120)
    value: str = Field(default="", max_length=2000)
    status: ConfirmationStatus = ConfirmationStatus.unconfirmed


class ExtractionOutput(BaseModel):
    attributes: list[ExtractionAttribute] = Field(default_factory=list)
