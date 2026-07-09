"""
Example Extensions - Demonstrating Extension API

Sample extensions showing how to integrate with the platform.
"""

from typing import Any, Dict, List, Optional


class ExampleWebScannerExtension:
    """
    Example web vulnerability scanner extension.

    Demonstrates:
    - Scanner extension type
    - Async scanning
    - Result formatting
    - Configuration management
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.name = "example-web-scanner"
        self.version = "1.0.0"
        self.description = "Example web vulnerability scanner"

    async def scan(self, target: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Scan target URL for vulnerabilities.

        Args:
            target: Target URL to scan
            options: Scanner options

        Returns:
            Scan results with findings
        """
        options = options or {}

        # Example scan logic
        findings = []

        # Check for common headers
        if options.get("check_headers", True):
            findings.extend(await self._check_security_headers(target))

        # Check for common vulnerabilities
        if options.get("check_vulns", True):
            findings.extend(await self._check_common_vulnerabilities(target))

        return {
            "target": target,
            "scanner": self.name,
            "version": self.version,
            "findings": findings,
            "scan_complete": True,
        }

    async def _check_security_headers(self, target: str) -> List[Dict[str, Any]]:
        """Check for security headers"""
        # Placeholder - would make actual HTTP request
        return [
            {
                "title": "Missing Security Headers",
                "severity": "medium",
                "description": "Server missing recommended security headers",
                "affected_headers": ["X-Frame-Options", "X-Content-Type-Options"],
                "remediation": "Add security headers to server configuration",
            }
        ]

    async def _check_common_vulnerabilities(self, target: str) -> List[Dict[str, Any]]:
        """Check for common web vulnerabilities"""
        # Placeholder - would perform actual vulnerability checks
        return [
            {
                "title": "Potential XSS Vulnerability",
                "severity": "high",
                "description": "Input validation may be insufficient",
                "location": "/search?q=",
                "remediation": "Implement proper input sanitization",
            }
        ]

    def get_metadata(self) -> Dict[str, Any]:
        """Get extension metadata"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": "Nethical Team",
            "type": "scanner",
            "capabilities": ["web_scanning", "vulnerability_detection"],
            "config_schema": {
                "check_headers": {"type": "boolean", "default": True},
                "check_vulns": {"type": "boolean", "default": True},
                "timeout": {"type": "integer", "default": 30},
            },
        }


class ExampleDNSEnrichmentExtension:
    """
    Example DNS enrichment extension.

    Demonstrates:
    - Enrichment extension type
    - Data enrichment
    - Multiple data sources
    """

    def __init__(self):
        self.name = "example-dns-enrichment"
        self.version = "1.0.0"
        self.description = "Example DNS data enrichment"

    async def enrich(self, domain: str) -> Dict[str, Any]:
        """
        Enrich domain with DNS information.

        Args:
            domain: Domain to enrich

        Returns:
            Enrichment data
        """
        # Example enrichment logic
        enrichment_data = {
            "domain": domain,
            "dns_records": await self._get_dns_records(domain),
            "whois": await self._get_whois_info(domain),
            "subdomains": await self._discover_subdomains(domain),
            "reputation": await self._check_reputation(domain),
        }

        return enrichment_data

    async def _get_dns_records(self, domain: str) -> Dict[str, List[str]]:
        """Get DNS records"""
        # Placeholder - would query DNS
        return {
            "A": ["93.184.216.34"],
            "MX": ["mail.example.com"],
            "NS": ["ns1.example.com", "ns2.example.com"],
            "TXT": ["v=spf1 include:_spf.example.com ~all"],
        }

    async def _get_whois_info(self, domain: str) -> Dict[str, Any]:
        """Get WHOIS information"""
        # Placeholder - would query WHOIS
        return {
            "registrar": "Example Registrar Inc.",
            "creation_date": "1995-08-14",
            "expiration_date": "2025-08-13",
            "status": "clientTransferProhibited",
        }

    async def _discover_subdomains(self, domain: str) -> List[str]:
        """Discover subdomains"""
        # Placeholder - would perform subdomain enumeration
        return [
            f"www.{domain}",
            f"mail.{domain}",
            f"ftp.{domain}",
        ]

    async def _check_reputation(self, domain: str) -> Dict[str, Any]:
        """Check domain reputation"""
        # Placeholder - would check threat intel sources
        return {
            "reputation_score": 95,
            "is_malicious": False,
            "categories": ["business", "technology"],
        }

    def get_metadata(self) -> Dict[str, Any]:
        """Get extension metadata"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": "Nethical Team",
            "type": "enrichment",
            "capabilities": ["dns_resolution", "whois_lookup", "subdomain_discovery", "reputation_check"],
        }


