"""
Httpx Adapter - HTTP Toolkit

Httpx is a fast multi-purpose HTTP toolkit for probing web servers
and extracting information about them.
"""

import json
from pathlib import Path
from typing import Any
from uuid import UUID

from nethical_recon.adapters.base_plugin import ToolPlugin
from nethical_recon.core.models import Confidence, Finding, Severity


class HttpxAdapter(ToolPlugin):
    """Adapter for httpx HTTP toolkit."""

    def __init__(self, tool_path: str | None = None):
        super().__init__("httpx", tool_path)

    def validate_target(self, target: str) -> tuple[bool, str]:
        """Validate target is a URL, domain, or IP."""
        # Accept URLs, domains, and IPs
        return True, ""

    def build_command(self, target: str, output_path: Path, options: dict[str, Any] | None = None) -> list[str]:
        """Build httpx command."""
        options = options or {}

        cmd = [
            self.tool_path,
            "-u",
            target,
            "-json",  # JSON output
            "-o",
            str(output_path),
            "-silent",  # Suppress banner
        ]

        # Common probing options
        if options.get("status_code", True):
            cmd.append("-status-code")

        if options.get("title", True):
            cmd.append("-title")

        if options.get("tech_detect", True):
            cmd.append("-tech-detect")

        if options.get("web_server", True):
            cmd.append("-web-server")

        # Response headers
        if options.get("response_headers"):
            cmd.append("-include-response-header")

        # Follow redirects
        if options.get("follow_redirects", True):
            cmd.append("-follow-redirects")

        # Threads
        if options.get("threads"):
            cmd.extend(["-threads", str(options["threads"])])

        # Rate limit
        if options.get("rate_limit"):
            cmd.extend(["-rate-limit", str(options["rate_limit"])])

        return cmd

    def parse_output(self, content: str) -> dict[str, Any]:
        """Parse httpx JSON output."""
        if not content or not content.strip():
            return {"endpoints": []}

        endpoints = []

        # Httpx outputs one JSON object per line
        for line in content.strip().split("\n"):
            line = line.strip()
            if not line:
                continue

            try:
                endpoint = json.loads(line)
                endpoints.append(endpoint)
            except json.JSONDecodeError as e:
                self.logger.warning(f"Failed to parse httpx line: {e}")
                continue

        return {"endpoints": endpoints}

    def to_findings(self, parsed_data: dict[str, Any], run_id: UUID, evidence_id: UUID) -> list[Finding]:
        """Convert httpx results to findings."""
        findings = []

        for endpoint in parsed_data.get("endpoints", []):
            url = endpoint.get("url", endpoint.get("input", ""))
            host = endpoint.get("host", "")

            # Extract key information
            status_code = endpoint.get("status_code")
            title = endpoint.get("title", "")
            web_server = endpoint.get("webserver", "")
            technologies = endpoint.get("technologies", [])
            content_length = endpoint.get("content_length", 0)

            # Create base finding for the endpoint
            description_parts = [f"HTTP endpoint discovered at {url}"]

            if status_code:
                description_parts.append(f"Status: {status_code}")
            if title:
                description_parts.append(f"Title: {title}")
            if web_server:
                description_parts.append(f"Server: {web_server}")
            if technologies:
                tech_str = ", ".join(technologies)
                description_parts.append(f"Technologies: {tech_str}")

            description = ". ".join(description_parts)

            # Determine severity based on findings
            severity = self._assess_endpoint_severity(endpoint)

            finding = Finding(
                run_id=run_id,
                title=f"HTTP Endpoint: {url}",
                description=description,
                severity=severity,
                confidence=Confidence.HIGH,
                category="web_endpoint",
                affected_asset=host or url,
                protocol="http",
                service="http",
                service_version=web_server,
                tags=["httpx", "web", "http"] + technologies,
                evidence_ids=[evidence_id],
                raw_data=endpoint,
            )

            findings.append(finding)

            # Create additional findings for specific issues
            findings.extend(self._check_security_issues(endpoint, run_id, evidence_id, url, host))

        return findings

    def _assess_endpoint_severity(self, endpoint: dict[str, Any]) -> Severity:
        """Assess severity of endpoint based on characteristics."""
        status_code = endpoint.get("status_code", 0)

        # Check for potentially sensitive endpoints
        url = endpoint.get("url", "").lower()

        # High severity indicators
        if any(keyword in url for keyword in ["/admin", "/backup", "/.git", "/.env", "/config"]):
            return Severity.HIGH

        # Error pages might expose information
        if status_code >= 500:
            return Severity.MEDIUM

        # Authentication pages
        if any(keyword in url for keyword in ["/login", "/auth", "/signin"]):
            return Severity.MEDIUM

        # Directory listings
        if "index of /" in endpoint.get("title", "").lower():
            return Severity.MEDIUM

        # Default: info level
        return Severity.INFO

    def _check_security_issues(
        self, endpoint: dict[str, Any], run_id: UUID, evidence_id: UUID, url: str, host: str
    ) -> list[Finding]:
        """Check for specific security issues in endpoint."""
        issues = []

        # Check for missing security headers
        headers = endpoint.get("header", {})

        if not headers.get("strict-transport-security"):
            issues.append(
                Finding(
                    run_id=run_id,
                    title="Missing HSTS Header",
                    description=f"Endpoint {url} does not set Strict-Transport-Security header",
                    severity=Severity.LOW,
                    confidence=Confidence.HIGH,
                    category="missing_header",
                    affected_asset=host or url,
                    protocol="http",
                    tags=["httpx", "security-header", "hsts"],
                    evidence_ids=[evidence_id],
                )
            )

        if not headers.get("x-frame-options") and not headers.get("content-security-policy"):
            issues.append(
                Finding(
                    run_id=run_id,
                    title="Missing Clickjacking Protection",
                    description=f"Endpoint {url} missing X-Frame-Options or CSP frame-ancestors",
                    severity=Severity.LOW,
                    confidence=Confidence.MEDIUM,
                    category="missing_header",
                    affected_asset=host or url,
                    protocol="http",
                    tags=["httpx", "security-header", "clickjacking"],
                    evidence_ids=[evidence_id],
                )
            )

        # Check for server version disclosure
        server_header = headers.get("server", "")
        if server_header and any(char.isdigit() for char in server_header):
            issues.append(
                Finding(
                    run_id=run_id,
                    title="Server Version Disclosure",
                    description=f"Server header reveals version: {server_header}",
                    severity=Severity.LOW,
                    confidence=Confidence.HIGH,
                    category="information_disclosure",
                    affected_asset=host or url,
                    protocol="http",
                    tags=["httpx", "information-disclosure"],
                    evidence_ids=[evidence_id],
                )
            )

        return issues
