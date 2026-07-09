"""WHOIS lookup module for passive OSINT."""

import socket
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class WHOISResult:
    """Represents WHOIS query result."""

    domain: str
    registrar: Optional[str] = None
    creation_date: Optional[datetime] = None
    expiration_date: Optional[datetime] = None
    updated_date: Optional[datetime] = None
    nameservers: list[str] = None
    status: list[str] = None
    emails: list[str] = None
    organization: Optional[str] = None
    raw_response: Optional[str] = None

    def __post_init__(self):
        if self.nameservers is None:
            self.nameservers = []
        if self.status is None:
            self.status = []
        if self.emails is None:
            self.emails = []


class WHOISLookup:
    """Passive WHOIS reconnaissance."""

    WHOIS_SERVERS = {
        "com": "whois.verisign-grs.com",
        "net": "whois.verisign-grs.com",
        "org": "whois.pir.org",
        "info": "whois.afilias.net",
        "biz": "whois.biz",
        "io": "whois.nic.io",
        "co": "whois.nic.co",
        "uk": "whois.nic.uk",
        "de": "whois.denic.de",
        "fr": "whois.nic.fr",
    }

    DEFAULT_WHOIS_SERVER = "whois.iana.org"
    WHOIS_PORT = 43
    TIMEOUT = 10

    def __init__(self, timeout: int = 10):
        """Initialize WHOIS lookup.

        Args:
            timeout: Query timeout in seconds
        """
        self.timeout = timeout

    def _get_whois_server(self, domain: str) -> str:
        """Determine appropriate WHOIS server for domain.

        Args:
            domain: Domain name

        Returns:
            WHOIS server hostname
        """
        tld = domain.split(".")[-1].lower()
        return self.WHOIS_SERVERS.get(tld, self.DEFAULT_WHOIS_SERVER)

    def _query_whois_server(self, domain: str, whois_server: str) -> str:
        """Query WHOIS server for domain information.

        Args:
            domain: Domain name to query
            whois_server: WHOIS server to query

        Returns:
            Raw WHOIS response
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect((whois_server, self.WHOIS_PORT))

            # Send domain query
            query = f"{domain}\r\n"
            sock.send(query.encode())

            # Receive response
            response = b""
            while True:
                data = sock.recv(4096)
                if not data:
                    break
                response += data

            sock.close()
            return response.decode("utf-8", errors="ignore")

        except Exception as e:
            return f"Error querying WHOIS: {str(e)}"

    def lookup(self, domain: str) -> WHOISResult:
        """Perform WHOIS lookup for a domain.

        Args:
            domain: Domain name to look up

        Returns:
            WHOISResult with parsed information
        """
        whois_server = self._get_whois_server(domain)
        raw_response = self._query_whois_server(domain, whois_server)

        result = WHOISResult(domain=domain, raw_response=raw_response)

        # Parse common fields from response
        lines = raw_response.lower().split("\n")
        for line in lines:
            if ":" not in line:
                continue

            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()

            if "registrar" in key and not result.registrar:
                result.registrar = value
            elif "organization" in key or "org:" == key:
                result.organization = value
            elif "creation date" in key or "created" in key:
                # Would need proper date parsing in production
                pass
            elif "expir" in key:
                pass
            elif "name server" in key:
                result.nameservers.append(value)
            elif "status" in key:
                result.status.append(value)
            elif "@" in value and "email" in key:
                result.emails.append(value)

        return result

    def get_domain_age_days(self, result: WHOISResult) -> Optional[int]:
        """Calculate domain age in days.

        Args:
            result: WHOIS result with creation date

        Returns:
            Age in days, or None if creation date not available
        """
        if result.creation_date:
            age = datetime.now() - result.creation_date
            return age.days
        return None

    def is_domain_expired(self, result: WHOISResult) -> bool:
        """Check if domain is expired.

        Args:
            result: WHOIS result with expiration date

        Returns:
            True if domain is expired
        """
        if result.expiration_date:
            return datetime.now() > result.expiration_date
        return False
