"""
Tests for caching module.

Tests bounded cache with TTL, LRU eviction, and statistics.
"""

import time
import pytest
from src.core.cache import (
    BoundedTTLCache,
    cached,
    get_sequence_cache,
    get_transform_cache,
)


def test_cache_basic_operations():
    """Test basic get/set operations."""
    cache = BoundedTTLCache(max_size=10, ttl_seconds=10)

    # Set and get
    cache.set("key1", "value1")
    assert cache.get("key1") == "value1"

    # Get non-existent key
    assert cache.get("key2") is None


def test_cache_expiration():
    """Test TTL-based expiration."""
    cache = BoundedTTLCache(max_size=10, ttl_seconds=0.1)

    cache.set("key1", "value1")
    assert cache.get("key1") == "value1"

    # Wait for expiration
    time.sleep(0.2)
    assert cache.get("key1") is None


def test_cache_custom_ttl():
    """Test custom TTL per entry."""
    cache = BoundedTTLCache(max_size=10, ttl_seconds=10)

    # Set with custom short TTL
    cache.set("key1", "value1", ttl_seconds=0.1)
    cache.set("key2", "value2", ttl_seconds=10)

    assert cache.get("key1") == "value1"
    assert cache.get("key2") == "value2"

    # Wait for key1 to expire
    time.sleep(0.2)
    assert cache.get("key1") is None
    assert cache.get("key2") == "value2"


def test_cache_lru_eviction():
    """Test LRU eviction when cache is full."""
    cache = BoundedTTLCache(max_size=3, ttl_seconds=10)

    # Fill cache
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    cache.set("key3", "value3")

    # All should be present
    assert cache.get("key1") == "value1"
    assert cache.get("key2") == "value2"
    assert cache.get("key3") == "value3"

    # Add one more - should evict key1 (oldest)
    cache.set("key4", "value4")
    assert cache.get("key1") is None
    assert cache.get("key2") == "value2"
    assert cache.get("key3") == "value3"
    assert cache.get("key4") == "value4"


def test_cache_update_moves_to_end():
    """Test that accessing an entry moves it to end (MRU)."""
    cache = BoundedTTLCache(max_size=3, ttl_seconds=10)

    cache.set("key1", "value1")
    cache.set("key2", "value2")
    cache.set("key3", "value3")

    # Access key1 to make it most recently used
    cache.get("key1")

    # Add key4 - should evict key2 (now oldest)
    cache.set("key4", "value4")
    assert cache.get("key1") == "value1"  # Still present
    assert cache.get("key2") is None  # Evicted
    assert cache.get("key3") == "value3"
    assert cache.get("key4") == "value4"


def test_cache_delete():
    """Test deleting entries."""
    cache = BoundedTTLCache(max_size=10, ttl_seconds=10)

    cache.set("key1", "value1")
    assert cache.get("key1") == "value1"

    # Delete existing key
    assert cache.delete("key1") is True
    assert cache.get("key1") is None

    # Delete non-existent key
    assert cache.delete("key2") is False


def test_cache_clear():
    """Test clearing all entries."""
    cache = BoundedTTLCache(max_size=10, ttl_seconds=10)

    cache.set("key1", "value1")
    cache.set("key2", "value2")
    cache.set("key3", "value3")

    cache.clear()

    assert cache.get("key1") is None
    assert cache.get("key2") is None
    assert cache.get("key3") is None


def test_cache_cleanup_expired():
    """Test manual cleanup of expired entries."""
    cache = BoundedTTLCache(max_size=10, ttl_seconds=0.1)

    cache.set("key1", "value1")
    cache.set("key2", "value2")
    cache.set("key3", "value3")

    # Wait for expiration
    time.sleep(0.2)

    # Cleanup expired entries
    removed = cache.cleanup_expired()
    assert removed == 3


def test_cache_statistics():
    """Test cache statistics tracking."""
    cache = BoundedTTLCache(max_size=10, ttl_seconds=10)

    cache.set("key1", "value1")
    cache.set("key2", "value2")

    # Generate some hits
    cache.get("key1")
    cache.get("key1")

    # Generate some misses
    cache.get("key3")
    cache.get("key4")

    stats = cache.get_stats()
    assert stats["size"] == 2
    assert stats["max_size"] == 10
    assert stats["hits"] == 2
    assert stats["misses"] == 2
    assert stats["total_requests"] == 4
    assert stats["hit_rate_percent"] == 50.0


def test_cache_stats_reset():
    """Test resetting statistics."""
    cache = BoundedTTLCache(max_size=10, ttl_seconds=10)

    cache.set("key1", "value1")
    cache.get("key1")
    cache.get("key2")

    stats = cache.get_stats()
    assert stats["hits"] > 0 or stats["misses"] > 0

    cache.reset_stats()
    stats = cache.get_stats()
    assert stats["hits"] == 0
    assert stats["misses"] == 0


def test_cached_decorator():
    """Test @cached decorator."""
    call_count = [0]

    @cached(max_size=10, ttl_seconds=10)
    def expensive_function(x, y):
        call_count[0] += 1
        return x + y

    # First call - should compute
    result1 = expensive_function(1, 2)
    assert result1 == 3
    assert call_count[0] == 1

    # Second call with same args - should use cache
    result2 = expensive_function(1, 2)
    assert result2 == 3
    assert call_count[0] == 1  # Not incremented

    # Different args - should compute
    result3 = expensive_function(2, 3)
    assert result3 == 5
    assert call_count[0] == 2


def test_cached_decorator_with_kwargs():
    """Test @cached decorator with keyword arguments."""
    @cached(max_size=10, ttl_seconds=10)
    def func(x, y=10):
        return x + y

    result1 = func(5)
    result2 = func(5)  # Should hit cache
    result3 = func(5, y=20)  # Different kwargs, should miss

    assert result1 == 15
    assert result2 == 15
    assert result3 == 25


def test_cached_decorator_cache_management():
    """Test cache management methods on decorated function."""
    @cached(max_size=10, ttl_seconds=10)
    def func(x):
        return x * 2

    func(1)
    func(2)

    # Get stats
    stats = func.cache_stats()
    assert stats["size"] == 2

    # Clear cache
    func.cache_clear()
    stats = func.cache_stats()
    assert stats["size"] == 0


def test_global_caches():
    """Test global cache accessors."""
    seq_cache = get_sequence_cache()
    assert seq_cache is not None
    assert isinstance(seq_cache, BoundedTTLCache)

    transform_cache = get_transform_cache()
    assert transform_cache is not None
    assert isinstance(transform_cache, BoundedTTLCache)

    # Should return same instance
    seq_cache2 = get_sequence_cache()
    assert seq_cache is seq_cache2


def test_cache_validation():
    """Test cache parameter validation."""
    with pytest.raises(ValueError, match="max_size must be at least 1"):
        BoundedTTLCache(max_size=0, ttl_seconds=10)

    with pytest.raises(ValueError, match="ttl_seconds must be positive"):
        BoundedTTLCache(max_size=10, ttl_seconds=0)

    with pytest.raises(ValueError, match="ttl_seconds must be positive"):
        BoundedTTLCache(max_size=10, ttl_seconds=-1)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
