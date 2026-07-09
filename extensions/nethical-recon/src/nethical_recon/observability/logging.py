"""
Structured logging configuration using structlog.

Provides JSON logging with correlation IDs and multi-level logging
for audit, security, and operational concerns.
"""

import logging
import sys
from typing import Any, Dict, Optional

import structlog
from structlog.types import EventDict, Processor


def add_correlation_ids(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """
    Add correlation IDs to log entries.

    Looks for job_id, run_id, target_id in context and adds them to logs.
    """
    # These are typically added via bind() when creating contextual loggers
    return event_dict


def add_log_level(logger: Any, method_name: str, event_dict: EventDict) -> EventDict:
    """Add log level classification (audit/security/ops)."""
    # Map log levels to categories
    level = event_dict.get("level", "").upper()

    if "audit" in event_dict.get("event", "").lower():
        event_dict["category"] = "audit"
    elif "security" in event_dict.get("event", "").lower() or level == "CRITICAL":
        event_dict["category"] = "security"
    else:
        event_dict["category"] = "ops"

    return event_dict


def configure_logging(level: str = "INFO", json_logs: bool = True, output_file: Optional[str] = None) -> None:
    """
    Configure structured logging for the application.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_logs: Whether to output logs in JSON format (True) or human-readable (False)
        output_file: Optional file path to write logs to (in addition to stdout)
    """
    # Configure standard logging to work with structlog
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper()),
    )

    # Define processors
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        add_correlation_ids,
        add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if json_logs:
        # JSON output for production
        processors.append(structlog.processors.JSONRenderer())
    else:
        # Human-readable output for development
        processors.extend(
            [
                structlog.dev.set_exc_info,
                structlog.dev.ConsoleRenderer(colors=True),
            ]
        )

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # If output file is specified, add file handler
    if output_file:
        file_handler = logging.FileHandler(output_file)
        file_handler.setLevel(getattr(logging, level.upper()))
        logging.root.addHandler(file_handler)


def get_logger(name: str, **initial_context: Any) -> structlog.stdlib.BoundLogger:
    """
    Get a logger instance with optional initial context.

    Args:
        name: Logger name (typically __name__)
        **initial_context: Initial context to bind to logger (e.g., job_id, run_id)

    Returns:
        Bound logger instance with context

    Example:
        >>> logger = get_logger(__name__, job_id="job-123", target_id="target-456")
        >>> logger.info("scan started", tool="nmap")
    """
    logger = structlog.get_logger(name)

    if initial_context:
        logger = logger.bind(**initial_context)

    return logger


# Convenience functions for specific log categories
def audit_log(message: str, **context: Any) -> None:
    """Log audit trail event."""
    logger = get_logger("audit")
    logger.info(f"AUDIT: {message}", **context)


def security_log(message: str, **context: Any) -> None:
    """Log security-related event."""
    logger = get_logger("security")
    logger.warning(f"SECURITY: {message}", **context)


def ops_log(message: str, **context: Any) -> None:
    """Log operational event."""
    logger = get_logger("ops")
    logger.info(f"OPS: {message}", **context)
