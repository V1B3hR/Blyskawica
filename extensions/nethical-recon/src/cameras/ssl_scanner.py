"""
SSL Scanner - X-ray Vision Camera
🕳️ Rentgen Mode - Sees through encryption

Analyzes SSL/TLS certificates and configurations:
- Certificate details
- Cipher suites
- Protocol versions
- Vulnerabilities (weak ciphers, expired certs, etc.)
"""

import socket
import ssl
from datetime import datetime
from typing import Any

from .base import BaseCamera, CameraMode


class SSLScanner(BaseCamera):
    """
    SSL/TLS analysis camera with X-ray vision

    Configuration:
        ports: List of ports to scan (default: [443, 8443])
        timeout: Connection timeout in seconds (default: 5)
        check_vulnerabilities: Check for known SSL/TLS vulnerabilities (default: True)
    """

    def __init__(self, config: dict[str, Any] = None):
        super().__init__("SSLScanner", CameraMode.XRAY, config)
        self.ports = self.config.get("ports", [443, 8443])
        self.timeout = self.config.get("timeout", 5)
        self.check_vulns = self.config.get("check_vulnerabilities", True)

    def scan(self, target: str) -> dict[str, Any]:
        """
        Scan target for SSL/TLS information

        Args:
            target: Hostname or IP address

        Returns:
            Dict with SSL/TLS analysis results
        """
        self.logger.info(f"🕳️ X-ray Vision: Scanning SSL/TLS on {target}...")

        results = {"target": target, "certificates": {}, "vulnerabilities": [], "summary": {}}

        # Scan each port
        for port in self.ports:
            try:
                self.logger.info(f"Analyzing SSL/TLS on {target}:{port}")
                cert_info = self._analyze_certificate(target, port)

                if cert_info:
                    results["certificates"][port] = cert_info

                    # Check for vulnerabilities
                    if self.check_vulns:
                        vulns = self._check_vulnerabilities(cert_info, target, port)
                        results["vulnerabilities"].extend(vulns)

            except Exception as e:
                self.logger.warning(f"Failed to analyze {target}:{port}: {e}")
                continue

        # Generate summary
        results["summary"] = self._generate_summary(results)

        return results

    def _analyze_certificate(self, hostname: str, port: int) -> dict[str, Any] | None:
        """
        Analyze SSL/TLS certificate

        Args:
            hostname: Target hostname
            port: Target port

        Returns:
            Dict with certificate information
        """
        try:
            # Create SSL context with intentionally relaxed settings for reconnaissance
            # This allows us to connect to and analyze servers with weak configurations
            # Note: This is a security scanner - we WANT to connect to insecure servers
            #       to identify and report their vulnerabilities
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            # Allow connection to servers using old TLS versions (TLSv1, TLSv1.1)
            # so we can detect and report these as vulnerabilities
            context.minimum_version = ssl.TLSVersion.TLSv1  # nosec - intentional for reconnaissance

            # Connect and get certificate
            with socket.create_connection((hostname, port), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    # Get certificate
                    cert = ssock.getpeercert()

                    # Get cipher info
                    cipher = ssock.cipher()

                    # Get protocol version
                    protocol = ssock.version()

                    # Parse certificate
                    cert_info = {
                        "subject": self._parse_dn(cert.get("subject", [])),
                        "issuer": self._parse_dn(cert.get("issuer", [])),
                        "version": cert.get("version"),
                        "serial_number": cert.get("serialNumber"),
                        "not_before": cert.get("notBefore"),
                        "not_after": cert.get("notAfter"),
                        "subject_alt_names": self._parse_san(cert.get("subjectAltName", [])),
                        "cipher": {
                            "name": cipher[0] if cipher else "Unknown",
                            "protocol": cipher[1] if cipher else "Unknown",
                            "bits": cipher[2] if cipher else 0,
                        },
                        "protocol_version": protocol,
                        "hostname": hostname,
                        "port": port,
                    }

                    # Record discovery
                    self.record_discovery(
                        "ssl_certificate", f"{hostname}:{port}", cert_info, confidence=1.0, severity="INFO"
                    )

                    return cert_info

        except ssl.SSLError as e:
            self.logger.error(f"SSL error on {hostname}:{port}: {e}")
            return None

        except TimeoutError:
            self.logger.error(f"Connection timeout on {hostname}:{port}")
            return None

        except Exception as e:
            self.logger.error(f"Failed to get certificate from {hostname}:{port}: {e}")
            return None

    def _parse_dn(self, dn_tuple: tuple) -> str:
        """Parse Distinguished Name tuple"""
        parts = []
        for rdn in dn_tuple:
            for name, value in rdn:
                parts.append(f"{name}={value}")
        return ", ".join(parts)

    def _parse_san(self, san_tuple: tuple) -> list[str]:
        """Parse Subject Alternative Names"""
        return [value for name, value in san_tuple if name == "DNS"]

    def _check_vulnerabilities(self, cert_info: dict[str, Any], hostname: str, port: int) -> list[dict[str, Any]]:
        """
        Check for SSL/TLS vulnerabilities

        Args:
            cert_info: Certificate information
            hostname: Target hostname
            port: Target port

        Returns:
            List of vulnerabilities
        """
        vulns = []

        # Check certificate expiration
        not_after = cert_info.get("not_after", "")
        if not_after:
            try:
                expiry = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
                days_until_expiry = (expiry - datetime.now()).days

                if days_until_expiry < 0:
                    vulns.append(
                        {
                            "type": "expired_certificate",
                            "severity": "CRITICAL",
                            "description": f"Certificate expired {abs(days_until_expiry)} days ago",
                            "target": f"{hostname}:{port}",
                        }
                    )
                    self.record_discovery(
                        "vulnerability",
                        f"{hostname}:{port}",
                        {"type": "expired_certificate", "days": days_until_expiry},
                        confidence=1.0,
                        severity="CRITICAL",
                    )
                elif days_until_expiry < 30:
                    vulns.append(
                        {
                            "type": "expiring_certificate",
                            "severity": "WARNING",
                            "description": f"Certificate expires in {days_until_expiry} days",
                            "target": f"{hostname}:{port}",
                        }
                    )
            except ValueError:
                pass

        # Check for weak ciphers
        cipher_name = cert_info.get("cipher", {}).get("name", "")
        weak_ciphers = ["RC4", "DES", "3DES", "MD5", "NULL", "EXPORT", "anon"]

        for weak in weak_ciphers:
            if weak.upper() in cipher_name.upper():
                vulns.append(
                    {
                        "type": "weak_cipher",
                        "severity": "CRITICAL",
                        "description": f"Weak cipher suite in use: {cipher_name}",
                        "target": f"{hostname}:{port}",
                    }
                )
                self.record_discovery(
                    "vulnerability",
                    f"{hostname}:{port}",
                    {"type": "weak_cipher", "cipher": cipher_name},
                    confidence=0.9,
                    severity="CRITICAL",
                )
                break

        # Check protocol version
        protocol = cert_info.get("protocol_version", "")
        if protocol in ["SSLv2", "SSLv3", "TLSv1", "TLSv1.1"]:
            vulns.append(
                {
                    "type": "outdated_protocol",
                    "severity": "CRITICAL" if protocol.startswith("SSL") else "WARNING",
                    "description": f"Outdated protocol in use: {protocol}",
                    "target": f"{hostname}:{port}",
                }
            )
            self.record_discovery(
                "vulnerability",
                f"{hostname}:{port}",
                {"type": "outdated_protocol", "protocol": protocol},
                confidence=1.0,
                severity="CRITICAL" if protocol.startswith("SSL") else "WARNING",
            )

        # Check key size
        cipher_bits = cert_info.get("cipher", {}).get("bits", 0)
        if cipher_bits < 128:
            vulns.append(
                {
                    "type": "weak_key_size",
                    "severity": "CRITICAL",
                    "description": f"Weak key size: {cipher_bits} bits",
                    "target": f"{hostname}:{port}",
                }
            )

        # Check for self-signed certificate (basic check)
        subject = cert_info.get("subject", "")
        issuer = cert_info.get("issuer", "")
        if subject and subject == issuer:
            vulns.append(
                {
                    "type": "self_signed_certificate",
                    "severity": "WARNING",
                    "description": "Certificate is self-signed",
                    "target": f"{hostname}:{port}",
                }
            )

        return vulns

    def _generate_summary(self, results: dict[str, Any]) -> dict[str, Any]:
        """Generate summary of findings"""
        summary = {
            "total_ports_scanned": len(self.ports),
            "ssl_enabled_ports": len(results["certificates"]),
            "total_vulnerabilities": len(results["vulnerabilities"]),
            "critical_vulnerabilities": sum(1 for v in results["vulnerabilities"] if v.get("severity") == "CRITICAL"),
            "warning_vulnerabilities": sum(1 for v in results["vulnerabilities"] if v.get("severity") == "WARNING"),
        }

        return summary

    def quick_scan(self, hostname: str, port: int = 443) -> dict[str, Any] | None:
        """
        Quick scan of a single host:port

        Args:
            hostname: Target hostname
            port: Target port (default: 443)

        Returns:
            Certificate information
        """
        return self._analyze_certificate(hostname, port)
