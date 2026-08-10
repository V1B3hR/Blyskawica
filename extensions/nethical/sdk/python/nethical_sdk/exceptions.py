"""SDK exceptions for Nethical Python SDK.

These exceptions provide structured error handling for
API interactions.
"""

from __future__ import annotations

from typing import Any


class NethicalError(Exception):
    """Base exception for Nethical SDK errors."""

    def __init__(
        self,
        message: str,
        request_id: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.request_id = request_id
        self.details = details or {}

    def __str__(self) -> str:
        parts = [self.message]
        if self.request_id:
            parts.append(f"(request_id: {self.request_id})")
        return " ".join(parts)


class AuthenticationError(NethicalError):
    """Raised when authentication fails.
    
    This can occur when:
    - API key is missing
    - API key is invalid
    - API key has expired
    - Insufficient permissions
    """  # noqa: W293
    pass


class RateLimitError(NethicalError):
    """Raised when rate limit is exceeded.
    
    Contains information about when to retry.
    """  # noqa: W293

    def __init__(
        self,
        message: str,
        retry_after: int | None = None,
        limit: int | None = None,
        remaining: int | None = None,
        reset_at: str | None = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after
        self.limit = limit
        self.remaining = remaining
        self.reset_at = reset_at


class ValidationError(NethicalError):
    """Raised when request validation fails.
    
    Contains details about which fields failed validation.
    """  # noqa: W293

    def __init__(
        self,
        message: str,
        field_errors: dict[str, list[str]] | None = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.field_errors = field_errors or {}


class ServerError(NethicalError):
    """Raised when the server encounters an error.
    
    This indicates a problem on the server side that may
    be transient.
    """  # noqa: W293

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.status_code = status_code


class TimeoutError(NethicalError):
    """Raised when a request times out."""
    pass


class ConnectionError(NethicalError):
    """Raised when connection to the server fails."""
    pass


class DecisionBlockedError(NethicalError):
    """Raised when a decision results in BLOCK or TERMINATE.
    
    This is a convenience exception for when you want to
    treat blocked decisions as errors.
    """  # noqa: W293

    def __init__(
        self,
        message: str,
        decision: str,
        reason: str,
        violations: list[dict] | None = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.decision = decision
        self.reason = reason
        self.violations = violations or []
