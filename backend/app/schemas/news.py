from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator


class NewsInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., min_length=1, max_length=300)
    summary: str | None = Field(None, max_length=5000)
    summary_type: Literal["source_provided", "generated"] | None = None
    source: str = Field(..., min_length=1, max_length=200)
    published_at: datetime | None = None
    category: str = Field(..., min_length=1, max_length=100)
    region: str | None = Field(None, min_length=1, max_length=100)
    original_url: HttpUrl

    @model_validator(mode="after")
    def summary_must_be_labeled(self):
        if (self.summary is None) != (self.summary_type is None):
            raise ValueError(
                "summary and summary_type must both be provided or omitted"
            )
        return self


class NewsRecord(NewsInput):
    news_id: str
    created_at: datetime
    updated_at: datetime


class NewsListResponse(BaseModel):
    count: int
    total: int
    limit: int
    offset: int
    articles: list[NewsRecord]
