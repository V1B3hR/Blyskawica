import time
import threading
import logging
from collections import OrderedDict
from functools import wraps
from typing import Any, Callable, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class BoundedTTLCache:
    """
    A simple thread-safe bounded LRU cache with per-item TTL support and statistics.
    """

    def __init__(self, max_size: int = 128, ttl_seconds: float = 60.0, logger_obj: Optional[logging.Logger] = None):
        if max_size < 1:
            raise ValueError("max_size must be at least 1")
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")

        self.logger = logger_obj or logging.getLogger(__name__)
        self.max_size = max_size
        self.default_ttl = float(ttl_seconds)

        # OrderedDict maps key -> (value, expiry_ts)
        self._store: "OrderedDict[Any, Tuple[Any, float]]" = OrderedDict()
        self._lock = threading.RLock()

        # Stats
        self._hits = 0
        self._misses = 0

    # Internal helpers

    def _now(self) -> float:
        return time.time()

    def _is_expired(self, expiry_ts: float) -> bool:
        return expiry_ts <= self._now()

    # Public API expected by tests

    def set(self, key: Any, value: Any, ttl_seconds: Optional[float] = None) -> None:
        """Set value for key with optional custom TTL. Moves key to end (MRU)."""
        ttl = float(ttl_seconds) if ttl_seconds is not None else self.default_ttl
        expiry = self._now() + ttl
        with self._lock:
            if key in self._store:
                self.logger.debug("Updating existing key in cache: %r", key)
                # remove then re-insert to move to end
                del self._store[key]
            else:
                self.logger.debug("Inserting new key in cache: %r", key)
            self._store[key] = (value, expiry)

            # Evict LRU items if we're over capacity
            while len(self._store) > self.max_size:
                evicted_key, _ = self._store.popitem(last=False)
                self.logger.debug("Evicted LRU key due to capacity: %r", evicted_key)

    def get(self, key: Any) -> Optional[Any]:
        """Get value for key or None if missing/expired. Access moves key to end (MRU) if present and not expired."""
        with self._lock:
            item = self._store.get(key)
            if item is None:
                self._misses += 1
                self.logger.debug("Cache miss for key: %r", key)
                return None

            value, expiry = item
            if self._is_expired(expiry):
                # remove expired entry
                self.logger.debug("Cache entry expired for key: %r", key)
                del self._store[key]
                self._misses += 1
                return None

            # Move to end (most recently used)
            del self._store[key]
            self._store[key] = (value, expiry)
            self._hits += 1
            self.logger.debug("Cache hit for key: %r", key)
            return value

    def delete(self, key: Any) -> bool:
        """Delete key from cache. Return True if removed, False if not present."""
        with self._lock:
            if key in self._store:
                del self._store[key]
                self.logger.debug("Deleted key from cache: %r", key)
                return True
            self.logger.debug("Attempted to delete non-existent key: %r", key)
            return False

    def clear(self) -> None:
        """Clear all entries from cache."""
        with self._lock:
            self._store.clear()
            self.logger.debug("Cache cleared.")

    def cleanup_expired(self) -> int:
        """
        Remove expired entries and return the number removed.
        This does a full scan of entries; acceptable for tests and moderate sizes.
        """
        removed = 0
        now = self._now()
        with self._lock:
            keys_to_remove = [k for k, (_, exp) in self._store.items() if exp <= now]
            for k in keys_to_remove:
                del self._store[k]
                removed += 1
                self.logger.debug("Removed expired key during cleanup: %r", k)
        self.logger.debug("cleanup_expired removed %d entries", removed)
        return removed

    def get_stats(self) -> Dict[str, Any]:
        """Return dictionary with statistics expected by tests."""
        with self._lock:
            size = len(self._store)
            hits = self._hits
            misses = self._misses
        total_requests = hits + misses
        hit_rate_percent = (hits / total_requests * 100.0) if total_requests > 0 else 0.0
        stats = {
            "size": size,
            "max_size": self.max_size,
            "hits": hits,
            "misses": misses,
            "total_requests": total_requests,
            "hit_rate_percent": hit_rate_percent,
        }
        self.logger.debug("Cache stats: %s", stats)
        return stats

    def reset_stats(self) -> None:
        with self._lock:
            self._hits = 0
            self._misses = 0
        self.logger.debug("Cache statistics reset.")


# Decorator factory

def _make_key(args: Tuple[Any, ...], kwargs: Dict[str, Any]) -> Tuple:
    """
    Produce a hashable key from function arguments.
    Uses tuple(args) + tuple(sorted(kwargs.items())) so that kwargs ordering is normalized.
    """
    if kwargs:
        items = tuple(sorted(kwargs.items()))
        return tuple(args) + items
    return tuple(args)


def cached(max_size: int = 128, ttl_seconds: float = 60.0):
    """
    Decorator that caches function results in a BoundedTTLCache instance attached to the wrapper.
    Provides wrapper.cache_clear() and wrapper.cache_stats() for test management.
    """

    def decorator(func: Callable):
        cache = BoundedTTLCache(max_size=max_size, ttl_seconds=ttl_seconds, logger_obj=logger)

        @wraps(func)
        def wrapper(*args, **kwargs):
            key = _make_key(args, kwargs)
            result = cache.get(key)
            if result is not None:
                return result
            # compute and store
            value = func(*args, **kwargs)
            cache.set(key, value)
            return value

        # Attach management helpers expected in tests
        def cache_clear():
            cache.clear()

        def cache_stats():
            return cache.get_stats()

        wrapper.cache_clear = cache_clear
        wrapper.cache_stats = cache_stats
        wrapper._cache = cache  # expose underlying cache if needed
        return wrapper

    return decorator


# Global caches for get_sequence_cache and get_transform_cache

_sequence_cache: Optional[BoundedTTLCache] = None
_transform_cache: Optional[BoundedTTLCache] = None
_sequence_lock = threading.Lock()
_transform_lock = threading.Lock()


def get_sequence_cache() -> BoundedTTLCache:
    global _sequence_cache
    if _sequence_cache is None:
        with _sequence_lock:
            if _sequence_cache is None:
                # default capacity and TTL chosen to match reasonable defaults in tests
                _sequence_cache = BoundedTTLCache(max_size=1024, ttl_seconds=300.0, logger_obj=logger)
                logger.debug("Created global sequence cache")
    return _sequence_cache


def get_transform_cache() -> BoundedTTLCache:
    global _transform_cache
    if _transform_cache is None:
        with _transform_lock:
            if _transform_cache is None:
                _transform_cache = BoundedTTLCache(max_size=1024, ttl_seconds=300.0, logger_obj=logger)
                logger.debug("Created global transform cache")
    return _transform_cache
