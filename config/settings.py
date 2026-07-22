"""Centralized configuration management for CanvasGen.

Uses Pydantic BaseSettings when available, with a pure Python dataclass fallback
for environments without third-party dependencies installed.
"""

from dataclasses import dataclass, field, fields
from functools import lru_cache
import os
from pathlib import Path
from typing import Optional

try:
    from pydantic import Field
    from pydantic_settings import BaseSettings, SettingsConfigDict
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False


if PYDANTIC_AVAILABLE:

    class Settings(BaseSettings):
        """Central configuration class for CanvasGen application settings."""

        app_name: str = Field(default="CanvasGen", description="Application identifier")
        app_env: str = Field(default="development", description="Execution environment")
        debug: bool = Field(default=True, description="Enable debug logging and features")
        log_level: str = Field(default="INFO", description="Logging output detail level")

        model_id: str = Field(
            default="runwayml/stable-diffusion-v1-5",
            description="HuggingFace model repository ID or local path",
        )
        device: str = Field(default="cuda", description="Target hardware device")
        precision: str = Field(default="fp16", description="Model weight precision")
        safety_checker: bool = Field(default=True, description="Enable safety checker filter")

        hf_token: Optional[str] = Field(default=None, description="HuggingFace user access token")

        base_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent)
        output_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent / "outputs")
        assets_dir: Path = Field(default_factory=lambda: Path(__file__).resolve().parent.parent / "assets")

        default_width: int = Field(default=512, ge=64, le=2048, description="Default image width")
        default_height: int = Field(default=512, ge=64, le=2048, description="Default image height")
        default_num_inference_steps: int = Field(default=30, ge=1, le=150, description="Default sampling steps")
        default_guidance_scale: float = Field(default=7.5, ge=1.0, le=30.0, description="Default CFG scale")

        model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            extra="ignore",
            case_sensitive=False,
        )

else:

    @dataclass
    class Settings:
        """Fallback dataclass configuration class for pure Python environments."""

        app_name: str = "CanvasGen"
        app_env: str = "development"
        debug: bool = True
        log_level: str = "INFO"

        model_id: str = "runwayml/stable-diffusion-v1-5"
        device: str = "cuda"
        precision: str = "fp16"
        safety_checker: bool = True

        hf_token: Optional[str] = None

        base_dir: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent)
        output_dir: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent / "outputs")
        assets_dir: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent / "assets")

        default_width: int = 512
        default_height: int = 512
        default_num_inference_steps: int = 30
        default_guidance_scale: float = 7.5

        def model_dump(self, mode: str = "python") -> dict:
            """Serializes settings to a dictionary format matching pydantic model_dump."""
            result = {}
            for f in fields(self):
                val = getattr(self, f.name)
                if isinstance(val, Path):
                    result[f.name] = str(val)
                else:
                    result[f.name] = val
            return result


@lru_cache()
def get_settings() -> Settings:
    """Returns cached Settings instance.

    Returns:
        Singleton Settings object initialized from environment variables or defaults.
    """
    return Settings()
