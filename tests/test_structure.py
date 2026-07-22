"""Project directory structure and file presence test suite."""

from pathlib import Path
import unittest

BASE_DIR = Path(__file__).resolve().parent.parent

REQUIRED_DIRECTORIES = [
    "config",
    "engine",
    "services",
    "utils",
    "assets",
    "outputs",
    "notebooks",
    "tests",
    "docs",
    "scripts",
    "submit",
]

REQUIRED_FILES = [
    "app.py",
    "requirements.txt",
    "README.md",
    "LICENSE",
    ".gitignore",
    ".env.example",
    "config/settings.py",
    "engine/loader.py",
    "engine/generator.py",
    "engine/scheduler.py",
    "engine/inpaint.py",
    "engine/outpaint.py",
    "services/generation_service.py",
    "utils/image.py",
    "utils/memory.py",
    "utils/seed.py",
    "utils/logger.py",
    "utils/file_manager.py",
    "scripts/setup_env.bat",
    "scripts/setup_env.sh",
    "scripts/run_app.bat",
    "scripts/run_app.sh",
    "scripts/run_tests.py",
    "tests/test_imports.py",
    "tests/test_structure.py",
    "tests/test_smoke.py",
    "tests/test_stage2_engine.py",
    "notebooks/local_demo.ipynb",
    "notebooks/colab.ipynb",
    "docs/Architecture.md",
    "docs/Development.md",
    "docs/Workflow.md",
    "docs/Submission.md",
    "submit/Pipeline_submission_BFGAI_Imam.ipynb",
    "submit/Streamlit_submission_BFGAI_Imam.ipynb",
    "submit/requirements.txt",
    "submit/README.md",
    "submit/submission_checklist.md",
]


class TestStructure(unittest.TestCase):
    """Test case verifying required project structure and file existence."""

    def test_directory_existence(self):
        """Verifies that all required project subdirectories exist."""
        for dir_name in REQUIRED_DIRECTORIES:
            dir_path = BASE_DIR / dir_name
            self.assertTrue(
                dir_path.exists() and dir_path.is_dir(),
                f"Missing directory: {dir_name}",
            )

    def test_file_existence(self):
        """Verifies that all required core files exist."""
        for file_name in REQUIRED_FILES:
            file_path = BASE_DIR / file_name
            self.assertTrue(
                file_path.exists() and file_path.is_file(),
                f"Missing file: {file_name}",
            )


if __name__ == "__main__":
    unittest.main()
