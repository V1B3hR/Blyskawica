"""TLS fingerprinting module (JA3/JA4 foundation)."""

from __future__ import annotations

import hashlib
import socket
import ssl
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TLSInfo:
    """TLS/SSL information."""

    host: str
    port: int
    protocol_version: Optional[str] = None
    cipher_suite: Optional[str] = None
    certificate_subject: Optional[str] = None
    certificate_issuer: Optional[str] = None
    certificate_serial: Optional[str] = None
    certificate_not_before: Optional[str] = None
    certificate_not_after: Optional[str] = None
    san_list: list[str] = field(default_factory=list)
    ja3_hash: Optional[str] = None
    error: Optional[str] = None


class TLSFingerprinter:
    """TLS/SSL fingerprinter with JA3 foundation."""

    def __init__(self, timeout: int = 5):
        """Initialize TLS fingerprinter.

        Args:
            timeout: Connection timeout in seconds
        """
        self.timeout = timeout

    def fingerprint(self, host: str, port: int = 443) -> TLSInfo:
        """Fingerprint TLS/SSL connection.

        Args:
            host: Target host
            port: Target port (default: 443)

        Returns:
            TLSInfo object
        """
        result = TLSInfo(host=host, port=port)

        try:
            # Create SSL context
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            # Create socket and connect
            with socket.create_connection((host, port), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    # Get protocol version
                    result.protocol_version = ssock.version()

                    # Get cipher suite
                    cipher = ssock.cipher()
                    if cipher:
                        result.cipher_suite = cipher[0]

                    # Get certificate information
                    cert = ssock.getpeercert()
                    if cert:
                        result.certificate_subject = self._format_name(cert.get("subject", []))
                        result.certificate_issuer = self._format_name(cert.get("issuer", []))
                        result.certificate_serial = str(cert.get("serialNumber", ""))
                        result.certificate_not_before = cert.get("notBefore")
                        result.certificate_not_after = cert.get("notAfter")

                        # Extract Subject Alternative Names (SAN)
                        if "subjectAltName" in cert:
                            result.san_list = [item[1] for item in cert["subjectAltName"]]

                    # JA3 hash computation (foundation - simplified version)
                    # Full JA3 requires capturing TLS ClientHello details
                    # This is a placeholder for future enhancement
                    result.ja3_hash = self._compute_ja3_hash(ssock)

        except socket.timeout:
            result.error = "Connection timeout"
        except ssl.SSLError as e:
            result.error = f"SSL error: {str(e)}"
        except Exception as e:
            result.error = f"Error: {str(e)}"

        return result

    def fingerprint_multiple(self, targets: list[tuple[str, int]]) -> list[TLSInfo]:
        """Fingerprint multiple TLS endpoints.

        Args:
            targets: List of (host, port) tuples

        Returns:
            List of TLSInfo objects
        """
        results = []
        for host, port in targets:
            result = self.fingerprint(host, port)
            results.append(result)
        return results

    def _format_name(self, name_tuple: tuple) -> str:
        """Format X.509 name tuple.

        Args:
            name_tuple: Name tuple from certificate

        Returns:
            Formatted name string
        """
        if not name_tuple:
            return ""

        parts = []
        for item in name_tuple:
            if isinstance(item, tuple) and len(item) > 0:
                for subitem in item:
                    if isinstance(subitem, tuple) and len(subitem) == 2:
                        key, value = subitem
                        parts.append(f"{key}={value}")
            elif isinstance(item, tuple) and len(item) == 2:
                key, value = item
                parts.append(f"{key}={value}")

        return ", ".join(parts)

    def _compute_ja3_hash(self, ssock: ssl.SSLSocket) -> str:
        """Compute JA3 hash (simplified foundation).

        Note: Full JA3 requires capturing raw TLS ClientHello packet.
        This is a simplified version based on available information.

        Args:
            ssock: SSL socket

        Returns:
            JA3-like hash
        """
        try:
            # Get available information
            protocol = ssock.version() or ""
            cipher = ssock.cipher()
            cipher_name = cipher[0] if cipher else ""

            # Create a simple fingerprint (not true JA3)
            # True JA3 requires: TLS Version, Ciphers, Extensions, Curves, Point Formats
            # Note: MD5 is used here for JA3 compatibility (JA3 standard uses MD5)
            # This is not for cryptographic security but for fingerprint consistency
            fingerprint_string = f"{protocol}|{cipher_name}"
            ja3_hash = hashlib.md5(fingerprint_string.encode()).hexdigest()

            return ja3_hash

        except Exception:
            return ""

    def check_vulnerabilities(self, tls_info: TLSInfo) -> list[str]:
        """Check for common TLS vulnerabilities.

        Args:
            tls_info: TLS information

        Returns:
            List of vulnerability descriptions
        """
        vulnerabilities = []

        # Check for old protocols
        if tls_info.protocol_version:
            if "SSLv2" in tls_info.protocol_version or "SSLv3" in tls_info.protocol_version:
                vulnerabilities.append("Deprecated SSL protocol (SSLv2/SSLv3) - vulnerable to POODLE")
            elif "TLSv1.0" in tls_info.protocol_version or "TLSv1.1" in tls_info.protocol_version:
                vulnerabilities.append("Old TLS version (1.0/1.1) - consider upgrading to TLS 1.2+")

        # Check for weak ciphers
        if tls_info.cipher_suite:
            cipher_lower = tls_info.cipher_suite.lower()
            if "rc4" in cipher_lower:
                vulnerabilities.append("Weak cipher (RC4) detected")
            if "des" in cipher_lower and "3des" not in cipher_lower:
                vulnerabilities.append("Weak cipher (DES) detected")
            if "export" in cipher_lower:
                vulnerabilities.append("Export-grade cipher detected - vulnerable to FREAK")
            if "null" in cipher_lower:
                vulnerabilities.append("NULL cipher detected - no encryption")

        # Check certificate validity
        if tls_info.certificate_not_after:
            # Note: Would need to parse date and compare with current date
            # This is a placeholder for future enhancement
            pass

        return vulnerabilities
