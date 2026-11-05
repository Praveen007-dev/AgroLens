from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class MandiPrice(BaseModel):
    model_config = ConfigDict(extra="forbid")

    price_id: str
    state: str
    district: str
    market: str
    commodity: str
    variety: str | None
    grade: str | None
    arrival_date: date
    minimum_price: float | None = Field(default=None, ge=0)
    maximum_price: float | None = Field(default=None, ge=0)
    modal_price: float | None = Field(default=None, ge=0)
    price_unit: str | None = None
    data_source: str
    retrieved_at: datetime


class MandiPriceListResponse(BaseModel):
    count: int
    total: int
    limit: int
    offset: int
    prices: list[MandiPrice]


class MandiSyncResponse(BaseModel):
    fetched: int
    inserted_or_updated: int
    offset: int
    limit: int
    data_source: str
    retrieved_at: datetime


class NationalMandiDailySummary(BaseModel):
    summary_id: str
    report_date: date
    commodity_group: str
    commodity: str
    msp_year: str | None
    msp_rs_per_quintal: float | None = Field(default=None, ge=0)
    observation_date: date
    price_rs_per_quintal: float | None = Field(default=None, ge=0)
    arrival_metric_tonnes: float | None = Field(default=None, ge=0)
    data_source: str
    retrieved_at: datetime


class NationalMandiSummaryListResponse(BaseModel):
    count: int
    total: int
    limit: int
    offset: int
    summaries: list[NationalMandiDailySummary]
