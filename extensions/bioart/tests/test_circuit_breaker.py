"""Tests for circuit breaker functionality."""
import pytest
import time
from src.resilience.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerError,
    CircuitBreakerRegistry,
    CircuitState,
    circuit_breaker,
)


class CustomError(Exception):
    """Custom exception for testing."""
    pass


class TestCircuitBreaker:
    """Test CircuitBreaker class."""
    
    def test_init_default_exceptions(self):
        """Test that default exceptions is set to (Exception,)."""
        cb = CircuitBreaker(name="test", failure_threshold=3)
        assert cb.expected_exceptions == (Exception,)
        assert cb.name == "test"
        assert cb.failure_threshold == 3
    
    def test_init_custom_exceptions(self):
        """Test initialization with custom exception tuple."""
        cb = CircuitBreaker(
            name="test",
            failure_threshold=3,
            expected_exceptions=(ValueError, TypeError)
        )
        assert cb.expected_exceptions == (ValueError, TypeError)
    
    def test_init_none_exceptions_becomes_exception_tuple(self):
        """Test that None for expected_exceptions becomes (Exception,)."""
        cb = CircuitBreaker(
            name="test",
            failure_threshold=3,
            expected_exceptions=None
        )
        assert cb.expected_exceptions == (Exception,)
    
    def test_initial_state_is_closed(self):
        """Test circuit breaker starts in CLOSED state."""
        cb = CircuitBreaker(name="test", failure_threshold=3)
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0
    
    def test_successful_call(self):
        """Test successful function execution."""
        cb = CircuitBreaker(name="test", failure_threshold=3)
        
        def successful_func():
            return "success"
        
        result = cb.call(successful_func)
        assert result == "success"
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0
    
    def test_failing_call_increments_count(self):
        """Test that failures increment the counter."""
        cb = CircuitBreaker(name="test", failure_threshold=3)
        
        def failing_func():
            raise ValueError("test error")
        
        for i in range(2):
            with pytest.raises(ValueError):
                cb.call(failing_func)
            assert cb.failure_count == i + 1
            assert cb.state == CircuitState.CLOSED
    
    def test_circuit_opens_after_threshold(self):
        """Test circuit opens after reaching failure threshold."""
        cb = CircuitBreaker(name="test", failure_threshold=3)
        
        def failing_func():
            raise ValueError("test error")
        
        # Fail 3 times to reach threshold
        for _ in range(3):
            with pytest.raises(ValueError):
                cb.call(failing_func)
        
        assert cb.state == CircuitState.OPEN
        assert cb.failure_count == 3
    
    def test_open_circuit_raises_error(self):
        """Test that open circuit raises CircuitBreakerError."""
        cb = CircuitBreaker(name="test", failure_threshold=3)
        
        def failing_func():
            raise ValueError("test error")
        
        # Open the circuit
        for _ in range(3):
            with pytest.raises(ValueError):
                cb.call(failing_func)
        
        # Now circuit should be open
        def successful_func():
            return "success"
        
        with pytest.raises(CircuitBreakerError) as exc_info:
            cb.call(successful_func)
        
        assert "OPEN" in str(exc_info.value)
    
    def test_circuit_half_open_after_timeout(self):
        """Test circuit moves to HALF_OPEN after recovery timeout."""
        cb = CircuitBreaker(
            name="test",
            failure_threshold=2,
            recovery_timeout=0.1  # Short timeout for testing
        )
        
        def failing_func():
            raise ValueError("test error")
        
        # Open the circuit
        for _ in range(2):
            with pytest.raises(ValueError):
                cb.call(failing_func)
        
        assert cb.state == CircuitState.OPEN
        
        # Wait for recovery timeout
        time.sleep(0.15)
        
        def successful_func():
            return "success"
        
        # Should transition to HALF_OPEN and succeed
        result = cb.call(successful_func)
        assert result == "success"
        assert cb.state == CircuitState.CLOSED
    
    def test_custom_exceptions_only(self):
        """Test that only specified exceptions are caught."""
        cb = CircuitBreaker(
            name="test",
            failure_threshold=3,
            expected_exceptions=(ValueError,)
        )
        
        def type_error_func():
            raise TypeError("not caught")
        
        # TypeError should not be caught and should propagate
        with pytest.raises(TypeError):
            cb.call(type_error_func)
        
        # Circuit should still be closed
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0
    
    def test_get_stats(self):
        """Test get_stats returns correct statistics."""
        cb = CircuitBreaker(name="test_stats", failure_threshold=5)
        
        stats = cb.get_stats()
        
        assert isinstance(stats, dict)
        assert stats["name"] == "test_stats"
        assert stats["state"] == CircuitState.CLOSED.value
        assert stats["failure_count"] == 0
        assert stats["failure_threshold"] == 5


