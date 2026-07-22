"""Structured logging utility module for CanvasGen.

Provides custom logger initialization with console and file output support.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str = "CanvasGen",
    log_level: str = "INFO",
    log_file: Optional[Path] = None,
) -> logging.Logger:
    """Configures and returns a structured logger instance.

    Args:
        name: Name of the logger instance.
        log_level: Desired log level string (e.g., 'DEBUG', 'INFO', 'WARNING', 'ERROR').
        log_file: Optional Path object specifying file output location.

    Returns:
        Configured logging.Logger object.
    """
    logger = logging.getLogger(name)
    level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(level)

    # Avoid duplicate handlers if logger is re-initialized
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    logger.addHandler(console_handler)

    # File Handler if path specified
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "CanvasGen") -> logging.Logger:
    """Retrieves an existing logger or initializes a default instance.

    Args:
        name: Name of the logger to retrieve.

    Returns:
        logging.Logger instance.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logger(name)
    return logger
