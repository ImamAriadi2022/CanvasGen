"""Suite pengujian unit Tahap 2 untuk engine Diffusers, Inpainting, Outpainting, dan Scheduler."""

import unittest
from PIL import Image

from engine.generator import ImageGenerator
from engine.inpaint import InpaintPipeline
from engine.loader import ModelLoader
from engine.outpaint import OutpaintPipeline
from engine.scheduler import SchedulerManager
from services.generation_service import GenerationService


class TestStage2Engine(unittest.TestCase):
    """Pengujian komprehensif untuk fitur-fitur Tahap 2 CanvasGen."""

    def setUp(self):
        """Menyiapkan instance komponen layanan dan engine."""
        self.loader = ModelLoader()
        self.generator = ImageGenerator(loader=self.loader)
        self.scheduler_manager = SchedulerManager()
        self.inpaint_pipeline = InpaintPipeline(loader=self.loader)
        self.outpaint_pipeline = OutpaintPipeline(inpaint_pipeline=self.inpaint_pipeline)
        self.service = GenerationService()

    def test_loader_device_resolution(self):
        """Memeriksa penanganan resolusi perangkat dan presisi pada ModelLoader."""
        info = self.loader.load_pipeline(precision="fp16")
        self.assertIsNotNone(info)
        loader_info = self.loader.get_info()
        self.assertTrue(loader_info["is_loaded"])
        self.assertEqual(loader_info["precision"], "fp16")

    def test_generator_single_and_batch(self):
        """Memeriksa generasi tunggal dan generasi batch pada ImageGenerator."""
        img = self.generator.generate(prompt="Prompt pengujian", seed=100)
        self.assertIsInstance(img, Image.Image)

        batch = self.generator.generate_batch(prompt="Prompt batch", batch_size=3, base_seed=200)
        self.assertEqual(len(batch), 3)
        for b_img in batch:
            self.assertIsInstance(b_img, Image.Image)

    def test_scheduler_swapping(self):
        """Memeriksa pergantian seluruh scheduler noise yang didukung."""
        schedulers = self.scheduler_manager.list_available_schedulers()
        self.assertIn("DPMSolverMultistep", schedulers)
        self.assertIn("EulerDiscrete", schedulers)

        for s_name in schedulers[:4]:
            updated_pipe = self.scheduler_manager.set_scheduler(self.loader.pipeline, s_name)
            self.assertEqual(self.scheduler_manager.current_scheduler_name, s_name)

        comparison = self.scheduler_manager.compare_schedulers(
            self.loader.pipeline, prompt="Pengujian komparasi"
        )
        self.assertGreater(len(comparison), 0)

    def test_inpaint_execution(self):
        """Memeriksa eksekusi inpainting dengan validasi ukuran gambar dan mask."""
        base_img = Image.new("RGB", (256, 256), color="blue")
        mask_img = Image.new("L", (128, 128), color=255)  # sengaja beda ukuran untuk menguji resize

        result = self.inpaint_pipeline.inpaint(
            image=base_img,
            mask_image=mask_img,
            prompt="Ganti area masker dengan bunga",
            seed=42,
        )
        self.assertIsInstance(result, Image.Image)
        self.assertEqual(result.size, (256, 256))

    def test_outpaint_execution(self):
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

    def test_service_inpaint_and_outpaint_facade(self):
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