class TestCircuitBreakerRegistry:
    """Test CircuitBreakerRegistry class."""
    
    def test_get_or_create_new(self):
        """Test creating a new circuit breaker."""
        registry = CircuitBreakerRegistry()
        cb = registry.get_or_create("test1", failure_threshold=3)
        
        assert isinstance(cb, CircuitBreaker)
        assert cb.name == "test1"
        assert cb.failure_threshold == 3
    
    def test_get_or_create_existing(self):
        """Test getting an existing circuit breaker."""
        registry = CircuitBreakerRegistry()
        cb1 = registry.get_or_create("test2", failure_threshold=3)
        cb2 = registry.get_or_create("test2", failure_threshold=5)
        
        # Should return the same instance
        assert cb1 is cb2
        # Original threshold should be preserved
        assert cb1.failure_threshold == 3
    
    def test_get_nonexistent(self):
        """Test getting a non-existent circuit breaker."""
        registry = CircuitBreakerRegistry()
        cb = registry.get("nonexistent")
        
        assert cb is None
    
    def test_get_all_stats(self):
        """Test getting statistics for all circuit breakers."""
        registry = CircuitBreakerRegistry()
        registry.get_or_create("test1", failure_threshold=3)
        registry.get_or_create("test2", failure_threshold=5)
        
        all_stats = registry.get_all_stats()
        
        assert isinstance(all_stats, list)
        assert len(all_stats) == 2
        assert all(isinstance(stats, dict) for stats in all_stats)
        
        names = [stats["name"] for stats in all_stats]
        assert "test1" in names
        assert "test2" in names


    def test_decorator_basic(self):
        call_count = {"n": 0}

        @circuit_breaker(name="test_decorator", failure_threshold=2)
        def test_func():
            call_count["n"] += 1
            return "success"

        result = test_func()
        assert result == "success"
        assert call_count["n"] == 1
        
    def test_decorator_with_exceptions(self):
        """Test decorator with exception handling."""
        call_count = 0
        
        @circuit_breaker(
            name="test_decorator_exc",
            failure_threshold=2,
            expected_exceptions=(ValueError,)
        )
        def failing_func():
            nonlocal call_count
            call_count += 1
            raise ValueError("test error")
        
        # First failure
        with pytest.raises(ValueError):
            failing_func()
        assert call_count == 1
        
        # Second failure - should open circuit
        with pytest.raises(ValueError):
            failing_func()
        assert call_count == 2
        
        # Circuit is now open
        with pytest.raises(CircuitBreakerError):
            failing_func()
        # Function should not be called when circuit is open
        assert call_count == 2


class TestPython38Compatibility:
    """Test that type annotations are Python 3.8 compatible."""
    
    def test_import_with_typing_module(self):
        """Test that imports use typing module types."""
        from typing import Tuple, Dict, List, Type
        
        # These should work in Python 3.8+
        cb = CircuitBreaker(
            name="test",
            failure_threshold=3,
            expected_exceptions=(ValueError, TypeError)
        )
        
        # Verify the type is correct
        assert isinstance(cb.expected_exceptions, tuple)
        assert all(issubclass(exc, Exception) for exc in cb.expected_exceptions)
    
    def test_get_stats_dict_type(self):
        """Test that get_stats returns dict type."""
        cb = CircuitBreaker(name="test")
        stats = cb.get_stats()
        
        # Should return a dict (not dict[str, Any] which requires 3.9+)
        assert isinstance(stats, dict)
    
    def test_get_all_stats_list_type(self):
        """Test that get_all_stats returns list type."""
        registry = CircuitBreakerRegistry()
        registry.get_or_create("test1")
        registry.get_or_create("test2")
        
        all_stats = registry.get_all_stats()
        
        # Should return a list (not list[dict[str, Any]] which requires 3.9+)
        assert isinstance(all_stats, list)
        assert all(isinstance(stats, dict) for stats in all_stats)
