"""
Report Generator - PDF/HTML client-ready reporting

Generates professional reports in PDF and HTML formats for reconnaissance
findings, compliance, and executive summaries.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import UUID


class ReportFormat(str, Enum):
    """Report output formats"""

    PDF = "pdf"
    HTML = "html"
    JSON = "json"
    MARKDOWN = "markdown"


class ReportType(str, Enum):
    """Types of reports"""

    EXECUTIVE_SUMMARY = "executive_summary"
    TECHNICAL_FINDINGS = "technical_findings"
    COMPLIANCE = "compliance"
    VULNERABILITY_SCAN = "vulnerability_scan"
    PENETRATION_TEST = "penetration_test"
    ASSET_INVENTORY = "asset_inventory"


@dataclass
class ReportSection:
    """Section in report"""

    title: str
    content: str
    subsections: List["ReportSection"] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReportFinding:
    """Finding in report"""

    title: str
    severity: str
    description: str
    affected_assets: List[str] = field(default_factory=list)
    cvss_score: Optional[float] = None
    cve_ids: List[str] = field(default_factory=list)
    remediation: Optional[str] = None
    references: List[str] = field(default_factory=list)


@dataclass
class ReportMetadata:
    """Report metadata"""

    title: str
    report_type: ReportType
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    generated_by: str = "Nethical Recon"
    version: str = "1.0"
    classification: str = "Confidential"
    client_name: Optional[str] = None
    scan_period_start: Optional[datetime] = None
    scan_period_end: Optional[datetime] = None


class ReportGenerator:
    """
    Professional report generator for security findings.

    Generates client-ready reports in multiple formats with customizable
    templates and branding.
    """

    def __init__(self):
        self.metadata: Optional[ReportMetadata] = None
        self.sections: List[ReportSection] = []
        self.findings: List[ReportFinding] = []
        self.statistics: Dict[str, Any] = {}

    def set_metadata(self, metadata: ReportMetadata):
        """Set report metadata"""
        self.metadata = metadata

    def add_section(self, section: ReportSection):
        """Add section to report"""
        self.sections.append(section)

    def add_finding(self, finding: ReportFinding):
        """Add finding to report"""
        self.findings.append(finding)

    def set_statistics(self, statistics: Dict[str, Any]):
        """Set report statistics"""
        self.statistics = statistics

    def generate_executive_summary(
        self,
        total_assets: int,
        critical_findings: int,
        high_findings: int,
        medium_findings: int,
        low_findings: int,
        scan_duration_hours: float,
    ) -> ReportSection:
        """Generate executive summary section"""
        content = f"""
## Executive Summary

This report presents the findings from a comprehensive security reconnaissance 
conducted on {total_assets} assets over a period of {scan_duration_hours:.1f} hours.

### Key Findings

- **Critical Severity**: {critical_findings} findings
- **High Severity**: {high_findings} findings
- **Medium Severity**: {medium_findings} findings
- **Low Severity**: {low_findings} findings

### Risk Assessment

The overall security posture shows {self._assess_risk_level(critical_findings, high_findings)} risk level.
Immediate attention is required for critical and high-severity findings.

### Recommendations

1. Address all critical severity findings within 24 hours
2. Plan remediation for high severity findings within 1 week
3. Schedule regular security assessments to maintain security posture
"""
        return ReportSection(
            title="Executive Summary",
            content=content,
            metadata={
                "total_assets": total_assets,
                "critical_findings": critical_findings,
                "high_findings": high_findings,
            },
        )

    def generate_findings_section(self) -> ReportSection:
        """Generate detailed findings section"""
        # Sort findings by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
        sorted_findings = sorted(self.findings, key=lambda f: severity_order.get(f.severity.lower(), 5))

        content_parts = ["## Detailed Findings\n"]

        for i, finding in enumerate(sorted_findings, 1):
            content_parts.append(f"\n### {i}. {finding.title}\n")
            content_parts.append(f"**Severity**: {finding.severity.upper()}\n\n")

            if finding.cvss_score:
                content_parts.append(f"**CVSS Score**: {finding.cvss_score}\n\n")

            if finding.cve_ids:
                content_parts.append(f"**CVE IDs**: {', '.join(finding.cve_ids)}\n\n")

            content_parts.append(f"**Description**: {finding.description}\n\n")

            if finding.affected_assets:
                content_parts.append("**Affected Assets**:\n")
                for asset in finding.affected_assets:
                    content_parts.append(f"- {asset}\n")
                content_parts.append("\n")

            if finding.remediation:
                content_parts.append(f"**Remediation**: {finding.remediation}\n\n")

            if finding.references:
                content_parts.append("**References**:\n")
                for ref in finding.references:
                    content_parts.append(f"- {ref}\n")
                content_parts.append("\n")

        return ReportSection(title="Detailed Findings", content="".join(content_parts))

    def generate_compliance_section(self, framework: str = "OWASP") -> ReportSection:
        """Generate compliance section"""
        content = f"""
## Compliance Assessment - {framework}

This section maps findings to {framework} requirements and provides
compliance status.

### Compliance Coverage

The assessment covered the following {framework} categories:
- Input Validation
- Authentication & Session Management
- Access Control
- Cryptography
- Error Handling & Logging
- Data Protection
- Communication Security
- HTTP Security Configuration

### Compliance Status

