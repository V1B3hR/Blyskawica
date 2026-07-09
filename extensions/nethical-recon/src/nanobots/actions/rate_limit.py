"""
Rate Limiting Action - Defensive nanobot that limits request rates.

Part of the defensive mode (🛡️ antibody behavior).
"""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any

from ..base import ActionResult, ActionStatus, ActionType, BaseNanobot, NanobotMode


class RateLimiterNanobot(BaseNanobot):
    """
    Nanobot that automatically applies rate limiting to suspicious sources.

    Tracks request rates and applies throttling when thresholds are exceeded.
    """

    def __init__(self, nanobot_id: str = "rate_limiter", config: dict[str, Any] | None = None):
        """
        Initialize rate limiter nanobot.

        Args:
            nanobot_id: Unique identifier
            config: Configuration options:
                - requests_per_minute: Default rate limit (default: 60)
                - burst_threshold: Burst detection threshold (default: 100)
                - time_window: Time window in seconds (default: 60)
        """
        super().__init__(nanobot_id, NanobotMode.DEFENSIVE, config)

        self.requests_per_minute = self.config.get("requests_per_minute", 60)
        self.burst_threshold = self.config.get("burst_threshold", 100)
        self.time_window = self.config.get("time_window", 60)

        # Track rate limits per source
        self.rate_limits: dict[str, dict[str, Any]] = {}
        self.request_history: dict[str, list[datetime]] = defaultdict(list)

    def can_handle(self, event: dict[str, Any]) -> bool:
        """Check if this event is related to request rate"""
        return "source_ip" in event or "source" in event

    def assess_threat(self, event: dict[str, Any]) -> float:
        """
        Assess threat level based on request rate patterns.

        Factors considered:
        - Current request rate
        - Burst detection
        - Historical behavior
        """
        source = event.get("source_ip") or event.get("source")
        if not source:
            return 0.0

        base_confidence = event.get("confidence", 0.5)

        # Get recent requests from this source
        now = datetime.now()
        recent_requests = [
            req_time
            for req_time in self.request_history.get(source, [])
            if (now - req_time).total_seconds() <= self.time_window
        ]

        request_count = len(recent_requests)
        confidence = base_confidence

        # High request rate
        rate_per_minute = (request_count / self.time_window) * 60
        if rate_per_minute > self.burst_threshold:
            confidence += 0.3
        elif rate_per_minute > self.requests_per_minute * 2:
            confidence += 0.2
        elif rate_per_minute > self.requests_per_minute:
            confidence += 0.1

        # Burst detection (many requests in short time)
        burst_window = 10  # seconds
        burst_requests = [req_time for req_time in recent_requests if (now - req_time).total_seconds() <= burst_window]
        if len(burst_requests) > self.requests_per_minute / 6:  # More than 10 req/sec
            confidence += 0.2

        # Already rate limited source making more requests
        if source in self.rate_limits:
            confidence += 0.15

        return min(confidence, 1.0)

    def execute_action(self, event: dict[str, Any], confidence: float) -> ActionResult:
        """
        Apply rate limiting to the source.

        Args:
            event: Event containing source to rate limit
            confidence: Confidence level

        Returns:
            ActionResult with rate limiting details
        """
        source = event.get("source_ip") or event.get("source")

        if not source:
            return ActionResult(
                action_type=ActionType.RATE_LIMIT,
                status=ActionStatus.FAILED,
                confidence=confidence,
                error_message="No source found in event",
            )

        # Track this request
        now = datetime.now()
        self.request_history[source].append(now)

        # Clean old requests
        self._clean_old_requests(source, now)

        # Calculate current rate
        recent_requests = self.request_history[source]
        request_count = len(recent_requests)
        rate_per_minute = (request_count / self.time_window) * 60

        # Determine rate limit to apply
        if rate_per_minute > self.burst_threshold:
            # Severe limiting - 1 request per 5 seconds
            limit = 12  # requests per minute
            duration_minutes = 15
        elif rate_per_minute > self.requests_per_minute * 2:
            # Moderate limiting - 1 request per 2 seconds
            limit = 30
            duration_minutes = 10
        else:
            # Light limiting - normal rate
            limit = self.requests_per_minute
            duration_minutes = 5

        # Apply rate limit
        expiry = now + timedelta(minutes=duration_minutes)
        self.rate_limits[source] = {
            "limit": limit,
            "expiry": expiry,
            "applied_at": now,
            "current_rate": rate_per_minute,
        }

        return ActionResult(
            action_type=ActionType.RATE_LIMIT,
            status=ActionStatus.SUCCESS,
            confidence=confidence,
            details={
                "source": source,
                "rate_limit": limit,
                "duration_minutes": duration_minutes,
                "current_rate": rate_per_minute,
                "request_count": request_count,
                "expiry": expiry.isoformat(),
            },
        )

    def _clean_old_requests(self, source: str, now: datetime):
        """Remove requests older than time window"""
        cutoff = now - timedelta(seconds=self.time_window)
        self.request_history[source] = [req_time for req_time in self.request_history[source] if req_time > cutoff]

    def is_rate_limited(self, source: str) -> bool:
        """
        Check if a source is currently rate limited.

        Args:
            source: Source identifier (IP or other)

        Returns:
            True if rate limited
        """
        if source not in self.rate_limits:
            return False

        limit_info = self.rate_limits[source]
        if datetime.now() > limit_info["expiry"]:
            # Limit expired
            del self.rate_limits[source]
            return False

        return True

    def get_rate_limit(self, source: str) -> dict[str, Any] | None:
        """
        Get rate limit details for a source.

        Args:
            source: Source identifier

        Returns:
            Rate limit details or None
        """
        if not self.is_rate_limited(source):
            return None

        return self.rate_limits[source].copy()

    def remove_rate_limit(self, source: str) -> bool:
        """
        Remove rate limit for a source.

        Args:
            source: Source identifier

        Returns:
            True if removed
        """
        if source in self.rate_limits:
            del self.rate_limits[source]
            return True
        return False

    def get_all_rate_limits(self) -> dict[str, dict[str, Any]]:
        """Get all active rate limits"""
        # Clean expired limits
        now = datetime.now()
        expired = [source for source, info in self.rate_limits.items() if now > info["expiry"]]
        for source in expired:
            del self.rate_limits[source]

        return self.rate_limits.copy()

    def clear_all_limits(self) -> int:
        """
        Clear all rate limits.

        Returns:
            Number of limits cleared
        """
        count = len(self.rate_limits)
        self.rate_limits.clear()
        self.request_history.clear()
        return count
