"""Seed management utilities for CanvasGen.

Provides random seed generation and deterministic seed configuration
across Python standard library, NumPy, and PyTorch.
"""

import random
import numpy as np
from typing import Optional

from utils.logger import get_logger

logger = get_logger("CanvasGen.Utils.Seed")

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


def generate_random_seed() -> int:
    """Generates a random 32-bit integer seed suitable for Stable Diffusion pipelines.

    Returns:
        Random integer seed between 0 and 2,147,483,647.
    """
    return random.randint(0, 2**31 - 1)


def set_seed(seed: Optional[int] = None) -> int:
    """Sets deterministic seed across random, numpy, and torch modules.

    Args:
        seed: Target integer seed. If None, a random seed will be generated.

    Returns:
        The active seed integer applied across all frameworks.
    """
    if seed is None or seed < 0:
        seed = generate_random_seed()

    random.seed(seed)
    np.random.seed(seed % (2**32))

    if TORCH_AVAILABLE:
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed(seed)
            torch.cuda.manual_seed_all(seed)
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False

    logger.info("Global deterministic random seed set to: %d", seed)
    return seed
