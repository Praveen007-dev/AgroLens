
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class ScanCreate(BaseModel):
    """Provisional schema for submitting an AgroLens scan."""

    model_config = ConfigDict(extra="forbid")

    scan_id: Optional[str] = None

    crop: str = Field(..., min_length=1, max_length=100)

    scan_timestamp: datetime

    model_version: str = Field(..., min_length=1, max_length=100)

    disease_label: str = Field(..., min_length=1, max_length=150)

    confidence: float = Field(..., ge=0.0, le=1.0)

    image_ref: Optional[str] = None

    # Optional farmer feedback
    farmer_confirmed_label: Optional[str] = None
    feedback_text: Optional[str] = None

    # Optional location information
    location_consent: bool = False
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)

    # Optional environmental metadata
    environmental_data: Optional[dict] = None
    additional_metadata: Optional[dict] = None


class ScanResponse(BaseModel):
    """Response returned after scan submission."""

    scan_id: str
    submission_status: str
    message: str


class ScanDetails(BaseModel):
    """Basic scan details returned by the API."""

    scan_id: str
    crop: str
    scan_timestamp: datetime
    model_version: str
    disease_label: str
    confidence: float
    image_ref: Optional[str] = None
    verification_status: str = "pending"
