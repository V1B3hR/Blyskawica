"""
Nuclei Adapter - Vulnerability Scanner

Nuclei is a fast vulnerability scanner that uses YAML templates
to identify security issues across targets.
"""

import json
from pathlib import Path
from typing import Any
from uuid import UUID

from nethical_recon.adapters.base_plugin import ToolPlugin
from nethical_recon.core.models import Confidence, Finding, Severity


class NucleiAdapter(ToolPlugin):
    """Adapter for nuclei vulnerability scanner."""

    def __init__(self, tool_path: str | None = None):
        super().__init__("nuclei", tool_path)

    def validate_target(self, target: str) -> tuple[bool, str]:
        """Validate target is a URL or IP."""
        if target.startswith(("http://", "https://")):
            return True, ""
        if target.replace(".", "").replace(":", "").replace("/", "").isalnum():
            return True, ""
        return False, "Target must be a URL or IP address"

    def build_command(self, target: str, output_path: Path, options: dict[str, Any] | None = None) -> list[str]:
        """Build nuclei command."""
        options = options or {}

        cmd = [
            self.tool_path,
            "-target",
            target,
            "-jsonl",  # JSON lines output
            "-o",
            str(output_path),
            "-silent",  # Suppress banner
        ]

        # Severity filter
        if options.get("severity"):
            cmd.extend(["-severity", options["severity"]])

        # Template tags
        if options.get("tags"):
            cmd.extend(["-tags", options["tags"]])

        # Template directory
        if options.get("templates"):
            cmd.extend(["-t", options["templates"]])

        # Rate limiting
        if options.get("rate_limit"):
            cmd.extend(["-rate-limit", str(options["rate_limit"])])

        return cmd

    def parse_output(self, content: str) -> dict[str, Any]:
        """Parse nuclei JSON output."""
        if not content or not content.strip():
            return {"vulnerabilities": []}

        vulnerabilities = []

        # Nuclei outputs one JSON object per line
        for line in content.strip().split("\n"):
            line = line.strip()
            if not line:
                continue

            try:
                vuln = json.loads(line)
                vulnerabilities.append(vuln)
            except json.JSONDecodeError as e:
                self.logger.warning(f"Failed to parse nuclei line: {e}")
                continue

        return {"vulnerabilities": vulnerabilities}

    def to_findings(self, parsed_data: dict[str, Any], run_id: UUID, evidence_id: UUID) -> list[Finding]:
        """Convert nuclei results to findings."""
        findings = []

        for vuln in parsed_data.get("vulnerabilities", []):
            template_id = vuln.get("template-id", "unknown")
            info = vuln.get("info", {})

            # Extract vulnerability details
            name = info.get("name", template_id)
            description = info.get("description", "No description available")
            severity_str = info.get("severity", "info").lower()

            # Map nuclei severity to our severity
            severity = self._map_severity(severity_str)

            # Extract affected URL/host
            matched_at = vuln.get("matched-at", vuln.get("host", ""))
            host = vuln.get("host", "")

            # Extract tags
            tags = info.get("tags", [])
            if isinstance(tags, str):
                tags = tags.split(",")
            tags = ["nuclei"] + [t.strip() for t in tags]

            # Extract references
            references = info.get("reference", [])
            if isinstance(references, str):
                references = [references]

            # Extract CVE/CWE
            cve_ids = []
            cwe_ids = []
            classification = info.get("classification", {})
            if "cve-id" in classification:
                cve_id = classification["cve-id"]
                if isinstance(cve_id, list):
                    cve_ids = cve_id
                else:
                    cve_ids = [cve_id]
            if "cwe-id" in classification:
                cwe_id = classification["cwe-id"]
                if isinstance(cwe_id, list):
                    cwe_ids = cwe_id
                else:
                    cwe_ids = [cwe_id]

            finding = Finding(
                run_id=run_id,
                title=name,
                description=description,
                severity=severity,
                confidence=Confidence.HIGH,  # Nuclei templates are usually reliable
                category="vulnerability",
                affected_asset=host,
                service="http",
                cve_ids=cve_ids,
                cwe_ids=cwe_ids,
                references=references,
                tags=tags,
                evidence_ids=[evidence_id],
                raw_data=vuln,
            )

            findings.append(finding)

        return findings

    def _map_severity(self, nuclei_severity: str) -> Severity:
        """Map nuclei severity to our severity enum."""
        severity_map = {
            "critical": Severity.CRITICAL,
            "high": Severity.HIGH,
            "medium": Severity.MEDIUM,
            "low": Severity.LOW,
            "info": Severity.INFO,
        }
        return severity_map.get(nuclei_severity.lower(), Severity.INFO)
