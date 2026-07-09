"""
Shodan Eye - Night Vision Camera
🌙 Nocny Mode - Sees hidden services in the darkness of the Internet

Uses Shodan API to discover:
- Open ports and services
- Exposed devices
- SSL certificates
- Vulnerabilities
- Geographic locations
"""

import os
from typing import Any

from .base import BaseCamera, CameraMode


class ShodanEye(BaseCamera):
    """
    Shodan-powered IR camera for discovering internet-exposed assets

    Configuration:
        api_key: Shodan API key (or set SHODAN_API_KEY env var)
        max_results: Maximum number of results to return (default: 100)
    """

    def __init__(self, config: dict[str, Any] = None):
        super().__init__("ShodanEye", CameraMode.NIGHT, config)
        self.api_key = self.config.get("api_key") or os.getenv("SHODAN_API_KEY")
        self.max_results = self.config.get("max_results", 100)
        self.shodan_api = None

    def validate_config(self) -> bool:
        """Validate Shodan configuration"""
        if not self.api_key:
            self.logger.error("Shodan API key not provided. Set 'api_key' in config or SHODAN_API_KEY env var")
            return False
        return True

    def _initialize_shodan(self):
        """Initialize Shodan API client"""
        if self.shodan_api:
            return True

        try:
            import shodan

            self.shodan_api = shodan.Shodan(self.api_key)
            self.logger.info("Shodan API initialized successfully")
            return True
        except ImportError:
            self.logger.error("Shodan library not installed. Install with: pip install shodan")
            return False
        except Exception as e:
            self.logger.error(f"Failed to initialize Shodan API: {e}")
            return False

    def scan(self, target: str) -> dict[str, Any]:
        """
        Scan target using Shodan

        Args:
            target: IP address or search query

        Returns:
            Dict with scan results
        """
        if not self.validate_config():
            return {"error": "Invalid configuration"}

        if not self._initialize_shodan():
            return {"error": "Failed to initialize Shodan"}

        self.logger.info(f"🌙 Night Vision: Scanning {target} with Shodan...")

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
            self.logger.error(f"Shodan scan failed: {e}")
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
            host = self.shodan_api.host(ip)

            # Extract key information
            host_info = {
                "ip": host.get("ip_str"),
                "organization": host.get("org", "Unknown"),
                "operating_system": host.get("os", "Unknown"),
                "ports": host.get("ports", []),
                "hostnames": host.get("hostnames", []),
                "country": host.get("country_name", "Unknown"),
                "city": host.get("city", "Unknown"),
                "last_update": host.get("last_update"),
                "vulns": host.get("vulns", []),
                "services": [],
            }

            # Extract service information
            for item in host.get("data", []):
                service = {
                    "port": item.get("port"),
                    "transport": item.get("transport", "tcp"),
                    "product": item.get("product", "Unknown"),
                    "version": item.get("version", ""),
                    "banner": item.get("data", "")[:200],  # First 200 chars
                }
                host_info["services"].append(service)

                # Record discovery for each service
                self.record_discovery("service", f"{ip}:{service['port']}", service, confidence=1.0, severity="INFO")

            # Record vulnerability discoveries
            if host_info["vulns"]:
                for vuln in host_info["vulns"]:
                    self.record_discovery(
                        "vulnerability", ip, {"cve": vuln, "source": "shodan"}, confidence=0.9, severity="CRITICAL"
                    )

            self.logger.info(f"Found {len(host_info['services'])} services on {ip}")
            return host_info

        except Exception as e:
            self.logger.error(f"Failed to get host info for {ip}: {e}")
            return None

    def _search_query(self, query: str) -> list[dict[str, Any]]:
        """
        Perform a Shodan search query

        Args:
            query: Search query (e.g., "apache city:London")

        Returns:
            List of search results
        """
        try:
            results = self.shodan_api.search(query, limit=self.max_results)

            search_results = []
            for result in results["matches"]:
                item = {
                    "ip": result.get("ip_str"),
                    "port": result.get("port"),
                    "organization": result.get("org", "Unknown"),
                    "hostnames": result.get("hostnames", []),
                    "country": result.get("location", {}).get("country_name", "Unknown"),
                    "product": result.get("product", "Unknown"),
                    "data": result.get("data", "")[:200],
                }
                search_results.append(item)

                # Record discovery
                self.record_discovery(
                    "exposed_service", f"{item['ip']}:{item['port']}", item, confidence=0.95, severity="WARNING"
                )

            self.logger.info(f"Found {len(search_results)} results for query: {query}")
            return search_results

        except Exception as e:
            self.logger.error(f"Search query failed: {e}")
            return []

    def search_exploits(self, query: str) -> list[dict[str, Any]]:
        """
        Search for exploits related to a query

        Args:
            query: Search query (e.g., "apache 2.4")

        Returns:
            List of exploits
        """
        if not self._initialize_shodan():
            return []

        try:
            exploits = self.shodan_api.exploits.search(query)

            exploit_list = []
            for exploit in exploits.get("matches", []):
                item = {
                    "source": exploit.get("source"),
                    "description": exploit.get("description", ""),
                    "cve": exploit.get("cve", []),
                    "type": exploit.get("type", "Unknown"),
                }
                exploit_list.append(item)

            self.logger.info(f"Found {len(exploit_list)} exploits for: {query}")
            return exploit_list

        except Exception as e:
            self.logger.error(f"Exploit search failed: {e}")
            return []
