from fastapi import APIRouter, HTTPException, Query

from backend.app.schemas.weather import (
    CurrentWeatherResponse,
    WeatherForecastResponse,
)
from backend.app.services.weather import WeatherServiceError, get_forecast


router = APIRouter(prefix="/api/weather", tags=["Weather"])


@router.get(
    "/current",
    response_model=CurrentWeatherResponse,
    summary="Get current weather for a supplied location",
)
def current_weather(
    location: str = Query(..., min_length=1, max_length=120),
):
    try:
        result = get_forecast(location, days=1)
    except WeatherServiceError as error:
        raise HTTPException(
            status_code=error.status_code,
            detail=error.detail,
        ) from error

    return CurrentWeatherResponse(
        provider=result.provider,
        retrieved_at=result.retrieved_at,
        location=result.location,
        current=result.current,
    )


@router.get(
    "/forecast",
    response_model=WeatherForecastResponse,
    summary="Get current conditions and daily forecast",
)
def weather_forecast(
    location: str = Query(..., min_length=1, max_length=120),
    days: int = Query(default=3, ge=1, le=14),
):
    try:
        return get_forecast(location, days=days)
    except WeatherServiceError as error:
        raise HTTPException(
            status_code=error.status_code,
            detail=error.detail,
        ) from error
