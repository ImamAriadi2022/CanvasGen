"""Scheduler management module for CanvasGen.

Handles diffusers noise scheduler selection, configuration swapping,
and multi-scheduler comparison workflows.
"""

from typing import Any, Dict, List, Optional
from utils.logger import get_logger

logger = get_logger("CanvasGen.Engine.Scheduler")


class SchedulerManager:
    """Manages noise schedulers and provides comparative scheduling utilities."""

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
        """Initializes the SchedulerManager with default scheduler state."""
        self.current_scheduler_name: str = "DPMSolverMultistep"

    def list_available_schedulers(self) -> List[str]:
        """Returns a list of all supported noise scheduler names.

        Returns:
            List of scheduler identifier strings.
        """
        return list(self.SUPPORTED_SCHEDULERS.keys())

    def set_scheduler(self, pipeline: Any, scheduler_name: str) -> Any:
        """Configures the pipeline to use the specified noise scheduler.

        Args:
            pipeline: Active diffusers pipeline instance.
            scheduler_name: Key from SUPPORTED_SCHEDULERS mapping.

        Returns:
            Updated pipeline instance.
        """
        if scheduler_name not in self.SUPPORTED_SCHEDULERS:
            raise ValueError(
                f"Unsupported scheduler '{scheduler_name}'. "
                f"Choose from: {self.list_available_schedulers()}"
            )

        logger.info("Setting pipeline scheduler to: %s", scheduler_name)

        # TODO (Stage 2): Swap scheduler on diffusers pipeline:
        # scheduler_class = getattr(diffusers, self.SUPPORTED_SCHEDULERS[scheduler_name])
        # pipeline.scheduler = scheduler_class.from_config(pipeline.scheduler.config)

        self.current_scheduler_name = scheduler_name
        return pipeline

    def compare_schedulers(
        self,
        pipeline: Any,
        prompt: str,
        scheduler_names: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Executes test generation across multiple schedulers for quality comparison.

        Args:
            pipeline: Active diffusers pipeline instance.
            prompt: Text prompt to generate image samples for.
            scheduler_names: Optional list of schedulers to compare.

        Returns:
            Dictionary mapping scheduler names to generated result placeholders.
        """
        targets = scheduler_names or self.list_available_schedulers()[:3]
        logger.info("Executing scheduler comparison across: %s", targets)

        results: Dict[str, Any] = {}
        for s_name in targets:
            # TODO (Stage 2): Apply scheduler to pipeline and run image synthesis
            results[s_name] = f"ComparisonSample[{s_name}]"

        return results
