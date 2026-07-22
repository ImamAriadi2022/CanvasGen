"""Memory cleanup and VRAM/RAM diagnostic utilities for CanvasGen.

Provides garbage collection triggers, PyTorch CUDA cache clearing,
and hardware memory state inspection functions.
"""

import gc
from typing import Dict, Union

from utils.logger import get_logger

logger = get_logger("CanvasGen.Utils.Memory")

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# Check if PyTorch is installed and available
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


def flush_vram() -> None:
    """Triggers Python garbage collection and clears PyTorch CUDA memory cache."""
    gc.collect()
    if TORCH_AVAILABLE and torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()
        logger.info("VRAM cache successfully flushed and garbage collection executed.")
    else:
        logger.debug("Garbage collection executed (CUDA unavailable or PyTorch not loaded).")


def get_vram_usage() -> Dict[str, Union[float, bool, str]]:
    """Inspects PyTorch CUDA VRAM usage metrics.

    Returns:
        Dictionary containing CUDA availability status, total, allocated, and reserved VRAM in MB.
    """
    if not TORCH_AVAILABLE or not torch.cuda.is_available():
        return {
            "cuda_available": False,
            "device_name": "N/A",
            "allocated_mb": 0.0,
            "reserved_mb": 0.0,
            "total_mb": 0.0,
        }

    device = torch.cuda.current_device()
    total_mem = torch.cuda.get_device_properties(device).total_memory / (1024 ** 2)
    allocated = torch.cuda.memory_allocated(device) / (1024 ** 2)
    reserved = torch.cuda.memory_reserved(device) / (1024 ** 2)

    return {
        "cuda_available": True,
        "device_name": torch.cuda.get_device_name(device),
        "allocated_mb": round(allocated, 2),
        "reserved_mb": round(reserved, 2),
        "total_mb": round(total_mem, 2),
    }


def get_ram_usage() -> Dict[str, float]:
    """Inspects host system RAM memory metrics using psutil.

    Returns:
        Dictionary containing total, used, available RAM in MB and memory percentage.
    """
    if not PSUTIL_AVAILABLE:
        return {
            "total_mb": 0.0,
            "used_mb": 0.0,
            "available_mb": 0.0,
            "percent_used": 0.0,
        }

    vm = psutil.virtual_memory()
    return {
        "total_mb": round(vm.total / (1024 ** 2), 2),
        "used_mb": round(vm.used / (1024 ** 2), 2),
        "available_mb": round(vm.available / (1024 ** 2), 2),
        "percent_used": vm.percent,
    }
