"""Train a mobile-first AgroLens classifier from folder-labelled images."""

from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import random
from typing import Iterable

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"}


def collect_images(dataset_roots: Iterable[Path]) -> list[tuple[Path, str]]:
    """Find images recursively and use each image's parent folder as its label."""
    records: list[tuple[Path, str]] = []
    for root in dataset_roots:
        if not root.is_dir():
            raise FileNotFoundError(f"dataset directory does not exist: {root}")
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS:
                label = path.parent.name.strip()
                if label:
                    records.append((path, label))
    if not records:
        raise ValueError("no supported images were found in the dataset roots")
    return records


def stratified_split(
    records: list[tuple[Path, str]], validation_fraction: float, seed: int
) -> tuple[list[tuple[Path, str]], list[tuple[Path, str]]]:
    """Split each class independently so validation contains every class."""
    if not 0.0 < validation_fraction < 1.0:
        raise ValueError("validation_fraction must be between 0 and 1")
    by_label: dict[str, list[tuple[Path, str]]] = defaultdict(list)
    for record in records:
        by_label[record[1]].append(record)
    rng = random.Random(seed)
    train: list[tuple[Path, str]] = []
    validation: list[tuple[Path, str]] = []
    for label, items in by_label.items():
        rng.shuffle(items)
        validation_count = max(1, round(len(items) * validation_fraction))
        if validation_count >= len(items):
            validation_count = 1
        validation.extend(items[:validation_count])
        train.extend(items[validation_count:])
    rng.shuffle(train)
    rng.shuffle(validation)
    return train, validation


def build_model(tf, class_count: int, image_size: int):
    augmentation = tf.keras.Sequential(
        [
            tf.keras.layers.RandomFlip("horizontal"),
            tf.keras.layers.RandomRotation(0.08),
            tf.keras.layers.RandomZoom(0.1),
        ],
        name="augmentation",
    )
    base = tf.keras.applications.MobileNetV2(
        input_shape=(image_size, image_size, 3),
        include_top=False,
        weights="imagenet",
    )
    base.trainable = False
    inputs = tf.keras.Input(shape=(image_size, image_size, 3), name="image")
    x = augmentation(inputs)
    x = tf.keras.applications.mobilenet_v2.preprocess_input(x)
    x = base(x, training=False)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dropout(0.2)(x)
    outputs = tf.keras.layers.Dense(class_count, activation="softmax", name="scores")(x)
    return tf.keras.Model(inputs, outputs, name="agrolens_mobilenetv2")


def make_dataset(tf, records, label_to_index, image_size, batch_size, training):
    paths = [str(path) for path, _ in records]
    labels = [label_to_index[label] for _, label in records]
    dataset = tf.data.Dataset.from_tensor_slices((paths, labels))
    if training:
        dataset = dataset.shuffle(len(records), seed=42, reshuffle_each_iteration=True)

    def load(path, label):
        image = tf.io.read_file(path)
        image = tf.image.decode_image(image, channels=3, expand_animations=False)
        image.set_shape([None, None, 3])
        image = tf.image.resize(image, [image_size, image_size])
        return tf.cast(image, tf.float32), label

    return dataset.map(load, num_parallel_calls=tf.data.AUTOTUNE).batch(
        batch_size
    ).prefetch(tf.data.AUTOTUNE)


def export_tflite(tf, model, output_path: Path) -> None:
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(converter.convert())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dataset", action="append", type=Path, required=True,
        help="Dataset root; repeat for PlantDoc and PlantVillage",
    )
    parser.add_argument("--output-dir", type=Path, default=Path("ml/models/agrolens"))
    parser.add_argument("--epochs", type=int, default=12)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--image-size", type=int, default=224)
    parser.add_argument("--validation-fraction", type=float, default=0.2)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    if args.epochs < 1 or args.batch_size < 1 or args.image_size < 1:
        raise SystemExit("epochs, batch-size, and image-size must be positive")

    try:
        import tensorflow as tf
    except ImportError as exc:
        raise SystemExit(
            "TensorFlow is required; install ml/requirements-tflite.txt"
        ) from exc

    records = collect_images(args.dataset)
    train_records, validation_records = stratified_split(
        records, args.validation_fraction, args.seed
    )
    labels = sorted({label for _, label in records})
    label_to_index = {label: index for index, label in enumerate(labels)}
    train_dataset = make_dataset(
        tf, train_records, label_to_index, args.image_size, args.batch_size, True
    )
    validation_dataset = make_dataset(
        tf, validation_records, label_to_index, args.image_size, args.batch_size, False
    )
    model = build_model(tf, len(labels), args.image_size)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_accuracy", patience=3, restore_best_weights=True
        ),
        tf.keras.callbacks.ModelCheckpoint(
            args.output_dir / "best.keras", monitor="val_accuracy", save_best_only=True
        ),
    ]
    history = model.fit(
        train_dataset,
        validation_data=validation_dataset,
        epochs=args.epochs,
        callbacks=callbacks,
    )
    model.export(args.output_dir / "saved_model")
    export_tflite(tf, model, args.output_dir / "agrolens.tflite")
    (args.output_dir / "labels.json").write_text(
        json.dumps(labels, indent=2) + "\n", encoding="utf-8"
    )
    (args.output_dir / "training_summary.json").write_text(
        json.dumps(
            {
                "architecture": "MobileNetV2",
                "image_size": [args.image_size, args.image_size],
                "class_count": len(labels),
                "image_count": len(records),
                "train_count": len(train_records),
                "validation_count": len(validation_records),
                "final_metrics": {
                    key: float(values[-1]) for key, values in history.history.items()
                },
                "datasets": [str(root) for root in args.dataset],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
