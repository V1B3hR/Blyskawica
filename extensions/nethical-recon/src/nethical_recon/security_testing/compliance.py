"""Compliance reporting module."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ComplianceFramework(Enum):
    """Compliance frameworks."""

    OWASP_ASVS = "owasp_asvs"
    OWASP_WSTG = "owasp_wstg"
    PCI_DSS = "pci_dss"
    GDPR = "gdpr"
    NIST = "nist"
    CISA_KEV = "cisa_kev"


@dataclass
class ComplianceCheck:
    """Individual compliance check."""

    check_id: str
    framework: ComplianceFramework
    category: str
    description: str
    status: str  # pass, fail, warning, not_applicable
    evidence: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


@dataclass
class ComplianceReport:
    """Compliance report."""

    framework: ComplianceFramework
    timestamp: datetime
    target: str
    checks: list[ComplianceCheck] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)


class ComplianceReporter:
    """Generate compliance reports."""

    def __init__(self):
        """Initialize compliance reporter."""
        self.reports: list[ComplianceReport] = []

    def generate_owasp_report(self, target: str, test_results: list[Any]) -> ComplianceReport:
        """Generate OWASP compliance report.

        Args:
            target: Target system
            test_results: List of test results

        Returns:
            ComplianceReport
        """
        report = ComplianceReport(
            framework=ComplianceFramework.OWASP_WSTG,
            timestamp=datetime.now(),
            target=target,
        )

        # Convert test results to compliance checks
        for result in test_results:
            check = ComplianceCheck(
                check_id=result.test_id,
                framework=ComplianceFramework.OWASP_WSTG,
                category=getattr(result, "category", "general"),
                description=result.description,
                status=result.status.value,
                evidence=[str(result.details)],
                recommendations=result.recommendations,
            )
            report.checks.append(check)

        # Generate summary
        report.summary = {
            "total_checks": len(report.checks),
            "passed": len([c for c in report.checks if c.status == "pass"]),
            "failed": len([c for c in report.checks if c.status == "fail"]),
            "warnings": len([c for c in report.checks if c.status == "warning"]),
            "compliance_score": self._calculate_compliance_score(report.checks),
        }

        self.reports.append(report)
        return report

    def generate_pci_dss_report(self, target: str, findings: list[Any]) -> ComplianceReport:
        """Generate PCI DSS compliance report.

        Args:
            target: Target system
            findings: List of security findings

        Returns:
            ComplianceReport
        """
        report = ComplianceReport(
            framework=ComplianceFramework.PCI_DSS,
            timestamp=datetime.now(),
            target=target,
        )

        # PCI DSS requirements mapping (simplified)
        pci_requirements = {
            "encryption": "Requirement 4: Encrypt transmission of cardholder data",
            "access_control": "Requirement 7: Restrict access to cardholder data",
            "security_testing": "Requirement 11: Regularly test security systems",
        }

        for category, requirement in pci_requirements.items():
            check = ComplianceCheck(
                check_id=f"pci_dss_{category}",
                framework=ComplianceFramework.PCI_DSS,
                category=category,
                description=requirement,
                status="not_applicable",  # Would need actual assessment
                evidence=["Manual review required"],
            )
            report.checks.append(check)

        report.summary = {"total_checks": len(report.checks), "manual_review_required": True}

        self.reports.append(report)
        return report

    def _calculate_compliance_score(self, checks: list[ComplianceCheck]) -> float:
        """Calculate compliance score percentage.

        Args:
            checks: List of compliance checks

        Returns:
            Score as percentage (0-100)
        """
        if not checks:
            return 0.0

        passed = len([c for c in checks if c.status == "pass"])
        total = len(checks)

        return (passed / total) * 100

    def export_to_dict(self, report: ComplianceReport) -> dict[str, Any]:
        """Export report to dictionary.

        Args:
            report: Compliance report

        Returns:
            Dictionary representation
        """
        return {
            "framework": report.framework.value,
            "timestamp": report.timestamp.isoformat(),
            "target": report.target,
            "summary": report.summary,
            "checks": [
                {
                    "check_id": c.check_id,
                    "category": c.category,
                    "description": c.description,
                    "status": c.status,
                    "evidence": c.evidence,
                    "recommendations": c.recommendations,
                }
                for c in report.checks
            ],
        }

    def export_to_html(self, report: ComplianceReport) -> str:
        """Export report to HTML.

        Args:
            report: Compliance report

        Returns:
            HTML string
        """
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{report.framework.value.upper()} Compliance Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .summary {{ background: #f0f0f0; padding: 15px; margin: 20px 0; }}
        .check {{ border: 1px solid #ddd; margin: 10px 0; padding: 10px; }}
        .pass {{ border-left: 5px solid #4CAF50; }}
        .fail {{ border-left: 5px solid #f44336; }}
        .warning {{ border-left: 5px solid #ff9800; }}
    </style>
</head>
<body>
    <h1>{report.framework.value.upper()} Compliance Report</h1>
    <div class="summary">
        <h2>Summary</h2>
        <p><strong>Target:</strong> {report.target}</p>
        <p><strong>Date:</strong> {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Total Checks:</strong> {report.summary.get('total_checks', 0)}</p>
        <p><strong>Passed:</strong> {report.summary.get('passed', 0)}</p>
        <p><strong>Failed:</strong> {report.summary.get('failed', 0)}</p>
        <p><strong>Compliance Score:</strong> {report.summary.get('compliance_score', 0):.1f}%</p>
    </div>
    <h2>Checks</h2>
"""

        for check in report.checks:
            html += f"""
    <div class="check {check.status}">
        <h3>{check.description}</h3>
        <p><strong>Status:</strong> {check.status}</p>
        <p><strong>Category:</strong> {check.category}</p>
"""
            if check.recommendations:
                html += "        <p><strong>Recommendations:</strong></p><ul>"
                for rec in check.recommendations:
                    html += f"<li>{rec}</li>"
                html += "</ul>"

            html += "    </div>"

        html += """
</body>
</html>
"""
        return html
