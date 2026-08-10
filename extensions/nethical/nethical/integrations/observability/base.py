"""Base classes for observability integrations.

This module provides abstract interfaces for ML observability platforms
to integrate with Nethical governance.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class TraceSpan:
    """Represents a trace span with governance data."""

    trace_id: str
    span_id: str
    parent_span_id: str | None
    name: str
    start_time: datetime
    end_time: datetime | None
    attributes: dict[str, Any]
    governance_result: dict[str, Any] | None = None


@dataclass
class GovernanceMetrics:
    """Aggregated governance metrics for observability."""

    total_evaluations: int
    allowed_count: int
    blocked_count: int
    restricted_count: int
    average_risk_score: float
    pii_detections: int
    latency_p50_ms: float
    latency_p99_ms: float
    timestamp: datetime = field(default_factory=datetime.utcnow)


class ObservabilityProvider(ABC):
    """Base class for observability integrations."""

    @abstractmethod
    def log_trace(self, span: TraceSpan) -> None:
        """Log a trace span with governance data.
        
        Args:
            span: TraceSpan object containing trace information
        """  # noqa: W293
        pass

    @abstractmethod
    def log_governance_event(
        self,
        action: str,
        decision: str,
        risk_score: float,
        metadata: dict[str, Any]
    ) -> None:
        """Log a governance evaluation event.
        
        Args:
            action: The action being evaluated
            decision: Governance decision (ALLOW, BLOCK, RESTRICT)
            risk_score: Risk score (0.0-1.0)
            metadata: Additional event metadata
        """  # noqa: W293
        pass

    @abstractmethod
    def log_metrics(self, metrics: GovernanceMetrics) -> None:
        """Log aggregated governance metrics.
        
        Args:
            metrics: GovernanceMetrics object with aggregated data
        """  # noqa: W293
        pass

    @abstractmethod
    def create_dashboard(self, name: str) -> str:
        """Create a governance dashboard.
        
        Args:
            name: Dashboard name
            
        Returns:
            URL or ID of created dashboard
        """  # noqa: W293
        pass

    def flush(self) -> None:  # noqa: B027
        """Flush any buffered events (optional)."""
        pass

    def close(self) -> None:  # noqa: B027
        """Close connections and cleanup (optional)."""
        pass
