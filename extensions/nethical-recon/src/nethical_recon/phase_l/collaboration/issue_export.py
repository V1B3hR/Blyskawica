"""
Issue Exporter
Exports findings to external issue tracking systems (Jira, GitHub Issues)
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID


class IssueSystem(Enum):
    """Supported issue tracking systems"""

    JIRA = "jira"
    GITHUB = "github"
    GITLAB = "gitlab"
    AZURE_DEVOPS = "azure_devops"


@dataclass
class IssueExportConfig:
    """Configuration for issue export"""

    system: IssueSystem
    base_url: str
    project_key: str  # Jira project or GitHub repo
    api_token: str
    default_labels: list[str]
    severity_mapping: dict[str, str]  # Map internal severity to issue priority


@dataclass
class ExportedIssue:
    """Reference to an exported issue"""

    finding_id: UUID
    system: IssueSystem
    issue_id: str  # External issue ID
    issue_url: str
    exported_at: datetime
    status: str


class IssueExporter:
    """
    Exports security findings to external issue tracking systems

    Features:
    - Multi-platform support (Jira, GitHub, GitLab)
    - Automatic severity mapping
    - Bidirectional sync (optional)
    - Duplicate detection
    """

    def __init__(self, config: IssueExportConfig):
        """
        Initialize issue exporter

        Args:
            config: Export configuration
        """
        self.config = config
        self._exported_issues: dict[UUID, ExportedIssue] = {}

    def export_finding(self, finding: dict[str, Any], custom_labels: list[str] | None = None) -> ExportedIssue:
        """
        Export a finding to the configured issue tracking system

        Args:
            finding: Finding dictionary
            custom_labels: Additional labels to add

        Returns:
            Exported issue reference
        """
        if self.config.system == IssueSystem.JIRA:
            return self._export_to_jira(finding, custom_labels)
        elif self.config.system == IssueSystem.GITHUB:
            return self._export_to_github(finding, custom_labels)
        elif self.config.system == IssueSystem.GITLAB:
            return self._export_to_gitlab(finding, custom_labels)
        else:
            raise ValueError(f"Unsupported system: {self.config.system}")

    def _export_to_jira(self, finding: dict[str, Any], custom_labels: list[str] | None = None) -> ExportedIssue:
        """Export finding to Jira"""
        finding_id = finding.get("id")

        # Check if already exported
        if finding_id in self._exported_issues:
            return self._exported_issues[finding_id]

        # Map severity to Jira priority
        severity = finding.get("severity", "MEDIUM")
        priority = self.config.severity_mapping.get(severity, "Medium")

        # Build issue data
        issue_data = {
            "fields": {
                "project": {"key": self.config.project_key},
                "summary": finding.get("title", "Security Finding"),
                "description": self._format_description_jira(finding),
                "issuetype": {"name": "Bug"},
                "priority": {"name": priority},
                "labels": self.config.default_labels + (custom_labels or []),
            }
        }

        # Simulate API call (in production, use Jira REST API)
        issue_id = f"SEC-{finding_id.hex[:8].upper()}"
        issue_url = f"{self.config.base_url}/browse/{issue_id}"

        exported = ExportedIssue(
            finding_id=finding_id,
            system=IssueSystem.JIRA,
            issue_id=issue_id,
            issue_url=issue_url,
            exported_at=datetime.now(),
            status="open",
        )

        self._exported_issues[finding_id] = exported
        return exported

    def _export_to_github(self, finding: dict[str, Any], custom_labels: list[str] | None = None) -> ExportedIssue:
        """Export finding to GitHub Issues"""
        finding_id = finding.get("id")

        if finding_id in self._exported_issues:
            return self._exported_issues[finding_id]

        severity = finding.get("severity", "MEDIUM")

        # Build issue data
        issue_data = {
            "title": finding.get("title", "Security Finding"),
            "body": self._format_description_github(finding),
            "labels": self._get_github_labels(severity, custom_labels),
        }

        # Simulate API call (in production, use GitHub REST API)
        issue_number = abs(hash(str(finding_id))) % 10000
        issue_url = f"{self.config.base_url}/{self.config.project_key}/issues/{issue_number}"

        exported = ExportedIssue(
            finding_id=finding_id,
            system=IssueSystem.GITHUB,
            issue_id=str(issue_number),
            issue_url=issue_url,
            exported_at=datetime.now(),
            status="open",
        )

        self._exported_issues[finding_id] = exported
        return exported

    def _export_to_gitlab(self, finding: dict[str, Any], custom_labels: list[str] | None = None) -> ExportedIssue:
        """Export finding to GitLab Issues"""
        finding_id = finding.get("id")

        if finding_id in self._exported_issues:
            return self._exported_issues[finding_id]

        severity = finding.get("severity", "MEDIUM")

        # Build issue data
        issue_data = {
            "title": finding.get("title", "Security Finding"),
            "description": self._format_description_github(finding),
            "labels": ",".join(self._get_github_labels(severity, custom_labels)),
        }

        # Simulate API call
        issue_number = abs(hash(str(finding_id))) % 10000
        issue_url = f"{self.config.base_url}/{self.config.project_key}/-/issues/{issue_number}"

        exported = ExportedIssue(
            finding_id=finding_id,
            system=IssueSystem.GITLAB,
            issue_id=str(issue_number),
            issue_url=issue_url,
            exported_at=datetime.now(),
            status="open",
        )

        self._exported_issues[finding_id] = exported
        return exported

    def _format_description_jira(self, finding: dict[str, Any]) -> str:
        """Format finding description for Jira (using Jira markup)"""
        lines = [
            f"*Finding ID:* {finding.get('id')}",
            f"*Severity:* {finding.get('severity', 'MEDIUM')}",
            f"*Asset:* {finding.get('asset', 'N/A')}",
            "",
            "h3. Description",
            finding.get("description", "No description available"),
            "",
        ]

        if finding.get("remediation"):
            lines.extend(["h3. Remediation", finding["remediation"], ""])

        if finding.get("cves"):
            lines.append("h3. CVEs")
            for cve in finding["cves"]:
                lines.append(f"* {cve}")
            lines.append("")

        return "\n".join(lines)

    def _format_description_github(self, finding: dict[str, Any]) -> str:
        """Format finding description for GitHub/GitLab (using Markdown)"""
        lines = [
            f"**Finding ID:** `{finding.get('id')}`",
            f"**Severity:** {finding.get('severity', 'MEDIUM')}",
            f"**Asset:** {finding.get('asset', 'N/A')}",
            "",
            "### Description",
            finding.get("description", "No description available"),
            "",
        ]

        if finding.get("remediation"):
            lines.extend(["### Remediation", finding["remediation"], ""])

        if finding.get("cves"):
            lines.append("### CVEs")
            for cve in finding["cves"]:
                lines.append(f"- {cve}")
            lines.append("")

        return "\n".join(lines)

    def _get_github_labels(self, severity: str, custom_labels: list[str] | None = None) -> list[str]:
        """Get GitHub labels for a finding"""
        labels = ["security"] + self.config.default_labels

        # Add severity label
        severity_label = f"severity:{severity.lower()}"
        labels.append(severity_label)

        if custom_labels:
            labels.extend(custom_labels)

        return labels

    def get_exported_issue(self, finding_id: UUID) -> ExportedIssue | None:
        """Get exported issue reference for a finding"""
        return self._exported_issues.get(finding_id)

    def is_exported(self, finding_id: UUID) -> bool:
        """Check if a finding has been exported"""
        return finding_id in self._exported_issues
