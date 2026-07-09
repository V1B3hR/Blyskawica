"""Tests for observability module."""

import pytest
from prometheus_client import REGISTRY

from nethical_recon.observability import (
    configure_logging,
    get_logger,
    increment_counter,
    observe_value,
    track_duration,
    track_errors,
    track_findings,
    track_tool_run,
)
from nethical_recon.observability.metrics import get_metrics, update_active_workers, update_queue_depth


class TestLogging:
    """Test structured logging functionality."""

    def test_configure_logging_json(self):
        """Test JSON logging configuration."""
        configure_logging(level="INFO", json_logs=True)
        logger = get_logger(__name__)
        assert logger is not None

    def test_configure_logging_console(self):
        """Test console logging configuration."""
        configure_logging(level="DEBUG", json_logs=False)
        logger = get_logger(__name__)
        assert logger is not None

    def test_get_logger_with_context(self):
        """Test logger with initial context."""
        logger = get_logger(__name__, job_id="test-job-123", target_id="test-target-456")
        assert logger is not None

        # Log a message - should include context
        logger.info("test message", extra_field="extra_value")

    def test_logger_binding(self):
        """Test logger context binding."""
        logger = get_logger(__name__)
        bound_logger = logger.bind(job_id="job-123")

        # Both loggers should be valid
        assert logger is not None
        assert bound_logger is not None


class TestMetrics:
    """Test Prometheus metrics functionality."""

    def test_track_tool_run_success(self):
        """Test tracking successful tool run."""
        with track_tool_run("test_tool") as metrics:
            # Simulate work
            pass

        assert metrics["status"] == "success"

        # Verify metrics were collected
        metrics_data = get_metrics().decode("utf-8")
        assert "nethical_tool_run_total" in metrics_data

    def test_track_tool_run_error(self):
        """Test tracking failed tool run."""
        try:
            with track_tool_run("test_tool") as metrics:
                raise ValueError("Test error")
        except ValueError:
            pass

        # Verify error metrics were collected
        metrics_data = get_metrics().decode("utf-8")
        assert "nethical_tool_run_errors_total" in metrics_data

    def test_track_findings(self):
        """Test tracking findings metrics."""
        track_findings(findings_count=10, severity="high", tool_name="nmap", job_id="job-123")

        metrics_data = get_metrics().decode("utf-8")
        assert "nethical_findings_total" in metrics_data

    def test_track_errors(self):
        """Test tracking error metrics."""
        track_errors(component="worker", error_type="TimeoutError")

        metrics_data = get_metrics().decode("utf-8")
        assert "nethical_errors_total" in metrics_data

    def test_increment_counter(self):
        """Test incrementing counter metrics."""
        increment_counter("job_total", {"status": "completed"})

        metrics_data = get_metrics().decode("utf-8")
        assert "nethical_job_total" in metrics_data

    def test_observe_value(self):
        """Test observing histogram values."""
        observe_value("tool_run_duration", 120.5, {"tool_name": "nmap", "status": "success"})

        metrics_data = get_metrics().decode("utf-8")
        assert "nethical_tool_run_duration_seconds" in metrics_data

    def test_update_queue_depth(self):
        """Test updating queue depth gauge."""
        update_queue_depth("celery", 42)

        metrics_data = get_metrics().decode("utf-8")
        assert "nethical_queue_depth" in metrics_data

    def test_update_active_workers(self):
        """Test updating active workers gauge."""
        update_active_workers(4)

        metrics_data = get_metrics().decode("utf-8")
        assert "nethical_active_workers" in metrics_data

    def test_get_metrics_format(self):
        """Test metrics output format."""
        metrics_data = get_metrics()

        # Should be bytes
        assert isinstance(metrics_data, bytes)

        # Should contain Prometheus format markers
        metrics_str = metrics_data.decode("utf-8")
        assert "# HELP" in metrics_str or "# TYPE" in metrics_str or len(metrics_str) > 0

    def test_track_duration_decorator(self):
        """Test duration tracking decorator."""

        @track_duration("tool_run", {"tool_name": "test", "status": "success"})
        def sample_function():
            return "result"

        result = sample_function()
        assert result == "result"

        metrics_data = get_metrics().decode("utf-8")
        assert "nethical_tool_run_duration_seconds" in metrics_data


class TestMetricsIntegration:
    """Integration tests for metrics collection."""

    def test_full_tool_run_metrics_flow(self):
        """Test complete tool run metrics flow."""
        # Track tool run
        with track_tool_run("nmap") as metrics:
            # Track findings
            track_findings(5, "high", "nmap", "job-456")
            track_findings(10, "medium", "nmap", "job-456")

            metrics["status"] = "success"

        # Verify all metrics are present
        metrics_data = get_metrics().decode("utf-8")
        assert "nethical_tool_run_total" in metrics_data
        assert "nethical_findings_total" in metrics_data

    def test_error_tracking_flow(self):
        """Test error tracking flow."""
        # Track various errors
        track_errors("worker", "TimeoutError")
        track_errors("parser", "ValidationError")
        track_errors("api", "AuthenticationError")

        metrics_data = get_metrics().decode("utf-8")
        assert "nethical_errors_total" in metrics_data

    def test_metrics_persistence(self):
        """Test that metrics persist across calls."""
        # First operation
        increment_counter("job_total", {"status": "running"})

        # Second operation
        increment_counter("job_total", {"status": "completed"})

        # Both should be in metrics
        metrics_data = get_metrics().decode("utf-8")
        assert "nethical_job_total" in metrics_data


class TestLoggingIntegration:
    """Integration tests for logging."""

    def test_correlation_ids_in_logs(self):
        """Test that correlation IDs appear in logs."""
        logger = get_logger(__name__, job_id="test-123", run_id="run-456")

        # Should not raise
        logger.info("test message")
        logger.error("test error")
        logger.debug("test debug")

    def test_log_levels(self):
        """Test different log levels."""
        configure_logging(level="DEBUG", json_logs=False)
        logger = get_logger(__name__)

        # All should work without errors
        logger.debug("debug message")
        logger.info("info message")
        logger.warning("warning message")
        logger.error("error message")
        logger.critical("critical message")

    def test_exception_logging(self):
        """Test exception logging."""
        logger = get_logger(__name__)

        try:
            raise ValueError("Test exception")
        except ValueError:
            logger.error("caught exception", exc_info=True)
