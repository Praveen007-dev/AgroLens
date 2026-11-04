"""Convert a TensorFlow SavedModel or Keras model to float32 TFLite."""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_model", type=Path)
    parser.add_argument("output_model", type=Path)
    args = parser.parse_args()
    try:
        import tensorflow as tf
    except ImportError as exc:
        raise SystemExit(
            "TensorFlow is required; install ml/requirements-tflite.txt"
        ) from exc
    converter = (
        tf.lite.TFLiteConverter.from_saved_model(str(args.input_model))
        if args.input_model.is_dir()
        else tf.lite.TFLiteConverter.from_keras_model(
            tf.keras.models.load_model(args.input_model)
        )
    )
    converter.target_spec.supported_types = [tf.float32]
    args.output_model.parent.mkdir(parents=True, exist_ok=True)
    args.output_model.write_bytes(converter.convert())
    print(f"Wrote {args.output_model}")


if __name__ == "__main__":
    main()
