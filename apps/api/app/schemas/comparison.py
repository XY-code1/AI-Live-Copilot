from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.comparison import AdvantageSide, EvidenceType


class CompetitorCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    brand: str = ""
    price: float | None = None
    notes: str = ""
    material: str = ""


class CompetitorUpdate(BaseModel):
    name: str | None = None
    brand: str | None = None
    price: float | None = None
    notes: str | None = None
    material: str | None = None


class CompetitorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID | None = None
    name: str
    brand: str
    price: float | None = None
    notes: str
    material: str
    created_at: datetime


class DifferenceCreate(BaseModel):
    field: str = Field(min_length=1, max_length=120)
    ours: str = ""
    theirs: str = ""
    evidence_type: EvidenceType = EvidenceType.source
    side: AdvantageSide = AdvantageSide.neutral
    note: str | None = None


class GeneratedDifference(BaseModel):
    field: str = Field(min_length=1, max_length=120)
    ours: str = ""
    theirs: str = ""
    evidence_type: EvidenceType = EvidenceType.source
    side: AdvantageSide = AdvantageSide.neutral
    note: str | None = None


class ComparisonGenerationOutput(BaseModel):
    differences: list[GeneratedDifference] = Field(default_factory=list)
    missing_info: list[str] = Field(default_factory=list)


class DifferenceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    comparison_id: UUID
    field: str
    ours: str
    theirs: str
    evidence_type: EvidenceType
    side: AdvantageSide
    note: str | None = None
    origin: str
    source_reference: str | None = None
    created_at: datetime


class ComparisonCreate(BaseModel):
    product_id: UUID
    competitor_id: UUID


class ComparisonOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID | None = None
    product_id: UUID
    competitor_id: UUID
    status: str
    competitor: CompetitorOut
    missing_info: list[str] = Field(default_factory=list)
    differences: list[DifferenceOut] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
