"""
Prometheus metrics collection for Nethical Recon.

Provides metrics for:
- Tool run durations
- Finding counts per job
- Error rates
- Queue depth
- API request metrics
"""

import time
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, Generator, Optional

from prometheus_client import (
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    Summary,
    generate_latest,
)

# Create a custom registry to avoid conflicts
metrics_registry = CollectorRegistry()

# ============================================================================
# Tool Run Metrics
# ============================================================================

tool_run_duration = Histogram(
    "nethical_tool_run_duration_seconds",
    "Duration of tool runs in seconds",
    ["tool_name", "status"],
    registry=metrics_registry,
    buckets=(1, 5, 10, 30, 60, 120, 300, 600, 1800, 3600),  # 1s to 1h
)

tool_run_total = Counter(
    "nethical_tool_run_total",
    "Total number of tool runs",
    ["tool_name", "status"],
    registry=metrics_registry,
)

tool_run_errors = Counter(
    "nethical_tool_run_errors_total",
    "Total number of tool run errors",
    ["tool_name", "error_type"],
    registry=metrics_registry,
)

# ============================================================================
# Finding Metrics
# ============================================================================

findings_total = Counter(
    "nethical_findings_total",
    "Total number of findings discovered",
    ["severity", "tool_name"],
    registry=metrics_registry,
)

findings_per_job = Histogram(
    "nethical_findings_per_job",
    "Number of findings per job",
    ["job_id"],
    registry=metrics_registry,
    buckets=(0, 1, 5, 10, 25, 50, 100, 250, 500, 1000),
)

# ============================================================================
# Job Metrics
# ============================================================================

job_duration = Histogram(
    "nethical_job_duration_seconds",
    "Duration of scan jobs in seconds",
    ["status"],
    registry=metrics_registry,
    buckets=(10, 30, 60, 300, 600, 1800, 3600, 7200, 14400),  # 10s to 4h
)

job_total = Counter(
    "nethical_job_total",
    "Total number of jobs",
    ["status"],
    registry=metrics_registry,
)

# ============================================================================
# Queue Metrics
# ============================================================================

queue_depth = Gauge(
    "nethical_queue_depth",
    "Current depth of the task queue",
    ["queue_name"],
    registry=metrics_registry,
)

queue_processing_time = Summary(
    "nethical_queue_processing_seconds",
    "Time spent processing queue tasks",
    ["task_name"],
    registry=metrics_registry,
)

# ============================================================================
# API Metrics
# ============================================================================

api_requests_total = Counter(
    "nethical_api_requests_total",
    "Total number of API requests",
    ["method", "endpoint", "status_code"],
    registry=metrics_registry,
)

api_request_duration = Histogram(
    "nethical_api_request_duration_seconds",
    "API request duration in seconds",
    ["method", "endpoint"],
    registry=metrics_registry,
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10),
)

# ============================================================================
# System Metrics
# ============================================================================

active_workers = Gauge(
    "nethical_active_workers",
    "Number of active worker processes",
    registry=metrics_registry,
)

error_rate = Counter(
    "nethical_errors_total",
    "Total number of errors",
    ["component", "error_type"],
    registry=metrics_registry,
)

# ============================================================================
# Helper Functions
# ============================================================================


def track_duration(metric_name: str, labels: Optional[dict[str, str]] = None):
    """
    Decorator to track duration of a function execution.

    Args:
        metric_name: Name of the metric to use (tool_run, job, api_request)
        labels: Labels to add to the metric

    Example:
        @track_duration("tool_run", {"tool_name": "nmap", "status": "success"})
        def run_nmap():
            ...
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            status = "success"

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                status = "error"
                raise
            finally:
                duration = time.time() - start_time

                # Select appropriate metric
                if metric_name == "tool_run":
                    tool_run_duration.labels(**labels or {}).observe(duration)
                elif metric_name == "job":
                    job_duration.labels(status=status).observe(duration)
                elif metric_name == "api_request":
                    api_request_duration.labels(**labels or {}).observe(duration)

        return wrapper

    return decorator


@contextmanager
def track_tool_run(tool_name: str) -> Generator[dict[str, Any], None, None]:
    """
    Context manager to track tool run metrics.

    Example:
        with track_tool_run("nmap") as metrics:
            run_nmap()
            metrics["status"] = "success"
    """
    start_time = time.time()
    metrics_data = {"status": "success", "error_type": None}

    try:
        yield metrics_data
    except Exception as e:
        metrics_data["status"] = "error"
        metrics_data["error_type"] = type(e).__name__
        tool_run_errors.labels(tool_name=tool_name, error_type=type(e).__name__).inc()
        raise
    finally:
        duration = time.time() - start_time
        status = metrics_data["status"]

        tool_run_duration.labels(tool_name=tool_name, status=status).observe(duration)
        tool_run_total.labels(tool_name=tool_name, status=status).inc()


def track_findings(findings_count: int, severity: str, tool_name: str, job_id: Optional[str] = None) -> None:
    """
    Track findings metrics.

    Args:
        findings_count: Number of findings
        severity: Severity level (info, low, medium, high, critical)
        tool_name: Name of the tool that generated findings
        job_id: Optional job ID
    """
    findings_total.labels(severity=severity, tool_name=tool_name).inc(findings_count)

    if job_id:
        findings_per_job.labels(job_id=job_id).observe(findings_count)


def track_errors(component: str, error_type: str) -> None:
    """
    Track error occurrences.

    Args:
        component: Component where error occurred (e.g., "worker", "api", "parser")
        error_type: Type of error (e.g., "TimeoutError", "ValidationError")
    """
    error_rate.labels(component=component, error_type=error_type).inc()


def increment_counter(counter_name: str, labels: Optional[dict[str, str]] = None, value: float = 1) -> None:
    """
    Increment a counter metric.

    Args:
        counter_name: Name of the counter (job_total, tool_run_total, etc.)
        labels: Labels for the counter
        value: Value to increment by (default: 1)
    """
    labels = labels or {}

    if counter_name == "job_total":
        job_total.labels(**labels).inc(value)
    elif counter_name == "tool_run_total":
        tool_run_total.labels(**labels).inc(value)
    elif counter_name == "api_requests_total":
        api_requests_total.labels(**labels).inc(value)


def observe_value(metric_name: str, value: float, labels: Optional[dict[str, str]] = None) -> None:
    """
    Observe a value in a histogram or summary metric.

    Args:
        metric_name: Name of the metric
        value: Value to observe
        labels: Labels for the metric
    """
    labels = labels or {}

    if metric_name == "tool_run_duration":
        tool_run_duration.labels(**labels).observe(value)
    elif metric_name == "job_duration":
        job_duration.labels(**labels).observe(value)
    elif metric_name == "api_request_duration":
        api_request_duration.labels(**labels).observe(value)
    elif metric_name == "findings_per_job":
        findings_per_job.labels(**labels).observe(value)


def update_queue_depth(queue_name: str, depth: int) -> None:
    """
    Update queue depth gauge.

    Args:
        queue_name: Name of the queue (e.g., "celery", "default")
        depth: Current queue depth
    """
    queue_depth.labels(queue_name=queue_name).set(depth)


def update_active_workers(count: int) -> None:
    """
    Update active workers gauge.

    Args:
        count: Number of active workers
    """
    active_workers.set(count)


def get_metrics() -> bytes:
    """
    Get current metrics in Prometheus format.

    Returns:
        Metrics in Prometheus text format
    """
    return generate_latest(metrics_registry)