Based on the findings, the following compliance gaps were identified:
"""
        return ReportSection(title=f"{framework} Compliance", content=content)

    def to_html(self) -> str:
        """
        Generate HTML report.

        Returns:
            HTML string with complete report
        """
        html_parts = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            "<meta charset='utf-8'>",
            f"<title>{self.metadata.title if self.metadata else 'Security Report'}</title>",
            "<style>",
            self._get_html_styles(),
            "</style>",
            "</head>",
            "<body>",
        ]

        # Header
        if self.metadata:
            html_parts.extend(
                [
                    "<div class='header'>",
                    f"<h1>{self.metadata.title}</h1>",
                    f"<p class='metadata'>Generated: {self.metadata.generated_at.strftime('%Y-%m-%d %H:%M UTC')}</p>",
                    f"<p class='metadata'>Classification: {self.metadata.classification}</p>",
                    "</div>",
                ]
            )

        # Sections
        for section in self.sections:
            html_parts.extend(["<div class='section'>", self._markdown_to_html(section.content), "</div>"])

        # Findings
        if self.findings:
            findings_section = self.generate_findings_section()
            html_parts.extend(["<div class='section'>", self._markdown_to_html(findings_section.content), "</div>"])

        html_parts.extend(["</body>", "</html>"])

        return "\n".join(html_parts)

    def to_markdown(self) -> str:
        """
        Generate Markdown report.

        Returns:
            Markdown string with complete report
        """
        md_parts = []

        # Header
        if self.metadata:
            md_parts.extend(
                [
                    f"# {self.metadata.title}",
                    "",
                    f"**Generated**: {self.metadata.generated_at.strftime('%Y-%m-%d %H:%M UTC')}  ",
                    f"**Classification**: {self.metadata.classification}  ",
                    f"**Generated by**: {self.metadata.generated_by}",
                    "",
                    "---",
                    "",
                ]
            )

        # Sections
        for section in self.sections:
            md_parts.extend([section.content, "", "---", ""])

        # Findings
        if self.findings:
            findings_section = self.generate_findings_section()
            md_parts.append(findings_section.content)

        return "\n".join(md_parts)

    def save(self, output_path: Path, format: ReportFormat = ReportFormat.HTML):
        """
        Save report to file.

        Args:
            output_path: Path to save report
            format: Output format (PDF, HTML, Markdown)
        """
        output_path = Path(output_path)

        if format == ReportFormat.HTML:
            content = self.to_html()
            output_path.write_text(content, encoding="utf-8")
        elif format == ReportFormat.MARKDOWN:
            content = self.to_markdown()
            output_path.write_text(content, encoding="utf-8")
        elif format == ReportFormat.PDF:
            # For PDF generation, would use library like weasyprint or reportlab
            # For now, generate HTML and save with .pdf extension
            # In production, convert HTML to PDF
            html_content = self.to_html()
            output_path.write_text(html_content, encoding="utf-8")
        elif format == ReportFormat.JSON:
            import json

            content = json.dumps(self._to_dict(), indent=2)
            output_path.write_text(content, encoding="utf-8")

    def _assess_risk_level(self, critical: int, high: int) -> str:
        """Assess overall risk level"""
        if critical > 0:
            return "CRITICAL"
        elif high >= 5:
            return "HIGH"
        elif high > 0:
            return "MODERATE"
        else:
            return "LOW"

    def _get_html_styles(self) -> str:
        """Get HTML styles for report"""
        return """
            body { 
                font-family: Arial, sans-serif; 
                max-width: 1200px; 
                margin: 0 auto; 
                padding: 20px;
                line-height: 1.6;
            }
            .header { 
                border-bottom: 3px solid #333; 
                margin-bottom: 30px; 
                padding-bottom: 20px;
            }
            .metadata { 
                color: #666; 
                font-size: 14px; 
            }
            .section { 
                margin-bottom: 40px; 
            }
            h1 { color: #2c3e50; }
            h2 { color: #34495e; border-bottom: 2px solid #ecf0f1; padding-bottom: 10px; }
            h3 { color: #7f8c8d; }
            .critical { color: #c0392b; font-weight: bold; }
            .high { color: #e74c3c; font-weight: bold; }
            .medium { color: #f39c12; font-weight: bold; }
            .low { color: #3498db; }
            code { 
                background: #ecf0f1; 
                padding: 2px 6px; 
                border-radius: 3px; 
                font-family: monospace;
            }
        """

    def _markdown_to_html(self, markdown: str) -> str:
        """Simple markdown to HTML conversion"""
        # Basic conversion - in production use proper markdown library
        html = markdown
        html = html.replace("###", "<h3>").replace("\n", "</h3>\n", 1)
        html = html.replace("##", "<h2>").replace("\n", "</h2>\n", 1)
        html = html.replace("**", "<strong>", 1).replace("**", "</strong>", 1)
        html = html.replace("- ", "<li>").replace("\n", "</li>\n")
        return f"<div>{html}</div>"

    def _to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary"""
        return {
            "metadata": (
                {
                    "title": self.metadata.title,
                    "type": self.metadata.report_type.value,
                    "generated_at": self.metadata.generated_at.isoformat(),
                    "generated_by": self.metadata.generated_by,
                }
                if self.metadata
                else {}
            ),
            "sections": [{"title": s.title, "content": s.content} for s in self.sections],
            "findings": [
                {
                    "title": f.title,
                    "severity": f.severity,
                    "description": f.description,
                    "affected_assets": f.affected_assets,
                }
                for f in self.findings
            ],
            "statistics": self.statistics,
        }