class ExampleThreatIntelExtension:
    """
    Example threat intelligence integration extension.

    Demonstrates:
    - Integration extension type
    - External API integration
    - Threat context enrichment
    """

    def __init__(self, api_key: Optional[str] = None):
        self.name = "example-threat-intel"
        self.version = "1.0.0"
        self.description = "Example threat intelligence integration"
        self.api_key = api_key

    async def get_ip_reputation(self, ip_address: str) -> Dict[str, Any]:
        """
        Get IP reputation from threat intelligence.

        Args:
            ip_address: IP address to check

        Returns:
            Reputation data
        """
        # Placeholder - would query threat intel API
        return {
            "ip": ip_address,
            "reputation_score": 75,
            "is_malicious": False,
            "threat_types": [],
            "last_seen": None,
            "country": "US",
            "asn": "AS15169",
            "asn_org": "Google LLC",
        }

    async def get_domain_threats(self, domain: str) -> Dict[str, Any]:
        """
        Get domain threat information.

        Args:
            domain: Domain to check

        Returns:
            Threat data
        """
        # Placeholder - would query threat intel API
        return {
            "domain": domain,
            "is_malicious": False,
            "threat_categories": [],
            "malware_families": [],
            "phishing_detected": False,
            "risk_score": 10,
        }

    async def get_cve_info(self, cve_id: str) -> Dict[str, Any]:
        """
        Get CVE vulnerability information.

        Args:
            cve_id: CVE identifier (e.g., CVE-2021-44228)

        Returns:
            CVE information
        """
        # Placeholder - would query CVE database
        return {
            "cve_id": cve_id,
            "description": "Example vulnerability description",
            "cvss_score": 9.8,
            "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
            "published_date": "2021-12-10",
            "exploit_available": True,
            "references": [
                "https://nvd.nist.gov/vuln/detail/" + cve_id,
            ],
        }

    async def enrich_finding(self, finding: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich finding with threat intelligence.

        Args:
            finding: Finding to enrich

        Returns:
            Enriched finding
        """
        enriched = finding.copy()

        # Add threat context based on finding type
        if "ip_address" in finding:
            enriched["threat_intel"] = await self.get_ip_reputation(finding["ip_address"])

        if "domain" in finding:
            enriched["threat_intel"] = await self.get_domain_threats(finding["domain"])

        if "cve_id" in finding:
            enriched["cve_details"] = await self.get_cve_info(finding["cve_id"])

        return enriched

    def get_metadata(self) -> Dict[str, Any]:
        """Get extension metadata"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": "Nethical Team",
            "type": "integration",
            "capabilities": ["ip_reputation", "domain_threats", "cve_lookup", "finding_enrichment"],
            "config_schema": {"api_key": {"type": "string", "required": True, "description": "Threat intel API key"}},
        }


# Example usage demonstrating extension lifecycle
async def example_extension_usage():
    """
    Example demonstrating how to use extensions.

    This would typically be called by the platform's extension manager.
    """
    # 1. Web Scanner Extension
    scanner = ExampleWebScannerExtension()
    scan_results = await scanner.scan("https://example.com", {"check_headers": True, "check_vulns": True})
    print(f"Web scan found {len(scan_results['findings'])} findings")

    # 2. DNS Enrichment Extension
    dns_enricher = ExampleDNSEnrichmentExtension()
    enrichment = await dns_enricher.enrich("example.com")
    print(f"DNS enrichment found {len(enrichment['subdomains'])} subdomains")

    # 3. Threat Intel Extension
    threat_intel = ExampleThreatIntelExtension(api_key="example-key")
    ip_rep = await threat_intel.get_ip_reputation("8.8.8.8")
    print(f"IP reputation score: {ip_rep['reputation_score']}")

    # 4. Enrich finding with threat intel
    sample_finding = {
        "title": "Open Port Detected",
        "severity": "medium",
        "ip_address": "8.8.8.8",
    }
    enriched_finding = await threat_intel.enrich_finding(sample_finding)
    print(f"Finding enriched with threat intel: {enriched_finding.get('threat_intel', {}).get('asn_org')}")
