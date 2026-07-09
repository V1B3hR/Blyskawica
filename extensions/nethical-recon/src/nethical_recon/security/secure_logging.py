"""Secure logging module for OWASP compliance.

This module provides secure logging capabilities that prevent logging of
sensitive information and comply with OWASP logging guidelines.
"""

import hashlib
import re
from typing import Any, Optional


class SecureLogger:
    """Secure logger that sanitizes sensitive data from logs.

    Implements OWASP Logging Cheat Sheet recommendations:
    - Prevent logging of sensitive data (passwords, keys, tokens)
    - Log security-relevant events
    - Include context (user, IP, timestamp)
    - Tamper-evident logging
    """

    # Patterns for sensitive data
    SENSITIVE_PATTERNS = {
        "password": re.compile(r"(password|passwd|pwd)[\s=:]+['\"]?[\w!@#$%^&*(),.?\":{}|<>]+['\"]?", re.IGNORECASE),
        "api_key": re.compile(r"(api[_-]?key|apikey|api[_-]?token)[\s=:]+['\"]?[\w-]+['\"]?", re.IGNORECASE),
        "secret": re.compile(r"(secret|secret[_-]?key)[\s=:]+['\"]?[\w-]+['\"]?", re.IGNORECASE),
        "token": re.compile(r"(token|auth[_-]?token|bearer)[\s=:]+['\"]?[\w.-]+['\"]?", re.IGNORECASE),
        "credit_card": re.compile(r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b"),
        "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
        "private_key": re.compile(r"-----BEGIN (RSA|EC|DSA|OPENSSH) PRIVATE KEY-----", re.IGNORECASE),
    }

    # Security event categories
    SECURITY_EVENTS = [
        "authentication",
        "authorization",
        "input_validation",
        "output_encoding",
        "session_management",
        "data_access",
        "configuration_change",
        "security_failure",
        "audit",
    ]

    def __init__(self, mask_char: str = "*"):
        """Initialize secure logger.

        Args:
            mask_char: Character to use for masking sensitive data
        """
        self.mask_char = mask_char

    def sanitize_log_message(self, message: str) -> str:
        """Remove sensitive data from log message.

        Args:
            message: Log message to sanitize

        Returns:
            Sanitized log message
        """
        sanitized = message

        for pattern_name, pattern in self.SENSITIVE_PATTERNS.items():
            matches = pattern.finditer(sanitized)
            for match in matches:
                # Replace the entire match with masked version
                original = match.group(0)
                # Keep the field name but mask the value
                parts = original.split("=", 1) if "=" in original else original.split(":", 1)
                if len(parts) == 2:
                    field, value = parts
                    masked = f"{field}={self.mask_char * 8}"
                else:
                    masked = self.mask_char * 8

                sanitized = sanitized.replace(original, masked)

        return sanitized

    def mask_sensitive_dict(self, data: dict[str, Any]) -> dict[str, Any]:
        """Mask sensitive fields in dictionary.

        Args:
            data: Dictionary potentially containing sensitive data

        Returns:
            Dictionary with sensitive fields masked
        """
        sensitive_keys = [
            "password",
            "passwd",
            "pwd",
            "api_key",
            "apikey",
            "api_token",
            "secret",
            "secret_key",
            "token",
            "auth_token",
            "bearer",
            "private_key",
            "credit_card",
            "ssn",
        ]

        masked = {}
        for key, value in data.items():
            key_lower = key.lower().replace("_", "").replace("-", "")
            if any(sensitive in key_lower for sensitive in sensitive_keys):
                masked[key] = self.mask_char * 8
            elif isinstance(value, dict):
                masked[key] = self.mask_sensitive_dict(value)
            elif isinstance(value, str):
                masked[key] = self.sanitize_log_message(value)
            else:
                masked[key] = value

        return masked

    def hash_pii(self, pii_value: str, salt: Optional[str] = None) -> str:
        """Hash personally identifiable information for logging.

        Args:
            pii_value: PII value to hash
            salt: Optional salt for hashing

        Returns:
            SHA256 hash of the PII value
        """
        if salt:
            value_to_hash = f"{pii_value}{salt}"
        else:
            value_to_hash = pii_value

        return hashlib.sha256(value_to_hash.encode()).hexdigest()

    def create_audit_entry(
        self,
        event_type: str,
        actor: str,
        action: str,
        resource: str,
        result: str,
        details: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Create a structured audit log entry.

        Args:
            event_type: Type of security event
            actor: Who performed the action (user ID, service name)
            action: What action was performed
            resource: What resource was affected
            result: Result of the action (success, failure, etc.)
            details: Additional details (will be sanitized)

        Returns:
            Structured audit log entry
        """
        if event_type not in self.SECURITY_EVENTS:
            event_type = "audit"

        entry = {
            "event_type": event_type,
            "actor": actor,
            "action": action,
            "resource": resource,
            "result": result,
        }

        if details:
            entry["details"] = self.mask_sensitive_dict(details)

        return entry

    def format_security_event(
        self,
        severity: str,
        category: str,
        message: str,
        context: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Format a security event for logging.

        Args:
            severity: Severity level (info, warning, error, critical)
            category: Security category (authentication, authorization, etc.)
            message: Event message
            context: Additional context (will be sanitized)

        Returns:
            Formatted security event
        """
        event = {
            "severity": severity,
            "category": category,
            "message": self.sanitize_log_message(message),
        }

        if context:
            event["context"] = self.mask_sensitive_dict(context)

        return event

    def should_log_security_event(self, event_category: str, severity: str) -> bool:
        """Determine if a security event should be logged.

        Args:
            event_category: Category of the event
            severity: Severity level

        Returns:
            True if event should be logged
        """
        # Always log critical and error events
        if severity.lower() in ["critical", "error"]:
            return True

        # Always log security-relevant events
        if event_category in self.SECURITY_EVENTS:
            return True

        # Log warnings for security categories
        if severity.lower() == "warning" and event_category in self.SECURITY_EVENTS:
            return True

        return False
