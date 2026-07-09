"""
DNS Enumerator - Ghost Vision Camera
👻 Widmo Mode - Sees invisible subdomains

Discovers:
- Subdomains
- DNS records (A, AAAA, MX, NS, TXT, CNAME)
- Zone transfers (AXFR)
- DNS security (DNSSEC)
"""

import socket
from typing import Any

from .base import BaseCamera, CameraMode


class DNSEnumerator(BaseCamera):
    """
    DNS enumeration camera with ghost vision

    Configuration:
        wordlist: Path to subdomain wordlist (default: None - uses common list)
        nameservers: List of custom nameservers (default: None - uses system)
        timeout: DNS query timeout in seconds (default: 2)
        check_zone_transfer: Attempt zone transfer (default: True)
    """

    def __init__(self, config: dict[str, Any] = None):
        super().__init__("DNSEnumerator", CameraMode.GHOST, config)
        self.wordlist = self.config.get("wordlist")
        self.nameservers = self.config.get("nameservers", [])
        self.timeout = self.config.get("timeout", 2)
        self.check_zone_transfer = self.config.get("check_zone_transfer", True)
        self.common_subdomains = [
            "www",
            "mail",
            "ftp",
            "webmail",
            "smtp",
            "pop",
            "ns1",
            "ns2",
            "admin",
            "api",
            "dev",
            "staging",
            "test",
            "demo",
            "blog",
            "shop",
            "vpn",
            "remote",
            "portal",
            "dashboard",
            "app",
            "mobile",
            "cdn",
            "static",
            "assets",
            "img",
            "images",
        ]

    def validate_config(self) -> bool:
        """Validate configuration"""
        try:
            import dns.resolver

            return True
        except ImportError:
            self.logger.error("dnspython not installed. Install with: pip install dnspython")
            return False

    def scan(self, target: str) -> dict[str, Any]:
        """
        Enumerate DNS records for target domain

        Args:
            target: Domain name to scan

        Returns:
            Dict with DNS enumeration results
        """
        if not self.validate_config():
            return {"error": "dnspython not installed"}

        self.logger.info(f"👻 Ghost Vision: Enumerating DNS for {target}...")

        results = {
            "target": target,
            "subdomains": [],
            "dns_records": {},
            "nameservers": [],
            "zone_transfer": None,
            "dnssec": False,
        }

        # Get nameservers
        results["nameservers"] = self._get_nameservers(target)

        # Get DNS records for main domain
        results["dns_records"][target] = self._get_dns_records(target)

        # Enumerate subdomains
        results["subdomains"] = self._enumerate_subdomains(target)

        # Get DNS records for discovered subdomains
        for subdomain in results["subdomains"]:
            results["dns_records"][subdomain] = self._get_dns_records(subdomain)

        # Attempt zone transfer
        if self.check_zone_transfer and results["nameservers"]:
            results["zone_transfer"] = self._attempt_zone_transfer(target, results["nameservers"])

        # Check DNSSEC
        results["dnssec"] = self._check_dnssec(target)

        self.logger.info(f"Found {len(results['subdomains'])} subdomains")

        return results

    def _get_nameservers(self, domain: str) -> list[str]:
        """Get nameservers for domain"""
        try:
            import dns.resolver

            answers = dns.resolver.resolve(domain, "NS", lifetime=self.timeout)
            nameservers = [str(rdata.target).rstrip(".") for rdata in answers]

            self.logger.info(f"Found {len(nameservers)} nameservers for {domain}")
            return nameservers

        except Exception as e:
            self.logger.warning(f"Failed to get nameservers: {e}")
            return []

    def _get_dns_records(self, domain: str) -> dict[str, list[str]]:
        """
        Get various DNS records for a domain

        Args:
            domain: Domain name

        Returns:
            Dict mapping record types to values
        """
        import dns.resolver

        records = {}
        record_types = ["A", "AAAA", "MX", "TXT", "CNAME", "NS", "SOA"]

        for rtype in record_types:
            try:
                answers = dns.resolver.resolve(domain, rtype, lifetime=self.timeout)
                records[rtype] = []

                for rdata in answers:
                    if rtype == "MX":
                        records[rtype].append(f"{rdata.preference} {str(rdata.exchange)}")
                    elif rtype == "SOA":
                        records[rtype].append(f"{str(rdata.mname)} {str(rdata.rname)}")
                    else:
                        records[rtype].append(str(rdata))

                # Record discovery for interesting records
                if rtype in ["A", "AAAA"]:
                    for ip in records[rtype]:
                        self.record_discovery(
                            "dns_record", domain, {"type": rtype, "value": ip}, confidence=1.0, severity="INFO"
                        )

            except dns.resolver.NoAnswer:
                continue
            except dns.resolver.NXDOMAIN:
                self.logger.warning(f"Domain {domain} does not exist")
                break
            except Exception:
                continue

        return records

    def _enumerate_subdomains(self, domain: str) -> list[str]:
        """
        Enumerate subdomains

        Args:
            domain: Base domain

        Returns:
            List of discovered subdomains
        """
        subdomains = []

        # Use wordlist if provided
        if self.wordlist:
            try:
                with open(self.wordlist) as f:
                    wordlist = [line.strip() for line in f if line.strip()]
            except Exception as e:
                self.logger.warning(f"Failed to read wordlist: {e}")
                wordlist = self.common_subdomains
        else:
            wordlist = self.common_subdomains

        # Try each subdomain
        for sub in wordlist:
            subdomain = f"{sub}.{domain}"

            try:
                # Try to resolve
                socket.setdefaulttimeout(self.timeout)
                socket.gethostbyname(subdomain)

                subdomains.append(subdomain)
                self.logger.info(f"Found subdomain: {subdomain}")

                # Record discovery
                self.record_discovery("subdomain", subdomain, {"parent": domain}, confidence=1.0, severity="INFO")

            except socket.gaierror:
                # Subdomain doesn't exist
                continue
            except TimeoutError:
                continue
            except Exception:
                continue

        return subdomains

    def _attempt_zone_transfer(self, domain: str, nameservers: list[str]) -> dict[str, Any]:
        """
        Attempt DNS zone transfer (AXFR)

        Args:
            domain: Domain name
            nameservers: List of nameservers to try

        Returns:
            Dict with zone transfer results
        """
        import dns.query
        import dns.zone

        result = {"successful": False, "nameserver": None, "records": []}

        for ns in nameservers:
            try:
                # Resolve nameserver to IP
                ns_ip = socket.gethostbyname(ns)

                # Attempt zone transfer
                zone = dns.zone.from_xfr(dns.query.xfr(ns_ip, domain, timeout=self.timeout))

                # Zone transfer successful!
                result["successful"] = True
                result["nameserver"] = ns

                # Extract records
                for name, node in zone.nodes.items():
                    rdatasets = node.rdatasets
                    for rdataset in rdatasets:
                        for rdata in rdataset:
                            result["records"].append(
                                {"name": str(name), "type": dns.rdatatype.to_text(rdataset.rdtype), "value": str(rdata)}
                            )

                self.logger.warning(f"Zone transfer successful from {ns}! Found {len(result['records'])} records")

                # Record as a critical discovery
                self.record_discovery(
                    "vulnerability",
                    domain,
                    {"type": "zone_transfer", "nameserver": ns, "records_exposed": len(result["records"])},
                    confidence=1.0,
                    severity="CRITICAL",
                )

                break  # Stop after first successful transfer

            except Exception:
                continue

        if not result["successful"]:
            self.logger.info("Zone transfer not allowed (this is good)")

        return result

    def _check_dnssec(self, domain: str) -> bool:
        """
        Check if DNSSEC is enabled

        Args:
            domain: Domain name

        Returns:
            True if DNSSEC is enabled
        """
        try:
            import dns.resolver

            # Try to get DNSKEY record
            answers = dns.resolver.resolve(domain, "DNSKEY", lifetime=self.timeout)

            if answers:
                self.logger.info(f"DNSSEC is enabled for {domain}")
                return True

        except Exception:
            pass

        return False

    def quick_scan(self, domain: str) -> dict[str, Any]:
        """
        Quick DNS scan (basic records only)

        Args:
            domain: Domain to scan

        Returns:
            Basic DNS records
        """
        return {
            "domain": domain,
            "records": self._get_dns_records(domain),
            "nameservers": self._get_nameservers(domain),
        }
