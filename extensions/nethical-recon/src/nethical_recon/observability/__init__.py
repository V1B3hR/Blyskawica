"""
Observability module for Nethical Recon.

Provides structured logging, metrics collection, and tracing capabilities.
"""

from .logging import configure_logging, get_logger
from .metrics import (
    get_metrics,
    increment_counter,
    metrics_registry,
    observe_value,
    track_duration,
    track_errors,
    track_findings,
    track_tool_run,
)

__all__ = [
    # Logging
    "configure_logging",
    "get_logger",
    # Metrics
    "get_metrics",
    "metrics_registry",
    "track_duration",
    "track_tool_run",
    "track_findings",
    "track_errors",
    "increment_counter",
    "observe_value",
]
