from datetime import datetime
from typing import Literal

from pydantic import BaseModel, HttpUrl


class SchemeSourceLink(BaseModel):
    title: str
    url: HttpUrl


class SchemeCandidate(BaseModel):
    source_record_id: str
    department: str
    name: str
    local_name: str | None
    review_status: Literal["unverified"] = "unverified"


class SchemeSourceResult(BaseModel):
    source_id: str
    source_name: str
    government_level: Literal["central", "state"]
    state: str | None
    source_url: HttpUrl
    status: Literal[
        "available",
        "http_error",
        "redirected",
        "invalid_content",
        "fetch_error",
    ]
    content_status: Literal[
        "scheme_references_found",
        "error_page_detected",
        "no_scheme_references",
    ] | None
    collection_status: Literal["complete", "partial", "failed", "not_supported"]
    checked_at: datetime
    page_title: str | None
    headings: list[str]
    relevant_links: list[SchemeSourceLink]
    candidate_schemes: list[SchemeCandidate]


class SchemeDiscoveryResponse(BaseModel):
    agent: str
    cached: bool
    checked_at: datetime
    sources: list[SchemeSourceResult]
