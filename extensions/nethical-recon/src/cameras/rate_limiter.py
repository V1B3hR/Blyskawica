"""
API Rate Limiter for Cameras
Respects rate limits for external APIs like Shodan and Censys
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Any
from collections import defaultdict


class RateLimitConfig:
    """Configuration for a rate limit"""

    def __init__(self, requests_per_second: float = 1.0, requests_per_day: int | None = None):
        """
        Initialize rate limit configuration

        Args:
            requests_per_second: Maximum requests per second
            requests_per_day: Optional daily request limit
        """
        self.requests_per_second = requests_per_second
        self.requests_per_day = requests_per_day
        self.min_interval = 1.0 / requests_per_second if requests_per_second > 0 else 0


class APIRateLimiter:
    """
    Rate limiter for external API calls
    Prevents exceeding API rate limits and handles backoff
    """

    def __init__(self):
        """Initialize rate limiter"""
        self.logger = logging.getLogger("nethical.rate_limiter")
        self._initialize_logger()

        # Rate limit configurations per API
        self.configs: dict[str, RateLimitConfig] = {}

        # Track API call history
        self.last_call_time: dict[str, datetime] = {}
        self.call_count_today: dict[str, int] = defaultdict(int)
        self.daily_reset_time: dict[str, datetime] = {}

        # Backoff state
        self.backoff_until: dict[str, datetime] = {}

        # Statistics
        self.total_calls: dict[str, int] = defaultdict(int)
        self.total_waits: dict[str, float] = defaultdict(float)
        self.rate_limit_hits: dict[str, int] = defaultdict(int)

        # Register default API configurations
        self._register_defaults()

    def _initialize_logger(self):
        """Initialize logging"""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("[%(asctime)s] [RateLimiter] %(levelname)s: %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def _register_defaults(self):
        """Register default rate limits for known APIs"""
        # Shodan: 1 request per second, 100 per day (free tier)
        self.register_api("shodan", RateLimitConfig(requests_per_second=1.0, requests_per_day=100))

        # Censys: 0.4 requests per second (120/hour free tier)
        self.register_api("censys", RateLimitConfig(requests_per_second=0.4, requests_per_day=None))

        # Generic API (conservative defaults)
        self.register_api("generic", RateLimitConfig(requests_per_second=0.5, requests_per_day=1000))

    def register_api(self, api_name: str, config: RateLimitConfig):
        """
        Register an API with rate limit configuration

        Args:
            api_name: Name of the API
            config: Rate limit configuration
        """
        self.configs[api_name] = config
        self.daily_reset_time[api_name] = datetime.now() + timedelta(days=1)
        self.logger.info(
            f"Registered API {api_name}: {config.requests_per_second} req/s, "
            f"{config.requests_per_day or 'unlimited'} req/day"
        )

    def can_make_request(self, api_name: str) -> tuple[bool, str]:
        """
        Check if a request can be made now

        Args:
            api_name: Name of the API

        Returns:
            Tuple of (can_proceed, reason)
        """
        if api_name not in self.configs:
            return True, "No rate limit configured"

        config = self.configs[api_name]
        now = datetime.now()

        # Check if in backoff period
        if api_name in self.backoff_until and now < self.backoff_until[api_name]:
            wait_seconds = (self.backoff_until[api_name] - now).total_seconds()
            return False, f"In backoff period, wait {wait_seconds:.1f}s"

        # Check daily limit
        if config.requests_per_day:
            # Reset daily counter if needed
            if api_name in self.daily_reset_time and now >= self.daily_reset_time[api_name]:
                self.call_count_today[api_name] = 0
                self.daily_reset_time[api_name] = now + timedelta(days=1)
                self.logger.info(f"Reset daily counter for {api_name}")

            if self.call_count_today[api_name] >= config.requests_per_day:
                return False, f"Daily limit reached ({config.requests_per_day} requests)"

        # Check per-second rate limit
        if api_name in self.last_call_time:
            time_since_last = (now - self.last_call_time[api_name]).total_seconds()
            if time_since_last < config.min_interval:
                wait_time = config.min_interval - time_since_last
                return False, f"Too soon, wait {wait_time:.2f}s"

        return True, "OK"

    def wait_if_needed(self, api_name: str) -> float:
        """
        Wait if necessary to respect rate limits

        Args:
            api_name: Name of the API

        Returns:
            Time waited in seconds
        """
        can_proceed, reason = self.can_make_request(api_name)

        if can_proceed:
            return 0.0

        # Calculate wait time
        wait_time = 0.0

        if api_name in self.configs:
            config = self.configs[api_name]

            # Check if we need to wait for rate limit
            if api_name in self.last_call_time:
                now = datetime.now()
                time_since_last = (now - self.last_call_time[api_name]).total_seconds()
                if time_since_last < config.min_interval:
                    wait_time = config.min_interval - time_since_last

            # Check backoff
            if api_name in self.backoff_until:
                now = datetime.now()
                if now < self.backoff_until[api_name]:
                    backoff_wait = (self.backoff_until[api_name] - now).total_seconds()
                    wait_time = max(wait_time, backoff_wait)

        if wait_time > 0:
            self.logger.debug(f"Waiting {wait_time:.2f}s for {api_name} rate limit")
            time.sleep(wait_time)
            self.total_waits[api_name] += wait_time

        return wait_time

    def record_request(self, api_name: str):
        """
        Record that a request was made

        Args:
            api_name: Name of the API
        """
        now = datetime.now()
        self.last_call_time[api_name] = now
        self.call_count_today[api_name] += 1
        self.total_calls[api_name] += 1

    def record_rate_limit_hit(self, api_name: str, backoff_seconds: float = 60.0):
        """
        Record that we hit a rate limit

        Args:
            api_name: Name of the API
            backoff_seconds: How long to back off
        """
        self.rate_limit_hits[api_name] += 1
        self.backoff_until[api_name] = datetime.now() + timedelta(seconds=backoff_seconds)
        self.logger.warning(f"Rate limit hit for {api_name}, backing off for {backoff_seconds}s")

    def make_request(self, api_name: str, request_func: callable, *args, **kwargs) -> Any:
        """
        Make an API request with rate limiting

        Args:
            api_name: Name of the API
            request_func: Function to call for the request
            *args, **kwargs: Arguments to pass to request_func

        Returns:
            Result of request_func
        """
        # Wait if needed
        self.wait_if_needed(api_name)

        # Make the request
        try:
            result = request_func(*args, **kwargs)
            self.record_request(api_name)
            return result
        except Exception as e:
            # Check if it's a rate limit error
            error_str = str(e).lower()
            if "rate limit" in error_str or "429" in error_str:
                self.record_rate_limit_hit(api_name)
            raise

    def get_statistics(self, api_name: str | None = None) -> dict[str, Any]:
        """
        Get rate limiter statistics

        Args:
            api_name: Optional specific API, or None for all APIs

        Returns:
            Statistics dictionary
        """
        if api_name:
            if api_name not in self.configs:
                return {}

            config = self.configs[api_name]
            remaining_today = None
            if config.requests_per_day:
                remaining_today = config.requests_per_day - self.call_count_today[api_name]

            return {
                "api_name": api_name,
                "total_calls": self.total_calls[api_name],
                "calls_today": self.call_count_today[api_name],
                "remaining_today": remaining_today,
                "total_wait_time": self.total_waits[api_name],
                "rate_limit_hits": self.rate_limit_hits[api_name],
                "requests_per_second": config.requests_per_second,
                "daily_limit": config.requests_per_day,
            }
        else:
            return {"apis": {name: self.get_statistics(name) for name in self.configs}, "total_apis": len(self.configs)}

    def reset_statistics(self, api_name: str | None = None):
        """
        Reset statistics

        Args:
            api_name: Optional specific API, or None for all
        """
        if api_name:
            self.total_calls[api_name] = 0
            self.total_waits[api_name] = 0.0
            self.rate_limit_hits[api_name] = 0
            self.logger.info(f"Reset statistics for {api_name}")
        else:
            self.total_calls.clear()
            self.total_waits.clear()
            self.rate_limit_hits.clear()
            self.logger.info("Reset all statistics")
