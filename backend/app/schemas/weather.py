from datetime import datetime

from pydantic import BaseModel


class WeatherCondition(BaseModel):
    text: str
    icon: str | None = None
    code: int | None = None


class WeatherLocation(BaseModel):
    name: str
    region: str
    country: str
    latitude: float
    longitude: float
    localtime: str


class CurrentWeather(BaseModel):
    observed_at: str
    temperature_c: float
    feels_like_c: float
    humidity_percent: int
    wind_kph: float
    precipitation_mm: float
    is_day: bool
    condition: WeatherCondition


class DailyForecast(BaseModel):
    date: str
    min_temperature_c: float
    max_temperature_c: float
    average_temperature_c: float
    max_wind_kph: float
    total_precipitation_mm: float
    chance_of_rain_percent: int | None
    chance_of_snow_percent: int | None
    condition: WeatherCondition


class WeatherAlert(BaseModel):
    headline: str | None = None
    severity: str | None = None
    event: str | None = None
    effective: str | None = None
    expires: str | None = None
    description: str | None = None
    instruction: str | None = None


class CurrentWeatherResponse(BaseModel):
    provider: str
    retrieved_at: datetime
    location: WeatherLocation
    current: CurrentWeather


class WeatherForecastResponse(BaseModel):
    provider: str
    retrieved_at: datetime
    location: WeatherLocation
    current: CurrentWeather
    forecast: list[DailyForecast]
    alerts: list[WeatherAlert]
