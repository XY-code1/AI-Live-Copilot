from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.script import ScriptSectionKind, ScriptStatus


class ScriptSectionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    script_id: UUID
    kind: ScriptSectionKind
    title: str
    content: str
    position: int
    origin: str


class ScriptOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    series_id: UUID
    product_id: UUID
    comparison_id: UUID | None = None
    version: int
    title: str
    scenario: str
    audience: str
    style: str
    status: ScriptStatus
    verification_status: str
    sections: list[ScriptSectionOut] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class ScriptGenerateRequest(BaseModel):
    title: str = Field(default="", max_length=200)
    scenario: str = Field(default="日常带货", max_length=120)
    audience: str = Field(default="", max_length=120)
    style: str = Field(default="亲切自然", max_length=120)
    comparison_id: UUID | None = None


class ScriptSectionInput(BaseModel):
    kind: ScriptSectionKind
    title: str = Field(default="", max_length=120)
    content: str = Field(default="", max_length=5000)


class ScriptVersionCreate(BaseModel):
    title: str | None = None
    sections: list[ScriptSectionInput] = Field(default_factory=list, min_length=1)


class SectionRewriteRequest(BaseModel):
    instruction: str = Field(
        default="更口语、更有感染力，但不得夸大或绝对化", min_length=1, max_length=500
    )


class SectionRewriteOutput(BaseModel):
    content: str
