import hashlib
import logging
import re
import threading
import time
from datetime import datetime, timezone
from typing import Any

import httpx

from backend.app.config import get_setting
from backend.app.schemas.weather import (
    CurrentWeather,
    DailyForecast,
    WeatherCondition,
    WeatherAlert,
    WeatherForecastResponse,
    WeatherLocation,
)


WEATHERAPI_FORECAST_URL = "https://api.weatherapi.com/v1/forecast.json"
OPEN_METEO_GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
OPEN_METEO_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
CACHE_TTL_SECONDS = 600
CACHE_MAX_ENTRIES = 256
REQUEST_TIMEOUT_SECONDS = 8.0
PROVIDER_NAME = "WeatherAPI.com"
OPEN_METEO_PROVIDER_NAME = "Open-Meteo"
_logger = logging.getLogger(__name__)

_cache: dict[tuple[str, int, str], tuple[float, WeatherForecastResponse]] = {}
_cache_lock = threading.Lock()


class WeatherServiceError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


def clear_cache() -> None:
    with _cache_lock:
        _cache.clear()


def _condition(data: dict[str, Any]) -> WeatherCondition:
    condition = data["condition"]
    return WeatherCondition(
        text=condition["text"],
        icon=condition.get("icon"),
        code=condition.get("code"),
    )


def _normalize_response(data: dict[str, Any]) -> WeatherForecastResponse:
    location = data["location"]
    current = data["current"]
    forecast_days = data["forecast"]["forecastday"]

    return WeatherForecastResponse(
        provider=PROVIDER_NAME,
        retrieved_at=datetime.now(timezone.utc),
        location=WeatherLocation(
            name=location["name"],
            region=location["region"],
            country=location["country"],
            latitude=location["lat"],
            longitude=location["lon"],
            localtime=location["localtime"],
        ),
        current=CurrentWeather(
            observed_at=current["last_updated"],
            temperature_c=current["temp_c"],
            feels_like_c=current["feelslike_c"],
            humidity_percent=current["humidity"],
            wind_kph=current["wind_kph"],
            precipitation_mm=current["precip_mm"],
            is_day=bool(current["is_day"]),
            condition=_condition(current),
        ),
        forecast=[
            DailyForecast(
                date=day["date"],
                min_temperature_c=day["day"]["mintemp_c"],
                max_temperature_c=day["day"]["maxtemp_c"],
                average_temperature_c=day["day"]["avgtemp_c"],
                max_wind_kph=day["day"]["maxwind_kph"],
                total_precipitation_mm=day["day"]["totalprecip_mm"],
                chance_of_rain_percent=day["day"]["daily_chance_of_rain"],
                chance_of_snow_percent=day["day"]["daily_chance_of_snow"],
                condition=_condition(day["day"]),
            )
            for day in forecast_days
        ],
        alerts=[
            WeatherAlert(
                headline=alert.get("headline"),
                severity=alert.get("severity"),
                event=alert.get("event"),
                effective=alert.get("effective"),
                expires=alert.get("expires"),
                description=alert.get("desc"),
                instruction=alert.get("instruction"),
            )
            for alert in data.get("alerts", {}).get("alert", [])
        ],
    )


def _fetch_from_provider(
    location: str,
    days: int,
    api_key: str,
) -> WeatherForecastResponse:
    try:
        response = httpx.get(
            WEATHERAPI_FORECAST_URL,
            params={
                "key": api_key,
                "q": location,
                "days": days,
                "aqi": "no",
                "alerts": "yes",
            },
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except httpx.TimeoutException as error:
        raise WeatherServiceError(
            504,
            "The weather provider did not respond before the timeout.",
        ) from error
    except httpx.RequestError as error:
        raise WeatherServiceError(
            502,
            "Unable to connect to the weather provider.",
        ) from error

    if response.is_error:
        try:
            provider_payload = response.json()
        except ValueError:
            provider_payload = {}
        provider_error = (
            provider_payload.get("error", {})
            if isinstance(provider_payload, dict)
            else {}
        )
        if not isinstance(provider_error, dict):
            provider_error = {}

        if provider_error.get("code") == 1006:
            raise WeatherServiceError(404, "Weather location was not found.")
        if response.status_code in (401, 403):
            raise WeatherServiceError(
                503,
                "Weather provider credentials were rejected.",
            )
        raise WeatherServiceError(
            502,
            "The weather provider returned an error.",
        )

    try:
        return _normalize_response(response.json())
    except (KeyError, TypeError, ValueError) as error:
        raise WeatherServiceError(
            502,
            "The weather provider returned an invalid response.",
        ) from error


def _open_meteo_condition(code: int) -> WeatherCondition:
    descriptions = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        56: "Light freezing drizzle",
        57: "Dense freezing drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        66: "Light freezing rain",
        67: "Heavy freezing rain",
        71: "Slight snow fall",
        73: "Moderate snow fall",
        75: "Heavy snow fall",
        77: "Snow grains",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        85: "Slight snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail",
    }
    return WeatherCondition(
        text=descriptions.get(code, "Unknown weather conditions"),
        code=code,
    )


