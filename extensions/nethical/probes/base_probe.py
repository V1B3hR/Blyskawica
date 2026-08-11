"""
Base Probe Infrastructure

Provides abstract base classes and common functionality for all runtime probes.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ProbeStatus(Enum):
    """Status of a probe check"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class ProbeResult:
    """Result from a probe check"""
    probe_name: str
    status: ProbeStatus
    timestamp: datetime
    message: str
    metrics: dict[str, Any] = field(default_factory=dict)
    details: dict[str, Any] | None = None
    violations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "probe_name": self.probe_name,
            "status": self.status.value,
            "timestamp": self.timestamp.isoformat(),
            "message": self.message,
            "metrics": self.metrics,
            "details": self.details or {},
            "violations": self.violations,
        }


class BaseProbe(ABC):
    """
    Abstract base class for all runtime probes.
    
    Probes monitor specific invariants, governance properties, or performance
    metrics in production environments. They provide continuous validation
    that the system operates according to its formal specifications.
    """  # noqa: W293

    def __init__(
        self,
        name: str,
        check_interval_seconds: int = 60,
        alert_threshold: int | None = None,
    ):
        """
        Initialize base probe.
        
        Args:
            name: Unique identifier for this probe
            check_interval_seconds: How often to run checks
            alert_threshold: Number of consecutive failures before alerting
        """  # noqa: W293
        self.name = name
        self.check_interval_seconds = check_interval_seconds
        self.alert_threshold = alert_threshold or 3
        self._consecutive_failures = 0
        self._last_check_time: datetime | None = None
        self._check_history: list[ProbeResult] = []
        self._max_history_size = 1000

    @abstractmethod
    def check(self) -> ProbeResult:
        """
        Execute probe check.
        
        Returns:
            ProbeResult containing check status and metrics
        """  # noqa: W293
        pass

    def run(self) -> ProbeResult:
        """
        Run probe check with error handling and history tracking.
        
        Returns:
            ProbeResult from the check
        """  # noqa: W293
        try:
            result = self.check()
            self._last_check_time = result.timestamp

            # Track consecutive failures for alerting
            if result.status == ProbeStatus.CRITICAL:
                self._consecutive_failures += 1
            else:
                self._consecutive_failures = 0

            # Add to history
            self._check_history.append(result)
            if len(self._check_history) > self._max_history_size:
                self._check_history.pop(0)

            return result

        except Exception as e:
            # Handle unexpected errors
            result = ProbeResult(
                probe_name=self.name,
                status=ProbeStatus.UNKNOWN,
                timestamp=datetime.utcnow(),
                message=f"Probe check failed with error: {str(e)}",
                details={"error_type": type(e).__name__},
            )
            self._check_history.append(result)
            return result

    def should_alert(self) -> bool:
        """Check if probe should trigger an alert"""
        return self._consecutive_failures >= self.alert_threshold

    def get_history(self, limit: int | None = None) -> list[ProbeResult]:
        """
        Get check history.
        
        Args:
            limit: Maximum number of results to return (most recent first)
        
        Returns:
            List of ProbeResults
        """  # noqa: W293
        history = list(reversed(self._check_history))
        if limit:
            return history[:limit]
        return history

    def get_metrics(self) -> dict[str, Any]:
        """
        Get aggregated metrics from probe history.
        
        Returns:
            Dictionary of computed metrics
        """  # noqa: W293
        if not self._check_history:
            return {}

        total = len(self._check_history)
        healthy = sum(1 for r in self._check_history if r.status == ProbeStatus.HEALTHY)
        warning = sum(1 for r in self._check_history if r.status == ProbeStatus.WARNING)
        critical = sum(1 for r in self._check_history if r.status == ProbeStatus.CRITICAL)

        return {
            "total_checks": total,
            "healthy_count": healthy,
            "warning_count": warning,
            "critical_count": critical,
            "health_rate": healthy / total if total > 0 else 0,
            "consecutive_failures": self._consecutive_failures,
            "last_check_time": self._last_check_time.isoformat() if self._last_check_time else None,
        }

    def reset(self):
        """Reset probe state"""
        self._consecutive_failures = 0
        self._check_history.clear()
        self._last_check_time = None
