"""Layanan generasi tingkat tinggi yang membungkus komponen engine untuk interaksi UI dan API."""

from typing import Any, Dict, List, Optional, Tuple
from PIL import Image

from config.settings import Settings, get_settings
from engine.generator import ImageGenerator
from engine.inpaint import InpaintPipeline
from engine.loader import ModelLoader
from engine.outpaint import OutpaintPipeline
from engine.scheduler import SchedulerManager
from utils.file_manager import generate_output_path
from utils.logger import get_logger
from utils.memory import flush_vram, get_vram_usage

logger = get_logger("CanvasGen.Services.Generation")


class GenerationService:
    """Fasad layanan terpadu yang membungkus seluruh operasi generasi AI CanvasGen."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        """Menginisialisasi komponen GenerationService.

        Args:
            settings: Instance Settings. Default ke settings global jika diabaikan.
        """
        self.settings = settings or get_settings()
        self.loader = ModelLoader(self.settings)
        self.generator = ImageGenerator(loader=self.loader, settings=self.settings)
        self.scheduler_manager = SchedulerManager()
        self.inpaint_pipeline = InpaintPipeline(loader=self.loader, settings=self.settings)
        self.outpaint_pipeline = OutpaintPipeline(
            inpaint_pipeline=self.inpaint_pipeline, settings=self.settings
        )

    def initialize_model(
        self,
        model_id: Optional[str] = None,
        device: Optional[str] = None,
        precision: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Memuat pipeline model target ke dalam memori.

        Returns:
            Dictionary berisi status informasi loader.
        """
        self.loader.load_pipeline(model_id=model_id, device=device, precision=precision)
        return self.loader.get_info()

    def generate_text_to_image(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: Optional[int] = None,
        height: Optional[int] = None,
        num_inference_steps: Optional[int] = None,
        guidance_scale: Optional[float] = None,
        seed: Optional[int] = None,
        save_output: bool = True,
    ) -> Tuple[Image.Image, Optional[str]]:
        """Mengeksekusi sintesis text-to-image dan secara opsional menyimpan artefak gambar.

        Returns:
            Tuple dari (gambar_PIL_hasil, string_jalur_tersimpan).
        """
        img = self.generator.generate(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            num_inference_steps=num_inference_steps,
            guidance_scale=guidance_scale,
            seed=seed,
        )

        saved_path: Optional[str] = None
        if save_output:
            out_file = generate_output_path(
                output_dir=self.settings.output_dir, prefix="txt2img"
            )
            img.save(out_file)
            saved_path = str(out_file)
            logger.info("Menyimpan artefak text-to-image ke: %s", saved_path)

        return img, saved_path

    def generate_batch_images(
        self,
        prompt: str,
        batch_size: int = 4,
        negative_prompt: str = "",
        save_outputs: bool = True,
    ) -> Tuple[List[Image.Image], List[str]]:
        """Mengeksekusi generasi gambar secara batch.

        Returns:
            Tuple dari (daftar_gambar, daftar_jalur_tersimpan).
        """
        images = self.generator.generate_batch(
            prompt=prompt,
            batch_size=batch_size,
            negative_prompt=negative_prompt,
        )

        saved_paths: List[str] = []
        if save_outputs:
            for idx, img in enumerate(images):
                out_file = generate_output_path(
                    output_dir=self.settings.output_dir, prefix=f"batch_{idx+1}"
                )
                img.save(out_file)
                saved_paths.append(str(out_file))

        return images, saved_paths

    def inpaint_image(
        self,
        image: Image.Image,
        mask_image: Image.Image,
        prompt: str,
        negative_prompt: str = "",
        seed: Optional[int] = None,
        save_output: bool = True,
    ) -> Tuple[Image.Image, Optional[str]]:
        """Mengeksekusi inpainting pada area gambar yang bermasker.

        Returns:
            Tuple dari (gambar_PIL_inpaint, string_jalur_tersimpan).
        """
        img = self.inpaint_pipeline.inpaint(
            image=image,
            mask_image=mask_image,
            prompt=prompt,
            negative_prompt=negative_prompt,
            seed=seed,
        )

        saved_path: Optional[str] = None
        if save_output:
            out_file = generate_output_path(
                output_dir=self.settings.output_dir, prefix="inpaint"
            )
            img.save(out_file)
            saved_path = str(out_file)
            logger.info("Menyimpan artefak inpaint ke: %s", saved_path)

        return img, saved_path

    def outpaint_image(
        self,
        image: Image.Image,
        padding: Tuple[int, int, int, int],
        prompt: str,
        negative_prompt: str = "",
        seed: Optional[int] = None,
        save_output: bool = True,
    ) -> Tuple[Image.Image, Optional[str]]:
        """Mengeksekusi outpainting untuk memperluas kanvas gambar.

        Returns:
            Tuple dari (gambar_PIL_outpaint, string_jalur_tersimpan).
        """
        img = self.outpaint_pipeline.outpaint(
            image=image,
            padding=padding,
            prompt=prompt,
            negative_prompt=negative_prompt,
            seed=seed,
        )

        saved_path: Optional[str] = None
        if save_output:
            out_file = generate_output_path(
                output_dir=self.settings.output_dir, prefix="outpaint"
            )
            img.save(out_file)
            saved_path = str(out_file)
            logger.info("Menyimpan artefak outpaint ke: %s", saved_path)

        return img, saved_path

    def cleanup_resources(self) -> Dict[str, Any]:
        """Melepaskan pipeline dan membersihkan VRAM sistem.

        Returns:
            Dictionary statistik diagnosa VRAM terbaru.
        """
        self.loader.unload_pipeline()
        flush_vram()
        return get_vram_usage()
