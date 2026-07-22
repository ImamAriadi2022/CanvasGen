"""Inpainting Engine for CanvasGen supporting masked diffusion synthesis."""

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
    """Inpainting pipeline manager executing StableDiffusionInpaintPipeline."""

    def __init__(
        self,
        loader: Optional[ModelLoader] = None,
        settings: Optional[Settings] = None,
    ) -> None:
        """Initializes InpaintPipeline with ModelLoader singleton and Settings."""
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
        """Replaces masked region of image using prompt and StableDiffusionInpaintPipeline.

        Raises:
            RuntimeError: If execution fails or pipeline is unavailable.
        """
        if image.size != mask_image.size:
            logger.warning(
                "Image size %s does not match mask size %s. Resizing mask.",
                image.size,
                mask_image.size,
            )
            mask_image = mask_image.resize(image.size, Image.Resampling.NEAREST)

        if image.mode != "RGB":
            image = image.convert("RGB")
        if mask_image.mode not in ["L", "RGB"]:
            mask_image = mask_image.convert("L")

        active_seed = set_seed(seed)
        steps = num_inference_steps or self.settings.default_num_inference_steps
        cfg = guidance_scale or self.settings.default_guidance_scale

        logger.info(
            "Executing Inpainting [Prompt: '%s' | Steps: %d | CFG: %.1f | Seed: %d]",
            prompt,
            steps,
            cfg,
            active_seed,
        )

        pipe = self.loader.load_inpaint_pipeline()

        try:
            if hasattr(pipe, "__call__") and TORCH_AVAILABLE:
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
                logger.info("Stable Diffusion Inpainting inference successful.")
                return output.images[0]
            elif hasattr(pipe, "__call__"):
                output = pipe(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    image=image,
                    mask_image=mask_image,
                    num_inference_steps=steps,
                    guidance_scale=cfg,
                )
                logger.info("Stable Diffusion Inpainting inference successful.")
                return output.images[0]
            else:
                raise RuntimeError("Stable Diffusion Inpaint pipeline is not callable.")
        except Exception as e:
            logger.error("Stable Diffusion Inpainting failed: %s", e)
            raise e
