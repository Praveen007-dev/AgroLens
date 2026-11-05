"""Model implementations and loading helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

import numpy as np


class Predictor(Protocol):
    """Minimal interface required by :class:`InferenceEngine`."""

    def predict(self, batch: np.ndarray) -> np.ndarray:
        """Return one score per configured label for each batch item."""


class MockModel:
    """Deterministic placeholder until a trained model is supplied."""

    def predict(self, batch: np.ndarray) -> np.ndarray:
        """Produce stable, non-trained scores based on image channel means."""
        if batch.ndim != 4 or batch.shape[0] != 1:
            raise ValueError("mock model expects a single image batch")
        means = batch[0].mean(axis=(0, 1))
        scores = np.array(
            [0.34 + float(means[1]) * 0.2, 0.33 + float(means[0]) * 0.2,
             0.33 + float(means[2]) * 0.2],
            dtype=np.float32,
        )
        return scores / scores.sum()


class TFLiteModel:
    """Small adapter around a TensorFlow Lite interpreter."""

    def __init__(self, model_path: str | Path) -> None:
        try:
            import tensorflow as tf
        except ImportError as exc:
            raise RuntimeError(
                "TensorFlow is required to load a TFLite model; install "
                "ml/requirements-tflite.txt"
            ) from exc
        self._interpreter = tf.lite.Interpreter(model_path=str(model_path))
        self._interpreter.allocate_tensors()
        self._input = self._interpreter.get_input_details()[0]
        self._output = self._interpreter.get_output_details()[0]

    def predict(self, batch: np.ndarray) -> np.ndarray:
        """Run one preprocessed image through the TFLite interpreter."""
        self._interpreter.set_tensor(self._input["index"], batch.astype(np.float32))
        self._interpreter.invoke()
        return np.asarray(self._interpreter.get_tensor(self._output["index"])[0])
