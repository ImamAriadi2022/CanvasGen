"""Image Generator Engine for CanvasGen supporting Text-to-Image and Batch synthesis via Diffusers."""

from typing import Any, Dict, List, Optional
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
    """Orchestrates real Stable Diffusion image generation for simple, advanced, and batch requests."""

    def __init__(
        self,
        loader: Optional[ModelLoader] = None,
        settings: Optional[Settings] = None,
    ) -> None:
        """Initializes ImageGenerator with ModelLoader singleton and Settings."""
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
        """Generates a single image from text prompt using StableDiffusionPipeline.

        Raises:
            RuntimeError: If execution fails or pipeline is unavailable.
        """
        w = width or self.settings.default_width
        h = height or self.settings.default_height
        steps = num_inference_steps or self.settings.default_num_inference_steps
        cfg = guidance_scale or self.settings.default_guidance_scale
        active_seed = set_seed(seed)

        logger.info(
            "Generating image [Prompt: '%s' | Size: %dx%d | Steps: %d | CFG: %.1f | Seed: %d]",
            prompt,
            w,
            h,
            steps,
            cfg,
            active_seed,
        )

        pipe = self.loader.load_pipeline()

        try:
            if hasattr(pipe, "__call__") and TORCH_AVAILABLE:
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
                logger.info("Stable Diffusion Text-to-Image inference successful.")
                return output.images[0]
            elif hasattr(pipe, "__call__"):
                output = pipe(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    width=w,
                    height=h,
                    num_inference_steps=steps,
                    guidance_scale=cfg,
                )
                logger.info("Stable Diffusion Text-to-Image inference successful.")
                return output.images[0]
            else:
                raise RuntimeError("Stable Diffusion pipeline is not callable.")
        except Exception as e:
            logger.error("Stable Diffusion generation failed: %s", e)
            raise e

    def generate_simple_image(
        self,
        prompt: str,
        negative_prompt: str = "",
        seed: Optional[int] = None,
    ) -> Image.Image:
        """Required Dicoding simple image generation function returning PIL.Image."""
        return self.generate(prompt=prompt, negative_prompt=negative_prompt, seed=seed)

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
        """Required Dicoding advanced image generation function returning List[PIL.Image]."""
        if scheduler_name and self.loader.pipeline:
            from engine.scheduler import SchedulerManager
            SchedulerManager().set_scheduler(self.loader.pipeline, scheduler_name)

        if num_images == 1:
            img = self.generate(
                prompt=prompt,
                negative_prompt=negative_prompt,
                guidance_scale=guidance_scale,
                num_inference_steps=num_inference_steps,
                seed=seed,
            )
            return [img]
        else:
            return self.generate_batch(
                prompt=prompt,
                batch_size=num_images,
                negative_prompt=negative_prompt,
                guidance_scale=guidance_scale,
                num_inference_steps=num_inference_steps,
                base_seed=seed,
            )

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
        """Generates a batch of images from text prompt with sequential seeds."""
        logger.info("Executing batch generation with size: %d", batch_size)
        start_seed = base_seed if (base_seed is not None and base_seed != -1) else set_seed()

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
