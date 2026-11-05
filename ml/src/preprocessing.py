"""Image loading and preprocessing for AgroLens inference."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import BinaryIO

import numpy as np
from PIL import Image, UnidentifiedImageError

ImageSource = str | Path | bytes | bytearray | BinaryIO
DEFAULT_INPUT_SIZE = (224, 224)


class ImageInputError(ValueError):
    """Raised when an input cannot be decoded as a non-empty image."""


def load_image(source: ImageSource) -> Image.Image:
    """Decode an image source and return it as an RGB PIL image."""
    try:
        if isinstance(source, (str, Path)):
            image = Image.open(source)
        elif isinstance(source, (bytes, bytearray)):
            image = Image.open(BytesIO(source))
        elif hasattr(source, "read"):
            image = Image.open(source)
        else:
            raise ImageInputError("image source must be a path, bytes, or binary stream")
        image.load()
        if image.width < 1 or image.height < 1:
            raise ImageInputError("image dimensions must be positive")
        return image.convert("RGB")
    except (OSError, UnidentifiedImageError) as exc:
        raise ImageInputError("image source is not a readable image") from exc


def preprocess_image(
    source: ImageSource, input_size: tuple[int, int] = DEFAULT_INPUT_SIZE
) -> np.ndarray:
    """Decode, resize, and normalize an image into a model batch."""
    if len(input_size) != 2 or any(d < 1 for d in input_size):
        raise ValueError("input_size must contain two positive dimensions")
    image = load_image(source).resize(input_size, Image.Resampling.BILINEAR)
    array = np.asarray(image, dtype=np.float32) / 255.0
    if array.shape != (input_size[1], input_size[0], 3):
        raise ImageInputError("preprocessed image has an unexpected shape")
    return np.expand_dims(array, axis=0)
