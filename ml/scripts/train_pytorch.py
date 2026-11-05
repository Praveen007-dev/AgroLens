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


class LowResolutionDegradation:
    """Simulate small, compressed, noisy phone images during training."""

    def __init__(self, min_size: int = 48, probability: float = 0.7):
        self.min_size = min_size
        self.probability = probability

    def __call__(self, image):
        if random.random() > self.probability:
            return image
        width, height = image.size
        size = random.randint(self.min_size, max(self.min_size, min(width, height) // 2))
        image = image.resize((size, size))
        return image.resize((width, height))


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
    parser.add_argument("--patience", type=int, default=4)
    parser.add_argument("--min-delta", type=float, default=0.001)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--validation-fraction", type=float, default=0.2)
    parser.add_argument("--image-size", type=int, default=224)
    parser.add_argument(
        "--architecture",
        choices=("mobilenet_v3_small", "mobilenet_v3_large"),
        default="mobilenet_v3_small",
    )
    parser.add_argument(
        "--low-resolution",
        action="store_true",
        help="use 160x160 input and low-resolution degradation augmentation",
    )
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    if args.epochs < 1 or args.batch_size < 1 or args.patience < 1:
        raise SystemExit("epochs, batch-size, and patience must be positive")
    if args.min_delta < 0:
        raise SystemExit("min-delta must not be negative")
    random.seed(args.seed)
    torch.manual_seed(args.seed)
    if not torch.cuda.is_available():
        raise SystemExit("CUDA is unavailable; refusing to run this GPU trainer on CPU")
    device = torch.device("cuda")
    print(f"Using {torch.cuda.get_device_name(device)}")
    if args.low_resolution:
        args.image_size = 160
        print("Low-resolution mode: 160x160 input with degradation augmentation")

    normalize = transforms.Normalize(
        mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)
    )
    train_transform = transforms.Compose(
        [
            transforms.Resize((args.image_size, args.image_size)),
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(10),
            transforms.RandomApply(
                [transforms.GaussianBlur(kernel_size=3, sigma=(0.1, 2.0))], p=0.25
            ),
            LowResolutionDegradation(),
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
        num_workers=args.num_workers, pin_memory=True,
    )
    validation_loader = DataLoader(
        Subset(validation_base, validation_indices), batch_size=args.batch_size,
        shuffle=False, num_workers=args.num_workers, pin_memory=True,
    )
    if args.architecture == "mobilenet_v3_large":
        weights = models.MobileNet_V3_Large_Weights.DEFAULT
        model = models.mobilenet_v3_large(weights=weights)
        architecture_name = "MobileNetV3-Large"
    else:
        weights = models.MobileNet_V3_Small_Weights.DEFAULT
        model = models.mobilenet_v3_small(weights=weights)
        architecture_name = "MobileNetV3-Small"
    model.classifier[3] = nn.Linear(model.classifier[3].in_features, len(base.classes))
    model.to(device)
    loss_function = nn.CrossEntropyLoss(label_smoothing=0.1)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="min", factor=0.5, patience=1, min_lr=1e-6
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    best_validation_loss = float("inf")
    best_epoch = 0
    epochs_without_improvement = 0
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
        scheduler.step(validation_loss)
        metrics = {
            "epoch": epoch + 1,
            "train_loss": running_loss / count,
            "train_accuracy": correct / count,
            "validation_loss": validation_loss,
            "validation_accuracy": validation_accuracy,
            "learning_rate": optimizer.param_groups[0]["lr"],
        }
        summary.append(metrics)
        print(json.dumps(metrics))
        if validation_loss < best_validation_loss - args.min_delta:
            best_validation_loss = validation_loss
            best_epoch = epoch + 1
            epochs_without_improvement = 0
            torch.save(
                {
                    "model_state": model.state_dict(),
                    "classes": base.classes,
                    "image_size": args.image_size,
                    "architecture": architecture_name,
                    "low_resolution": args.low_resolution,
                },
                args.output_dir / "best.pt",
            )
        else:
            epochs_without_improvement += 1
            if epochs_without_improvement >= args.patience:
                print(
                    f"Early stopping at epoch {epoch + 1}; "
                    f"best validation loss was epoch {best_epoch}."
                )
                break
    (args.output_dir / "labels.json").write_text(
        json.dumps(base.classes, indent=2) + "\n", encoding="utf-8"
    )
    (args.output_dir / "training_summary.json").write_text(
        json.dumps(
            {
                "architecture": architecture_name,
                "low_resolution": args.low_resolution,
                "device": torch.cuda.get_device_name(device),
                "dataset": str(args.dataset),
                "test_dataset": str(args.test_dataset) if args.test_dataset else None,
                "image_count": len(base),
                "train_count": len(train_indices),
                "validation_count": len(validation_indices),
                "best_epoch": best_epoch,
                "best_validation_loss": best_validation_loss,
                "early_stopping_patience": args.patience,
                "metrics": summary,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
