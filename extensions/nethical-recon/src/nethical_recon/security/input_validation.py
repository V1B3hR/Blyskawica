"""Input validation and sanitization for OWASP compliance.

This module provides comprehensive input validation and sanitization
to prevent common security vulnerabilities like injection attacks, XSS,
SSRF, and other OWASP Top 10 vulnerabilities.
"""

import ipaddress
import re
import urllib.parse
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


class ValidationError(Exception):
    """Exception raised when input validation fails."""

    pass


class InputType(Enum):
    """Types of inputs that can be validated."""

    IP_ADDRESS = "ip_address"
    DOMAIN = "domain"
    URL = "url"
    EMAIL = "email"
    CIDR = "cidr"
    PORT = "port"
    ALPHANUMERIC = "alphanumeric"
    FILENAME = "filename"
    PATH = "path"
    SQL_SAFE = "sql_safe"


@dataclass
class SanitizationResult:
    """Result of input sanitization."""

    original: str
    sanitized: str
    was_modified: bool
    removed_chars: list[str]
    validation_passed: bool
    error_message: Optional[str] = None


class InputValidator:
    """Validates and sanitizes user inputs according to OWASP guidelines.

    Implements OWASP ASVS requirements for input validation:
    - V5.1: Input Validation Requirements
    - V5.2: Sanitization and Sandboxing Requirements
    - V5.3: Output Encoding and Injection Prevention Requirements
    """

    # Regex patterns for validation
    DOMAIN_PATTERN = re.compile(
        r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$"
    )
    EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    ALPHANUMERIC_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")
    FILENAME_PATTERN = re.compile(r"^[a-zA-Z0-9._-]+$")

    # Dangerous characters for injection prevention
    SQL_DANGEROUS = ["'", '"', ";", "--", "/*", "*/", "xp_", "sp_", "exec", "execute", "union", "select", "insert"]
    COMMAND_DANGEROUS = [";", "|", "&", "$", "`", "\n", "\r", ">", "<"]
    PATH_DANGEROUS = ["../", "..\\", "~", "$"]

    def __init__(self, strict_mode: bool = True):
        """Initialize validator.

        Args:
            strict_mode: If True, applies stricter validation rules
        """
        self.strict_mode = strict_mode

    def validate_ip_address(self, ip: str) -> bool:
        """Validate IP address (IPv4 or IPv6).

        Args:
            ip: IP address string to validate

        Returns:
            True if valid IP address

        Raises:
            ValidationError: If IP is invalid
        """
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError as e:
            raise ValidationError(f"Invalid IP address: {ip}") from e

    def validate_cidr(self, cidr: str) -> bool:
        """Validate CIDR notation.

        Args:
            cidr: CIDR string to validate (e.g., '192.168.1.0/24')

        Returns:
            True if valid CIDR

        Raises:
            ValidationError: If CIDR is invalid
        """
        try:
            ipaddress.ip_network(cidr, strict=False)
            return True
        except ValueError as e:
            raise ValidationError(f"Invalid CIDR notation: {cidr}") from e

    def validate_domain(self, domain: str) -> bool:
        """Validate domain name.

        Args:
            domain: Domain name to validate

        Returns:
            True if valid domain

        Raises:
            ValidationError: If domain is invalid
        """
        if not domain or len(domain) > 253:
            raise ValidationError(f"Invalid domain length: {domain}")

        if not self.DOMAIN_PATTERN.match(domain):
            raise ValidationError(f"Invalid domain format: {domain}")

        return True

    def validate_url(self, url: str, allowed_schemes: Optional[list[str]] = None) -> bool:
        """Validate URL and prevent SSRF attacks.

        Args:
            url: URL to validate
            allowed_schemes: List of allowed schemes (default: ['http', 'https'])

        Returns:
            True if valid URL

        Raises:
            ValidationError: If URL is invalid or potentially dangerous
        """
        if allowed_schemes is None:
            allowed_schemes = ["http", "https"]

        try:
            parsed = urllib.parse.urlparse(url)

            # Check scheme
            if parsed.scheme not in allowed_schemes:
                raise ValidationError(f"URL scheme not allowed: {parsed.scheme}")

            # Check for empty netloc
            if not parsed.netloc:
                raise ValidationError("URL must have a hostname")

            # Prevent localhost/private IP access (SSRF prevention)
            if self.strict_mode:
                hostname = parsed.hostname
                if hostname in ["localhost", "127.0.0.1", "::1"]:
                    raise ValidationError("Localhost URLs not allowed")

                # Check if hostname is a private IP
                try:
                    ip = ipaddress.ip_address(hostname)
                    if ip.is_private or ip.is_loopback or ip.is_reserved:
                        raise ValidationError(f"Private/reserved IP not allowed: {hostname}")
                except ValueError:
                    # Not an IP, check domain
                    pass

            return True
        except Exception as e:
            raise ValidationError(f"Invalid URL: {url}") from e

    def validate_email(self, email: str) -> bool:
        """Validate email address.

        Args:
            email: Email address to validate

        Returns:
            True if valid email

        Raises:
            ValidationError: If email is invalid
        """
        if not email or len(email) > 254:
            raise ValidationError(f"Invalid email length: {email}")

        if not self.EMAIL_PATTERN.match(email):
            raise ValidationError(f"Invalid email format: {email}")

        return True

    def validate_port(self, port: int) -> bool:
        """Validate port number.

        Args:
            port: Port number to validate

        Returns:
            True if valid port

        Raises:
            ValidationError: If port is invalid
        """
        if not isinstance(port, int) or port < 1 or port > 65535:
            raise ValidationError(f"Invalid port number: {port}")

        return True

    def sanitize_sql_input(self, input_str: str) -> SanitizationResult:
        """Sanitize input to prevent SQL injection.

        Args:
            input_str: Input string to sanitize

        Returns:
            SanitizationResult with sanitized output
        """
        original = input_str
        sanitized = input_str
        removed = []

        # Remove dangerous SQL keywords and characters
        for dangerous in self.SQL_DANGEROUS:
            if dangerous.lower() in sanitized.lower():
                sanitized = sanitized.replace(dangerous, "")
                removed.append(dangerous)

        # Escape remaining single quotes
        sanitized = sanitized.replace("'", "''")

        return SanitizationResult(
            original=original,
            sanitized=sanitized,
            was_modified=original != sanitized,
            removed_chars=removed,
            validation_passed=len(removed) == 0,
        )

    def sanitize_command_input(self, input_str: str) -> SanitizationResult:
        """Sanitize input to prevent command injection.

        Args:
            input_str: Input string to sanitize

        Returns:
            SanitizationResult with sanitized output
        """
        original = input_str
        sanitized = input_str
        removed = []

        # Remove dangerous command characters
        for dangerous in self.COMMAND_DANGEROUS:
            if dangerous in sanitized:
                sanitized = sanitized.replace(dangerous, "")
                removed.append(dangerous)

        return SanitizationResult(
            original=original,
            sanitized=sanitized,
            was_modified=original != sanitized,
            removed_chars=removed,
            validation_passed=len(removed) == 0,
        )

    def sanitize_path(self, path: str) -> SanitizationResult:
        """Sanitize file path to prevent directory traversal.

        Args:
            path: File path to sanitize

        Returns:
            SanitizationResult with sanitized output
        """
        original = path
        sanitized = path
        removed = []

        # Remove dangerous path components
        for dangerous in self.PATH_DANGEROUS:
            if dangerous in sanitized:
                sanitized = sanitized.replace(dangerous, "")
                removed.append(dangerous)

        # Remove leading/trailing slashes
        sanitized = sanitized.strip("/\\")

        return SanitizationResult(
            original=original,
            sanitized=sanitized,
            was_modified=original != sanitized,
            removed_chars=removed,
            validation_passed=len(removed) == 0,
        )

    def sanitize_alphanumeric(self, input_str: str) -> SanitizationResult:
        """Sanitize to allow only alphanumeric characters.

        Args:
            input_str: Input string to sanitize

        Returns:
            SanitizationResult with sanitized output
        """
        original = input_str
        sanitized = re.sub(r"[^a-zA-Z0-9_-]", "", input_str)
        removed = [c for c in original if c not in sanitized]

        return SanitizationResult(
            original=original,
            sanitized=sanitized,
            was_modified=original != sanitized,
            removed_chars=removed,
            validation_passed=original == sanitized,
        )

    def validate_and_sanitize(self, input_str: str, input_type: InputType) -> SanitizationResult:
        """Validate and sanitize input based on type.

        Args:
            input_str: Input string to validate and sanitize
            input_type: Type of input for validation

        Returns:
            SanitizationResult with validation and sanitization results
        """
        try:
            if input_type == InputType.IP_ADDRESS:
                self.validate_ip_address(input_str)
                return SanitizationResult(
                    original=input_str,
                    sanitized=input_str,
                    was_modified=False,
                    removed_chars=[],
                    validation_passed=True,
                )
            elif input_type == InputType.DOMAIN:
                self.validate_domain(input_str)
                return SanitizationResult(
                    original=input_str,
                    sanitized=input_str,
                    was_modified=False,
                    removed_chars=[],
                    validation_passed=True,
                )
            elif input_type == InputType.URL:
                self.validate_url(input_str)
                return SanitizationResult(
                    original=input_str,
                    sanitized=input_str,
                    was_modified=False,
                    removed_chars=[],
                    validation_passed=True,
                )
            elif input_type == InputType.EMAIL:
                self.validate_email(input_str)
                return SanitizationResult(
                    original=input_str,
                    sanitized=input_str,
                    was_modified=False,
                    removed_chars=[],
                    validation_passed=True,
                )
            elif input_type == InputType.CIDR:
                self.validate_cidr(input_str)
                return SanitizationResult(
                    original=input_str,
                    sanitized=input_str,
                    was_modified=False,
                    removed_chars=[],
                    validation_passed=True,
                )
            elif input_type == InputType.SQL_SAFE:
                return self.sanitize_sql_input(input_str)
            elif input_type == InputType.PATH:
                return self.sanitize_path(input_str)
            elif input_type == InputType.ALPHANUMERIC:
                return self.sanitize_alphanumeric(input_str)
            else:
                return SanitizationResult(
                    original=input_str,
                    sanitized=input_str,
                    was_modified=False,
                    removed_chars=[],
                    validation_passed=True,
                )
        except ValidationError as e:
            return SanitizationResult(
                original=input_str,
                sanitized="",
                was_modified=True,
                removed_chars=[],
                validation_passed=False,
                error_message=str(e),
            )
