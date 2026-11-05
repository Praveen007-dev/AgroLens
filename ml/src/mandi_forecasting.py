"""Small-data mandi price forecasting with a chronological naive baseline."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
import csv
import math
from pathlib import Path
from statistics import mean
from typing import Any, Iterable


@dataclass(frozen=True)
class MandiPriceRecord:
    date: date
    commodity: str
    market: str
    modal_price: float
    unit: str = "INR/quintal"


FORECAST_VERSION = "naive-trend-0.1.0"
MINIMUM_HISTORY = 7


def _finite_price(value: float) -> bool:
    return math.isfinite(value) and value >= 0


def _metrics(actual: list[float], predicted: list[float]) -> dict[str, float]:
    errors = [a - p for a, p in zip(actual, predicted)]
    return {
        "mae": round(mean(abs(error) for error in errors), 4),
        "rmse": round(math.sqrt(mean(error * error for error in errors)), 4),
    }


def _clean_records(records: Iterable[MandiPriceRecord]) -> list[MandiPriceRecord]:
    cleaned = [
        record
        for record in records
        if _finite_price(record.modal_price)
        and record.commodity.strip()
        and record.market.strip()
        and record.unit.strip()
    ]
    return sorted(cleaned, key=lambda record: record.date)


def load_mandi_csv(path: str | Path) -> list[MandiPriceRecord]:
    """Load a CSV with date, commodity, market, modal_price, and optional unit."""
    records: list[MandiPriceRecord] = []
    with Path(path).open(newline="", encoding="utf-8-sig") as file:
        for row in csv.DictReader(file):
            records.append(
                MandiPriceRecord(
                    date=date.fromisoformat(row["date"]),
                    commodity=row["commodity"],
                    market=row["market"],
                    modal_price=float(row["modal_price"]),
                    unit=row.get("unit") or "INR/quintal",
                )
            )
    return records


def forecast_mandi_prices(
    records: Iterable[MandiPriceRecord],
    commodity: str,
    market: str,
    horizon: int = 5,
) -> dict[str, Any]:
    """Forecast prices using a recent linear trend after a naive baseline."""
    if horizon < 1:
        raise ValueError("horizon must be positive")
    if not commodity.strip() or not market.strip():
        raise ValueError("commodity and market must not be empty")
    input_records = list(records)
    cleaned_records = _clean_records(input_records)
    matching = [
        record
        for record in cleaned_records
        if record.commodity.casefold() == commodity.casefold()
        and record.market.casefold() == market.casefold()
    ]
    if len(matching) < MINIMUM_HISTORY:
        return {
            "status": "insufficient_data",
            "commodity": commodity,
            "market": market,
            "forecast": [],
            "history_count": len(matching),
            "required_minimum_history": MINIMUM_HISTORY,
            "data_quality": {
                "invalid_records_excluded": len(input_records) - len(cleaned_records)
            },
            "model_version": FORECAST_VERSION,
            "limitations": ["At least 7 valid historical records are required."],
        }

    values = [record.modal_price for record in matching]
    observed_dates = {record.date for record in matching}
    expected_dates = {
        matching[0].date + timedelta(days=offset)
        for offset in range((matching[-1].date - matching[0].date).days + 1)
    }
    missing_dates = sorted((expected_dates - observed_dates))
    median = sorted(values)[len(values) // 2]
    outliers = [
        record.date.isoformat()
        for record in matching
        if median and abs(record.modal_price - median) / median > 0.5
    ]
    split = max(1, len(values) - max(3, min(5, len(values) // 4)))
    validation_actual = values[split:]
    last_train = values[:split]
    naive_prediction = [last_train[-1]] * len(validation_actual)
    baseline = _metrics(validation_actual, naive_prediction)

    recent = values[-min(7, len(values)) :]
    slope = (recent[-1] - recent[0]) / max(1, len(recent) - 1)
    forecasts = []
    last_date = matching[-1].date
    last_value = values[-1]
    for offset in range(1, horizon + 1):
        forecasts.append(
            {
                "date": (last_date + timedelta(days=offset)).isoformat(),
                "predicted_price": round(max(0.0, last_value + slope * offset), 2),
                "is_forecast": True,
                "unit": matching[-1].unit,
            }
        )
    return {
        "status": "ok",
        "commodity": commodity,
        "market": market,
        "forecast": forecasts,
        "history_count": len(matching),
        "last_observed_date": last_date.isoformat(),
        "data_quality": {
            "missing_dates": [item.isoformat() for item in missing_dates],
            "outlier_dates": outliers,
            "invalid_records_excluded": len(input_records) - len(cleaned_records),
        },
        "baseline_metrics": baseline,
        "model_version": FORECAST_VERSION,
        "uncertainty": "No calibrated prediction interval is available; treat outputs as directional.",
        "limitations": [
            "Forecasts use a recent linear trend and are not a substitute for market advice.",
            "Missing dates, holidays, arrivals, and market shocks are not modelled.",
        ],
    }
