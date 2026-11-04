"""Run AgroLens predictions on one image or all images in a folder."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from uuid import uuid4

import torch
from PIL import Image, UnidentifiedImageError
from torchvision import models, transforms

IMAGE_EXTENSIONS = {".bmp", ".gif", ".jpeg", ".jpg", ".png", ".webp"}
DEFAULT_MODEL = Path("ml/models/plantleaf-withoutaug-mobilenetv3/best.pt")
DEFAULT_THRESHOLD = 0.60


def load_model(checkpoint_path: Path, device: torch.device):
    """Load the checkpoint and return its model, labels, and input size."""
    if not checkpoint_path.is_file():
        raise FileNotFoundError(f"checkpoint not found: {checkpoint_path}")
    checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=True)
    labels = checkpoint.get("classes")
    if not isinstance(labels, list) or not labels:
        raise ValueError("checkpoint does not contain a valid class list")
    model = models.mobilenet_v3_small(weights=None)
    model.classifier[3] = torch.nn.Linear(model.classifier[3].in_features, len(labels))
    model.load_state_dict(checkpoint["model_state"])
    model.to(device)
    model.eval()
    return model, labels, int(checkpoint.get("image_size", 224)), checkpoint.get(
        "architecture", "unknown"
    )


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
            batch = transform(image).unsqueeze(0).to(device)
    except (OSError, UnidentifiedImageError) as exc:
        raise ValueError(f"cannot read image: {path}") from exc

    with torch.inference_mode():
        probabilities = torch.softmax(model(batch), dim=1)[0]
    values, indices = torch.topk(probabilities, k=min(top_k, len(labels)))
    confidence = float(values[0].item())
    return {
        "prediction_id": str(uuid4()),
        "crop": "unknown",
        "disease_label": labels[int(indices[0].item())],
        "confidence": confidence,
        "top_predictions": [
            {"label": labels[int(index)], "confidence": float(value)}
            for value, index in zip(values.tolist(), indices.tolist())
        ],
        "is_low_confidence": confidence < threshold,
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
        print(f"Prediction: {result['disease_label']}")
        print(f"Confidence: {result['confidence']:.2%}")
        print(f"Low confidence: {result['is_low_confidence']}")
        print("Top predictions:")
        for prediction in result["top_predictions"]:
            print(f"  - {prediction['label']}: {prediction['confidence']:.2%}")


if __name__ == "__main__":
    main()
