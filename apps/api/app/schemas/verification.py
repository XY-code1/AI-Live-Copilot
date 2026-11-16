from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.verification import IssueSeverity, IssueType


class VerificationIssueOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    verification_id: UUID
    section_id: UUID | None = None
    type: IssueType
    severity: IssueSeverity
    message: str
    quote: str | None = None
    suggestion: str | None = None
    source_reference: str | None = None
    origin: str


class ScriptVerificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    script_id: UUID
    status: str
    summary: str
    issues: list[VerificationIssueOut] = Field(default_factory=list)
    created_at: datetime


class VerificationIssueInput(BaseModel):
    section_index: int | None = None
    type: IssueType = IssueType.unsupported_claim
    severity: IssueSeverity = IssueSeverity.medium
    message: str = Field(default="", max_length=1000)
    quote: str | None = Field(default=None, max_length=2000)
    suggestion: str | None = Field(default=None, max_length=2000)
    source_reference: str | None = Field(default=None, max_length=255)


class VerificationOutput(BaseModel):
    issues: list[VerificationIssueInput] = Field(default_factory=list)
    summary: str = ""
