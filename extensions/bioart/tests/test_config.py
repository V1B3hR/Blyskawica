"""
Tests for configuration module.

Tests centralized configuration with validation and environment variable loading.
"""

import os
import pytest
from src.core.config import (
    BioartConfig,
    LogLevel,
    LogFormat,
    get_config,
    set_config,
    reset_config,
)


def test_default_config():
    """Test default configuration values."""
    config = BioartConfig()
    assert config.logging.level == LogLevel.INFO
    assert config.logging.format == LogFormat.JSON
    assert config.performance.enable_caching is True
    assert config.vm.memory_size == 256
    assert config.error_correction.enable_hamming_code is True


def test_config_validation():
    """Test configuration validation."""
    config = BioartConfig()
    config.validate()  # Should not raise

    # Test invalid values
    config.performance.cache_ttl_seconds = -1
    with pytest.raises(ValueError, match="cache_ttl_seconds must be non-negative"):
        config.validate()

    config = BioartConfig()
    config.performance.cache_max_size = 0
    with pytest.raises(ValueError, match="cache_max_size must be positive"):
        config.validate()

    config = BioartConfig()
    config.vm.memory_size = 0
    with pytest.raises(ValueError, match="memory_size must be positive"):
        config.validate()


def test_config_from_env():
    """Test loading configuration from environment variables."""
    # Set environment variables
    os.environ["BIOART_LOG_LEVEL"] = "DEBUG"
    os.environ["BIOART_CACHE_TTL"] = "600"
    os.environ["BIOART_ENABLE_PROFILING"] = "true"

    try:
        config = BioartConfig.from_env()
        assert config.logging.level == LogLevel.DEBUG
        assert config.performance.cache_ttl_seconds == 600
        assert config.performance.enable_profiling is True
    finally:
        # Clean up environment
        del os.environ["BIOART_LOG_LEVEL"]
        del os.environ["BIOART_CACHE_TTL"]
        del os.environ["BIOART_ENABLE_PROFILING"]


def test_config_to_dict():
    """Test configuration serialization to dictionary."""
    config = BioartConfig()
    config_dict = config.to_dict()

    assert isinstance(config_dict, dict)
    assert "logging" in config_dict
    assert "performance" in config_dict
    assert "vm" in config_dict
    assert config_dict["logging"]["level"] == "INFO"
    assert config_dict["vm"]["memory_size"] == 256


def test_global_config():
    """Test global configuration management."""
    reset_config()

    # Get config should create default
    config1 = get_config()
    assert config1 is not None
    assert config1.logging.level == LogLevel.INFO

    # Get config again should return same instance
    config2 = get_config()
    assert config1 is config2

    # Set new config
    new_config = BioartConfig()
    new_config.logging.level = LogLevel.DEBUG
    set_config(new_config)

    config3 = get_config()
    assert config3 is new_config
    assert config3.logging.level == LogLevel.DEBUG

    # Reset
    reset_config()


def test_performance_config_validation():
    """Test performance configuration validation."""
    config = BioartConfig()

    # Valid profiling sample rate
    config.performance.profiling_sample_rate = 0.5
    config.validate()

    # Invalid profiling sample rate
    config.performance.profiling_sample_rate = 1.5
    with pytest.raises(ValueError, match="profiling_sample_rate must be between"):
        config.validate()


def test_cost_config():
    """Test cost configuration."""
    config = BioartConfig()
    assert config.cost.enable_cost_tracking is True
    assert config.cost.cost_per_100_jobs_budget is None

    # Set budget
    config.cost.cost_per_100_jobs_budget = 100.0
    config.validate()

    # Invalid budget
    config.cost.cost_per_100_jobs_budget = -10.0
    with pytest.raises(ValueError, match="cost_per_100_jobs_budget must be non-negative"):
        config.validate()


def test_adapter_config():
    """Test adapter configuration."""
    config = BioartConfig()
    assert config.adapter.default_adapter == "sandbox"
    assert config.adapter.enable_retry is True
    assert config.adapter.max_retries == 3
    assert config.adapter.enable_circuit_breaker is True

    # Test validation
    config.adapter.max_retries = -1
    with pytest.raises(ValueError, match="max_retries must be non-negative"):
        config.validate()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
