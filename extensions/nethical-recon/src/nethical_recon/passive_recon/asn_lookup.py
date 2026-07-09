"""ASN and IP range lookup module."""

import requests
from dataclasses import dataclass
from typing import Optional


@dataclass
class ASNInfo:
    """ASN information."""

    asn: str
    organization: str
    country: str
    ip_ranges: list[str]


class ASNLookup:
    """Lookup ASN and IP range information."""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def lookup_ip(self, ip_address: str) -> Optional[ASNInfo]:
        """Lookup ASN information for an IP address.

        Args:
            ip_address: IP address to lookup

        Returns:
            ASNInfo if found, None otherwise
        """
        try:
            # Using ipapi.co for ASN lookup (free tier available)
            url = f"https://ipapi.co/{ip_address}/json/"
            response = requests.get(url, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                return ASNInfo(
                    asn=data.get("asn", ""),
                    organization=data.get("org", ""),
                    country=data.get("country_name", ""),
                    ip_ranges=[],  # Would need additional API for full ranges
                )
        except Exception:
            pass

        return None
