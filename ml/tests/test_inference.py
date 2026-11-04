from io import BytesIO
import json
from datetime import datetime

import numpy as np
from PIL import Image
import pytest

from ml.src.inference import InferenceEngine
from ml.src.preprocessing import ImageInputError, preprocess_image
from ml.scripts.train import stratified_split


def image_bytes(color=(20, 120, 40)) -> bytes:
    buffer = BytesIO()
    Image.new("RGB", (32, 16), color).save(buffer, format="PNG")
    return buffer.getvalue()


def test_preprocessing_returns_rgb_normalized_batch():
    batch = preprocess_image(image_bytes())
    assert batch.shape == (1, 224, 224, 3)
    assert batch.dtype == np.float32
    assert 0.0 <= float(batch.min()) <= float(batch.max()) <= 1.0


def test_invalid_image_is_rejected():
    with pytest.raises(ImageInputError):
        preprocess_image(b"not an image")


def test_mock_inference_matches_contract_shape():
    result = InferenceEngine().infer(image_bytes(), crop=" tomato ")
    assert result["crop"] == "tomato"
    assert isinstance(result["prediction_id"], str)
    assert 0.0 <= result["confidence"] <= 1.0
    assert len(result["top_predictions"]) == 3
    assert result["top_predictions"][0]["label"] == result["disease_label"]
    assert all(0.0 <= item["confidence"] <= 1.0 for item in result["top_predictions"])
    datetime.fromisoformat(result["inference_timestamp"].replace("Z", "+00:00"))
    assert result["model_version"] == "mock-0.1.0"


def test_low_confidence_flag_uses_configured_threshold():
    result = InferenceEngine(low_confidence_threshold=1.0).infer(image_bytes())
    assert result["is_low_confidence"] is True


def test_model_output_must_match_labels():
    class WrongShapeModel:
        def predict(self, batch):
            return np.array([1.0, 0.0])

    with pytest.raises(ValueError, match="one finite score"):
        InferenceEngine(model=WrongShapeModel()).infer(image_bytes())


def test_result_is_json_serializable():
    json.dumps(InferenceEngine().infer(image_bytes()))


def test_training_split_keeps_each_class_in_both_sets():
    records = [(f"image-{index}.jpg", label) for label in ("a", "b") for index in range(5)]
    train, validation = stratified_split(records, validation_fraction=0.2, seed=42)
    assert {label for _, label in train} == {"a", "b"}
    assert {label for _, label in validation} == {"a", "b"}
