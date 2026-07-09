"""
Ffuf Adapter - Fast Web Fuzzer

Ffuf is a fast web fuzzer for discovering hidden content,
directories, and parameters.
"""

import json
from pathlib import Path
from typing import Any
from uuid import UUID

from nethical_recon.adapters.base_plugin import ToolPlugin
from nethical_recon.core.models import Confidence, Finding, Severity


class FfufAdapter(ToolPlugin):
    """Adapter for ffuf web fuzzer."""

    def __init__(self, tool_path: str | None = None):
        super().__init__("ffuf", tool_path)

    def validate_target(self, target: str) -> tuple[bool, str]:
        """Validate target is a URL with FUZZ keyword."""
        if not target.startswith(("http://", "https://")):
            return False, "Target must be a URL starting with http:// or https://"
        if "FUZZ" not in target:
            return False, "Target must contain FUZZ keyword for fuzzing"
        return True, ""

    def build_command(self, target: str, output_path: Path, options: dict[str, Any] | None = None) -> list[str]:
        """Build ffuf command."""
        options = options or {}

        cmd = [
            self.tool_path,
            "-u",
            target,
            "-of",
            "json",  # JSON output format
            "-o",
            str(output_path),
            "-s",  # Silent mode
        ]

        # Wordlist (required)
        wordlist = options.get("wordlist", "/usr/share/wordlists/dirb/common.txt")
        cmd.extend(["-w", wordlist])

        # Match/filter options
        if options.get("match_codes"):
            cmd.extend(["-mc", options["match_codes"]])
        else:
            cmd.extend(["-mc", "200,204,301,302,307,401,403"])  # Common interesting codes

        if options.get("filter_size"):
            cmd.extend(["-fs", str(options["filter_size"])])

        if options.get("filter_words"):
            cmd.extend(["-fw", str(options["filter_words"])])

        # Threads and rate limiting
        threads = options.get("threads", 40)
        cmd.extend(["-t", str(threads)])

        if options.get("rate"):
            cmd.extend(["-rate", str(options["rate"])])

        # Timeout
        timeout = options.get("timeout", 10)
        cmd.extend(["-timeout", str(timeout)])

        # Follow redirects
        if options.get("follow_redirects", False):
            cmd.append("-r")

        return cmd

    def parse_output(self, content: str) -> dict[str, Any]:
        """Parse ffuf JSON output."""
        if not content or not content.strip():
            return {"results": []}

        try:
            data = json.loads(content)
            results = data.get("results", [])
            return {"results": results, "config": data.get("config", {})}
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse ffuf output: {e}")
            return {"results": []}

    def to_findings(self, parsed_data: dict[str, Any], run_id: UUID, evidence_id: UUID) -> list[Finding]:
        """Convert ffuf results to findings."""
        findings = []

        for result in parsed_data.get("results", []):
            url = result.get("url", "")
            status = result.get("status", 0)
            length = result.get("length", 0)
            words = result.get("words", 0)
            lines = result.get("lines", 0)
            input_data = result.get("input", {})

            # Extract the fuzzed value
            fuzzed_value = input_data.get("FUZZ", "unknown")

            # Determine severity based on status code and content type
            severity = self._assess_finding_severity(url, status, fuzzed_value)

            # Build description
            description = (
                f"Discovered path: {fuzzed_value} "
                f"(Status: {status}, Length: {length} bytes, "
                f"Words: {words}, Lines: {lines})"
            )

            # Determine category
            category = self._categorize_finding(url, status, fuzzed_value)

            finding = Finding(
                run_id=run_id,
                title=f"Discovered: {fuzzed_value}",
                description=description,
                severity=severity,
                confidence=Confidence.HIGH,
                category=category,
                affected_asset=url,
                protocol="http",
                service="http",
                tags=["ffuf", "fuzzing", "content-discovery", f"status-{status}"],
                evidence_ids=[evidence_id],
                raw_data=result,
            )

            findings.append(finding)

        return findings

    def _assess_finding_severity(self, url: str, status: int, path: str) -> Severity:
        """Assess severity of discovered content."""
        url_lower = url.lower()
        path_lower = path.lower()

        # Critical paths
        critical_paths = [".env", ".git", "config", "backup", "database", "admin", "phpinfo", "credentials", "password"]
        if any(crit in path_lower for crit in critical_paths):
            return Severity.CRITICAL

        # High severity - sensitive areas
        high_paths = ["admin", "manage", "console", "dashboard", "api", "upload", "login", "user"]
        if any(high in path_lower for high in high_paths):
            return Severity.HIGH

        # Medium - internal paths
        if status == 200 or status == 401 or status == 403:
            return Severity.MEDIUM

        # Low - redirects and other
        return Severity.LOW

    def _categorize_finding(self, url: str, status: int, path: str) -> str:
        """Categorize the type of finding."""
        if ".env" in path.lower() or "config" in path.lower():
            return "config_file"

        if ".git" in path.lower() or "backup" in path.lower():
            return "backup_file"

        if "admin" in path.lower():
            return "admin_panel"

        if "api" in path.lower():
            return "api_endpoint"

        if status == 200:
            return "accessible_content"

        if status == 401:
            return "auth_required"

        if status == 403:
            return "forbidden_access"

        if status in (301, 302, 307):
            return "redirect"

        return "discovered_content"
