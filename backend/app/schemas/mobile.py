from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class MobileModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class TopPrediction(MobileModel):
    label: str = Field(min_length=1, max_length=200)
    confidence: float = Field(ge=0, le=1)


class AIPrediction(MobileModel):
    prediction_id: str = Field(min_length=1, max_length=100)
    crop: str = Field(min_length=1, max_length=100)
    disease_label: str = Field(min_length=1, max_length=200)
    confidence: float = Field(ge=0, le=1)
    top_predictions: list[TopPrediction] = Field(default_factory=list, max_length=20)
    is_low_confidence: bool = False
    model_version: str = Field(min_length=1, max_length=100)
    inference_timestamp: datetime

    @field_validator("inference_timestamp")
    @classmethod
    def inference_timestamp_must_include_timezone(
        cls, value: datetime
    ) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("inference_timestamp must include a timezone.")
        return value


class ScanLocation(MobileModel):
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    region: str | None = Field(default=None, max_length=150)
    has_consent: bool = False


class FarmerFeedback(MobileModel):
    is_confirmed: bool
    corrected_label: str | None = Field(default=None, max_length=200)
    notes: str | None = Field(default=None, max_length=5000)
    submitted_at: datetime

    @field_validator("submitted_at")
    @classmethod
    def submitted_at_must_include_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("submitted_at must include a timezone.")
        return value

    @model_validator(mode="after")
    def corrected_label_requires_disagreement(self):
        if self.is_confirmed and self.corrected_label is not None:
            raise ValueError(
                "corrected_label is only valid when is_confirmed is false."
            )
        return self


class ScanFeedback(FarmerFeedback):
    pass


class MobileScanCreate(MobileModel):
    scan_id: str = Field(min_length=1, max_length=100)
    timestamp: datetime
    crop: str = Field(min_length=1, max_length=100)
    image_path: str | None = Field(default=None, max_length=2048)
    image_reference: str | None = Field(default=None, max_length=500)
    ai_prediction: AIPrediction
    farmer_feedback: FarmerFeedback | None = None
    expert_verification: dict[str, Any] | None = None
    location: ScanLocation = Field(default_factory=ScanLocation)
    sync_status: Literal["pending", "synced"] = "pending"
    metadata: dict[str, Any] | None = None

    @field_validator("timestamp")
    @classmethod
    def timestamp_must_include_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timestamp must include a timezone.")
        return value

    @model_validator(mode="after")
    def prediction_crop_must_match_scan(self):
        self.crop = self.crop.strip()
        if self.crop.casefold() != self.ai_prediction.crop.strip().casefold():
            raise ValueError("ai_prediction.crop must match scan crop.")
        return self


class ScanBatchResponse(BaseModel):
    synced_count: int


class ScanFeedbackInput(FarmerFeedback):
    pass


class BasicUserProfile(BaseModel):
    user_id: str
    username: str
    email: str
    created_at: datetime


class AuthCredentials(MobileModel):
    username: str = Field(min_length=3, max_length=32)
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=8, max_length=128)


class AuthLogin(MobileModel):
    identifier: str = Field(min_length=1, max_length=254)
    password: str = Field(min_length=1, max_length=128)


class AuthSessionResponse(BaseModel):
    access_token: str
    token_type: Literal["Bearer"] = "Bearer"
    expires_at: datetime
    user: BasicUserProfile


class ForgotPasswordRequest(MobileModel):
    email: str = Field(min_length=3, max_length=254)


class ResetPasswordRequest(MobileModel):
    reset_token: str = Field(min_length=20, max_length=200)
    new_password: str = Field(min_length=8, max_length=128)


class ChangePasswordRequest(MobileModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class GenericMessage(BaseModel):
    message: str
