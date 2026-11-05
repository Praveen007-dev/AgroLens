from datetime import date, timedelta
from typing import Annotated

from fastapi import APIRouter, Body, HTTPException, Query

from backend.app.routers.auth import router as auth_router
from backend.app.schemas.mobile import (
    MobileScanCreate,
    ScanBatchResponse,
    ScanFeedbackInput,
)
from backend.app.services import mandi, mobile_scans, news, schemes, weather
from backend.app.services.mobile_scans import DuplicateScanError, MobileScanStorageError


router = APIRouter(prefix="/api/v1", tags=["Mobile API"])
router.include_router(auth_router)


@router.get("/health", tags=["System"])
def mobile_health():
    return {"status": "healthy", "service": "AgroLens Backend"}


def _save_mobile_scans(scans: list[MobileScanCreate]) -> int:
    try:
        return mobile_scans.save_scans(scans)
    except DuplicateScanError as error:
        raise HTTPException(
            status_code=409,
            detail="A scan with this scan_id already exists with different data.",
        ) from error
    except MobileScanStorageError as error:
        raise HTTPException(
            status_code=500,
            detail="Failed to store scan record.",
        ) from error


@router.post("/scans", status_code=201)
def create_scan(scan: MobileScanCreate):
    _save_mobile_scans([scan])
    return {
        "scan_id": scan.scan_id,
        "submission_status": "success",
        "message": "Scan record submitted successfully.",
    }


@router.post("/scans/batch", response_model=ScanBatchResponse)
def create_scan_batch(
    scans: Annotated[list[MobileScanCreate], Body(min_length=1, max_length=100)],
):
    return ScanBatchResponse(synced_count=_save_mobile_scans(scans))


@router.get("/scans")
def list_mobile_scans(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    items, total = mobile_scans.list_scans(limit, offset)
    return {"items": items, "limit": limit, "offset": offset, "total": total}


@router.get("/scans/{scan_id}")
def get_mobile_scan(scan_id: str):
    record = mobile_scans.get_scan(scan_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Scan record not found.")
    return record


@router.post("/scans/{scan_id}/feedback", status_code=204)
def submit_scan_feedback(scan_id: str, feedback: ScanFeedbackInput):
    try:
        exists = mobile_scans.save_feedback(scan_id, feedback)
    except MobileScanStorageError as error:
        raise HTTPException(
            status_code=500,
            detail="Failed to save scan feedback.",
        ) from error
    if not exists:
        raise HTTPException(status_code=404, detail="Scan record not found.")
    return None


@router.get("/weather")
def mobile_weather(
    location: str = Query(min_length=1, max_length=120),
    days: int = Query(default=3, ge=1, le=14),
):
    try:
        result = weather.get_forecast(location, days)
    except weather.WeatherServiceError as error:
        raise HTTPException(
            status_code=error.status_code,
            detail=error.detail,
        ) from error

    next_day = result.forecast[0] if result.forecast else None
    advisory = None
    if result.alerts:
        alert = result.alerts[0]
        advisory = alert.instruction or alert.description or alert.event or alert.headline
    return {
        "provider": result.provider,
        "retrieved_at": result.retrieved_at,
        "location": result.location,
        "temperature_c": result.current.temperature_c,
        "rainfall_mm": result.current.precipitation_mm,
        "rain_probability_pct": (
            next_day.chance_of_rain_percent if next_day else None
        ),
        "humidity_pct": result.current.humidity_percent,
        "wind_speed_kph": result.current.wind_kph,
        "wind_direction": None,
        "advisory": advisory,
        "forecast": [
            {
                "date": item.date,
                "min_temperature_c": item.min_temperature_c,
                "max_temperature_c": item.max_temperature_c,
                "rainfall_mm": item.total_precipitation_mm,
                "rain_probability_pct": item.chance_of_rain_percent,
                "humidity_pct": None,
                "wind_speed_kph": item.max_wind_kph,
                "wind_direction": None,
            }
            for item in result.forecast
        ],
        "alerts": result.alerts,
    }


@router.get("/schemes")
def list_mobile_schemes(
    state: str | None = Query(default=None, min_length=1, max_length=100),
    category: str | None = Query(default=None, min_length=1, max_length=100),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    records, total = schemes.list_schemes(
        government_level=None,
        state=state,
        category=category,
        limit=limit,
        offset=offset,
    )
    return {
        "items": [
            {
                "scheme_id": item.scheme_id,
                "name": item.scheme_name,
                "scope": item.government_level,
                "state": item.state,
                "category": item.category,
                "description": item.description,
                "eligibility": item.eligibility,
                "benefits": item.benefits,
                "required_documents": item.required_documents,
                "application_deadline": item.application_deadline,
                "official_url": item.official_url,
            }
            for item in records
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/news")
def list_mobile_news(
    category: str | None = Query(default=None, min_length=1, max_length=100),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    records, total = news.list_news(category, None, limit, offset)
    return {
        "items": [
            {
                "news_id": item.news_id,
                "title": item.title,
                "summary": item.summary,
                "source": item.source,
                "published_at": item.published_at,
                "category": item.category,
                "original_url": item.original_url,
            }
            for item in records
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/market/prices")
def list_market_prices(
    commodity: str = Query(min_length=1, max_length=150),
    state: str | None = Query(default=None, min_length=1, max_length=100),
    district: str | None = Query(default=None, min_length=1, max_length=100),
    market: str | None = Query(default=None, min_length=1, max_length=150),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    records, total = mandi.list_prices(
        commodity=commodity,
        state=state,
        district=district,
        market=market,
        variety=None,
        start_date=None,
        end_date=None,
        latest_only=True,
        limit=limit,
        offset=offset,
    )
    return {
        "items": [
            {
                "commodity": item.commodity,
                "state": item.state,
                "district": item.district,
                "market": item.market,
                "min_price": item.minimum_price,
                "modal_price": item.modal_price,
                "max_price": item.maximum_price,
                "currency": "INR",
                "unit": item.price_unit,
                "price_date": item.arrival_date,
                "data_source": item.data_source,
            }
            for item in records
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/market/history")
def market_price_history(
    commodity: str = Query(min_length=1, max_length=150),
    market: str | None = Query(default=None, min_length=1, max_length=150),
    days: int = Query(default=30, ge=1, le=3650),
    limit: int = Query(default=100, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    records, total = mandi.list_prices(
        commodity=commodity,
        state=None,
        district=None,
        market=market,
        variety=None,
        start_date=date.today() - timedelta(days=days - 1),
        end_date=date.today(),
        latest_only=False,
        limit=limit,
        offset=offset,
    )
    return {
        "items": [
            {
                "date": item.arrival_date,
                "modal_price": item.modal_price,
                "currency": "INR",
                "unit": item.price_unit,
                "commodity": item.commodity,
                "market": item.market,
            }
            for item in records
        ],
        "total": total,
        "days": days,
        "limit": limit,
        "offset": offset,
    }


@router.get("/market/forecast")
def market_price_forecast(
    commodity: str = Query(min_length=1, max_length=150),
    market: str | None = Query(default=None, min_length=1, max_length=150),
    days: int = Query(default=5, ge=1, le=30),
):
    return {
        "commodity": commodity,
        "market": market,
        "days": days,
        "forecast_available": False,
        "items": [],
        "message": "No validated mandi price forecasting model is configured.",
        "guarantee": "No price estimate is available.",
    }