def _open_meteo_get(url: str, params: dict[str, Any]):
    try:
        response = httpx.get(
            url,
            params=params,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except httpx.TimeoutException as error:
        raise WeatherServiceError(
            504,
            "The public weather provider did not respond before the timeout.",
        ) from error
    except httpx.RequestError as error:
        raise WeatherServiceError(
            502,
            "Unable to connect to the public weather provider.",
        ) from error

    if response.is_error:
        raise WeatherServiceError(
            502,
            "The public weather provider returned an error.",
        )
    try:
        payload = response.json()
    except ValueError as error:
        raise WeatherServiceError(
            502,
            "The public weather provider returned invalid JSON.",
        ) from error
    if not isinstance(payload, dict):
        raise WeatherServiceError(
            502,
            "The public weather provider returned an invalid response.",
        )
    return payload


def _fetch_from_open_meteo(
    location: str,
    days: int,
) -> WeatherForecastResponse:
    coordinate_match = re.fullmatch(
        r"\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*",
        location,
    )
    if coordinate_match:
        latitude, longitude = map(float, coordinate_match.groups())
        if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
            raise WeatherServiceError(
                422,
                "Weather coordinates must be valid latitude and longitude.",
            )
        location_name = f"{latitude:g}, {longitude:g}"
        region = ""
        country = ""
    else:
        geocoding = _open_meteo_get(
            OPEN_METEO_GEOCODING_URL,
            {
                "name": location,
                "count": 1,
                "language": "en",
                "format": "json",
            },
        )
        results = geocoding.get("results")
        if not isinstance(results, list) or not results:
            raise WeatherServiceError(404, "Weather location was not found.")
        place = results[0]
        if not isinstance(place, dict):
            raise WeatherServiceError(
                502,
                "The public weather provider returned an invalid location.",
            )
        try:
            latitude = float(place["latitude"])
            longitude = float(place["longitude"])
            location_name = str(place["name"])
        except (KeyError, TypeError, ValueError) as error:
            raise WeatherServiceError(
                502,
                "The public weather provider returned an invalid location.",
            ) from error
        region = str(place.get("admin1") or "")
        country = str(place.get("country") or "")

    data = _open_meteo_get(
        OPEN_METEO_FORECAST_URL,
        {
            "latitude": latitude,
            "longitude": longitude,
            "current": (
                "temperature_2m,relative_humidity_2m,apparent_temperature,"
                "is_day,precipitation,weather_code,wind_speed_10m"
            ),
            "daily": (
                "weather_code,temperature_2m_max,temperature_2m_min,"
                "temperature_2m_mean,precipitation_probability_max,"
                "precipitation_sum,wind_speed_10m_max"
            ),
            "forecast_days": days,
            "timezone": "auto",
            "wind_speed_unit": "kmh",
            "precipitation_unit": "mm",
        },
    )
    try:
        current = data["current"]
        daily = data["daily"]
        daily_dates = daily["time"]
        if not isinstance(daily_dates, list) or len(daily_dates) != days:
            raise ValueError("Unexpected number of forecast days.")
        response = WeatherForecastResponse(
            provider=OPEN_METEO_PROVIDER_NAME,
            retrieved_at=datetime.now(timezone.utc),
            location=WeatherLocation(
                name=location_name,
                region=region,
                country=country,
                latitude=latitude,
                longitude=longitude,
                localtime=str(current["time"]),
            ),
            current=CurrentWeather(
                observed_at=str(current["time"]),
                temperature_c=current["temperature_2m"],
                feels_like_c=current["apparent_temperature"],
                humidity_percent=current["relative_humidity_2m"],
                wind_kph=current["wind_speed_10m"],
                precipitation_mm=current["precipitation"],
                is_day=bool(current["is_day"]),
                condition=_open_meteo_condition(current["weather_code"]),
            ),
            forecast=[
                DailyForecast(
                    date=daily_dates[index],
                    min_temperature_c=daily["temperature_2m_min"][index],
                    max_temperature_c=daily["temperature_2m_max"][index],
                    average_temperature_c=daily["temperature_2m_mean"][index],
                    max_wind_kph=daily["wind_speed_10m_max"][index],
                    total_precipitation_mm=daily["precipitation_sum"][index],
                    chance_of_rain_percent=(
                        daily["precipitation_probability_max"][index]
                    ),
                    chance_of_snow_percent=None,
                    condition=_open_meteo_condition(daily["weather_code"][index]),
                )
                for index in range(days)
            ],
            alerts=[],
        )
    except (IndexError, KeyError, TypeError, ValueError) as error:
        raise WeatherServiceError(
            502,
            "The public weather provider returned an invalid response.",
        ) from error
    return response


def get_forecast(location: str, days: int) -> WeatherForecastResponse:
    api_key = get_setting("AGROLENS_WEATHERAPI_KEY")

    key_fingerprint = (
        hashlib.sha256(api_key.encode()).hexdigest()
        if api_key
        else OPEN_METEO_PROVIDER_NAME
    )
    cache_key = (location.casefold(), days, key_fingerprint)
    now = time.monotonic()
    with _cache_lock:
        cached = _cache.get(cache_key)
        if cached is not None and cached[0] > now:
            return cached[1]
        _cache.pop(cache_key, None)

    if not api_key:
        result = _fetch_from_open_meteo(location, days)
    else:
        try:
            result = _fetch_from_provider(location, days, api_key)
        except WeatherServiceError as error:
            if error.status_code == 404:
                raise
            _logger.warning(
                "%s failed (%s); trying %s.",
                PROVIDER_NAME,
                error.detail,
                OPEN_METEO_PROVIDER_NAME,
            )
            result = _fetch_from_open_meteo(location, days)

    with _cache_lock:
        if len(_cache) >= CACHE_MAX_ENTRIES:
            oldest_key = min(_cache, key=lambda key: _cache[key][0])
            del _cache[oldest_key]
        _cache[cache_key] = (time.monotonic() + CACHE_TTL_SECONDS, result)

    return result
