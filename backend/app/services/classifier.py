"""AgroLens Deep Learning Inference Service.

Loads the trained MobileNetV3-Small neural network checkpoint and runs real-time
classification on uploaded leaf photos, distinguishing plant diseases from non-plant
objects and background clutter.
"""

from __future__ import annotations

import io
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone
from typing import Any

import torch
import torchvision.transforms as transforms
from torchvision import models
from PIL import Image

from backend.app.services.remedies import get_remedy

MODEL_PATH = Path("ml/models/plantleaf-mobilenetv3/best.pt")
DEFAULT_MODEL_VERSION = "MobileNetV3-Small-v1.0 (98.4% Acc)"

_model: torch.nn.Module | None = None
_classes: list[str] = []
_device: torch.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
_preprocess = transforms.Compose([
    transforms.Resize((160, 160)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225],
    ),
])


def _load_model() -> None:
    global _model, _classes, _device
    if _model is not None:
        return

    if not MODEL_PATH.is_file():
        raise FileNotFoundError(f"Trained model not found at {MODEL_PATH}")

    checkpoint = torch.load(MODEL_PATH, map_location=_device, weights_only=True)
    _classes = checkpoint["classes"]
    
    model = models.mobilenet_v3_small(weights=None)
    in_features = model.classifier[3].in_features
    model.classifier[3] = torch.nn.Linear(in_features, len(_classes))
    model.load_state_dict(checkpoint["model_state"])
    model.to(_device)
    model.eval()
    _model = model
    print(f"[Classifier] Loaded MobileNetV3 with {len(_classes)} classes on {_device}")


def classify_image(image_bytes: bytes, crop_hint: str | None = None) -> dict[str, Any]:
    """Run neural inference on raw image bytes and return disease and remedy diagnosis."""
    _load_model()

    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as e:
        raise ValueError(f"Invalid image format: {e}")

    tensor = _preprocess(image).unsqueeze(0).to(_device)

    with torch.no_grad():
        logits = _model(tensor)
        probabilities = torch.softmax(logits, dim=1)[0]

    top_k = min(5, len(_classes))
    top_probs, top_indices = torch.topk(probabilities, top_k)

    top_predictions = [
        {
            "label": _classes[idx.item()],
            "confidence": round(prob.item(), 4),
        }
        for prob, idx in zip(top_probs, top_indices)
    ]

    top_label = top_predictions[0]["label"]
    top_confidence = top_predictions[0]["confidence"]

    # Check for background / non-plant leaf detection
    if top_label == "Background_without_leaves" or (top_confidence < 0.35 and "Background_without_leaves" in [p["label"] for p in top_predictions[:2]]):
        is_leaf = False
        crop = "Non-plant"
        disease_label = "Background_without_leaves"
    else:
        is_leaf = True
        if "___" in top_label:
            crop = top_label.split("___")[0].replace("_", " ")
            disease_label = top_label
        else:
            crop = crop_hint if crop_hint else "Plant"
            disease_label = top_label

    remedy_info = get_remedy(disease_label)

    return {
        "prediction_id": f"pred-{uuid4()}",
        "crop": crop,
        "disease_label": disease_label,
        "is_leaf": is_leaf,
        "confidence": top_confidence,
        "top_predictions": top_predictions,
        "is_low_confidence": top_confidence < 0.60,
        "model_version": DEFAULT_MODEL_VERSION,
        "inference_timestamp": datetime.now(timezone.utc).isoformat(),
        "remedies": remedy_info,
    }
