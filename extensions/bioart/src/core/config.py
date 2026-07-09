"""
Central configuration management for Bioart.

This module provides centralized configuration with validation and schema enforcement
for the Bioart DNA programming language system.

Implements M0 requirement: "Central config (pydantic/dataclass) + schema validation"
"""

import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, Optional


class LogLevel(str, Enum):
    """Logging levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogFormat(str, Enum):
    """Log output formats."""
    JSON = "json"
    TEXT = "text"


@dataclass
class LoggingConfig:
    """Logging configuration with structured output support."""
    level: LogLevel = LogLevel.INFO
    format: LogFormat = LogFormat.JSON
    include_correlation_id: bool = True
    include_timestamps: bool = True
    include_timing: bool = True
    log_file: Optional[Path] = None


@dataclass
class PerformanceConfig:
    """Performance tuning and optimization settings."""
    enable_caching: bool = True
    cache_ttl_seconds: int = 300
    cache_max_size: int = 1000
    enable_profiling: bool = False
    profiling_sample_rate: float = 0.01


@dataclass
class VMConfig:
    """Virtual Machine configuration."""
    memory_size: int = 256
    max_execution_steps: int = 1_000_000
    enable_debug_mode: bool = False
    enable_tracing: bool = False


@dataclass
class ErrorCorrectionConfig:
    """Error correction and reliability settings."""
    enable_hamming_code: bool = True
    enable_redundancy: bool = True
    redundancy_factor: int = 3
    enable_contextual_checks: bool = True


@dataclass
class CostConfig:
    """Cost tracking and budget configuration."""
    enable_cost_tracking: bool = True
    cost_per_100_jobs_budget: Optional[float] = None
    enable_cost_alerts: bool = True
    alert_threshold_percent: float = 80.0


@dataclass
class AdapterConfig:
    """Adapter and integration configuration."""
    default_adapter: str = "sandbox"
    enable_circuit_breaker: bool = True
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout_seconds: int = 60
    enable_retry: bool = True
    max_retries: int = 3
    retry_backoff_base_seconds: float = 1.0
    retry_backoff_max_seconds: float = 60.0
    enable_jitter: bool = True


@dataclass
class BioartConfig:
    """
    Main Bioart configuration container.

    Provides centralized, validated configuration for all system components.
    Configuration can be loaded from environment variables with BIOART_ prefix.
    """
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    vm: VMConfig = field(default_factory=VMConfig)
    error_correction: ErrorCorrectionConfig = field(default_factory=ErrorCorrectionConfig)
    cost: CostConfig = field(default_factory=CostConfig)
    adapter: AdapterConfig = field(default_factory=AdapterConfig)

    # Global settings
    environment: str = field(default_factory=lambda: os.getenv("BIOART_ENV", "development"))
    debug: bool = field(default_factory=lambda: os.getenv("BIOART_DEBUG", "false").lower() == "true")

    def validate(self) -> None:
        """
        Validate configuration settings.

        Raises:
            ValueError: If configuration is invalid
        """
        # Validate performance settings
        if self.performance.cache_ttl_seconds < 0:
            raise ValueError("cache_ttl_seconds must be non-negative")
        if self.performance.cache_max_size < 1:
            raise ValueError("cache_max_size must be positive")
        if not 0.0 <= self.performance.profiling_sample_rate <= 1.0:
            raise ValueError("profiling_sample_rate must be between 0.0 and 1.0")

        # Validate VM settings
        if self.vm.memory_size < 1:
            raise ValueError("memory_size must be positive")
        if self.vm.max_execution_steps < 1:
            raise ValueError("max_execution_steps must be positive")

        # Validate error correction settings
        if self.error_correction.redundancy_factor < 1:
            raise ValueError("redundancy_factor must be at least 1")

        # Validate cost settings
        if self.cost.cost_per_100_jobs_budget is not None and self.cost.cost_per_100_jobs_budget < 0:
            raise ValueError("cost_per_100_jobs_budget must be non-negative")
        if not 0.0 <= self.cost.alert_threshold_percent <= 100.0:
            raise ValueError("alert_threshold_percent must be between 0 and 100")

        # Validate adapter settings
        if self.adapter.circuit_breaker_threshold < 1:
            raise ValueError("circuit_breaker_threshold must be positive")
        if self.adapter.max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        if self.adapter.retry_backoff_base_seconds <= 0:
            raise ValueError("retry_backoff_base_seconds must be positive")

    @classmethod
    def from_env(cls) -> "BioartConfig":
        """
        Create configuration from environment variables.

        Environment variables use BIOART_ prefix, e.g.:
        - BIOART_LOG_LEVEL=INFO
        - BIOART_CACHE_TTL=600
        - BIOART_ENABLE_PROFILING=true

        Returns:
            BioartConfig: Configuration instance
        """
        config = cls()

        # Logging
        if log_level := os.getenv("BIOART_LOG_LEVEL"):
            try:
                config.logging.level = LogLevel(log_level)
            except ValueError:
                pass

        if log_format := os.getenv("BIOART_LOG_FORMAT"):
            try:
                config.logging.format = LogFormat(log_format)
            except ValueError:
                pass

        # Performance
        if cache_ttl := os.getenv("BIOART_CACHE_TTL"):
            try:
                config.performance.cache_ttl_seconds = int(cache_ttl)
            except ValueError:
                pass

        if enable_profiling := os.getenv("BIOART_ENABLE_PROFILING"):
            config.performance.enable_profiling = enable_profiling.lower() == "true"

        # VM
        if memory_size := os.getenv("BIOART_VM_MEMORY_SIZE"):
            try:
                config.vm.memory_size = int(memory_size)
            except ValueError:
                pass

        # Cost tracking
        if cost_budget := os.getenv("BIOART_COST_BUDGET"):
            try:
                config.cost.cost_per_100_jobs_budget = float(cost_budget)
            except ValueError:
                pass

        config.validate()
        return config

    def to_dict(self) -> Dict:
        """Convert configuration to dictionary."""
        return {
            "logging": {
                "level": self.logging.level.value,
                "format": self.logging.format.value,
                "include_correlation_id": self.logging.include_correlation_id,
                "include_timestamps": self.logging.include_timestamps,
                "include_timing": self.logging.include_timing,
            },
            "performance": {
                "enable_caching": self.performance.enable_caching,
                "cache_ttl_seconds": self.performance.cache_ttl_seconds,
                "cache_max_size": self.performance.cache_max_size,
                "enable_profiling": self.performance.enable_profiling,
            },
            "vm": {
                "memory_size": self.vm.memory_size,
                "max_execution_steps": self.vm.max_execution_steps,
                "enable_debug_mode": self.vm.enable_debug_mode,
            },
            "error_correction": {
                "enable_hamming_code": self.error_correction.enable_hamming_code,
                "enable_redundancy": self.error_correction.enable_redundancy,
                "redundancy_factor": self.error_correction.redundancy_factor,
            },
            "cost": {
                "enable_cost_tracking": self.cost.enable_cost_tracking,
                "cost_per_100_jobs_budget": self.cost.cost_per_100_jobs_budget,
                "enable_cost_alerts": self.cost.enable_cost_alerts,
            },
            "adapter": {
                "default_adapter": self.adapter.default_adapter,
                "enable_circuit_breaker": self.adapter.enable_circuit_breaker,
                "enable_retry": self.adapter.enable_retry,
                "max_retries": self.adapter.max_retries,
            },
            "environment": self.environment,
            "debug": self.debug,
        }


# Global configuration instance
_config: Optional[BioartConfig] = None


def get_config() -> BioartConfig:
    """
    Get the global configuration instance.

    Returns:
        BioartConfig: Global configuration
    """
    global _config
    if _config is None:
        _config = BioartConfig.from_env()
    return _config


def set_config(config: BioartConfig) -> None:
    """
    Set the global configuration instance.

    Args:
        config: Configuration to set
    """
    global _config
    config.validate()
    _config = config


def reset_config() -> None:
    """Reset the global configuration to default."""
    global _config
    _config = None
