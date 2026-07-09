"""Secrets sanitizer to prevent secrets from appearing in logs and outputs."""

import re
from typing import Any


class SecretsSanitizer:
    """
    Sanitizer to mask secrets in logs and outputs.

    Detects and masks:
    - API keys
    - Tokens
    - Passwords
    - Secret keys
    - Connection strings
    """

    # Patterns for detecting secrets
    SECRET_PATTERNS = [
        # Generic API keys and tokens
        (r"api[_-]?key['\"]?\s*[:=]\s*['\"]?([a-zA-Z0-9_\-]{20,})", "API_KEY"),
        (r"token['\"]?\s*[:=]\s*['\"]?([a-zA-Z0-9_\-\.]{20,})", "TOKEN"),
        (r"bearer\s+([a-zA-Z0-9_\-\.]{20,})", "BEARER_TOKEN"),
        # Passwords
        (r"password['\"]?\s*[:=]\s*['\"]?([^\s'\"]{8,})", "PASSWORD"),
        (r"passwd['\"]?\s*[:=]\s*['\"]?([^\s'\"]{8,})", "PASSWORD"),
        (r"pwd['\"]?\s*[:=]\s*['\"]?([^\s'\"]{8,})", "PASSWORD"),
        # Secret keys
        (r"secret[_-]?key['\"]?\s*[:=]\s*['\"]?([a-zA-Z0-9_\-]{20,})", "SECRET_KEY"),
        (r"secret['\"]?\s*[:=]\s*['\"]?([a-zA-Z0-9_\-]{20,})", "SECRET"),
        # Database connection strings
        (r"postgresql://[^:]+:([^@]+)@", "DB_PASSWORD"),
        (r"mysql://[^:]+:([^@]+)@", "DB_PASSWORD"),
        (r"mongodb://[^:]+:([^@]+)@", "DB_PASSWORD"),
        # AWS keys
        (r"AKIA[0-9A-Z]{16}", "AWS_ACCESS_KEY"),
        (r"aws_secret_access_key['\"]?\s*[:=]\s*['\"]?([a-zA-Z0-9/+=]{40})", "AWS_SECRET_KEY"),
        # JWT tokens
        (r"eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+", "JWT_TOKEN"),
        # GitHub tokens
        (r"gh[ps]_[a-zA-Z0-9]{36,}", "GITHUB_TOKEN"),
        # Slack tokens
        (r"xox[baprs]-[a-zA-Z0-9-]+", "SLACK_TOKEN"),
        # Generic long alphanumeric strings that look like secrets
        (r"['\"]([a-zA-Z0-9_\-]{32,})['\"]", "POSSIBLE_SECRET"),
    ]

    def __init__(self, mask_char: str = "*", min_reveal: int = 4):
        """
        Initialize the sanitizer.

        Args:
            mask_char: Character to use for masking
            min_reveal: Minimum number of characters to reveal at start/end
        """
        self.mask_char = mask_char
        self.min_reveal = min_reveal
        self._compiled_patterns = [(re.compile(pattern, re.IGNORECASE), name) for pattern, name in self.SECRET_PATTERNS]

    def sanitize_string(self, text: str) -> str:
        """
        Sanitize a string by masking detected secrets.

        Args:
            text: String to sanitize

        Returns:
            Sanitized string with secrets masked
        """
        if not text:
            return text

        sanitized = text
        for pattern, secret_type in self._compiled_patterns:
            sanitized = pattern.sub(lambda m: self._mask_secret(m.group(0), secret_type), sanitized)

        return sanitized

    def _mask_secret(self, secret: str, secret_type: str) -> str:
        """
        Mask a secret value.

        Args:
            secret: Secret value to mask
            secret_type: Type of secret

        Returns:
            Masked secret
        """
        if len(secret) <= self.min_reveal * 2:
            return self.mask_char * len(secret)

        # Show first and last few characters
        visible_chars = self.min_reveal
        masked_length = len(secret) - (visible_chars * 2)

        return f"{secret[:visible_chars]}{self.mask_char * masked_length}{secret[-visible_chars:]}"

    def sanitize_dict(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Recursively sanitize a dictionary.

        Args:
            data: Dictionary to sanitize

        Returns:
            Sanitized dictionary
        """
        if not isinstance(data, dict):
            return data

        sanitized = {}
        for key, value in data.items():
            # Check if key suggests it's a secret
            key_lower = key.lower()
            is_secret_key = any(
                secret_word in key_lower for secret_word in ["password", "secret", "token", "key", "credential", "auth"]
            )

            if is_secret_key and isinstance(value, str):
                # Mask the entire value
                sanitized[key] = self._mask_value(value)
            elif isinstance(value, dict):
                # Recursively sanitize nested dicts
                sanitized[key] = self.sanitize_dict(value)
            elif isinstance(value, list):
                # Sanitize list items
                sanitized[key] = [self.sanitize_dict(item) if isinstance(item, dict) else item for item in value]
            elif isinstance(value, str):
                # Sanitize string values
                sanitized[key] = self.sanitize_string(value)
            else:
                sanitized[key] = value

        return sanitized

    def _mask_value(self, value: str) -> str:
        """
        Mask a secret value completely.

        Args:
            value: Value to mask

        Returns:
            Masked value
        """
        if not value:
            return value

        if len(value) <= 8:
            return self.mask_char * len(value)

        # Show only first 4 characters
        return f"{value[:4]}{self.mask_char * (len(value) - 4)}"

    def sanitize_list(self, items: list[Any]) -> list[Any]:
        """
        Sanitize a list of items.

        Args:
            items: List to sanitize

        Returns:
            Sanitized list
        """
        sanitized = []
        for item in items:
            if isinstance(item, dict):
                sanitized.append(self.sanitize_dict(item))
            elif isinstance(item, str):
                sanitized.append(self.sanitize_string(item))
            elif isinstance(item, list):
                sanitized.append(self.sanitize_list(item))
            else:
                sanitized.append(item)

        return sanitized


# Global sanitizer instance
_sanitizer = SecretsSanitizer()


def sanitize_string(text: str) -> str:
    """
    Sanitize a string using the global sanitizer.

    Args:
        text: String to sanitize

    Returns:
        Sanitized string
    """
    return _sanitizer.sanitize_string(text)


def sanitize_dict(data: dict[str, Any]) -> dict[str, Any]:
    """
    Sanitize a dictionary using the global sanitizer.

    Args:
        data: Dictionary to sanitize

    Returns:
        Sanitized dictionary
    """
    return _sanitizer.sanitize_dict(data)


def sanitize_list(items: list[Any]) -> list[Any]:
    """
    Sanitize a list using the global sanitizer.

    Args:
        items: List to sanitize

    Returns:
        Sanitized list
    """
    return _sanitizer.sanitize_list(items)
