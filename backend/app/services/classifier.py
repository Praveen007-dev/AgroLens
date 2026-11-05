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


_last_model_mtime: float = 0.0


def _load_model() -> None:
    global _model, _classes, _device, _last_model_mtime
    if not MODEL_PATH.is_file():
        raise FileNotFoundError(f"Trained model not found at {MODEL_PATH}")

    current_mtime = MODEL_PATH.stat().st_mtime
    if _model is not None and current_mtime == _last_model_mtime:
        return

    checkpoint = torch.load(MODEL_PATH, map_location=_device, weights_only=True)
    _classes = checkpoint["classes"]
    
    model = models.mobilenet_v3_small(weights=None)
    in_features = model.classifier[3].in_features
    model.classifier[3] = torch.nn.Linear(in_features, len(_classes))
    model.load_state_dict(checkpoint["model_state"])
    model.to(_device)
    model.eval()
    _model = model
    _last_model_mtime = current_mtime
    print(f"[Classifier] Loaded MobileNetV3 ({len(_classes)} classes, mtime: {_last_model_mtime}) on {_device}")


def _normalize_crop(name: str | None) -> str | None:
    if not name:
        return None
    cleaned = name.strip().lower()
    if "tomato" in cleaned:
        return "Tomato"
    if "potato" in cleaned:
        return "Potato"
    if "corn" in cleaned or "maize" in cleaned:
        return "Corn"
    if "pepper" in cleaned:
        return "Pepper,_bell"
    if "apple" in cleaned:
        return "Apple"
    if "grape" in cleaned:
        return "Grape"
    if "cherry" in cleaned:
        return "Cherry"
    if "peach" in cleaned:
        return "Peach"
    if "strawberry" in cleaned:
        return "Strawberry"
    if "blueberry" in cleaned:
        return "Blueberry"
    if "raspberry" in cleaned:
        return "Raspberry"
    if "soybean" in cleaned:
        return "Soybean"
    if "squash" in cleaned:
        return "Squash"
    if "orange" in cleaned or "citrus" in cleaned:
        return "Orange"
    return None


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

    unconstrained_label = top_predictions[0]["label"]
    unconstrained_confidence = top_predictions[0]["confidence"]

    # 1. Non-plant / background detection
    bg_prob = 0.0
    if "Background_without_leaves" in _classes:
        bg_idx = _classes.index("Background_without_leaves")
        bg_prob = probabilities[bg_idx].item()

    if unconstrained_label == "Background_without_leaves" or bg_prob >= 0.40:
        is_leaf = False
        crop = "Non-plant"
        disease_label = "Background_without_leaves"
        top_label = disease_label
        top_confidence = round(max(unconstrained_confidence, bg_prob), 4)
    else:
        is_leaf = True
        matched_crop_prefix = _normalize_crop(crop_hint)
        crop_indices = [
            i for i, c in enumerate(_classes)
            if matched_crop_prefix and c.startswith(matched_crop_prefix + "___")
        ]

        if crop_indices:
            # Condition inference on the user's selected crop prior
            sub_probs = probabilities[crop_indices]
            sub_total = sub_probs.sum().item()
            best_sub_idx_in_crop = sub_probs.argmax().item()
            best_global_idx = crop_indices[best_sub_idx_in_crop]
            
            top_label = _classes[best_global_idx]
            raw_conf = probabilities[best_global_idx].item()
            conditioned_conf = (sub_probs[best_sub_idx_in_crop].item() / max(sub_total, 1e-6))
            # Reflect high conditioned certainty for the selected crop
            top_confidence = round(max(raw_conf, conditioned_conf), 4)
            crop = top_label.split("___")[0].replace("_", " ")
            disease_label = top_label
        else:
            top_label = unconstrained_label
            top_confidence = unconstrained_confidence
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
