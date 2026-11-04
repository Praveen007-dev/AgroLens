"""GPU-native MobileNetV3 training for folder-labelled AgroLens images."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import random

import torch
from torch import nn
from torch.utils.data import DataLoader, Subset
from torchvision import datasets, models, transforms


def split_indices(targets: list[int], fraction: float, seed: int):
    if not 0.0 < fraction < 1.0:
        raise ValueError("validation_fraction must be between 0 and 1")
    by_class: dict[int, list[int]] = {}
    for index, target in enumerate(targets):
        by_class.setdefault(target, []).append(index)
    rng = random.Random(seed)
    train, validation = [], []
    for indices in by_class.values():
        rng.shuffle(indices)
        count = max(1, round(len(indices) * fraction))
        count = min(count, len(indices) - 1) if len(indices) > 1 else 0
        validation.extend(indices[:count])
        train.extend(indices[count:])
    rng.shuffle(train)
    rng.shuffle(validation)
    return train, validation


def evaluate(model, loader, device, loss_function):
    model.eval()
    total_loss = correct = count = 0
    with torch.no_grad():
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            total_loss += loss_function(outputs, labels).item() * labels.size(0)
            correct += (outputs.argmax(1) == labels).sum().item()
            count += labels.size(0)
    return total_loss / count, correct / count


def remove_missing_samples(dataset):
    """Drop stale dataset entries without changing class indices."""
    valid = [(path, target) for path, target in dataset.samples if Path(path).is_file()]
    dataset.samples = valid
    dataset.imgs = valid
    dataset.targets = [target for _, target in valid]
    return len(valid)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--test-dataset", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("ml/models/plantdoc-mobilenetv3"))
    parser.add_argument("--epochs", type=int, default=12)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--validation-fraction", type=float, default=0.2)
    parser.add_argument("--image-size", type=int, default=224)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    if args.epochs < 1 or args.batch_size < 1:
        raise SystemExit("epochs and batch-size must be positive")
    random.seed(args.seed)
    torch.manual_seed(args.seed)
    if not torch.cuda.is_available():
        raise SystemExit("CUDA is unavailable; refusing to run this GPU trainer on CPU")
    device = torch.device("cuda")
    print(f"Using {torch.cuda.get_device_name(device)}")

    normalize = transforms.Normalize(
        mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)
    )
    train_transform = transforms.Compose(
        [
            transforms.Resize((args.image_size, args.image_size)),
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(10),
            transforms.ToTensor(),
            normalize,
        ]
    )
    eval_transform = transforms.Compose(
        [transforms.Resize((args.image_size, args.image_size)), transforms.ToTensor(), normalize]
    )
    base = datasets.ImageFolder(args.dataset, transform=train_transform)
    original_count = len(base.samples)
    remove_missing_samples(base)
    if not base.samples:
        raise SystemExit("dataset contains no readable image files")
    if len(base.samples) != original_count:
        print(f"Skipped {original_count - len(base.samples)} missing image files")
    train_indices, validation_indices = split_indices(
        base.targets, args.validation_fraction, args.seed
    )
    validation_base = datasets.ImageFolder(args.dataset, transform=eval_transform)
    remove_missing_samples(validation_base)
    train_loader = DataLoader(
        Subset(base, train_indices), batch_size=args.batch_size, shuffle=True,
        num_workers=2, pin_memory=True,
    )
    validation_loader = DataLoader(
        Subset(validation_base, validation_indices), batch_size=args.batch_size,
        shuffle=False, num_workers=2, pin_memory=True,
    )
    weights = models.MobileNet_V3_Small_Weights.DEFAULT
    model = models.mobilenet_v3_small(weights=weights)
    model.classifier[3] = nn.Linear(model.classifier[3].in_features, len(base.classes))
    model.to(device)
    loss_function = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    best_accuracy = -1.0
    summary = []
    for epoch in range(args.epochs):
        model.train()
        running_loss = correct = count = 0
        for images, labels in train_loader:
            images, labels = images.to(device, non_blocking=True), labels.to(device, non_blocking=True)
            optimizer.zero_grad(set_to_none=True)
            outputs = model(images)
            loss = loss_function(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * labels.size(0)
            correct += (outputs.argmax(1) == labels).sum().item()
            count += labels.size(0)
        validation_loss, validation_accuracy = evaluate(
            model, validation_loader, device, loss_function
        )
        metrics = {
            "epoch": epoch + 1,
            "train_loss": running_loss / count,
            "train_accuracy": correct / count,
            "validation_loss": validation_loss,
            "validation_accuracy": validation_accuracy,
        }
        summary.append(metrics)
        print(json.dumps(metrics))
        if validation_accuracy > best_accuracy:
            best_accuracy = validation_accuracy
            torch.save(
                {
                    "model_state": model.state_dict(),
                    "classes": base.classes,
                    "image_size": args.image_size,
                    "architecture": "MobileNetV3-Small",
                },
                args.output_dir / "best.pt",
            )
    (args.output_dir / "labels.json").write_text(
        json.dumps(base.classes, indent=2) + "\n", encoding="utf-8"
    )
    (args.output_dir / "training_summary.json").write_text(
        json.dumps(
            {
                "architecture": "MobileNetV3-Small",
                "device": torch.cuda.get_device_name(device),
                "dataset": str(args.dataset),
                "test_dataset": str(args.test_dataset) if args.test_dataset else None,
                "image_count": len(base),
                "train_count": len(train_indices),
                "validation_count": len(validation_indices),
                "metrics": summary,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
