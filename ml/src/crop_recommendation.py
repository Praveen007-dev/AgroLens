"""Transparent crop suitability recommendations.

This module is a rule-based prototype, not an agronomically validated model.
Rules are intentionally exposed through the response limitations and version.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class CropRecommendationInput:
    """Weather, soil, and farm information used by the rule engine."""

    season: str | None = None
    temperature_c: float | None = None
    rainfall_mm: float | None = None
    humidity_percent: float | None = None
    soil_type: str | None = None
    irrigation_available: bool | None = None
    location: str | None = None
    crop_duration_days: int | None = None


@dataclass(frozen=True)
class _CropRule:
    name: str
    seasons: frozenset[str]
    temperature: tuple[float, float]
    rainfall: tuple[float, float]
    humidity: tuple[float, float]
    soils: frozenset[str]
    duration: tuple[int, int]
    irrigation_required: bool


RULE_VERSION = "rules-0.1.0"
REQUIRED_PARAMETERS = ["season", "temperature_c", "rainfall_mm"]
_RULES = (
    _CropRule(
        "rice",
        frozenset({"kharif", "monsoon"}),
        (20.0, 35.0),
        (100.0, 300.0),
        (60.0, 95.0),
        frozenset({"clay", "clay_loam", "loam"}),
        (90, 180),
        True,
    ),
    _CropRule(
        "wheat",
        frozenset({"rabi", "winter"}),
        (10.0, 25.0),
        (30.0, 100.0),
        (40.0, 75.0),
        frozenset({"loam", "clay_loam"}),
        (100, 150),
        False,
    ),
    _CropRule(
        "tomato",
        frozenset({"rabi", "summer", "winter"}),
        (18.0, 30.0),
        (40.0, 150.0),
        (50.0, 80.0),
        frozenset({"loam", "sandy_loam"}),
        (60, 120),
        False,
    ),
)


def _normalise(value: str | None) -> str | None:
    return value.strip().lower().replace("-", "_") if value else None


def _in_range(value: float | None, bounds: tuple[float, float]) -> bool | None:
    return None if value is None else bounds[0] <= value <= bounds[1]


def recommend_crops(
    inputs: CropRecommendationInput, top_k: int = 3
) -> dict[str, Any]:
    """Return ranked suitability scores with reasons and explicit limitations."""
    if top_k < 1:
        raise ValueError("top_k must be positive")
    season = _normalise(inputs.season)
    soil = _normalise(inputs.soil_type)
    missing = [
        name
        for name in REQUIRED_PARAMETERS
        if getattr(inputs, name) is None
    ]
    results: list[dict[str, Any]] = []
    for rule in _RULES:
        score = 0.0
        reasons: list[str] = []
        limitations: list[str] = []

        if season is None:
            limitations.append("season was not provided")
        elif season in rule.seasons:
            score += 25
            reasons.append("season matches the rule")
        else:
            limitations.append("season is outside the rule's preferred seasons")

        for label, value, bounds in (
            ("temperature", inputs.temperature_c, rule.temperature),
            ("rainfall", inputs.rainfall_mm, rule.rainfall),
            ("humidity", inputs.humidity_percent, rule.humidity),
        ):
            match = _in_range(value, bounds)
            if match is None:
                limitations.append(f"{label} was not provided")
            elif match:
                score += 20
                reasons.append(f"{label} is within the rule range")
            else:
                limitations.append(f"{label} is outside the rule range")

        if soil is None:
            limitations.append("soil type was not provided")
        elif soil in rule.soils:
            score += 10
            reasons.append("soil type matches the rule")
        else:
            limitations.append("soil type is not in the preferred rule set")

        if inputs.irrigation_available is None:
            limitations.append("irrigation availability was not provided")
        elif inputs.irrigation_available or not rule.irrigation_required:
            score += 5
            reasons.append("irrigation condition is compatible")
        else:
            limitations.append("irrigation is required by this rule")

        if inputs.crop_duration_days is not None:
            if rule.duration[0] <= inputs.crop_duration_days <= rule.duration[1]:
                score += 5
                reasons.append("crop duration is within the rule range")
            else:
                limitations.append("requested crop duration is outside the rule range")

        results.append(
            {
                "crop": rule.name,
                "suitability_score": round(score / 100, 3),
                "suitability_category": (
                    "suitable" if score >= 70 else "conditionally_suitable" if score >= 40 else "insufficient_data_or_fit"
                ),
                "reasons": reasons,
                "limitations": limitations,
            }
        )

    results.sort(key=lambda result: (-result["suitability_score"], result["crop"]))
    return {
        "recommendations": results[:top_k],
        "required_input_parameters": REQUIRED_PARAMETERS,
        "model_version": RULE_VERSION,
        "validated": False,
        "location": inputs.location,
        "limitations": [
            "Prototype rules are not expert-reviewed or agronomically validated.",
            "Recommendations must be checked with local agricultural guidance.",
            *([f"Missing required inputs: {', '.join(missing)}"] if missing else []),
        ],
    }
