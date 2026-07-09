"""
Censys Eye - Night Vision Camera (Alternative)
🌙 Nocny Mode - Another way to see in the darkness

Uses Censys API to discover:
- Internet-wide scan data
- Certificates
- Hosts
- Services
"""

import os
from typing import Any

from .base import BaseCamera, CameraMode


class CensysEye(BaseCamera):
    """
    Censys-powered IR camera for discovering internet assets

    Configuration:
        api_id: Censys API ID (or set CENSYS_API_ID env var)
        api_secret: Censys API Secret (or set CENSYS_API_SECRET env var)
        max_results: Maximum number of results to return (default: 100)
    """

    def __init__(self, config: dict[str, Any] = None):
        super().__init__("CensysEye", CameraMode.NIGHT, config)
        self.api_id = self.config.get("api_id") or os.getenv("CENSYS_API_ID")
        self.api_secret = self.config.get("api_secret") or os.getenv("CENSYS_API_SECRET")
        self.max_results = self.config.get("max_results", 100)
        self.censys_hosts = None
        self.censys_certs = None

    def validate_config(self) -> bool:
        """Validate Censys configuration"""
        if not self.api_id or not self.api_secret:
            self.logger.error("Censys API credentials not provided. Set CENSYS_API_ID and CENSYS_API_SECRET")
            return False
        return True

    def _initialize_censys(self):
        """Initialize Censys API client"""
        if self.censys_hosts:
            return True

        try:
            from censys.search import CensysCerts, CensysHosts

            self.censys_hosts = CensysHosts(self.api_id, self.api_secret)
            self.censys_certs = CensysCerts(self.api_id, self.api_secret)
            self.logger.info("Censys API initialized successfully")
            return True
        except ImportError:
            self.logger.error("Censys library not installed. Install with: pip install censys")
            return False
        except Exception as e:
            self.logger.error(f"Failed to initialize Censys API: {e}")
            return False

    def scan(self, target: str) -> dict[str, Any]:
        """
        Scan target using Censys

        Args:
            target: IP address or search query

        Returns:
            Dict with scan results
        """
        if not self.validate_config():
            return {"error": "Invalid configuration"}

        if not self._initialize_censys():
            return {"error": "Failed to initialize Censys"}

        self.logger.info(f"🌙 Night Vision: Scanning {target} with Censys...")

        results = {"target": target, "host_info": None, "search_results": [], "total_results": 0}

        try:
            # Try to get host information if target looks like an IP
            if self._is_ip_address(target):
                results["host_info"] = self._scan_host(target)
            else:
                # Otherwise, perform a search query
                results["search_results"] = self._search_query(target)
                results["total_results"] = len(results["search_results"])

        except Exception as e:
            self.logger.error(f"Censys scan failed: {e}")
            results["error"] = str(e)

        return results

    def _is_ip_address(self, target: str) -> bool:
        """Check if target is a valid IP address"""
        import re

        ip_pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
        return bool(re.match(ip_pattern, target))

    def _scan_host(self, ip: str) -> dict[str, Any] | None:
        """
        Get detailed information about a specific host

        Args:
            ip: IP address to scan

        Returns:
            Dict with host information
        """
        try:
            host = self.censys_hosts.view(ip)

            # Extract key information
            host_info = {
                "ip": host.get("ip"),
                "autonomous_system": host.get("autonomous_system", {}).get("name", "Unknown"),
                "location": {
                    "country": host.get("location", {}).get("country", "Unknown"),
                    "city": host.get("location", {}).get("city", "Unknown"),
                    "coordinates": host.get("location", {}).get("coordinates", {}),
                },
                "last_updated": host.get("last_updated_at"),
                "services": [],
            }

            # Extract service information
            for service in host.get("services", []):
                svc = {
                    "port": service.get("port"),
                    "service_name": service.get("service_name", "Unknown"),
                    "transport_protocol": service.get("transport_protocol", "tcp"),
                    "banner": service.get("banner", "")[:200],
                }

                # Extract TLS/SSL info if available
                if "tls" in service:
                    tls = service["tls"]
                    svc["tls"] = {
                        "version": tls.get("version", {}).get("name", "Unknown"),
                        "cipher": tls.get("cipher_suite", {}).get("name", "Unknown"),
                        "certificate": {
                            "subject": tls.get("certificate", {}).get("parsed", {}).get("subject_dn", "Unknown"),
                            "issuer": tls.get("certificate", {}).get("parsed", {}).get("issuer_dn", "Unknown"),
                        },
                    }

                host_info["services"].append(svc)

                # Record discovery for each service
                self.record_discovery("service", f"{ip}:{svc['port']}", svc, confidence=1.0, severity="INFO")

            self.logger.info(f"Found {len(host_info['services'])} services on {ip}")
            return host_info

        except Exception as e:
            self.logger.error(f"Failed to get host info for {ip}: {e}")
            return None

    def _search_query(self, query: str) -> list[dict[str, Any]]:
        """
        Perform a Censys search query

        Args:
            query: Search query (e.g., "services.service_name: HTTP")

        Returns:
            List of search results
        """
        try:
            search_results = []

            # Perform search with pagination
            for page in self.censys_hosts.search(query, per_page=min(100, self.max_results)):
                for hit in page:
                    item = {
                        "ip": hit.get("ip"),
                        "autonomous_system": hit.get("autonomous_system", {}).get("name", "Unknown"),
                        "location": hit.get("location", {}),
                        "services": hit.get("services", [])[:3],  # First 3 services
                        "last_updated": hit.get("last_updated_at"),
                    }
                    search_results.append(item)

                    # Record discovery
                    self.record_discovery("exposed_host", item["ip"], item, confidence=0.95, severity="INFO")

                    if len(search_results) >= self.max_results:
                        break

                if len(search_results) >= self.max_results:
                    break

            self.logger.info(f"Found {len(search_results)} results for query: {query}")
            return search_results

        except Exception as e:
            self.logger.error(f"Search query failed: {e}")
            return []

    def search_certificates(self, query: str) -> list[dict[str, Any]]:
        """
        Search for SSL/TLS certificates

        Args:
            query: Search query (e.g., "parsed.names: example.com")

        Returns:
            List of certificates
        """
        if not self._initialize_censys():
            return []

        try:
            cert_results = []

            for page in self.censys_certs.search(query, per_page=min(100, self.max_results)):
                for cert in page:
                    item = {
                        "fingerprint": cert.get("fingerprint_sha256"),
                        "names": cert.get("parsed", {}).get("names", []),
                        "subject": cert.get("parsed", {}).get("subject_dn", "Unknown"),
                        "issuer": cert.get("parsed", {}).get("issuer_dn", "Unknown"),
                        "validity": {
                            "start": cert.get("parsed", {}).get("validity", {}).get("start"),
                            "end": cert.get("parsed", {}).get("validity", {}).get("end"),
                        },
                    }
                    cert_results.append(item)

                    # Record discovery
                    self.record_discovery("certificate", item["subject"], item, confidence=1.0, severity="INFO")

                    if len(cert_results) >= self.max_results:
                        break

                if len(cert_results) >= self.max_results:
                    break

            self.logger.info(f"Found {len(cert_results)} certificates for: {query}")
            return cert_results

        except Exception as e:
            self.logger.error(f"Certificate search failed: {e}")
            return []
