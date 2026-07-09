"""
Amass Adapter - Subdomain Enumeration

Amass is a powerful subdomain enumeration tool that uses OSINT
techniques and active reconnaissance to discover subdomains.
"""

import json
from pathlib import Path
from typing import Any
from uuid import UUID

from nethical_recon.adapters.base_plugin import ToolPlugin
from nethical_recon.core.models import Confidence, Finding, Severity


class AmassAdapter(ToolPlugin):
    """Adapter for amass subdomain enumeration tool."""

    def __init__(self, tool_path: str | None = None):
        super().__init__("amass", tool_path)

    def validate_target(self, target: str) -> tuple[bool, str]:
        """Validate target is a domain."""
        # Simple domain validation
        if "." not in target:
            return False, "Target must be a domain name (e.g., example.com)"
        if target.startswith(("http://", "https://")):
            return False, "Target should be a domain, not a URL"
        return True, ""

    def build_command(self, target: str, output_path: Path, options: dict[str, Any] | None = None) -> list[str]:
        """Build amass command."""
        options = options or {}

        cmd = [self.tool_path, "enum", "-d", target, "-json", str(output_path), "-silent"]

        # Passive mode (safer, no active scanning)
        if options.get("passive", True):
            cmd.append("-passive")

        # Use all available sources
        if options.get("all_sources", False):
            cmd.append("-alts")

        # Brute force mode
        if options.get("brute", False):
            cmd.append("-brute")

        # Minimum recursion depth
        if options.get("min_for_recursive"):
            cmd.extend(["-min-for-recursive", str(options["min_for_recursive"])])

        # Timeout
        if options.get("timeout"):
            cmd.extend(["-timeout", str(options["timeout"])])

        # Max DNS queries per minute
        if options.get("max_dns_queries"):
            cmd.extend(["-max-dns-queries", str(options["max_dns_queries"])])

        return cmd

    def parse_output(self, content: str) -> dict[str, Any]:
        """Parse amass JSON output."""
        if not content or not content.strip():
            return {"subdomains": []}

        subdomains = []

        # Amass outputs one JSON object per line
        for line in content.strip().split("\n"):
            line = line.strip()
            if not line:
                continue

            try:
                entry = json.loads(line)
                subdomains.append(entry)
            except json.JSONDecodeError as e:
                self.logger.warning(f"Failed to parse amass line: {e}")
                continue

        return {"subdomains": subdomains}

    def to_findings(self, parsed_data: dict[str, Any], run_id: UUID, evidence_id: UUID) -> list[Finding]:
        """Convert amass results to findings."""
        findings = []

        for subdomain_entry in parsed_data.get("subdomains", []):
            name = subdomain_entry.get("name", "")
            domain = subdomain_entry.get("domain", "")
            addresses = subdomain_entry.get("addresses", [])
            sources = subdomain_entry.get("sources", [])
            tag = subdomain_entry.get("tag", "")

            if not name:
                continue

            # Build description
            description_parts = [f"Subdomain discovered: {name}"]

            if addresses:
                addr_list = ", ".join([a.get("ip", "") for a in addresses if a.get("ip")])
                if addr_list:
                    description_parts.append(f"IPs: {addr_list}")

            if sources:
                source_list = ", ".join(sources)
                description_parts.append(f"Sources: {source_list}")

            description = ". ".join(description_parts)

            # Determine severity based on subdomain characteristics
            severity = self._assess_subdomain_severity(name, tag, addresses)

            # Determine confidence based on number of sources
            confidence = self._assess_confidence(sources)

            # Build tags
            tags = ["amass", "subdomain", "osint"]
            if tag:
                tags.append(tag)
            tags.extend(sources)

            finding = Finding(
                run_id=run_id,
                title=f"Subdomain: {name}",
                description=description,
                severity=severity,
                confidence=confidence,
                category="subdomain",
                affected_asset=name,
                protocol="dns",
                service="dns",
                tags=tags,
                evidence_ids=[evidence_id],
                raw_data=subdomain_entry,
            )

            findings.append(finding)

            # Create additional findings for each IP address
            for addr_info in addresses:
                ip = addr_info.get("ip", "")
                if ip:
                    ip_finding = Finding(
                        run_id=run_id,
                        title=f"DNS Resolution: {name} -> {ip}",
                        description=f"Subdomain {name} resolves to IP {ip}",
                        severity=Severity.INFO,
                        confidence=confidence,
                        category="dns_record",
                        affected_asset=ip,
                        protocol="dns",
                        service="dns",
                        tags=["amass", "dns", "ip-resolution"],
                        evidence_ids=[evidence_id],
                        raw_data={"subdomain": name, "ip": ip, "address_info": addr_info},
                    )
                    findings.append(ip_finding)

        return findings

    def _assess_subdomain_severity(self, name: str, tag: str, addresses: list[dict[str, Any]]) -> Severity:
        """Assess severity of discovered subdomain."""
        name_lower = name.lower()

        # Critical subdomains
        critical_keywords = ["admin", "api", "vpn", "backup", "database", "db", "internal", "staging", "dev", "test"]
        if any(keyword in name_lower for keyword in critical_keywords):
            return Severity.HIGH

        # Production/important services
        important_keywords = ["www", "mail", "smtp", "ftp", "ssh", "portal", "login", "auth"]
        if any(keyword in name_lower for keyword in important_keywords):
            return Severity.MEDIUM

        # Default
        return Severity.LOW

    def _assess_confidence(self, sources: list[str]) -> Confidence:
        """Assess confidence based on number of sources."""
        source_count = len(sources)

        if source_count >= 5:
            return Confidence.CONFIRMED
        elif source_count >= 3:
            return Confidence.HIGH
        elif source_count >= 2:
            return Confidence.MEDIUM
        elif source_count >= 1:
            return Confidence.LOW
        else:
            return Confidence.TENTATIVE
