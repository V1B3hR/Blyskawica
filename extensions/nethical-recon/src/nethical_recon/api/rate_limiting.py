"""
Rate Limiting Middleware (slowapi + Redis)
"""

import logging
from typing import Any
from datetime import datetime, timedelta
from collections import defaultdict


class RateLimiter:
    """Rate limiter for API endpoints"""

    def __init__(self, requests_per_minute: int = 60):
        self.logger = logging.getLogger("nethical.api.rate_limiter")
        self._initialize_logger()
        self.requests_per_minute = requests_per_minute
        self.request_history: dict[str, list[datetime]] = defaultdict(list)

    def _initialize_logger(self):
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("[%(asctime)s] [RateLimiter] %(levelname)s: %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed"""
        now = datetime.now()
        cutoff = now - timedelta(minutes=1)

        # Clean old requests
        self.request_history[client_id] = [ts for ts in self.request_history[client_id] if ts > cutoff]

        # Check limit
        if len(self.request_history[client_id]) >= self.requests_per_minute:
            self.logger.warning(f"Rate limit exceeded for {client_id}")
            return False

        # Record request
        self.request_history[client_id].append(now)
        return True
