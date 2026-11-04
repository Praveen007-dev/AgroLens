"""Run AgroLens predictions on one image or all images in a folder."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from uuid import uuid4

import torch
import numpy as np
from PIL import Image, UnidentifiedImageError
from torchvision import models, transforms

IMAGE_EXTENSIONS = {".bmp", ".gif", ".jpeg", ".jpg", ".png", ".webp"}
DEFAULT_MODEL = Path("ml/models/plantleaf-withoutaug-mobilenetv3/best.pt")
DEFAULT_THRESHOLD = 0.60
BACKGROUND_LABELS = {"Background_without_leaves"}


def label_details(label: str) -> tuple[str, str]:
    """Split PlantVillage-style labels into crop and disease text."""
    if label in BACKGROUND_LABELS:
        return "unknown", "no_leaf_detected"
    if "___" in label:
        crop, disease = label.split("___", 1)
        return crop.replace("_", " "), disease.replace("_", " ")
    return "unknown", label.replace("_", " ")


def load_model(checkpoint_path: Path, device: torch.device):
    """Load the checkpoint and return its model, labels, and input size."""
    if not checkpoint_path.is_file():
        raise FileNotFoundError(f"checkpoint not found: {checkpoint_path}")
    checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=True)
    labels = checkpoint.get("classes")
    if not isinstance(labels, list) or not labels:
        raise ValueError("checkpoint does not contain a valid class list")
    architecture = checkpoint.get("architecture", "MobileNetV3-Small")
    if architecture == "MobileNetV3-Large":
        model = models.mobilenet_v3_large(weights=None)
    else:
        model = models.mobilenet_v3_small(weights=None)
    model.classifier[3] = torch.nn.Linear(model.classifier[3].in_features, len(labels))
    model.load_state_dict(checkpoint["model_state"])
    model.to(device)
    model.eval()
    return model, labels, int(checkpoint.get("image_size", 224)), architecture


def image_paths(source: Path) -> list[Path]:
    """Return one image path or all supported images below a directory."""
    if source.is_file():
        return [source] if source.suffix.lower() in IMAGE_EXTENSIONS else []
    if source.is_dir():
        return sorted(
            path
            for path in source.rglob("*")
            if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
        )
    raise FileNotFoundError(f"image path does not exist: {source}")


def assess_image_quality(image: Image.Image) -> dict:
    """Reject images that are too small, blurred, dark, bright, or flat."""
    rgb = np.asarray(image.convert("RGB"), dtype=np.float32)
    gray = rgb.mean(axis=2)
    height, width = gray.shape
    issues: list[str] = []
    if min(width, height) < 96:
        issues.append("image resolution is too low")
    brightness = float(gray.mean())
    if brightness < 35:
        issues.append("image is too dark")
    elif brightness > 235:
        issues.append("image is overexposed")
    contrast = float(gray.std())
    if contrast < 12:
        issues.append("image has very low contrast")
    laplacian = (
        -4 * gray
        + np.roll(gray, 1, axis=0)
        + np.roll(gray, -1, axis=0)
        + np.roll(gray, 1, axis=1)
        + np.roll(gray, -1, axis=1)
    )
    blur_score = float(laplacian[1:-1, 1:-1].var())
    if blur_score < 8:
        issues.append("image appears blurry")
    return {
        "width": width,
        "height": height,
        "brightness": round(brightness, 2),
        "contrast": round(contrast, 2),
        "blur_score": round(blur_score, 2),
        "is_acceptable": not issues,
        "issues": issues,
    }


def predict_image(
    model,
    labels,
    transform,
    path: Path,
    device,
    top_k: int,
    threshold: float,
    architecture: str,
    image_size: int,
):
    """Predict one image and return the shared inference contract shape."""
    try:
        with Image.open(path) as image:
            image = image.convert("RGB")
            quality = assess_image_quality(image)
            batch = transform(image).unsqueeze(0).to(device)
    except (OSError, UnidentifiedImageError) as exc:
        raise ValueError(f"cannot read image: {path}") from exc

    with torch.inference_mode():
        probabilities = torch.softmax(model(batch), dim=1)[0]
    values, indices = torch.topk(probabilities, k=min(top_k, len(labels)))
    confidence = float(values[0].item())
    predicted_label = labels[int(indices[0].item())]
    crop, _ = label_details(predicted_label)
    is_background = predicted_label in BACKGROUND_LABELS
    needs_better_photo = bool(
        quality["issues"] or is_background or confidence < threshold
    )
    return {
        "prediction_id": str(uuid4()),
        "crop": crop,
        "disease_label": predicted_label,
        "confidence": confidence,
        "top_predictions": [
            {"label": labels[int(index)], "confidence": float(value)}
            for value, index in zip(values.tolist(), indices.tolist())
        ],
        "is_low_confidence": needs_better_photo,
        "image_quality": quality,
        "needs_better_photo": needs_better_photo,
        "model_version": f"{architecture}-lowres-{image_size}px",
        "inference_timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "image_path": str(path),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path, help="image file or folder of images")
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    parser.add_argument("--cpu", action="store_true", help="force CPU instead of CUDA")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args()
    if args.top_k < 1:
        raise SystemExit("--top-k must be positive")
    if not 0.0 <= args.threshold <= 1.0:
        raise SystemExit("--threshold must be between 0 and 1")
    paths = image_paths(args.image)
    if not paths:
        raise SystemExit("no supported images found (.jpg, .jpeg, .png, .bmp, .gif, .webp)")
    device = torch.device("cpu" if args.cpu or not torch.cuda.is_available() else "cuda")
    model, labels, image_size, architecture = load_model(args.model, device)
    transform = transforms.Compose(
        [
            transforms.Resize((image_size, image_size)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)
            ),
        ]
    )
    results = [
        predict_image(
            model,
            labels,
            transform,
            path,
            device,
            args.top_k,
            args.threshold,
            architecture,
            image_size,
        )
        for path in paths
    ]
    if args.json:
        print(json.dumps(results, indent=2))
        return
    print(f"Device: {torch.cuda.get_device_name(device) if device.type == 'cuda' else 'CPU'}")
    for result in results:
        print(f"\nImage: {result['image_path']}")
        if result["disease_label"] in BACKGROUND_LABELS:
            print("Result: No clear leaf detected; no disease diagnosis made")
        else:
            _, disease = label_details(result["disease_label"])
            print(f"Plant: {result['crop']}")
            print(f"Disease: {disease}")
        if result["needs_better_photo"]:
            print("Action: Please take a better photo before relying on this result")
            for issue in result["image_quality"]["issues"]:
                print(f"  - {issue}")
        print(f"Confidence: {result['confidence']:.2%}")
        print(f"Low confidence: {result['is_low_confidence']}")
        print("Top predictions:")
        for prediction in result["top_predictions"]:
            print(f"  - {prediction['label']}: {prediction['confidence']:.2%}")


if __name__ == "__main__":
    main()
