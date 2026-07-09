"""
API Key Rotation Manager for Cameras
Manages multiple API keys and rotates them to maximize throughput
"""

import logging
from datetime import datetime, timedelta
from typing import Any
from collections import deque


class APIKey:
    """Represents an API key with usage tracking"""

    def __init__(self, key_id: str, key_value: str, daily_limit: int | None = None):
        """
        Initialize API key

        Args:
            key_id: Unique identifier for this key
            key_value: The actual API key value
            daily_limit: Optional daily request limit
        """
        self.key_id = key_id
        self.key_value = key_value
        self.daily_limit = daily_limit

        # Usage tracking
        self.total_uses = 0
        self.uses_today = 0
        self.last_used = None
        self.daily_reset_time = datetime.now() + timedelta(days=1)

        # Status
        self.is_active = True
        self.cooldown_until = None
        self.error_count = 0

    def can_use(self) -> tuple[bool, str]:
        """
        Check if this key can be used now

        Returns:
            Tuple of (can_use, reason)
        """
        if not self.is_active:
            return False, "Key is inactive"

        # Check cooldown
        if self.cooldown_until and datetime.now() < self.cooldown_until:
            wait_seconds = (self.cooldown_until - datetime.now()).total_seconds()
            return False, f"In cooldown for {wait_seconds:.0f}s"

        # Check daily limit
        if self.daily_limit:
            # Reset counter if needed
            if datetime.now() >= self.daily_reset_time:
                self.uses_today = 0
                self.daily_reset_time = datetime.now() + timedelta(days=1)

            if self.uses_today >= self.daily_limit:
                return False, "Daily limit reached"

        return True, "OK"

    def record_use(self):
        """Record that this key was used"""
        self.total_uses += 1
        self.uses_today += 1
        self.last_used = datetime.now()

    def record_error(self):
        """Record an error for this key"""
        self.error_count += 1

        # Deactivate key after too many errors
        if self.error_count >= 5:
            self.is_active = False

    def set_cooldown(self, seconds: float):
        """Set a cooldown period for this key"""
        self.cooldown_until = datetime.now() + timedelta(seconds=seconds)

    def get_remaining_today(self) -> int | None:
        """Get remaining requests for today"""
        if self.daily_limit:
            return max(0, self.daily_limit - self.uses_today)
        return None


class APIKeyRotator:
    """
    Manages and rotates API keys to maximize throughput
    """

    def __init__(self, api_name: str):
        """
        Initialize key rotator

        Args:
            api_name: Name of the API (e.g., 'shodan', 'censys')
        """
        self.api_name = api_name
        self.logger = logging.getLogger(f"nethical.key_rotator.{api_name}")
        self._initialize_logger()

        # Keys storage
        self.keys: dict[str, APIKey] = {}
        self.key_queue: deque[str] = deque()  # Round-robin queue

        # Statistics
        self.total_rotations = 0
        self.total_requests = 0

    def _initialize_logger(self):
        """Initialize logging"""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(f"[%(asctime)s] [KeyRotator:{self.api_name}] %(levelname)s: %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def add_key(self, key_id: str, key_value: str, daily_limit: int | None = None) -> bool:
        """
        Add an API key to the rotation pool

        Args:
            key_id: Unique identifier for the key
            key_value: The actual API key
            daily_limit: Optional daily limit for this key

        Returns:
            bool: True if added successfully
        """
        if key_id in self.keys:
            self.logger.warning(f"Key {key_id} already exists")
            return False

        api_key = APIKey(key_id, key_value, daily_limit)
        self.keys[key_id] = api_key
        self.key_queue.append(key_id)

        self.logger.info(f"Added key {key_id} (daily_limit={daily_limit or 'unlimited'})")
        return True

    def remove_key(self, key_id: str) -> bool:
        """
        Remove a key from rotation

        Args:
            key_id: ID of key to remove

        Returns:
            bool: True if removed successfully
        """
        if key_id not in self.keys:
            self.logger.warning(f"Key {key_id} not found")
            return False

        del self.keys[key_id]
        try:
            self.key_queue.remove(key_id)
        except ValueError:
            pass

        self.logger.info(f"Removed key {key_id}")
        return True

    def get_next_key(self) -> APIKey | None:
        """
        Get the next available key using round-robin rotation

        Returns:
            APIKey or None if no keys available
        """
        if not self.key_queue:
            self.logger.error("No keys available")
            return None

        # Try each key in the queue
        attempts = len(self.key_queue)
        for _ in range(attempts):
            key_id = self.key_queue[0]
            key = self.keys.get(key_id)

            if not key:
                # Key was removed, clean up queue
                self.key_queue.popleft()
                continue

            can_use, reason = key.can_use()
            if can_use:
                # Rotate to back of queue
                self.key_queue.rotate(-1)
                self.total_rotations += 1
                return key
            else:
                # Try next key
                self.key_queue.rotate(-1)
                self.logger.debug(f"Key {key_id} unavailable: {reason}")

        self.logger.warning("No usable keys available")
        return None

    def use_key(self, key: APIKey) -> str:
        """
        Mark a key as used and return its value

        Args:
            key: The API key to use

        Returns:
            The API key value
        """
        key.record_use()
        self.total_requests += 1
        self.logger.debug(f"Using key {key.key_id} (uses today: {key.uses_today})")
        return key.key_value

    def get_key_value(self) -> str | None:
        """
        Get the next available key value

        Returns:
            API key value or None if no keys available
        """
        key = self.get_next_key()
        if key:
            return self.use_key(key)
        return None

    def record_error(self, key_value: str):
        """
        Record an error for a key

        Args:
            key_value: The API key that experienced an error
        """
        # Find the key by value
        for key in self.keys.values():
            if key.key_value == key_value:
                key.record_error()
                self.logger.warning(
                    f"Error recorded for key {key.key_id} " f"(errors: {key.error_count}, active: {key.is_active})"
                )
                break

    def record_rate_limit(self, key_value: str, cooldown_seconds: float = 60.0):
        """
        Record that a key hit a rate limit

        Args:
            key_value: The API key that hit the limit
            cooldown_seconds: Cooldown period in seconds
        """
        # Find the key by value
        for key in self.keys.values():
            if key.key_value == key_value:
                key.set_cooldown(cooldown_seconds)
                self.logger.warning(f"Rate limit hit for key {key.key_id}, " f"cooldown for {cooldown_seconds}s")
                break

    def get_statistics(self) -> dict[str, Any]:
        """Get rotation statistics"""
        active_keys = sum(1 for k in self.keys.values() if k.is_active)
        total_uses = sum(k.total_uses for k in self.keys.values())
        total_capacity_today = sum(k.get_remaining_today() or 0 for k in self.keys.values() if k.is_active)

        key_stats = []
        for key in self.keys.values():
            key_stats.append(
                {
                    "key_id": key.key_id,
                    "is_active": key.is_active,
                    "total_uses": key.total_uses,
                    "uses_today": key.uses_today,
                    "remaining_today": key.get_remaining_today(),
                    "error_count": key.error_count,
                    "last_used": key.last_used.isoformat() if key.last_used else None,
                }
            )

        return {
            "api_name": self.api_name,
            "total_keys": len(self.keys),
            "active_keys": active_keys,
            "total_rotations": self.total_rotations,
            "total_requests": total_requests,
            "total_uses": total_uses,
            "remaining_capacity_today": total_capacity_today,
            "keys": key_stats,
        }

    def get_available_keys_count(self) -> int:
        """Get count of currently available keys"""
        count = 0
        for key in self.keys.values():
            can_use, _ = key.can_use()
            if can_use:
                count += 1
        return count
