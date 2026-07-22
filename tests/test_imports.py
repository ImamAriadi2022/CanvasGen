"""Import verification unit test suite for CanvasGen.

Ensures all package modules can be imported without syntax errors or missing dependencies.
"""

import unittest


class TestImports(unittest.TestCase):
    """Test case for verifying module imports across CanvasGen packages."""

    def test_import_config(self):
        """Verify importing config module symbols."""
        from config import Settings, get_settings

        settings = get_settings()
        assert isinstance(settings, Settings)
        assert settings.app_name == "CanvasGen"

    def test_import_engine(self):
        """Verify importing engine module symbols."""
        from engine import (
            ModelLoader,
            ImageGenerator,
            SchedulerManager,
            InpaintPipeline,
            OutpaintPipeline,
        )

        loader = ModelLoader()
        self.assertIsNotNone(loader)

        generator = ImageGenerator(loader=loader)
        self.assertIsNotNone(generator)

        scheduler = SchedulerManager()
        self.assertIn("DPMSolverMultistep", scheduler.list_available_schedulers())

        inpaint = InpaintPipeline(loader=loader)
        self.assertIsNotNone(inpaint)

        outpaint = OutpaintPipeline(inpaint_pipeline=inpaint)
        self.assertIsNotNone(outpaint)

    def test_import_services(self):
        """Verify importing services module symbols."""
        from services import GenerationService

        service = GenerationService()
        self.assertIsNotNone(service)

    def test_import_utils(self):
        """Verify importing utility module symbols."""
        from utils import (
            get_logger,
            resize_image,
            create_image_grid,
            image_to_base64,
            base64_to_image,
            flush_vram,
            get_vram_usage,
            get_ram_usage,
            set_seed,
            generate_random_seed,
            ensure_directory,
            generate_output_path,
        )

        logger = get_logger("TestLogger")
        self.assertIsNotNone(logger)

        seed = set_seed(42)
        self.assertEqual(seed, 42)

        ram = get_ram_usage()
        self.assertIn("total_mb", ram)


if __name__ == "__main__":
    unittest.main()
