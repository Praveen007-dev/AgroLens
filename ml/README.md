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

## GPU training

Do not commit either dataset or generated weights. Install the GPU-native
training dependencies in the existing CUDA-enabled Python environment:

```powershell
python -m pip install -r ml\requirements-train-pytorch.txt
python ml\scripts\train_pytorch.py `
  --dataset C:\datasets\PlantLeafDiseasesWithoutAug `
  --output-dir ml\models\plantleaf-mobilenetv3 `
  --epochs 5 `
  --batch-size 16
```

For low-resolution phone images, use:

```powershell
python ml\scripts\train_pytorch.py `
  --dataset C:\datasets\PlantLeafDiseasesWithoutAug `
  --output-dir ml\models\plantleaf-lowres-mobilenetv3 `
  --epochs 5 `
  --batch-size 16 `
  --low-resolution
```

Low-resolution mode uses 160 x 160 input and randomly simulates downsampling,
blur, and compression-like quality loss during training. It writes a
checkpoint, labels, and measured training summary. The prediction script reads
the checkpoint input size automatically.

Mobile model options:

* **MobileNetV3-Small**: current choice; lowest compute and memory.
* **MobileNetV3-Large**: likely better accuracy, but slower and larger.
* **EfficientNet-Lite0**: strong accuracy/size tradeoff, but requires an
  additional export path for TFLite.
* **MobileNetV2**: stable fallback with broad deployment support.

Compare models on the same field-like holdout set rather than selecting by
training accuracy alone.

## Test an image with the trained model

```powershell
python ml\scripts\predict.py `
  "C:\path\to\leaf.jpg" `
  --model ml\models\plantleaf-lowres-mobilenetv3\best.pt
```

Or test every supported image in a folder:

```powershell
python ml\scripts\predict.py "C:\path\to\photos" --json
```

The program uses CUDA automatically when available, applies the checkpoint's
input size and ImageNet normalization, and prints the predicted label,
confidence, low-confidence flag, and top-five predictions. Use `--cpu` to force
CPU inference. A low-confidence result is only a model signal and must not be
presented as an expert-confirmed diagnosis.

## Contract interface

```python
from ml.src.inference import InferenceEngine

result = InferenceEngine().infer("path/to/leaf.jpg", crop="tomato")
```

The returned dictionary follows `contracts/inference_contract.json` exactly.
The default mock model is used only when a trained model is not supplied.

## TensorFlow Lite conversion

The native Windows PyTorch trainer produces `best.pt`, not TFLite. Convert the
selected model through a Linux/WSL TensorFlow or ONNX workflow after evaluation.
The existing TensorFlow conversion script remains available for SavedModel or
Keras inputs:

```powershell
python -m pip install -r ml\requirements-tflite.txt
python ml\scripts\convert_to_tflite.py path\to\saved_model ml\models\agrolens.tflite
```
