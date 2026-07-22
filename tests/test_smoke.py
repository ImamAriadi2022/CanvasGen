"""Smoke test suite for CanvasGen core functionality using real Diffusers integration with mock pretrained loaders."""

import unittest
from unittest.mock import MagicMock, patch
from PIL import Image

from config.settings import get_settings
from engine.generator import ImageGenerator
from engine.loader import ModelLoader
from engine.outpaint import OutpaintPipeline
from engine.scheduler import SchedulerManager
from services.generation_service import GenerationService
from utils.image import create_image_grid, image_to_base64, resize_image
from utils.memory import flush_vram, get_ram_usage, get_vram_usage
from utils.seed import set_seed


def create_dummy_diffusers_pipeline(*args, **kwargs):
    """Creates a mock Diffusers pipeline instance returning PIL images on call."""
    mock_pipe = MagicMock()
    mock_pipe.to.return_value = mock_pipe
    mock_pipe.enable_attention_slicing = MagicMock()
    mock_pipe.enable_vae_slicing = MagicMock()

    dummy_image = Image.new("RGB", (512, 512), color=(50, 100, 150))
    output_obj = type("DiffusersOutput", (), {"images": [dummy_image]})()
    mock_pipe.side_effect = lambda *a, **k: output_obj
    mock_pipe.return_value = output_obj
    mock_pipe.scheduler = MagicMock()
    return mock_pipe


class TestSmoke(unittest.TestCase):
    """Smoke tests for CanvasGen engine, utilities, and configuration."""

    def test_settings_defaults(self):
        """Smoke test settings default parameter bounds."""
        settings = get_settings()
        self.assertEqual(settings.default_width, 512)
        self.assertEqual(settings.default_height, 512)
        self.assertEqual(settings.default_num_inference_steps, 30)
        self.assertEqual(settings.default_guidance_scale, 7.5)

    def test_seed_reproducibility(self):
        """Smoke test deterministic seed setter."""
        seed1 = set_seed(12345)
        self.assertEqual(seed1, 12345)

    def test_memory_diagnostics(self):
        """Smoke test RAM and VRAM diagnostic functions."""
        ram = get_ram_usage()
        self.assertGreaterEqual(ram["total_mb"], 0)

        vram = get_vram_usage()
        self.assertIn("cuda_available", vram)

        flush_vram()

    def test_image_utils(self):
        """Smoke test image utilities processing."""
        img1 = Image.new("RGB", (100, 100), color="red")
        img2 = Image.new("RGB", (100, 100), color="blue")

        resized = resize_image(img1, (50, 50))
        self.assertEqual(resized.size, (50, 50))

        grid = create_image_grid([img1, img2], rows=1, cols=2)
        self.assertEqual(grid.size, (200, 100))

        b64 = image_to_base64(img1)
        self.assertTrue(b64.startswith("data:image/png;base64,"))

    @patch("engine.loader.ModelLoader.load_pipeline", side_effect=create_dummy_diffusers_pipeline)
    def test_engine_skeleton_flow(self, mock_load):
        """Smoke test engine generation flow."""
        loader = ModelLoader()
        pipe = loader.load_pipeline()
        self.assertIsNotNone(pipe)

        generator = ImageGenerator(loader=loader)
        img = generator.generate(prompt="Test prompt", seed=42)
        self.assertIsInstance(img, Image.Image)

        scheduler = SchedulerManager()
        schedulers = scheduler.list_available_schedulers()
        self.assertGreater(len(schedulers), 0)

    def test_outpaint_canvas_preparation(self):
        """Smoke test outpaint canvas expansion math and mask creation."""
        outpaint = OutpaintPipeline()
        base_img = Image.new("RGB", (200, 200), color="green")
        canvas, mask = outpaint.prepare_outpaint_canvas(base_img, padding=(50, 50, 50, 50))

        self.assertEqual(canvas.size, (300, 300))
        self.assertEqual(mask.size, (300, 300))
        self.assertEqual(mask.mode, "L")

    @patch("engine.loader.ModelLoader.load_pipeline", side_effect=create_dummy_diffusers_pipeline)
    def test_generation_service_end_to_end(self, mock_load):
        """Smoke test generation service API execution."""
        service = GenerationService()
        img, path = service.generate_text_to_image(
            prompt="A vibrant futuristic city", save_output=False
        )
        self.assertIsInstance(img, Image.Image)
        self.assertIsNone(path)


if __name__ == "__main__":
    unittest.main()
