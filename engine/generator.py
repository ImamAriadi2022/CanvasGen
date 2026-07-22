"""Modul engine generator gambar untuk CanvasGen.

Mengorkestrasi sintesis text-to-image, generasi batch, validasi parameter,
dan penerapan seed deterministik.
"""

from typing import Any, Dict, List, Optional, Union
from PIL import Image

from config.settings import Settings, get_settings
from engine.loader import ModelLoader
from utils.logger import get_logger
from utils.seed import set_seed

logger = get_logger("CanvasGen.Engine.Generator")

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


class ImageGenerator:
    """Orkestrator generasi gambar utama yang mengelola permintaan text-to-image dan batch."""

    def __init__(
        self,
        loader: Optional[ModelLoader] = None,
        settings: Optional[Settings] = None,
    ) -> None:
        """Menginisialisasi ImageGenerator dengan ModelLoader dan settings.

        Args:
            loader: Instance ModelLoader. Jika None, loader baru akan diinisialisasi.
            settings: Instance Settings. Jika None, settings default akan digunakan.
        """
        self.settings = settings or get_settings()
        self.loader = loader or ModelLoader(self.settings)

    def generate(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: Optional[int] = None,
        height: Optional[int] = None,
        num_inference_steps: Optional[int] = None,
        guidance_scale: Optional[float] = None,
        seed: Optional[int] = None,
    ) -> Image.Image:
        """Menghasilkan satu gambar dari prompt teks.

        Args:
            prompt: Prompt teks deskripsi gambar target.
            negative_prompt: Prompt teks untuk elemen yang dihindari.
            width: Lebar gambar target dalam piksel.
            height: Tinggi gambar target dalam piksel.
            num_inference_steps: Jumlah langkah iterasi denoising.
            guidance_scale: Skala guidance CFG.
            seed: Seed integer opsional untuk reproduksibilitas.

        Returns:
            Objek PIL Image hasil generasi.
        """
        w = width or self.settings.default_width
        h = height or self.settings.default_height
        steps = num_inference_steps or self.settings.default_num_inference_steps
        cfg = guidance_scale or self.settings.default_guidance_scale
        active_seed = set_seed(seed)

        logger.info(
            "Menghasilkan gambar [Prompt: '%s' | Ukuran: %dx%d | Steps: %d | CFG: %.1f | Seed: %d]",
            prompt,
            w,
            h,
            steps,
            cfg,
            active_seed,
        )

        # Pastikan pipeline telah dimuat
        if self.loader.pipeline is None:
            self.loader.load_pipeline()

        pipe = self.loader.pipeline

        # Eksekusi pipeline Diffusers jika objek pipeline riil
        if TORCH_AVAILABLE and hasattr(pipe, "__call__") and not isinstance(pipe, str):
            try:
                generator = torch.Generator(device=self.loader.device).manual_seed(active_seed)
                output = pipe(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    width=w,
                    height=h,
                    num_inference_steps=steps,
                    guidance_scale=cfg,
                    generator=generator,
                )
                generated_img = output.images[0]
                logger.info("Generasi Diffusers aktual berhasil diselesaikan.")
                return generated_img
            except Exception as e:
                logger.warning("Eksekusi Diffusers aktual gagal (%s). Menggunakan output placeholder.", e)

        # Output placeholder jika dalam mode mock / offline
        mock_image = Image.new("RGB", (w, h), color=(73, 109, 137))
        return mock_image

    def generate_batch(
        self,
        prompt: str,
        batch_size: int = 4,
        negative_prompt: str = "",
        width: Optional[int] = None,
        height: Optional[int] = None,
        num_inference_steps: Optional[int] = None,
        guidance_scale: Optional[float] = None,
        base_seed: Optional[int] = None,
    ) -> List[Image.Image]:
        """Menghasilkan sekumpulan (batch) gambar dari satu prompt teks.

        Args:
            prompt: Prompt teks deskripsi gambar target.
            batch_size: Jumlah gambar yang akan dihasilkan.
            negative_prompt: Prompt negatif.
            width: Lebar target piksel.
            height: Tinggi target piksel.
            num_inference_steps: Langkah sampling.
            guidance_scale: Nilai skala CFG.
            base_seed: Integer seed awal untuk urutan deterministik.

        Returns:
            Daftar instance gambar PIL Image.
        """
        logger.info("Mengeksekusi generasi batch dengan ukuran: %d", batch_size)
        start_seed = base_seed if base_seed is not None else set_seed()

        images: List[Image.Image] = []
        for i in range(batch_size):
            current_seed = start_seed + i
            img = self.generate(
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                seed=current_seed,
            )
            images.append(img)

        return images
