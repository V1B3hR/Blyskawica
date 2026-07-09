"""Passive subdomain enumeration module."""

from typing import Optional
import requests


class SubdomainEnumerator:
    """Passive subdomain enumeration using public sources."""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def enumerate_from_crtsh(self, domain: str) -> list[str]:
        """Enumerate subdomains using crt.sh certificate transparency logs.

        Args:
            domain: Target domain

        Returns:
            List of discovered subdomains
        """
        subdomains = set()
        try:
            url = f"https://crt.sh/?q=%.{domain}&output=json"
            response = requests.get(url, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                for entry in data:
                    name = entry.get("name_value", "")
                    # Handle wildcard and newline-separated names
                    names = name.replace("*.", "").split("\n")
                    for subdomain in names:
                        subdomain = subdomain.strip()
                        if subdomain and subdomain.endswith(domain):
                            subdomains.add(subdomain)
        except Exception:
            pass

        return sorted(list(subdomains))

    def enumerate(self, domain: str) -> list[str]:
        """Enumerate subdomains using multiple passive sources.

        Args:
            domain: Target domain

        Returns:
            List of unique subdomains discovered
        """
        subdomains = set()

        # Use crt.sh
        crtsh_results = self.enumerate_from_crtsh(domain)
        subdomains.update(crtsh_results)

        return sorted(list(subdomains))
