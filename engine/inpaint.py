"""Modul engine inpainting untuk CanvasGen.

Menangani penggantian area gambar bermasker (inpaint), validasi dimensi mask,
dan penyiapan pipeline inpainting.
"""

from typing import Any, Optional
from PIL import Image

from config.settings import Settings, get_settings
from engine.loader import ModelLoader
from utils.logger import get_logger
from utils.seed import set_seed

logger = get_logger("CanvasGen.Engine.Inpaint")

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


class InpaintPipeline:
    """Pemroses inpainting yang mengelola sintesis gambar pada area bermasker."""

    def __init__(
        self,
        loader: Optional[ModelLoader] = None,
        settings: Optional[Settings] = None,
    ) -> None:
        """Menginisialisasi InpaintPipeline dengan ModelLoader dan settings.

        Args:
            loader: Instance ModelLoader. Jika None, loader baru diinisialisasi.
            settings: Instance Settings. Jika None, settings default digunakan.
        """
        self.settings = settings or get_settings()
        self.loader = loader or ModelLoader(self.settings)

    def inpaint(
        self,
        image: Image.Image,
        mask_image: Image.Image,
        prompt: str,
        negative_prompt: str = "",
        num_inference_steps: Optional[int] = None,
        guidance_scale: Optional[float] = None,
        seed: Optional[int] = None,
    ) -> Image.Image:
        """Mengganti isi area bermasker pada gambar dengan konten baru dari prompt.

        Args:
            image: Gambar dasar PIL Image.
            mask_image: Masker grayscale PIL Image (putih = ganti, hitam = pertahankan).
            prompt: Prompt teks deskripsi penggantian inpainting.
            negative_prompt: Prompt panduan negatif.
            num_inference_steps: Langkah sampling denoising.
            guidance_scale: Pengali skala CFG.
            seed: Seed acak integer opsional.

        Returns:
            Objek PIL Image hasil inpainting.
        """
        if image.size != mask_image.size:
            logger.warning(
                "Ukuran gambar %s tidak cocok dengan mask %s. Mengubah ukuran mask agar cocok.",
                image.size,
                mask_image.size,
            )
            mask_image = mask_image.resize(image.size, Image.Resampling.NEAREST)

        # Ensure correct modes for image and mask
        if image.mode != "RGB":
            image = image.convert("RGB")
        if mask_image.mode not in ["L", "RGB"]:
            mask_image = mask_image.convert("L")

        active_seed = set_seed(seed)
        steps = num_inference_steps or self.settings.default_num_inference_steps
        cfg = guidance_scale or self.settings.default_guidance_scale

        logger.info(
            "Mengeksekusi Inpainting [Prompt: '%s' | Steps: %d | CFG: %.1f | Seed: %d]",
            prompt,
            steps,
            cfg,
            active_seed,
        )

        pipe = self.loader.pipeline

        # Eksekusi pipeline inpainting Diffusers jika objek pipeline riil
        if TORCH_AVAILABLE and hasattr(pipe, "__call__") and not isinstance(pipe, str):
            try:
                generator = torch.Generator(device=self.loader.device).manual_seed(active_seed)
                output = pipe(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    image=image,
                    mask_image=mask_image,
                    num_inference_steps=steps,
                    guidance_scale=cfg,
                    generator=generator,
                )
                logger.info("Eksekusi Inpainting Diffusers aktual berhasil.")
                return output.images[0]
            except Exception as e:
                logger.warning("Eksekusi Inpainting Diffusers aktual gagal (%s). Menggunakan komposisi mock.", e)

        # Output placeholder inpainting (komposisi dasar)
        result = image.copy()
        return result
