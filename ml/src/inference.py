"""Contract-compatible crop disease and pest inference."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Sequence
from uuid import uuid4

import numpy as np

from .model_loader import MockModel, Predictor
from .preprocessing import DEFAULT_INPUT_SIZE, ImageSource, preprocess_image

DEFAULT_LABELS_PATH = Path(__file__).parents[1] / "labels" / "labels.json"
DEFAULT_MODEL_VERSION = "mock-0.1.0"
DEFAULT_LOW_CONFIDENCE_THRESHOLD = 0.60


def load_labels(path: str | Path = DEFAULT_LABELS_PATH) -> list[str]:
    """Load and validate a JSON label list."""
    with Path(path).open(encoding="utf-8") as file:
        labels = json.load(file)
    if not isinstance(labels, list) or not labels or any(
        not isinstance(label, str) or not label.strip() for label in labels
    ):
        raise ValueError("labels file must contain a non-empty list of strings")
    if len(set(labels)) != len(labels):
        raise ValueError("labels must be unique")
    return labels


class InferenceEngine:
    """Run image inference and return the shared AgroLens output shape."""

    def __init__(
        self,
        model: Predictor | None = None,
        labels: Sequence[str] | None = None,
        model_version: str = DEFAULT_MODEL_VERSION,
        input_size: tuple[int, int] = DEFAULT_INPUT_SIZE,
        low_confidence_threshold: float = DEFAULT_LOW_CONFIDENCE_THRESHOLD,
        top_k: int = 3,
    ) -> None:
        if not model_version.strip():
            raise ValueError("model_version must not be empty")
        if not 0.0 <= low_confidence_threshold <= 1.0:
            raise ValueError("low_confidence_threshold must be between 0 and 1")
        if top_k < 1:
            raise ValueError("top_k must be positive")
        self.model = model or MockModel()
        self.labels = list(labels) if labels is not None else load_labels()
        if not self.labels or len(set(self.labels)) != len(self.labels):
            raise ValueError("labels must be a non-empty unique sequence")
        self.model_version = model_version
        self.input_size = input_size
        self.low_confidence_threshold = low_confidence_threshold
        self.top_k = min(top_k, len(self.labels))

    def infer(self, source: ImageSource, crop: str = "unknown") -> dict[str, Any]:
        """Infer one image and return fields required by the inference contract."""
        if not isinstance(crop, str) or not crop.strip():
            raise ValueError("crop must be a non-empty string")
        scores = np.asarray(self.model.predict(preprocess_image(source, self.input_size))).reshape(-1)
        if scores.size != len(self.labels) or not np.all(np.isfinite(scores)):
            raise ValueError("model output must contain one finite score per label")
        if np.any(scores < 0):
            raise ValueError("model output scores must not be negative")
        total = float(scores.sum())
        if total <= 0:
            raise ValueError("model output scores must have a positive sum")
        probabilities = scores / total
        ranked = np.argsort(-probabilities, kind="stable")[: self.top_k]
        confidence = float(probabilities[ranked[0]])
        return {
            "prediction_id": str(uuid4()),
            "crop": crop.strip(),
            "disease_label": self.labels[int(ranked[0])],
            "confidence": confidence,
            "top_predictions": [
                {"label": self.labels[int(index)], "confidence": float(probabilities[index])}
                for index in ranked
            ],
            "is_low_confidence": confidence < self.low_confidence_threshold,
            "model_version": self.model_version,
            "inference_timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }
