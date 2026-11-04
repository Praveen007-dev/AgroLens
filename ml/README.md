# AgroLens ML inference

This directory contains the Python inference and training interface for AgroLens.
The repository does not contain the datasets or trained weights. Until training
is run, the default implementation uses a clearly marked deterministic mock
model. It does **not** represent trained model performance or an expert
diagnosis.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r ml\requirements.txt
python -m pytest ml\tests
```

## Train with PlantDoc and PlantVillage

Do not commit either dataset to this repository. Clone or download them outside
the repository, then install the training dependencies:

```powershell
python -m pip install -r ml\requirements-train.txt
python ml\scripts\train.py `
  --dataset C:\datasets\PlantDoc-Dataset `
  --dataset C:\datasets\PlantVillage-Dataset\raw\color `
  --output-dir ml\models\agrolens `
  --epochs 12
```

On native Windows, use the GPU-native PyTorch trainer instead. TensorFlow
2.11+ does not provide native-Windows CUDA support:

```powershell
python ml\scripts\train_pytorch.py `
  --dataset C:\datasets\PlantDoc-Dataset\train `
  --test-dataset C:\datasets\PlantDoc-Dataset\test `
  --output-dir ml\models\plantdoc-mobilenetv3 `
  --epochs 12 `
  --batch-size 16
```

Install its dependencies with `ml\requirements-train-pytorch.txt`. This
produces a GPU-trained `best.pt` checkpoint and measured metrics. It does not
produce TFLite directly; convert the selected checkpoint through a Linux/WSL
TensorFlow or ONNX conversion workflow after evaluation.

The trainer recursively reads image files and uses each image's immediate parent
folder as its class label. This supports PlantDoc train/test class folders and
PlantVillage's `raw/color/<class>` layout. It creates a stratified validation
split, trains an ImageNet-initialized MobileNetV2 head at 224 x 224, and writes:

* `best.keras` — best validation checkpoint
* `saved_model/` — TensorFlow SavedModel
* `agrolens.tflite` — float32 mobile model
* `labels.json` — output-index mapping
* `training_summary.json` — counts and measured final metrics

The first run trains only the classification head. This is intentional for a
mobile-first baseline; fine-tuning selected MobileNetV2 layers can be added
after the baseline is evaluated on a held-out, field-like test set. Do not
report accuracy until this command has completed and the resulting metrics have
been reviewed.

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
