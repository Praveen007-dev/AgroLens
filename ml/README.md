# AgroLens ML inference

This directory contains the Python inference interface for AgroLens. No trained
model or dataset is present in this repository, so the default implementation
uses a clearly marked deterministic mock model. It is suitable for exercising
the mobile integration and contract handling, but it does **not** represent
trained model performance or an expert diagnosis.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r ml\requirements.txt
python -m pytest ml\tests
```

## Interface

```python
from ml.src.inference import InferenceEngine

result = InferenceEngine().infer("path/to/leaf.jpg", crop="tomato")
```

The returned dictionary follows `contracts/inference_contract.json` exactly:

```json
{
  "prediction_id": "UUID",
  "crop": "tomato",
  "disease_label": "healthy",
  "confidence": 0.42,
  "top_predictions": [{"label": "healthy", "confidence": 0.42}],
  "is_low_confidence": true,
  "model_version": "mock-0.1.0",
  "inference_timestamp": "2026-01-01T00:00:00Z"
}
```

The mock model is intentionally low-confidence for ambiguous images. Consumers
must not present a low-confidence result as a confirmed diagnosis.

### Input and preprocessing

* Input: a filesystem path, bytes, or a binary file-like object.
* Color: converted to RGB.
* Size: 224 x 224 pixels.
* Numeric representation: `float32`, channels-last, values normalized to
  `[0.0, 1.0]`.
* Top-k: three predictions by default, sorted by descending confidence.
* Threshold: confidence below `0.60` sets `is_low_confidence` to `true`.

The provisional labels are in `ml/labels/labels.json`. Replace that file and
provide a real model before using this in production; shared
`contracts/disease_labels.json` should take precedence when it becomes
available.

## Integrating a real model

Implement a model object with:

```python
predict(batch: numpy.ndarray) -> numpy.ndarray
```

It must return one probability per configured label. Pass it to
`InferenceEngine(model=your_model, labels=your_labels, model_version="...")`.
The engine validates the output, normalizes probabilities when necessary, and
keeps the contract response stable.

## TensorFlow Lite conversion

TensorFlow is intentionally not a required runtime dependency for the mock
interface. Install it separately in a model-development environment:

```powershell
python -m pip install -r ml\requirements-tflite.txt
python ml\scripts\convert_to_tflite.py path\to\saved_model ml\models\agrolens.tflite
```

The conversion script accepts a SavedModel directory or Keras model file and
uses float32 input/output. A mobile client should resize an image to 224 x 224,
convert it to RGB, normalize to `[0, 1]`, invoke the `.tflite` interpreter, and
map output indices through the same labels file.
