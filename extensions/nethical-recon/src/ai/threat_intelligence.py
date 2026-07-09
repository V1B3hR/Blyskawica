"""
Threat Intelligence Integration

Manages threat intelligence feeds and exports findings to standard formats
like STIX 2.1, JSON, Markdown, and PDF.
"""

import json
import logging
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class ThreatFeed(BaseModel):
    """Threat intelligence feed configuration."""

    name: str = Field(..., description="Feed name")
    source: str = Field(..., description="Feed source URL or identifier")
    feed_type: str = Field(..., description="Type: misp, opencti, stix, custom")
    enabled: bool = Field(default=True, description="Whether feed is active")
    last_updated: datetime | None = Field(None, description="Last update timestamp")
    update_interval_hours: int = Field(default=24, description="Update interval in hours")


class STIXIndicator(BaseModel):
    """STIX 2.1 Indicator representation."""

    type: str = Field(default="indicator", description="STIX object type")
    spec_version: str = Field(default="2.1", description="STIX spec version")
    id: str = Field(..., description="STIX ID")
    created: str = Field(..., description="Creation timestamp")
    modified: str = Field(..., description="Modification timestamp")
    name: str = Field(..., description="Indicator name")
    description: str = Field(..., description="Indicator description")
    pattern: str = Field(..., description="STIX pattern")
    pattern_type: str = Field(default="stix", description="Pattern type")
    valid_from: str = Field(..., description="Valid from timestamp")
    labels: list[str] = Field(default_factory=list, description="Indicator labels")


