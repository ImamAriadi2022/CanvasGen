"""Centralized Model Loader for CanvasGen Hugging Face Diffusers Pipelines."""

import gc
from typing import Any, Dict, Optional
from config.settings import Settings, get_settings
from utils.logger import get_logger

logger = get_logger("CanvasGen.Engine.Loader")

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    import diffusers
    from diffusers import StableDiffusionPipeline, StableDiffusionInpaintPipeline
    DIFFUSERS_AVAILABLE = True
except ImportError:
    DIFFUSERS_AVAILABLE = False


class ModelLoader:
    """Singleton model loader that caches and manages real Diffusers pipelines locally."""

    _instance: Optional["ModelLoader"] = None

    def __new__(cls, settings: Optional[Settings] = None) -> "ModelLoader":
        """Ensures single global loader instance (Singleton pattern)."""
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, settings: Optional[Settings] = None) -> None:
        """Initializes ModelLoader singleton."""
        if getattr(self, "_initialized", False):
            return

        self.settings = settings or get_settings()
        self.active_model_id: str = "runwayml/stable-diffusion-v1-5"
        self.inpaint_model_id: str = "runwayml/stable-diffusion-inpainting"
        self.pipeline: Optional[Any] = None
        self.inpaint_pipeline: Optional[Any] = None
        self.device: str = self._resolve_device()
        self.precision: str = self._resolve_precision()
        self._initialized = True

    def _resolve_device(self) -> str:
        """Detects hardware and resolves target device (CUDA GPU or CPU)."""
        if TORCH_AVAILABLE and torch.cuda.is_available():
            return "cuda"
        logger.warning("Running on CPU. Generation may take several minutes.")
        return "cpu"

    def _resolve_precision(self) -> str:
        """Resolves precision mode (fp16 for CUDA GPU, fp32 for CPU)."""
        if self._resolve_device() == "cuda":
            return "fp16"
        return "fp32"

    def _resolve_dtype(self) -> Any:
        """Maps precision mode to PyTorch dtype."""
        if not TORCH_AVAILABLE:
            return None
        if self.precision == "fp16":
            return torch.float16
        return torch.float32

    def load_pipeline(
        self,
        model_id: Optional[str] = None,
        device: Optional[str] = None,
        precision: Optional[str] = None,
    ) -> Any:
        """Loads and caches the primary Text-to-Image StableDiffusionPipeline.

        Raises:
            RuntimeError: If PyTorch or Diffusers is unavailable, or model loading/download fails.
        """
        target_model = model_id or self.active_model_id
        target_device = device or self.device
        target_precision = precision or self.precision
        self.precision = target_precision
        dtype = self._resolve_dtype()

        # Return cached pipeline if already loaded
        if self.pipeline is not None and self.active_model_id == target_model:
            logger.info("Reusing cached Text-to-Image Diffusers pipeline: %s", target_model)
            return self.pipeline

        if not (DIFFUSERS_AVAILABLE and TORCH_AVAILABLE):
            raise RuntimeError(
                "PyTorch or Hugging Face Diffusers is not installed. Please install diffusers and torch."
            )

        logger.info(
            "Loading Stable Diffusion model [Model: '%s' | Device: '%s' | Precision: '%s']",
            target_model,
            target_device,
            self.precision,
        )

        try:
            kwargs: Dict[str, Any] = {}
            if dtype is not None:
                kwargs["torch_dtype"] = dtype
            if not self.settings.safety_checker:
                kwargs["safety_checker"] = None

            logger.info("Downloading Stable Diffusion model...")
            pipe = StableDiffusionPipeline.from_pretrained(target_model, **kwargs)
            logger.info("Loading Stable Diffusion...")
            pipe = pipe.to(target_device)

            # Enable Memory Optimizations on CUDA
            if target_device == "cuda":
                if hasattr(pipe, "enable_attention_slicing"):
                    pipe.enable_attention_slicing()
                if hasattr(pipe, "enable_vae_slicing"):
                    pipe.enable_vae_slicing()

            self.pipeline = pipe
            self.active_model_id = target_model
            self.device = target_device
            logger.info("Text-to-Image Stable Diffusion pipeline loaded successfully.")
            return self.pipeline
        except Exception as e:
            logger.error("Failed to load StableDiffusionPipeline: %s", e)
            raise RuntimeError(f"Unable to load Stable Diffusion model '{target_model}': {e}") from e

    def load_inpaint_pipeline(self) -> Any:
        """Loads and caches the StableDiffusionInpaintPipeline for inpainting and outpainting.

        Raises:
            RuntimeError: If PyTorch or Diffusers is unavailable, or model loading/download fails.
        """
        if self.inpaint_pipeline is not None:
            logger.info("Reusing cached Inpaint pipeline: %s", self.inpaint_model_id)
            return self.inpaint_pipeline

        if not (DIFFUSERS_AVAILABLE and TORCH_AVAILABLE):
            raise RuntimeError(
                "PyTorch or Hugging Face Diffusers is not installed for Inpainting pipeline."
            )

        target_model = self.inpaint_model_id
        target_device = self.device
        dtype = self._resolve_dtype()

        logger.info(
            "Loading Inpaint pipeline [Model: '%s' | Device: '%s' | Precision: '%s']",
            target_model,
            target_device,
            self.precision,
        )

        try:
            kwargs: Dict[str, Any] = {}
            if dtype is not None:
                kwargs["torch_dtype"] = dtype
            if not self.settings.safety_checker:
                kwargs["safety_checker"] = None

            logger.info("Downloading Stable Diffusion Inpainting model...")
            pipe = StableDiffusionInpaintPipeline.from_pretrained(target_model, **kwargs)
            logger.info("Loading Stable Diffusion Inpainting...")
            pipe = pipe.to(target_device)

            if target_device == "cuda":
                if hasattr(pipe, "enable_attention_slicing"):
                    pipe.enable_attention_slicing()
                if hasattr(pipe, "enable_vae_slicing"):
                    pipe.enable_vae_slicing()

            self.inpaint_pipeline = pipe
            logger.info("Inpaint Diffusers pipeline loaded successfully.")
            return self.inpaint_pipeline
        except Exception as e:
            logger.error("Failed to load StableDiffusionInpaintPipeline: %s", e)
            raise RuntimeError(f"Unable to load Stable Diffusion Inpaint model '{target_model}': {e}") from e

    def unload_pipeline(self) -> None:
        """Unloads pipelines and flushes CUDA VRAM and system memory."""
        self.pipeline = None
        self.inpaint_pipeline = None
        if TORCH_AVAILABLE and torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()
        logger.info("Pipelines unloaded and CUDA memory flushed.")

    def get_info(self) -> Dict[str, Any]:
        """Returns metadata regarding active model loader state."""
        return {
            "active_model_id": self.active_model_id,
            "inpaint_model_id": self.inpaint_model_id,
            "device": self.device,
            "precision": self.precision,
            "is_loaded": self.pipeline is not None,
            "is_txt2img_loaded": self.pipeline is not None,
            "is_inpaint_loaded": self.inpaint_pipeline is not None,
        }
