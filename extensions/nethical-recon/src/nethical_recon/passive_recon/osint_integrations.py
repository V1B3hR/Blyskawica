"""OSINT integrations with public data sources."""

import requests
from typing import Optional


class CrtShClient:
    """Certificate Transparency Log client (crt.sh)."""

    BASE_URL = "https://crt.sh"

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def search_domain(self, domain: str) -> list[dict]:
        """Search for certificates by domain.

        Args:
            domain: Domain to search

        Returns:
            List of certificate entries
        """
        try:
            url = f"{self.BASE_URL}/?q=%.{domain}&output=json"
            response = requests.get(url, timeout=self.timeout)
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass
        return []


class SecurityTrailsClient:
    """SecurityTrails API client."""

    BASE_URL = "https://api.securitytrails.com/v1"

    def __init__(self, api_key: str, timeout: int = 10):
        self.api_key = api_key
        self.timeout = timeout
        self.headers = {"APIKEY": api_key}

    def get_subdomains(self, domain: str) -> list[str]:
        """Get subdomains for a domain.

        Args:
            domain: Target domain

        Returns:
            List of subdomains
        """
        try:
            url = f"{self.BASE_URL}/domain/{domain}/subdomains"
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                return data.get("subdomains", [])
        except Exception:
            pass
        return []


class ShodanClient:
    """Shodan API client."""

    BASE_URL = "https://api.shodan.io"

    def __init__(self, api_key: str, timeout: int = 10):
        self.api_key = api_key
        self.timeout = timeout

    def search_host(self, ip_address: str) -> Optional[dict]:
        """Get host information from Shodan.

        Args:
            ip_address: IP address to lookup

        Returns:
            Host information dict
        """
        try:
            url = f"{self.BASE_URL}/shodan/host/{ip_address}?key={self.api_key}"
            response = requests.get(url, timeout=self.timeout)
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass
        return None


class OSTNTClient:
    """OSINT Framework client placeholder."""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def search(self, query: str) -> list[dict]:
        """Generic OSINT search.

        Args:
            query: Search query

        Returns:
            List of results
        """
        # Placeholder for OSINT framework integration
        return []
