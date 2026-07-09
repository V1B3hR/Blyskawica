"""SSL/TLS certificate inspection module."""

import ssl
import socket
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class CertificateInfo:
    """SSL/TLS certificate information."""

    subject: dict
    issuer: dict
    version: int
    serial_number: str
    not_before: datetime
    not_after: datetime
    san: list[str]
    is_expired: bool
    days_until_expiry: int


class CertificateInspector:
    """Inspect SSL/TLS certificates."""

    def __init__(self, timeout: int = 5):
        self.timeout = timeout

    def get_certificate(self, hostname: str, port: int = 443) -> Optional[CertificateInfo]:
        """Retrieve and parse SSL certificate.

        Args:
            hostname: Target hostname
            port: HTTPS port (default: 443)

        Returns:
            CertificateInfo if successful, None otherwise
        """
        try:
            context = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()

            # Parse certificate
            subject = dict(x[0] for x in cert.get("subject", ()))
            issuer = dict(x[0] for x in cert.get("issuer", ()))

            # Parse dates
            not_before = datetime.strptime(cert["notBefore"], "%b %d %H:%M:%S %Y %Z")
            not_after = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")

            # Subject Alternative Names
            san = []
            for entry in cert.get("subjectAltName", []):
                if entry[0] == "DNS":
                    san.append(entry[1])

            # Check expiration
            now = datetime.now()
            is_expired = now > not_after
            days_until_expiry = (not_after - now).days

            return CertificateInfo(
                subject=subject,
                issuer=issuer,
                version=cert.get("version", 0),
                serial_number=cert.get("serialNumber", ""),
                not_before=not_before,
                not_after=not_after,
                san=san,
                is_expired=is_expired,
                days_until_expiry=days_until_expiry,
            )
        except Exception:
            return None
