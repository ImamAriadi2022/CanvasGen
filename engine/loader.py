"""Modul engine pemuat model (Model Loader) untuk CanvasGen.

Mengelola pemuatan model Stable Diffusion, penempatan perangkat (cuda/cpu/mps),
pemetaan presisi (fp16/fp32/bf16), token autentikasi HuggingFace,
dan optimasi memori VRAM.
"""

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
    """Pengelola pemuatan, penyiapan cache, dan pelepasan pipeline difusi."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        """Menginisialisasi instance ModelLoader dengan konfigurasi settings.

        Args:
            settings: Objek Settings opsional. Jika None, konfigurasi default akan digunakan.
        """
        self.settings = settings or get_settings()
        self.active_model_id: Optional[str] = None
        self.pipeline: Optional[Any] = None
        self.device: str = self.settings.device
        self.precision: str = self.settings.precision

    def _resolve_dtype(self, precision_str: str) -> Any:
        """Memetakan string presisi menjadi torch.dtype."""
        if not TORCH_AVAILABLE:
            return None
        p = precision_str.lower()
        if p in ["fp16", "float16"]:
            return torch.float16
        elif p in ["bf16", "bfloat16"]:
            return torch.bfloat16
        return torch.float32

    def load_pipeline(
        self,
        model_id: Optional[str] = None,
        device: Optional[str] = None,
        precision: Optional[str] = None,
        use_auth_token: Optional[str] = None,
    ) -> Any:
        """Memuat StableDiffusionPipeline atau pipeline difusi yang relevan.

        Args:
            model_id: ID repository HuggingFace atau jalur model lokal.
            device: Perangkat target ('cuda', 'cpu', 'mps').
            precision: Presisi data dtype ('fp16', 'fp32', 'bf16').
            use_auth_token: Token autentikasi pengguna HuggingFace.

        Returns:
            Instance pipeline difusi yang dimuat atau objek fallback.
        """
        target_model = model_id or self.settings.model_id
        target_device = device or self.device
        target_precision = precision or self.precision
        auth_token = use_auth_token or self.settings.hf_token

        # Penyesuaian otomatis jika CUDA tidak tersedia
        if TORCH_AVAILABLE and target_device == "cuda" and not torch.cuda.is_available():
            logger.warning("CUDA tidak tersedia di sistem ini. Beralih ke CPU.")
            target_device = "cpu"

        logger.info(
            "Menyiapkan pemuatan pipeline [Model: '%s' | Perangkat: '%s' | Presisi: '%s']",
            target_model,
            target_device,
            target_precision,
        )

        torch_dtype = self._resolve_dtype(target_precision)

        if DIFFUSERS_AVAILABLE and TORCH_AVAILABLE:
            try:
                kwargs: Dict[str, Any] = {"torch_dtype": torch_dtype}
                if auth_token:
                    kwargs["use_auth_token"] = auth_token
                if not self.settings.safety_checker:
                    kwargs["safety_checker"] = None

                logger.info("Memuat StableDiffusionPipeline dari repo: %s", target_model)
                pipe = StableDiffusionPipeline.from_pretrained(target_model, **kwargs)
                pipe.to(target_device)

                # Optimasi memori
                if hasattr(pipe, "enable_attention_slicing"):
                    pipe.enable_attention_slicing()

                self.pipeline = pipe
                self.active_model_id = target_model
                self.device = target_device
                self.precision = target_precision
                logger.info("Pipeline Diffusers '%s' berhasil dimuat ke perangkat %s.", target_model, target_device)
                return self.pipeline
            except Exception as e:
                logger.warning("Pemuatan Diffusers aktual gagal/offline (%s). Menggunakan mode PipelineMock.", e)

        # Fallback mode jika Diffusers/PyTorch belum mengunduh model lokal
        self.active_model_id = target_model
        self.device = target_device
        self.precision = target_precision
        self.pipeline = f"PipelineMock[{target_model}]"
        logger.info("Pipeline '%s' berhasil terdaftar (Mode Mock Engine).", target_model)
        return self.pipeline

    def unload_pipeline(self) -> None:
        """Melepaskan pipeline aktif dari memori perangkat dan menghapus referensi."""
        if self.pipeline is not None:
            logger.info("Melepaskan pipeline: '%s'", self.active_model_id)
            self.pipeline = None
            self.active_model_id = None
        else:
            logger.warning("Tidak ada pipeline aktif yang dapat dilepas.")

    def get_info(self) -> Dict[str, Any]:
        """Mengembalikan metadata mengenai pipeline aktif dan konfigurasi sistem.

        Returns:
            Dictionary berisi active_model_id, device, precision, dan status is_loaded.
        """
        return {
            "active_model_id": self.active_model_id,
            "device": self.device,
            "precision": self.precision,
            "is_loaded": self.pipeline is not None,
        }
