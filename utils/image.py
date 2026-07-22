"""Image utility module for CanvasGen.

Handles PIL Image resizing, aspect ratio calculation, grid layout generation,
and Base64 encoding/decoding for Streamlit and web API integrations.
"""

import base64
import io
import math
from typing import List, Tuple
from PIL import Image

from utils.logger import get_logger

logger = get_logger("CanvasGen.Utils.Image")


def resize_image(
    image: Image.Image,
    target_size: Tuple[int, int],
    resample_mode: int = Image.Resampling.LANCZOS,
) -> Image.Image:
    """Resizes a PIL image to specified target dimensions.

    Args:
        image: Source PIL Image object.
        target_size: Tuple of (width, height).
        resample_mode: PIL resample filter mode.

    Returns:
        Resized PIL Image instance.
    """
    logger.debug("Resizing image from %s to %s", image.size, target_size)
    return image.resize(target_size, resample=resample_mode)


def create_image_grid(
    images: List[Image.Image],
    rows: int = 0,
    cols: int = 0,
) -> Image.Image:
    """Arranges a list of PIL Images into a single grid image.

    Args:
        images: List of PIL Image objects to composite.
        rows: Optional fixed row count. Calculated automatically if 0.
        cols: Optional fixed column count. Calculated automatically if 0.

    Returns:
        Composited PIL Image containing all input images arranged in a grid.
    """
    if not images:
        raise ValueError("Cannot create image grid from an empty image list.")

    count = len(images)
    if cols == 0 and rows == 0:
        cols = math.ceil(math.sqrt(count))
        rows = math.ceil(count / cols)
    elif cols == 0:
        cols = math.ceil(count / rows)
    elif rows == 0:
        rows = math.ceil(count / cols)

    w, h = images[0].size
    grid = Image.new("RGB", size=(cols * w, rows * h))

    for i, img in enumerate(images):
        row_idx = i // cols
        col_idx = i % cols
        grid.paste(img, box=(col_idx * w, row_idx * h))

    logger.info("Created image grid of dimensions %dx%d for %d images", cols, rows, count)
    return grid


def image_to_base64(image: Image.Image, format_type: str = "PNG") -> str:
    """Encodes a PIL image object to a Base64 ASCII string.

    Args:
        image: Source PIL Image.
        format_type: Output image format string (e.g. 'PNG', 'JPEG').

    Returns:
        Base64 string representation.
    """
    buffer = io.BytesIO()
    image.save(buffer, format=format_type)
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/{format_type.lower()};base64,{encoded}"


def base64_to_image(base64_str: str) -> Image.Image:
    """Decodes a Base64 string into a PIL Image object.

    Args:
        base64_str: Encoded Base64 string representation.

    Returns:
        Decoded PIL Image.
    """
    if "," in base64_str:
        base64_str = base64_str.split(",", 1)[1]
    decoded = base64.b64decode(base64_str)
    return Image.open(io.BytesIO(decoded))
