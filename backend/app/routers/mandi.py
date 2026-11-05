import secrets
from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status

from backend.app.config import get_setting
from backend.app.schemas.mandi import (
    MandiPriceListResponse,
    MandiSyncResponse,
    NationalMandiSummaryListResponse,
)
from backend.app.services import mandi as mandi_service


router = APIRouter(prefix="/api/mandi", tags=["Mandi Prices"])


def require_mandi_admin(
    x_mandi_admin_token: str | None = Header(default=None),
) -> None:
    expected_token = get_setting("AGROLENS_MANDI_ADMIN_TOKEN")
    if not expected_token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Mandi synchronization is not configured.",
        )
    if (
        x_mandi_admin_token is None
        or not secrets.compare_digest(x_mandi_admin_token, expected_token)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A valid mandi admin token is required.",
        )


def _read_prices(
    *,
    commodity: str | None,
    state: str | None,
    district: str | None,
    market: str | None,
    variety: str | None,
    start_date: date | None,
    end_date: date | None,
    latest_only: bool,
    limit: int,
    offset: int,
):
    if start_date is not None and end_date is not None and start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="start_date must be on or before end_date.",
        )
    prices, total = mandi_service.list_prices(
        commodity=commodity,
        state=state,
        district=district,
        market=market,
        variety=variety,
        start_date=start_date,
        end_date=end_date,
        latest_only=latest_only,
        limit=limit,
        offset=offset,
    )
    return {
        "count": len(prices),
        "total": total,
        "limit": limit,
        "offset": offset,
        "prices": prices,
    }


@router.get(
    "/prices/latest",
    response_model=MandiPriceListResponse,
    summary="Get latest imported prices for each market and commodity",
)
def latest_prices(
    commodity: str | None = Query(default=None, min_length=1, max_length=150),
    state: str | None = Query(default=None, min_length=1, max_length=100),
    district: str | None = Query(default=None, min_length=1, max_length=100),
    market: str | None = Query(default=None, min_length=1, max_length=150),
    variety: str | None = Query(default=None, min_length=1, max_length=150),
    start_date: date | None = None,
    end_date: date | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return _read_prices(
        commodity=commodity,
        state=state,
        district=district,
        market=market,
        variety=variety,
        start_date=start_date,
        end_date=end_date,
        latest_only=True,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/prices/history",
    response_model=MandiPriceListResponse,
    summary="Get historical imported mandi prices",
)
def historical_prices(
    commodity: str | None = Query(default=None, min_length=1, max_length=150),
    state: str | None = Query(default=None, min_length=1, max_length=100),
    district: str | None = Query(default=None, min_length=1, max_length=100),
    market: str | None = Query(default=None, min_length=1, max_length=150),
    variety: str | None = Query(default=None, min_length=1, max_length=150),
    start_date: date | None = None,
    end_date: date | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return _read_prices(
        commodity=commodity,
        state=state,
        district=district,
        market=market,
        variety=variety,
        start_date=start_date,
        end_date=end_date,
        latest_only=False,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/national/daily",
    response_model=NationalMandiSummaryListResponse,
    summary="Get national daily commodity price and arrival summaries",
)
def national_daily_summaries(
    commodity: str | None = Query(default=None, min_length=1, max_length=150),
    start_date: date | None = None,
    end_date: date | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    if start_date is not None and end_date is not None and start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="start_date must be on or before end_date.",
        )
    summaries, total = mandi_service.list_national_summaries(
        commodity=commodity,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )
    return {
        "count": len(summaries),
        "total": total,
        "limit": limit,
        "offset": offset,
        "summaries": summaries,
    }


@router.post(
    "/sync",
    response_model=MandiSyncResponse,
    summary="Import one page from the official data.gov.in mandi dataset",
)
def sync_prices(
    _: None = Depends(require_mandi_admin),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=mandi_service.MAX_SYNC_LIMIT),
):
    try:
        imported = mandi_service.sync_prices(offset=offset, limit=limit)
    except mandi_service.MandiServiceError as error:
        raise HTTPException(
            status_code=error.status_code,
            detail=error.detail,
        ) from error
    return MandiSyncResponse(
        fetched=imported,
        inserted_or_updated=imported,
        offset=offset,
        limit=limit,
        data_source=mandi_service.DATA_SOURCE,
        retrieved_at=datetime.now(timezone.utc),
    )
