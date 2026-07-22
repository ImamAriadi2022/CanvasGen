"""Outpainting engine pipeline module for CanvasGen.

Handles directional canvas expansion, border padding, mask synthesis,
and outpainting pipeline execution.
"""

from typing import Any, Dict, Optional, Tuple
from PIL import Image, ImageOps

from config.settings import Settings, get_settings
from engine.inpaint import InpaintPipeline
from utils.logger import get_logger
from utils.seed import set_seed

logger = get_logger("CanvasGen.Engine.Outpaint")


class OutpaintPipeline:
    """Outpainting processor expanding image borders in specific directions."""

    def __init__(
        self,
        inpaint_pipeline: Optional[InpaintPipeline] = None,
        settings: Optional[Settings] = None,
    ) -> None:
        """Initializes OutpaintPipeline with an InpaintPipeline and settings.

        Args:
            inpaint_pipeline: InpaintPipeline instance for performing seamless diffusion generation.
            settings: Settings instance. If None, default settings are used.
        """
        self.settings = settings or get_settings()
        self.inpaint_engine = inpaint_pipeline or InpaintPipeline(settings=self.settings)

    def prepare_outpaint_canvas(
        self,
        image: Image.Image,
        padding: Tuple[int, int, int, int],  # (left, top, right, bottom)
    ) -> Tuple[Image.Image, Image.Image]:
        """Expands canvas dimensions and creates corresponding binary outpainting mask.

        Args:
            image: Original PIL Image.
            padding: Padding tuple in pixels (left, top, right, bottom).

        Returns:
            Tuple of (expanded_image, generated_mask).
        """
        left, top, right, bottom = padding

        # Expand original image with black border padding
        expanded_image = ImageOps.expand(
            image,
            border=(left, top, right, bottom),
            fill=(0, 0, 0),
        )

        # Create mask: White (255) for new padded areas, Black (0) for original content
        w, h = expanded_image.size
        mask = Image.new("L", (w, h), 255)

        # Paste black rectangle over original image coordinates
        orig_w, orig_h = image.size
        black_orig = Image.new("L", (orig_w, orig_h), 0)
        mask.paste(black_orig, (left, top))

        logger.info(
            "Canvas expanded from %s to %s with padding (L:%d, T:%d, R:%d, B:%d)",
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
        """Outpaints image borders based on directional pixel padding.

        Args:
            image: Original source PIL Image.
            padding: Pixel expansion tuple (left, top, right, bottom).
            prompt: Text prompt describing scene extensions.
            negative_prompt: Negative guidance prompt.
            num_inference_steps: Denoising sampling steps.
            guidance_scale: CFG scale multiplier.
            seed: Random seed integer.

        Returns:
            Outpainted PIL Image object.
        """
        canvas, mask = self.prepare_outpaint_canvas(image, padding)

        active_seed = set_seed(seed)
        logger.info("Executing Outpaint generation for expanded canvas...")

        # Perform inpainting over the expanded canvas and generated mask
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