class ThreatIntelligenceManager:
    """
    Threat Intelligence Manager

    Manages threat feeds and exports findings to standard formats:
    - STIX 2.1 (industry standard)
    - JSON (structured data)
    - Markdown (human-readable reports)
    - PDF (executive reports) - future
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.feeds: dict[str, ThreatFeed] = {}

    def register_feed(self, feed: ThreatFeed) -> None:
        """Register a threat intelligence feed."""
        self.feeds[feed.name] = feed
        self.logger.info(f"Registered threat feed: {feed.name} ({feed.feed_type})")

    def export_to_stix(self, findings: list[dict[str, Any]], context: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Export findings to STIX 2.1 format.

        Args:
            findings: List of findings to export
            context: Additional context (target, scan job, etc.)

        Returns:
            STIX 2.1 bundle
        """
        self.logger.info(f"Exporting {len(findings)} findings to STIX 2.1")

        stix_objects = []

        # Create identity object (the scanner)
        identity = {
            "type": "identity",
            "spec_version": "2.1",
            "id": f"identity--nethical-recon",
            "created": datetime.utcnow().isoformat() + "Z",
            "modified": datetime.utcnow().isoformat() + "Z",
            "name": "Nethical Recon",
            "identity_class": "system",
            "description": "Nethical Recon - Advanced Cybersecurity Reconnaissance Platform",
        }
        stix_objects.append(identity)

        # Convert each finding to STIX indicator
        for finding in findings:
            indicator = self._finding_to_stix_indicator(finding)
            stix_objects.append(indicator)

        # Create STIX bundle
        bundle = {
            "type": "bundle",
            "id": f"bundle--{UUID(int=0).hex}",  # Deterministic bundle ID
            "objects": stix_objects,
        }

        return bundle

    def _finding_to_stix_indicator(self, finding: dict[str, Any]) -> dict[str, Any]:
        """Convert a finding to a STIX 2.1 indicator."""
        finding_id = str(finding.get("id", UUID(int=0)))
        now = datetime.utcnow().isoformat() + "Z"

        # Build STIX pattern based on finding type
        pattern = self._build_stix_pattern(finding)

        # Map severity to STIX labels
        labels = self._get_stix_labels(finding)

        indicator = {
            "type": "indicator",
            "spec_version": "2.1",
            "id": f"indicator--{finding_id}",
            "created": finding.get("discovered_at", now),
            "modified": finding.get("discovered_at", now),
            "name": finding.get("title", "Unknown Finding"),
            "description": finding.get("description", ""),
            "pattern": pattern,
            "pattern_type": "stix",
            "valid_from": finding.get("discovered_at", now),
            "labels": labels,
        }

        return indicator

    def _build_stix_pattern(self, finding: dict[str, Any]) -> str:
        """Build STIX pattern from finding."""
        # Simple pattern based on available data
        patterns = []

        if finding.get("affected_asset"):
            patterns.append(f"[ipv4-addr:value = '{finding['affected_asset']}']")

        if finding.get("port"):
            patterns.append(f"[network-traffic:dst_port = {finding['port']}]")

        if finding.get("service"):
            patterns.append(f"[network-traffic:protocols[*] = '{finding['service']}']")

        # If no specific patterns, use generic
        if not patterns:
            return "[x-nethical-finding:exists = true]"

        return " AND ".join(patterns)

    def _get_stix_labels(self, finding: dict[str, Any]) -> list[str]:
        """Get STIX labels for finding."""
        labels = []

        # Add severity as label
        severity = finding.get("severity", "info")
        labels.append(f"severity:{severity}")

        # Add category
        category = finding.get("category", "unknown")
        labels.append(f"category:{category}")

        # Add custom tags
        labels.extend(finding.get("tags", []))

        return labels

    def export_to_json(self, findings: list[dict[str, Any]], pretty: bool = True) -> str:
        """
        Export findings to JSON format.

        Args:
            findings: List of findings
            pretty: Whether to pretty-print JSON

        Returns:
            JSON string
        """
        data = {
            "metadata": {
                "generator": "Nethical Recon",
                "version": "1.0",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "finding_count": len(findings),
            },
            "findings": findings,
        }

        indent = 2 if pretty else None
        return json.dumps(data, indent=indent, default=str)

    def export_to_markdown(self, findings: list[dict[str, Any]], context: dict[str, Any] | None = None) -> str:
        """
        Export findings to Markdown report.

        Args:
            findings: List of findings
            context: Additional context

        Returns:
            Markdown formatted report
        """
        lines = []

        # Header
        lines.append("# Threat Intelligence Report")
        lines.append("")
        lines.append(f"**Generated:** {datetime.utcnow().isoformat()}Z")
        lines.append(f"**Total Findings:** {len(findings)}")
        lines.append("")

        # Context section
        if context:
            lines.append("## Context")
            lines.append("")
            for key, value in context.items():
                lines.append(f"- **{key}:** {value}")
            lines.append("")

        # Summary by severity
        severity_counts = {}
        for finding in findings:
            sev = finding.get("severity", "info")
            severity_counts[sev] = severity_counts.get(sev, 0) + 1

        lines.append("## Summary")
        lines.append("")
        lines.append("| Severity | Count |")
        lines.append("|----------|-------|")
        for sev in ["critical", "high", "medium", "low", "info"]:
            if sev in severity_counts:
                lines.append(f"| {sev.upper()} | {severity_counts[sev]} |")
        lines.append("")

        # Detailed findings
        lines.append("## Findings")
        lines.append("")

        # Group by severity
        for severity in ["critical", "high", "medium", "low", "info"]:
            sev_findings = [f for f in findings if f.get("severity") == severity]
            if not sev_findings:
                continue

            lines.append(f"### {severity.upper()} Severity")
            lines.append("")

            for i, finding in enumerate(sev_findings, 1):
                lines.append(f"#### {i}. {finding.get('title', 'Unknown')}")
                lines.append("")
                lines.append(f"- **ID:** `{finding.get('id')}`")
                lines.append(f"- **Confidence:** {finding.get('confidence', 'unknown')}")
                lines.append(f"- **Category:** {finding.get('category', 'unknown')}")

                if finding.get("affected_asset"):
                    lines.append(f"- **Affected Asset:** {finding['affected_asset']}")

                if finding.get("port"):
                    lines.append(f"- **Port:** {finding['port']}")

                if finding.get("service"):
                    lines.append(f"- **Service:** {finding['service']}")
                    if finding.get("service_version"):
                        lines.append(f"- **Version:** {finding['service_version']}")

                if finding.get("cve_ids"):
                    lines.append(f"- **CVEs:** {', '.join(finding['cve_ids'])}")

                lines.append("")
                lines.append(f"**Description:** {finding.get('description', 'No description')}")
                lines.append("")

                if finding.get("evidence_ids"):
                    lines.append(f"**Evidence IDs:** {', '.join(str(e) for e in finding['evidence_ids'])}")
                    lines.append("")

        # Footer
        lines.append("---")
        lines.append("")
        lines.append("*Generated by Nethical Recon - Advanced Cybersecurity Reconnaissance Platform*")

        return "\n".join(lines)

    def export_to_pdf(
        self, findings: list[dict[str, Any]], output_path: str, context: dict[str, Any] | None = None
    ) -> str:
        """
        Export findings to PDF report (placeholder).

        Args:
            findings: List of findings
            output_path: Output file path
            context: Additional context

        Returns:
            Path to generated PDF

        Note:
            This is a placeholder. Future implementation will use
            WeasyPrint or similar to generate PDF from Markdown.
        """
        self.logger.warning("PDF export not yet implemented - generating Markdown instead")

        # Generate markdown
        markdown = self.export_to_markdown(findings, context)

        # Write to file
        md_path = output_path.replace(".pdf", ".md")
        with open(md_path, "w") as f:
            f.write(markdown)

        self.logger.info(f"Generated Markdown report: {md_path}")
        return md_path
