"""
Core modules for Bioart DNA programming language.

Provides centralized configuration, structured logging, caching, cost tracking,
and core encoding functionality.
"""

from .config import (
    BioartConfig,
    LoggingConfig,
    PerformanceConfig,
    VMConfig,
    ErrorCorrectionConfig,
    CostConfig,
    AdapterConfig,
    get_config,
    set_config,
    reset_config,
)

from .logging import (
    CorrelationLogger,
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

from .cache import (
    BoundedTTLCache,
    cached,
    get_sequence_cache,
    get_transform_cache,
)

from .cost import (
    CostTracker,
    CostBudget,
    OperationCost,
    get_cost_tracker,
)

__all__ = [
    # Config
    "BioartConfig",
    "LoggingConfig",
    "PerformanceConfig",
    "VMConfig",
    "ErrorCorrectionConfig",
    "CostConfig",
    "AdapterConfig",
    "get_config",
    "set_config",
    "reset_config",
    # Logging
    "CorrelationLogger",
    "get_logger",
    "correlation_context",
    "timed_operation",
    "timed",
    "set_correlation_context",
    "get_correlation_context",
    "clear_correlation_context",
    "increment_error_counter",
    "get_error_counters",
    "reset_error_counters",
    # Cache
    "BoundedTTLCache",
    "cached",
    "get_sequence_cache",
    "get_transform_cache",
    # Cost
    "CostTracker",
    "CostBudget",
    "OperationCost",
    "get_cost_tracker",
]

