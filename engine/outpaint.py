"""Modul engine outpainting untuk CanvasGen.

Menangani ekspansi kanvas berarah, pembuatan padding batas, sintesis mask biner,
dan eksekusi pipeline outpainting.
"""

from typing import Any, Dict, Optional, Tuple
from PIL import Image, ImageOps

from config.settings import Settings, get_settings
from engine.inpaint import InpaintPipeline
from utils.logger import get_logger
from utils.seed import set_seed

logger = get_logger("CanvasGen.Engine.Outpaint")


class OutpaintPipeline:
    """Pemroses outpainting yang memperluas batas gambar ke arah tertentu."""

    def __init__(
        self,
        inpaint_pipeline: Optional[InpaintPipeline] = None,
        settings: Optional[Settings] = None,
    ) -> None:
        """Menginisialisasi OutpaintPipeline dengan InpaintPipeline dan settings.

        Args:
            inpaint_pipeline: Instance InpaintPipeline untuk generasi difusi.
            settings: Instance Settings. Jika None, settings default digunakan.
        """
        self.settings = settings or get_settings()
        self.inpaint_engine = inpaint_pipeline or InpaintPipeline(settings=self.settings)

    def prepare_outpaint_canvas(
        self,
        image: Image.Image,
        padding: Tuple[int, int, int, int],  # (kiri, atas, kanan, bawah)
    ) -> Tuple[Image.Image, Image.Image]:
        """Memperluas dimensi kanvas dan membuat masker biner outpainting yang sesuai.

        Args:
            image: Gambar PIL Image asli.
            padding: Tuple padding piksel (kiri, atas, kanan, bawah).

        Returns:
            Tuple dari (gambar_diperluas, mask_dihasilkan).
        """
        left, top, right, bottom = padding

        # Memperluas gambar asli dengan batas hitam
        expanded_image = ImageOps.expand(
            image,
            border=(left, top, right, bottom),
            fill=(0, 0, 0),
        )

        # Membuat mask: Putih (255) untuk area padding baru, Hitam (0) untuk konten asli
        w, h = expanded_image.size
        mask = Image.new("L", (w, h), 255)

        # Menempelkan persegi panjang hitam di posisi gambar asli
        orig_w, orig_h = image.size
        black_orig = Image.new("L", (orig_w, orig_h), 0)
        mask.paste(black_orig, (left, top))

        logger.info(
            "Kanvas diperluas dari %s menjadi %s dengan padding (Kiri:%d, Atas:%d, Kanan:%d, Bawah:%d)",
            image.size,
            expanded_image.size,
            left,
            top,
            right,
            bottom,
        )
        return expanded_image, mask

    def outpaint(
        self,
        image: Image.Image,
        padding: Tuple[int, int, int, int],
        prompt: str,
        negative_prompt: str = "",
        num_inference_steps: Optional[int] = None,
        guidance_scale: Optional[float] = None,
        seed: Optional[int] = None,
    ) -> Image.Image:
        """Melakukan outpainting pada batas gambar berdasarkan padding piksel berarah.

        Args:
            image: Gambar sumber asli PIL Image.
            padding: Tuple ekspansi piksel (kiri, atas, kanan, bawah).
            prompt: Prompt teks deskripsi ekstensi pemandangan.
            negative_prompt: Prompt negatif.
            num_inference_steps: Langkah sampling denoising.
            guidance_scale: Pengali skala CFG.
            seed: Integer seed acak.

        Returns:
            Objek gambar hasil outpaint PIL Image.
        """
        canvas, mask = self.prepare_outpaint_canvas(image, padding)

        active_seed = set_seed(seed)
        logger.info("Mengeksekusi generasi Outpaint untuk kanvas yang diperluas...")

        # Menjalankan inpainting di atas kanvas yang telah diperluas dan mask yang dihasilkan
        result = self.inpaint_engine.inpaint(
            image=canvas,
            mask_image=mask,
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            seed=active_seed,
        )

        return result

    def zoom_out(
        self,
        image: Image.Image,
        zoom_factor: float = 1.5,
        prompt: str = "",
        negative_prompt: str = "",
        seed: Optional[int] = None,
    ) -> Image.Image:
        """Melakukan outpainting progresif (zoom out) untuk memperluas kanvas ke segala arah secara proporsional.

        Args:
            image: Gambar sumber asli.
            zoom_factor: Faktor pengali zoom out (misalnya 1.5x).
            prompt: Prompt deskripsi area luar.
            negative_prompt: Prompt negatif.
            seed: Seed integer.

        Returns:
            Objek PIL Image hasil zoom out.
        """
        w, h = image.size
        pad_x = int((w * (zoom_factor - 1.0)) / 2)
        pad_y = int((h * (zoom_factor - 1.0)) / 2)
        padding = (pad_x, pad_y, pad_x, pad_y)

        logger.info("Executing progressive zoom_out (factor: %.2f, padding: %s)", zoom_factor, padding)
        return self.outpaint(
            image=image,
            padding=padding,
            prompt=prompt,
            negative_prompt=negative_prompt,
            seed=seed,
        )
