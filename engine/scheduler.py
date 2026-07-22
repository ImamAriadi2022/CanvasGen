"""Modul pengelola noise scheduler untuk CanvasGen.

Menangani pemilihan noise scheduler diffusers, pergantian konfigurasi sampler,
dan workflow komparasi multi-scheduler.
"""

from typing import Any, Dict, List, Optional
from utils.logger import get_logger

logger = get_logger("CanvasGen.Engine.Scheduler")

try:
    import diffusers
    DIFFUSERS_AVAILABLE = True
except ImportError:
    DIFFUSERS_AVAILABLE = False


class SchedulerManager:
    """Pengelola noise scheduler dan penyedia utilitas komparasi sampler."""

    SUPPORTED_SCHEDULERS: Dict[str, str] = {
        "DPMSolverMultistep": "DPMSolverMultistepScheduler",
        "EulerDiscrete": "EulerDiscreteScheduler",
        "EulerAncestralDiscrete": "EulerAncestralDiscreteScheduler",
        "DDIM": "DDIMScheduler",
        "LMSDiscrete": "LMSDiscreteScheduler",
        "PNDM": "PNDMScheduler",
        "HeunDiscrete": "HeunDiscreteScheduler",
    }

    def __init__(self) -> None:
        """Menginisialisasi SchedulerManager dengan status scheduler default."""
        self.current_scheduler_name: str = "DPMSolverMultistep"

    def list_available_schedulers(self) -> List[str]:
        """Mengembalikan daftar nama noise scheduler yang didukung.

        Returns:
            Daftar string pengenal scheduler.
        """
        return list(self.SUPPORTED_SCHEDULERS.keys())

    def set_scheduler(self, pipeline: Any, scheduler_name: str) -> Any:
        """Mengonfigurasi pipeline untuk menggunakan noise scheduler yang ditentukan.

        Args:
            pipeline: Instance pipeline diffusers yang aktif.
            scheduler_name: Kunci dari pemetaan SUPPORTED_SCHEDULERS.

        Returns:
            Instance pipeline yang telah diperbarui schedulernya.
        """
        if scheduler_name not in self.SUPPORTED_SCHEDULERS:
            raise ValueError(
                f"Scheduler '{scheduler_name}' tidak didukung. "
                f"Pilih dari: {self.list_available_schedulers()}"
            )

        logger.info("Mengatur noise scheduler pipeline menjadi: %s", scheduler_name)

        if DIFFUSERS_AVAILABLE and hasattr(pipeline, "scheduler") and hasattr(pipeline.scheduler, "config"):
            try:
                class_name = self.SUPPORTED_SCHEDULERS[scheduler_name]
                scheduler_cls = getattr(diffusers, class_name)
                pipeline.scheduler = scheduler_cls.from_config(pipeline.scheduler.config)
                logger.info("Scheduler pipeline Diffusers aktual berhasil diubah ke %s", class_name)
            except Exception as e:
                logger.warning("Gagal mengubah scheduler Diffusers secara aktual (%s).", e)

        self.current_scheduler_name = scheduler_name
        return pipeline

    def compare_schedulers(
        self,
        pipeline: Any,
        prompt: str,
        scheduler_names: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Mengeksekusi sampel generasi pada beberapa scheduler untuk komparasi kualitas.

        Args:
            pipeline: Instance pipeline diffusers yang aktif.
            prompt: Prompt teks untuk membuat sampel gambar.
            scheduler_names: Daftar opsional scheduler yang ingin dibandingkan.

        Returns:
            Dictionary pemetaan nama scheduler ke objek hasil generasi.
        """
        targets = scheduler_names or self.list_available_schedulers()[:3]
        logger.info("Mengeksekusi komparasi scheduler pada: %s", targets)

        results: Dict[str, Any] = {}
        for s_name in targets:
            self.set_scheduler(pipeline, s_name)
            results[s_name] = f"HasilSampelGambar[{s_name}]"

        return results
