from datetime import date, timedelta
import json

import pytest

from ml.src.crop_recommendation import CropRecommendationInput, recommend_crops
from ml.src.mandi_forecasting import (
    MandiPriceRecord,
    forecast_mandi_prices,
)


def test_crop_recommendations_are_ranked_and_disclose_limitations():
    result = recommend_crops(
        CropRecommendationInput(
            season="kharif",
            temperature_c=28,
            rainfall_mm=180,
            humidity_percent=75,
            soil_type="clay",
            irrigation_available=True,
        )
    )
    assert result["recommendations"][0]["crop"] == "rice"
    assert result["validated"] is False
    assert result["model_version"] == "rules-0.1.0"
    json.dumps(result)


def test_crop_recommendations_report_missing_inputs():
    result = recommend_crops(CropRecommendationInput())
    assert "Missing required inputs" in result["limitations"][-1]
    assert all(item["suitability_score"] <= 0.1 for item in result["recommendations"])


def test_mandi_forecast_uses_future_dates_and_metrics():
    records = [
        MandiPriceRecord(
            date=date(2026, 1, 1) + timedelta(days=index),
            commodity="Tomato",
            market="Mandi A",
            modal_price=100 + index,
        )
        for index in range(10)
    ]
    result = forecast_mandi_prices(records, "tomato", "mandi a")
    assert result["status"] == "ok"
    assert len(result["forecast"]) == 5
    assert result["forecast"][0]["date"] == "2026-01-11"
    assert result["forecast"][0]["is_forecast"] is True
    assert set(result["baseline_metrics"]) == {"mae", "rmse"}
    assert result["data_quality"]["missing_dates"] == []


def test_mandi_forecast_rejects_insufficient_history():
    records = [
        MandiPriceRecord(date(2026, 1, index + 1), "Rice", "Mandi A", 2000)
        for index in range(3)
    ]
    result = forecast_mandi_prices(records, "Rice", "Mandi A")
    assert result["status"] == "insufficient_data"
    assert result["forecast"] == []


def test_mandi_forecast_reports_invalid_records():
    records = [
        MandiPriceRecord(date(2026, 1, index + 1), "Rice", "Mandi A", 2000)
        for index in range(7)
    ]
    records.append(MandiPriceRecord(date(2026, 1, 8), "Rice", "Mandi A", -1))
    result = forecast_mandi_prices(records, "Rice", "Mandi A")
    assert result["data_quality"]["invalid_records_excluded"] == 1


def test_mandi_forecast_rejects_invalid_horizon():
    with pytest.raises(ValueError, match="horizon"):
        forecast_mandi_prices([], "Rice", "Mandi A", horizon=0)
