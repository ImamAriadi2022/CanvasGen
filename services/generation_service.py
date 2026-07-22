"""High-level generation service encapsulating engine components for UI/API interaction."""

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
    """Unified service layer encapsulating all CanvasGen AI generation operations."""

    def __init__(self, settings: Optional[Settings] = None) -> None:
        """Initializes GenerationService components.

        Args:
            settings: Settings instance. Defaults to global settings if omitted.
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
        """Loads target model pipeline into memory.

        Returns:
            Dictionary containing loader info status.
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
        """Executes text-to-image synthesis and optionally persists output artifact.

        Returns:
            Tuple of (generated_PIL_Image, saved_filepath_string).
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
            logger.info("Saved text-to-image artifact to: %s", saved_path)

        return img, saved_path

    def generate_batch_images(
        self,
        prompt: str,
        batch_size: int = 4,
        negative_prompt: str = "",
        save_outputs: bool = True,
    ) -> Tuple[List[Image.Image], List[str]]:
        """Executes batch image generation.

        Returns:
            Tuple of (list_of_images, list_of_saved_filepaths).
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

    def cleanup_resources(self) -> Dict[str, Any]:
        """Unloads pipelines and flushes system VRAM.

        Returns:
            Updated VRAM diagnostic stats dictionary.
        """
        self.loader.unload_pipeline()
        flush_vram()
        return get_vram_usage()
