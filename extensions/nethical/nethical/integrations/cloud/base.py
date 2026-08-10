"""Base class for cloud ML platform integrations."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class RunStatus(Enum):
    """ML run status."""
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    KILLED = "killed"
    UNKNOWN = "unknown"


@dataclass
class ExperimentRun:
    """ML experiment run metadata."""
    run_id: str
    experiment_name: str
    parameters: dict[str, Any]
    metrics: dict[str, float]
    artifacts: list[str] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: datetime | None = None
    status: RunStatus = RunStatus.RUNNING
    tags: dict[str, str] = field(default_factory=dict)
    error_message: str | None = None


class CloudMLProvider(ABC):
    """Base class for cloud ML platform integrations."""

    @abstractmethod
    def start_run(self, experiment_name: str, run_name: str | None = None) -> str:
        """Start a new experiment run.
        
        Args:
            experiment_name: Name of the experiment
            run_name: Optional run name
            
        Returns:
            Run ID
        """  # noqa: W293
        pass

    @abstractmethod
    def log_parameters(self, run_id: str, parameters: dict[str, Any]) -> None:
        """Log experiment parameters.
        
        Args:
            run_id: Run identifier
            parameters: Parameters to log
        """  # noqa: W293
        pass

    @abstractmethod
    def log_metrics(self, run_id: str, metrics: dict[str, float], step: int | None = None) -> None:
        """Log metrics for a run.
        
        Args:
            run_id: Run identifier
            metrics: Metrics to log
            step: Optional step/iteration number
        """  # noqa: W293
        pass

    @abstractmethod
    def end_run(self, run_id: str, status: str = "completed") -> None:
        """End an experiment run.
        
        Args:
            run_id: Run identifier
            status: Run status (completed, failed, etc.)
        """  # noqa: W293
        pass

    def log_artifact(self, run_id: str, artifact_path: str) -> None:  # noqa: B027
        """Log an artifact (optional).
        
        Args:
            run_id: Run identifier
            artifact_path: Path to artifact
        """  # noqa: W293
        pass

    def get_run(self, run_id: str) -> ExperimentRun | None:
        """Get run metadata (optional).
        
        Args:
            run_id: Run identifier
            
        Returns:
            ExperimentRun or None
        """  # noqa: W293
        return None
