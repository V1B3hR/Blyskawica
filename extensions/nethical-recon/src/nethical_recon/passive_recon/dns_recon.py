"""DNS reconnaissance module for passive OSINT."""

import dns.resolver
import dns.zone
from dataclasses import dataclass
from typing import Optional


@dataclass
class DNSRecord:
    """Represents a DNS record."""

    name: str
    record_type: str
    value: str
    ttl: int


class DNSRecon:
    """Passive DNS reconnaissance without actively querying target servers."""

    # Common DNS record types to query
    RECORD_TYPES = ["A", "AAAA", "CNAME", "MX", "NS", "TXT", "SOA", "PTR"]

    def __init__(self, nameserver: Optional[str] = None, timeout: int = 5):
        """Initialize DNS reconnaissance.

        Args:
            nameserver: Custom DNS server to use (default: system resolver)
            timeout: Query timeout in seconds
        """
        self.resolver = dns.resolver.Resolver()
        if nameserver:
            self.resolver.nameservers = [nameserver]
        self.resolver.timeout = timeout
        self.resolver.lifetime = timeout

    def query_record(self, domain: str, record_type: str) -> list[DNSRecord]:
        """Query a specific DNS record type.

        Args:
            domain: Domain name to query
            record_type: DNS record type (A, AAAA, MX, etc.)

        Returns:
            List of DNS records found
        """
        records = []

        try:
            answers = self.resolver.resolve(domain, record_type)
            for rdata in answers:
                records.append(
                    DNSRecord(
                        name=domain,
                        record_type=record_type,
                        value=str(rdata),
                        ttl=answers.rrset.ttl,
                    )
                )
        except dns.resolver.NXDOMAIN:
            # Domain doesn't exist
            pass
        except dns.resolver.NoAnswer:
            # No records of this type
            pass
        except dns.resolver.Timeout:
            # Query timed out
            pass
        except Exception:
            # Other DNS errors
            pass

        return records

    def enumerate_records(self, domain: str, record_types: Optional[list[str]] = None) -> dict[str, list[DNSRecord]]:
        """Enumerate multiple DNS record types for a domain.

        Args:
            domain: Domain name to query
            record_types: List of record types to query (default: all common types)

        Returns:
            Dictionary mapping record type to list of records
        """
        if record_types is None:
            record_types = self.RECORD_TYPES

        results = {}
        for record_type in record_types:
            records = self.query_record(domain, record_type)
            if records:
                results[record_type] = records

        return results

    def get_mail_servers(self, domain: str) -> list[str]:
        """Get mail servers for a domain.

        Args:
            domain: Domain name to query

        Returns:
            List of mail server hostnames
        """
        mx_records = self.query_record(domain, "MX")
        # MX records include priority, extract just the hostname
        return [record.value.split()[-1].rstrip(".") for record in mx_records]

    def get_nameservers(self, domain: str) -> list[str]:
        """Get authoritative nameservers for a domain.

        Args:
            domain: Domain name to query

        Returns:
            List of nameserver hostnames
        """
        ns_records = self.query_record(domain, "NS")
        return [record.value.rstrip(".") for record in ns_records]

    def get_txt_records(self, domain: str) -> list[str]:
        """Get TXT records for a domain (often contains SPF, DKIM, etc.).

        Args:
            domain: Domain name to query

        Returns:
            List of TXT record values
        """
        txt_records = self.query_record(domain, "TXT")
        return [record.value.strip('"') for record in txt_records]

    def reverse_dns_lookup(self, ip_address: str) -> Optional[str]:
        """Perform reverse DNS lookup for an IP address.

        Args:
            ip_address: IP address to look up

        Returns:
            Hostname if found, None otherwise
        """
        try:
            # Convert IP to reverse DNS format
            reversed_ip = dns.reversename.from_address(ip_address)
            answers = self.resolver.resolve(reversed_ip, "PTR")
            if answers:
                return str(answers[0]).rstrip(".")
        except Exception:
            pass

        return None

    def check_spf_record(self, domain: str) -> Optional[str]:
        """Check for SPF record in TXT records.

        Args:
            domain: Domain name to check

        Returns:
            SPF record if found, None otherwise
        """
        txt_records = self.get_txt_records(domain)
        for record in txt_records:
            if record.startswith("v=spf1"):
                return record
        return None

    def check_dmarc_record(self, domain: str) -> Optional[str]:
        """Check for DMARC record.

        Args:
            domain: Domain name to check

        Returns:
            DMARC record if found, None otherwise
        """
        dmarc_domain = f"_dmarc.{domain}"
        txt_records = self.get_txt_records(dmarc_domain)
        for record in txt_records:
            if record.startswith("v=DMARC1"):
                return record
        return None
