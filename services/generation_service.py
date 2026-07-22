"""High-level Generation Service facade integrating engine pipelines with UI and API."""

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
    """Unified service facade wrapping all CanvasGen AI generation operations."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        """Initializes GenerationService components."""
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
        """Loads and caches the model pipeline."""
        self.loader.load_pipeline(model_id=model_id, device=device, precision=precision)
        return self.loader.get_info()

    def generate_simple_image(
        self,
        prompt: str,
        negative_prompt: str = "",
        seed: Optional[int] = None,
    ) -> Image.Image:
        """Required Dicoding simple image generation helper."""
        return self.generator.generate_simple_image(
            prompt=prompt, negative_prompt=negative_prompt, seed=seed
        )

    def generate_advanced_image(
        self,
        prompt: str,
        negative_prompt: str = "",
        guidance_scale: Optional[float] = None,
        num_inference_steps: Optional[int] = None,
        scheduler_name: Optional[str] = None,
        seed: Optional[int] = None,
        num_images: int = 1,
    ) -> List[Image.Image]:
        """Required Dicoding advanced image generation helper."""
        return self.generator.generate_advanced_image(
            prompt=prompt,
            negative_prompt=negative_prompt,
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps,
            scheduler_name=scheduler_name,
            seed=seed,
            num_images=num_images,
        )

    def generate_image(
        self,
        prompt: str,
        negative_prompt: str = "",
        scheduler_name: Optional[str] = None,
        guidance_scale: Optional[float] = None,
        num_inference_steps: Optional[int] = None,
        seed: Optional[int] = None,
    ) -> Image.Image:
        """Generates a single image and returns PIL.Image directly."""
        if scheduler_name and self.loader.pipeline:
            self.scheduler_manager.set_scheduler(self.loader.pipeline, scheduler_name)

        return self.generator.generate(
            prompt=prompt,
            negative_prompt=negative_prompt,
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps,
            seed=seed,
        )

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
        """Mengeksekusi sintesis text-to-image dan menyimpan artefak gambar."""
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
        guidance_scale: Optional[float] = None,
        num_inference_steps: Optional[int] = None,
        base_seed: Optional[int] = None,
        save_outputs: bool = True,
    ) -> Tuple[List[Image.Image], List[str]]:
        """Generates a batch of images and saves outputs."""
        images = self.generator.generate_batch(
            prompt=prompt,
            batch_size=batch_size,
            negative_prompt=negative_prompt,
            guidance_scale=guidance_scale,
            num_inference_steps=num_inference_steps,
            base_seed=base_seed,
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
        """Executes inpainting on masked image region."""
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
        """Executes outpainting to expand canvas."""
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

        return img, saved_path

    def zoom_out_image(
        self,
        image: Image.Image,
        zoom_factor: float = 1.5,
        prompt: str = "",
        negative_prompt: str = "",
        seed: Optional[int] = None,
        save_output: bool = True,
    ) -> Tuple[Image.Image, Optional[str]]:
        """Executes progressive zoom out outpainting."""
        img = self.outpaint_pipeline.zoom_out(
            image=image,
            zoom_factor=zoom_factor,
            prompt=prompt,
            negative_prompt=negative_prompt,
            seed=seed,
        )

        saved_path: Optional[str] = None
        if save_output:
            out_file = generate_output_path(
                output_dir=self.settings.output_dir, prefix="zoom_out"
            )
            img.save(out_file)
            saved_path = str(out_file)

        return img, saved_path

    def cleanup_resources(self) -> Dict[str, Any]:
        """Unloads pipelines and flushes VRAM/RAM."""
        self.loader.unload_pipeline()
        flush_vram()
        return get_vram_usage()
