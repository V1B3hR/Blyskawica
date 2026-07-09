"""
Tests for structured logging module.

Tests JSON logging, correlation IDs, timing, and error counters.
"""

import json
import pytest
import time
from src.core.logging import (
    get_logger,
    correlation_context,
    timed_operation,
    timed,
    set_correlation_context,
    get_correlation_context,
    clear_correlation_context,
    increment_error_counter,
    get_error_counters,
    reset_error_counters,
)


def test_logger_creation():
    """Test logger creation."""
    logger = get_logger("test")
    assert logger is not None
    assert logger.logger.name == "test"


def test_correlation_context():
    """Test correlation context management."""
    # Clear any existing context
    clear_correlation_context()

    # Set context
    set_correlation_context(job_id="job-123", step_id="step-1")
    context = get_correlation_context()
    assert context["job_id"] == "job-123"
    assert context["step_id"] == "step-1"

    # Clear context
    clear_correlation_context()
    context = get_correlation_context()
    assert context["job_id"] is None
    assert context["step_id"] is None


def test_correlation_context_manager():
    """Test correlation context manager."""
    clear_correlation_context()

    with correlation_context(job_id="job-456", step_id="encode") as job_id:
        assert job_id == "job-456"
        context = get_correlation_context()
        assert context["job_id"] == "job-456"
        assert context["step_id"] == "encode"

    # Context should be cleared after exiting
    context = get_correlation_context()
    assert context["job_id"] is None
    assert context["step_id"] is None


def test_correlation_context_auto_job_id():
    """Test correlation context with auto-generated job ID."""
    clear_correlation_context()

    with correlation_context(step_id="decode") as job_id:
        # Job ID should be auto-generated
        assert job_id is not None
        assert len(job_id) > 0
        context = get_correlation_context()
        assert context["job_id"] == job_id
        assert context["step_id"] == "decode"


def test_timed_operation_success():
    """Test timed operation context manager with success."""
    logger = get_logger("test", use_json=False)
    clear_correlation_context()

    start_time = time.time()
    with timed_operation(logger, "test_operation"):
        time.sleep(0.01)  # Small delay
    duration = time.time() - start_time

    # Operation should take at least 10ms
    assert duration >= 0.01


def test_timed_operation_failure():
    """Test timed operation context manager with failure."""
    logger = get_logger("test", use_json=False)
    clear_correlation_context()

    with pytest.raises(ValueError):
        with timed_operation(logger, "failing_operation"):
            raise ValueError("Test error")


def test_timed_decorator():
    """Test timed decorator."""
    logger = get_logger("test", use_json=False)
    clear_correlation_context()

    @timed(logger, "decorated_function")
    def sample_function(x, y):
        time.sleep(0.01)
        return x + y

    result = sample_function(2, 3)
    assert result == 5


def test_error_counters():
    """Test error counter tracking."""
    reset_error_counters()

    # Increment counters
    count1 = increment_error_counter("timeout")
    assert count1 == 1

    count2 = increment_error_counter("timeout")
    assert count2 == 2

    count3 = increment_error_counter("network_error")
    assert count3 == 1

    # Get all counters
    counters = get_error_counters()
    assert counters["timeout"] == 2
    assert counters["network_error"] == 1

    # Reset
    reset_error_counters()
    counters = get_error_counters()
    assert len(counters) == 0


def test_logger_with_extra_fields():
    """Test logging with extra fields."""
    logger = get_logger("test", use_json=True)
    clear_correlation_context()

    # This should not raise
    logger.info("Test message", extra_field="value", count=42)
    logger.debug("Debug message", detail="debug info")
    logger.warning("Warning message", code=100)
    logger.error("Error message", error_type="TestError")


def test_nested_correlation_context():
    """Test nested correlation contexts."""
    clear_correlation_context()

    with correlation_context(job_id="outer-job", step_id="outer-step"):
        context1 = get_correlation_context()
        assert context1["job_id"] == "outer-job"
        assert context1["step_id"] == "outer-step"

        with correlation_context(job_id="inner-job", step_id="inner-step"):
            context2 = get_correlation_context()
            assert context2["job_id"] == "inner-job"
            assert context2["step_id"] == "inner-step"

        # Should restore outer context
        context3 = get_correlation_context()
        assert context3["job_id"] == "outer-job"
        assert context3["step_id"] == "outer-step"


def test_text_logger():
    """Test text format logger."""
    logger = get_logger("test", use_json=False)
    clear_correlation_context()

    # Should work without raising
    set_correlation_context(job_id="test-job", step_id="test-step")
    logger.info("Test message")
    logger.debug("Debug message")
    logger.warning("Warning message")
    logger.error("Error message")
    clear_correlation_context()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
