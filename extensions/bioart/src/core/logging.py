"""
Structured logging with correlation IDs and timing for Bioart.

This module provides structured JSON logging with correlation tracking for job tracing,
timing information, and error counters.

Implements M0 requirement: "Logging: correlate job_id, step_id; timing and error counters"
"""

import json
import logging
import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from functools import wraps

# Thread-local storage for correlation context
import threading
_context = threading.local()


class StructuredFormatter(logging.Formatter):
    """
    JSON formatter for structured logging.

    Outputs log records as JSON with correlation IDs, timing, and metadata.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add correlation IDs if present
        if hasattr(_context, "job_id") and _context.job_id:
            log_data["job_id"] = _context.job_id
        if hasattr(_context, "step_id") and _context.step_id:
            log_data["step_id"] = _context.step_id

        # Add extra fields
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add timing information if present
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms

        # Add file location
        log_data["location"] = f"{record.filename}:{record.lineno}"

        return json.dumps(log_data)


class TextFormatter(logging.Formatter):
    """Human-readable text formatter with correlation IDs."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as text."""
        parts = [
            f"[{datetime.now(timezone.utc).isoformat()}]",
            f"[{record.levelname}]",
        ]

        # Add correlation IDs if present
        if hasattr(_context, "job_id") and _context.job_id:
            parts.append(f"[job:{_context.job_id}]")
        if hasattr(_context, "step_id") and _context.step_id:
            parts.append(f"[step:{_context.step_id}]")

        parts.append(f"{record.name}: {record.getMessage()}")

        # Add timing if present
        if hasattr(record, "duration_ms"):
            parts.append(f"({record.duration_ms:.2f}ms)")

        return " ".join(parts)


class CorrelationLogger:
    """
    Logger wrapper with correlation ID tracking and timing support.
    """

    def __init__(self, name: str, use_json: bool = True):
        """
        Initialize correlation logger.

        Args:
            name: Logger name
            use_json: Use JSON format (True) or text format (False)
        """
        self.logger = logging.getLogger(name)
        self.use_json = use_json

        # Set up handler if not already configured
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            if use_json:
                handler.setFormatter(StructuredFormatter())
            else:
                handler.setFormatter(TextFormatter())
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def _log(self, level: int, msg: str, **extra_fields) -> None:
        """Internal log method with extra fields."""
        record = self.logger.makeRecord(
            self.logger.name,
            level,
            "(unknown file)",
            0,
            msg,
            (),
            None,
        )
        if extra_fields:
            record.extra_fields = extra_fields
        self.logger.handle(record)

    def debug(self, msg: str, **extra_fields) -> None:
        """Log debug message."""
        self._log(logging.DEBUG, msg, **extra_fields)

    def info(self, msg: str, **extra_fields) -> None:
        """Log info message."""
        self._log(logging.INFO, msg, **extra_fields)

    def warning(self, msg: str, **extra_fields) -> None:
        """Log warning message."""
        self._log(logging.WARNING, msg, **extra_fields)

    def error(self, msg: str, **extra_fields) -> None:
        """Log error message."""
        self._log(logging.ERROR, msg, **extra_fields)

    def critical(self, msg: str, **extra_fields) -> None:
        """Log critical message."""
        self._log(logging.CRITICAL, msg, **extra_fields)


def set_correlation_context(job_id: Optional[str] = None, step_id: Optional[str] = None) -> None:
    """
    Set correlation context for current thread.

    Args:
        job_id: Job identifier
        step_id: Step identifier within job
    """
    _context.job_id = job_id
    _context.step_id = step_id


def get_correlation_context() -> Dict[str, Optional[str]]:
    """
    Get current correlation context.

    Returns:
        Dictionary with job_id and step_id
    """
    return {
        "job_id": getattr(_context, "job_id", None),
        "step_id": getattr(_context, "step_id", None),
    }


def clear_correlation_context() -> None:
    """Clear correlation context for current thread."""
    if hasattr(_context, "job_id"):
        delattr(_context, "job_id")
    if hasattr(_context, "step_id"):
        delattr(_context, "step_id")


@contextmanager
def correlation_context(job_id: Optional[str] = None, step_id: Optional[str] = None):
    """
    Context manager for correlation tracking.

    Example:
        with correlation_context(job_id="job-123", step_id="encode"):
            logger.info("Processing data")

    Args:
        job_id: Job identifier (generated if None)
        step_id: Step identifier
    """
    if job_id is None:
        job_id = str(uuid.uuid4())

    old_context = get_correlation_context()
    set_correlation_context(job_id, step_id)
    try:
        yield job_id
    finally:
        set_correlation_context(old_context["job_id"], old_context["step_id"])


@contextmanager
def timed_operation(logger: CorrelationLogger, operation: str, **extra_fields):
    """
    Context manager for timing operations.

    Example:
        with timed_operation(logger, "encode_sequence"):
            result = encode(data)

    Args:
        logger: Logger instance
        operation: Operation name
        extra_fields: Additional fields to log
    """
    start_time = time.time()
    logger.info(f"Starting {operation}", operation=operation, **extra_fields)
    try:
        yield
        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            f"Completed {operation}",
            operation=operation,
            duration_ms=duration_ms,
            status="success",
            **extra_fields
        )
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(
            f"Failed {operation}: {str(e)}",
            operation=operation,
            duration_ms=duration_ms,
            status="error",
            error_type=type(e).__name__,
            **extra_fields
        )
        raise


def timed(logger: CorrelationLogger, operation: Optional[str] = None):
    """
    Decorator for timing function execution.

    Example:
        @timed(logger, "encode_function")
        def encode_data(data):
            return process(data)

    Args:
        logger: Logger instance
        operation: Operation name (uses function name if None)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation or func.__name__
            with timed_operation(logger, op_name):
                return func(*args, **kwargs)
        return wrapper
    return decorator


# Error counter tracking
_error_counters: Dict[str, int] = {}
_error_counters_lock = threading.Lock()


def increment_error_counter(error_type: str) -> int:
    """
    Increment error counter for given type.

    Args:
        error_type: Type of error

    Returns:
        New count
    """
    with _error_counters_lock:
        _error_counters[error_type] = _error_counters.get(error_type, 0) + 1
        return _error_counters[error_type]


def get_error_counters() -> Dict[str, int]:
    """
    Get all error counters.

    Returns:
        Dictionary of error types and counts
    """
    with _error_counters_lock:
        return dict(_error_counters)


def reset_error_counters() -> None:
    """Reset all error counters."""
    with _error_counters_lock:
        _error_counters.clear()


# Default logger instance
def get_logger(name: str = "bioart", use_json: bool = True) -> CorrelationLogger:
    """
    Get a configured logger instance.

    Args:
        name: Logger name
        use_json: Use JSON format

    Returns:
        CorrelationLogger instance
    """
    return CorrelationLogger(name, use_json=use_json)
