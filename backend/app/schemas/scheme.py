from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator


class SchemeInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scheme_name: str = Field(..., min_length=1, max_length=200)
    government_level: Literal["central", "state"]
    state: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    eligibility: str | None = None
    benefits: str | None = None
    required_documents: list[str] | None = None
    application_deadline: date | None = None
    official_url: HttpUrl | None = None
    source_name: str = Field(..., min_length=1, max_length=200)
    source_url: HttpUrl
    last_verified_at: datetime

    @model_validator(mode="after")
    def require_state_for_state_schemes(self):
        if self.government_level == "state" and self.state is None:
            raise ValueError("state is required for state government schemes")
        return self


class SchemeRecord(SchemeInput):
    scheme_id: str
    created_at: datetime
    updated_at: datetime


class SchemeListResponse(BaseModel):
    count: int
    total: int
    limit: int
    offset: int
    schemes: list[SchemeRecord]
