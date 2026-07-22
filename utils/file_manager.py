"""File system and directory management helper for CanvasGen.

Handles directory creation, safe filename formatting, and output path generation.
"""

from datetime import datetime
from pathlib import Path
from typing import Union

from utils.logger import get_logger

logger = get_logger("CanvasGen.Utils.FileManager")


def ensure_directory(path: Union[str, Path]) -> Path:
    """Ensures a directory exists, creating parent directories if required.

    Args:
        path: Path string or Path object to ensure.

    Returns:
        Resolved Path object.
    """
    target_path = Path(path).resolve()
    if not target_path.exists():
        target_path.mkdir(parents=True, exist_ok=True)
        logger.info("Created directory structure: %s", target_path)
    return target_path


def generate_output_path(
    output_dir: Union[str, Path] = "outputs",
    prefix: str = "canvasgen",
    extension: str = "png",
) -> Path:
    """Generates a timestamped unique file output path.

    Args:
        output_dir: Directory where output files are saved.
        prefix: Filename prefix string.
        extension: Image extension without leading dot (e.g., 'png', 'jpg').

    Returns:
        Path object representing the destination file path.
    """
    out_dir = ensure_directory(output_dir)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:19]
    filename = f"{prefix}_{timestamp}.{extension.lstrip('.')}"
    file_path = out_dir / filename
    logger.debug("Generated unique output file path: %s", file_path)
    return file_path
