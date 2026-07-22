"""Suite pengujian unit Tahap 2 untuk engine Diffusers, Inpainting, Outpainting, dan Scheduler."""

import unittest
from unittest.mock import MagicMock, patch
from PIL import Image

from engine.generator import ImageGenerator
from engine.inpaint import InpaintPipeline
from engine.loader import ModelLoader
from engine.outpaint import OutpaintPipeline
from engine.scheduler import SchedulerManager
from services.generation_service import GenerationService


def create_dummy_diffusers_pipeline(*args, **kwargs):
    """Creates a mock Diffusers pipeline instance returning PIL images matching input size."""
    mock_pipe = MagicMock()
    mock_pipe.to.return_value = mock_pipe
    mock_pipe.enable_attention_slicing = MagicMock()
    mock_pipe.enable_vae_slicing = MagicMock()

    def dummy_call(*c_args, **c_kwargs):
        if "image" in c_kwargs and hasattr(c_kwargs["image"], "size"):
            target_size = c_kwargs["image"].size
        elif "width" in c_kwargs and "height" in c_kwargs:
            target_size = (c_kwargs["width"], c_kwargs["height"])
        else:
            target_size = (512, 512)
        dummy_image = Image.new("RGB", target_size, color=(50, 100, 150))
        return type("DiffusersOutput", (), {"images": [dummy_image]})()

    mock_pipe.side_effect = dummy_call
    mock_pipe.scheduler = MagicMock()
    return mock_pipe


class TestStage2Engine(unittest.TestCase):
    """Pengujian komprehensif untuk fitur-fitur Tahap 2 CanvasGen."""

    def setUp(self):
        """Menyiapkan instance komponen layanan dan engine."""
        ModelLoader._instance = None  # Reset singleton for clean test isolation
        self.loader = ModelLoader()
        self.generator = ImageGenerator(loader=self.loader)
        self.scheduler_manager = SchedulerManager()
        self.inpaint_pipeline = InpaintPipeline(loader=self.loader)
        self.outpaint_pipeline = OutpaintPipeline(inpaint_pipeline=self.inpaint_pipeline)
        self.service = GenerationService()

    def test_loader_device_resolution(self):
        """Memeriksa penanganan resolusi perangkat dan presisi pada ModelLoader."""
        self.loader.pipeline = create_dummy_diffusers_pipeline()
        self.loader.precision = "fp16"
        loader_info = self.loader.get_info()
        self.assertTrue(loader_info["is_loaded"])
        self.assertEqual(loader_info["precision"], "fp16")

    @patch("engine.loader.ModelLoader.load_pipeline", side_effect=create_dummy_diffusers_pipeline)
    def test_generator_single_and_batch(self, mock_load):
        """Memeriksa generasi tunggal dan generasi batch pada ImageGenerator."""
        img = self.generator.generate(prompt="Prompt pengujian", seed=100)
        self.assertIsInstance(img, Image.Image)

        batch = self.generator.generate_batch(prompt="Prompt batch", batch_size=3, base_seed=200)
        self.assertEqual(len(batch), 3)
        for b_img in batch:
            self.assertIsInstance(b_img, Image.Image)

    @patch("engine.loader.ModelLoader.load_pipeline", side_effect=create_dummy_diffusers_pipeline)
    def test_scheduler_swapping(self, mock_load):
        """Memeriksa pergantian seluruh scheduler noise yang didukung."""
        self.loader.pipeline = create_dummy_diffusers_pipeline()
        schedulers = self.scheduler_manager.list_available_schedulers()
        self.assertIn("DPMSolverMultistep", schedulers)
        self.assertIn("EulerDiscrete", schedulers)

        for s_name in schedulers[:4]:
            updated_pipe = self.scheduler_manager.set_scheduler(self.loader.pipeline, s_name)
            self.assertEqual(self.scheduler_manager.current_scheduler_name, s_name)

    @patch("engine.loader.ModelLoader.load_inpaint_pipeline", side_effect=create_dummy_diffusers_pipeline)
    def test_inpaint_execution(self, mock_load):
        """Memeriksa eksekusi inpainting dengan validasi ukuran gambar dan mask."""
        base_img = Image.new("RGB", (256, 256), color="blue")
        mask_img = Image.new("L", (128, 128), color=255)

        result = self.inpaint_pipeline.inpaint(
            image=base_img,
            mask_image=mask_img,
            prompt="Ganti area masker dengan bunga",
            seed=42,
        )
        self.assertIsInstance(result, Image.Image)
        self.assertEqual(result.size, (256, 256))

    @patch("engine.loader.ModelLoader.load_inpaint_pipeline", side_effect=create_dummy_diffusers_pipeline)
    def test_outpaint_execution(self, mock_load):
        """Memeriksa ekspansi kanvas outpainting dan pembuatan mask biner."""
        base_img = Image.new("RGB", (200, 200), color="red")
        padding = (50, 50, 50, 50)  # L, T, R, B

        canvas, mask = self.outpaint_pipeline.prepare_outpaint_canvas(base_img, padding)
        self.assertEqual(canvas.size, (300, 300))
        self.assertEqual(mask.size, (300, 300))

        out_result = self.outpaint_pipeline.outpaint(
            image=base_img,
            padding=padding,
            prompt="Perluas lanskap pemandangan",
            seed=77,
        )
        self.assertIsInstance(out_result, Image.Image)

    @patch("engine.loader.ModelLoader.load_inpaint_pipeline", side_effect=create_dummy_diffusers_pipeline)
    def test_service_inpaint_and_outpaint_facade(self, mock_load):
        """Memeriksa API facade GenerationService untuk inpainting dan outpainting."""
        base_img = Image.new("RGB", (100, 100), color="yellow")
        mask_img = Image.new("L", (100, 100), color=255)

        inp_img, inp_path = self.service.inpaint_image(
            image=base_img,
            mask_image=mask_img,
            prompt="Layanan inpaint test",
            save_output=False,
        )
        self.assertIsInstance(inp_img, Image.Image)
        self.assertIsNone(inp_path)

        out_img, out_path = self.service.outpaint_image(
            image=base_img,
            padding=(20, 20, 20, 20),
            prompt="Layanan outpaint test",
            save_output=False,
        )
        self.assertIsInstance(out_img, Image.Image)
        self.assertIsNone(out_path)


if __name__ == "__main__":
    unittest.main()
