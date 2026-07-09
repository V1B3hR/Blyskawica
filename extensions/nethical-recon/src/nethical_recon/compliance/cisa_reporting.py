"""
CISA Compliance Reporting

Generates HTML and PDF compliance reports with CISA KEV and alert mapping.
Provides executive summaries, remediation timelines, and gap analysis.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)


class ReportFormat(Enum):
    """Report output formats."""

    HTML = "html"
    PDF = "pdf"
    JSON = "json"


@dataclass
class CISAComplianceReport:
    """CISA compliance report."""

    report_id: UUID = field(default_factory=uuid4)
    generated_at: datetime = field(default_factory=datetime.utcnow)
    organization: str = ""
    policy_mode: str = ""
    executive_summary: dict[str, Any] = field(default_factory=dict)
    kev_section: dict[str, Any] = field(default_factory=dict)
    alerts_section: dict[str, Any] = field(default_factory=dict)
    compliance_section: dict[str, Any] = field(default_factory=dict)
    remediation_timeline: list[dict[str, Any]] = field(default_factory=list)


class CISAComplianceReporter:
    """
    CISA Compliance Reporter.

    Generates comprehensive compliance reports with CISA KEV and alert mapping.

    Features:
    - HTML/PDF report generation
    - Executive summary
    - KEV vulnerability tracking
    - Active alert mapping
    - Compliance gap analysis
    - Remediation timeline
    """

    def __init__(self):
        """Initialize CISA compliance reporter."""
        self._reports: dict[UUID, CISAComplianceReport] = {}

    def generate_report(
        self,
        organization: str,
        policy_mode: str,
        kev_vulnerabilities: list[dict[str, Any]],
        active_alerts: list[dict[str, Any]],
        compliance_data: dict[str, Any],
    ) -> CISAComplianceReport:
        """
        Generate CISA compliance report.

        Args:
            organization: Organization name
            policy_mode: CISA policy mode
            kev_vulnerabilities: List of KEV vulnerabilities found
            active_alerts: List of active CISA alerts
            compliance_data: Compliance metrics and data

        Returns:
            Generated compliance report
        """
        report = CISAComplianceReport(
            organization=organization,
            policy_mode=policy_mode,
        )

        # Generate executive summary
        report.executive_summary = self._generate_executive_summary(kev_vulnerabilities, active_alerts, compliance_data)

        # Generate KEV section
        report.kev_section = self._generate_kev_section(kev_vulnerabilities)

        # Generate alerts section
        report.alerts_section = self._generate_alerts_section(active_alerts)

        # Generate compliance section
        report.compliance_section = self._generate_compliance_section(compliance_data)

        # Generate remediation timeline
        report.remediation_timeline = self._generate_remediation_timeline(kev_vulnerabilities)

        # Store report
        self._reports[report.report_id] = report

        logger.info(f"Generated CISA compliance report: {report.report_id}")

        return report

    def _generate_executive_summary(
        self,
        kev_vulnerabilities: list[dict[str, Any]],
        active_alerts: list[dict[str, Any]],
        compliance_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Generate executive summary section."""
        total_kev = len(kev_vulnerabilities)
        open_kev = len([v for v in kev_vulnerabilities if v.get("status") == "open"])
        overdue_kev = len([v for v in kev_vulnerabilities if v.get("is_overdue", False)])

        # Calculate compliance score (0-100)
        compliance_score = 100.0
        if total_kev > 0:
            compliance_score -= (open_kev / total_kev) * 40
        if overdue_kev > 0:
            compliance_score -= overdue_kev * 10
        compliance_score = max(0, min(100, compliance_score))

        return {
            "compliance_score": round(compliance_score, 2),
            "risk_level": self._calculate_risk_level(compliance_score),
            "total_kev_vulnerabilities": total_kev,
            "open_kev_vulnerabilities": open_kev,
            "overdue_remediations": overdue_kev,
            "active_alerts": len(active_alerts),
            "critical_findings": compliance_data.get("critical_findings", 0),
            "recommendations": self._generate_recommendations(kev_vulnerabilities, active_alerts),
        }

    def _generate_kev_section(self, kev_vulnerabilities: list[dict[str, Any]]) -> dict[str, Any]:
        """Generate KEV vulnerabilities section."""
        return {
            "total_vulnerabilities": len(kev_vulnerabilities),
            "vulnerabilities": kev_vulnerabilities,
            "by_status": self._group_by_status(kev_vulnerabilities),
            "by_severity": self._group_by_severity(kev_vulnerabilities),
            "overdue": [v for v in kev_vulnerabilities if v.get("is_overdue", False)],
        }

    def _generate_alerts_section(self, active_alerts: list[dict[str, Any]]) -> dict[str, Any]:
        """Generate active CISA alerts section."""
        shields_up = any(alert.get("is_shields_up", False) for alert in active_alerts)

        return {
            "total_alerts": len(active_alerts),
            "shields_up_active": shields_up,
            "alerts": active_alerts,
            "by_severity": self._group_alerts_by_severity(active_alerts),
            "affecting_organization": [a for a in active_alerts if a.get("affects_org", False)],
        }

    def _generate_compliance_section(self, compliance_data: dict[str, Any]) -> dict[str, Any]:
        """Generate policy compliance section."""
        return {
            "policy_adherence": compliance_data.get("policy_adherence", 0),
            "scan_coverage": compliance_data.get("scan_coverage", 0),
            "asset_coverage": compliance_data.get("asset_coverage", 0),
            "gaps": compliance_data.get("gaps", []),
            "strengths": compliance_data.get("strengths", []),
            "recommendations": compliance_data.get("recommendations", []),
        }

    def _generate_remediation_timeline(self, kev_vulnerabilities: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Generate remediation timeline."""
        timeline = []

        for vuln in kev_vulnerabilities:
            if vuln.get("status") == "open":
                timeline.append(
                    {
                        "cve_id": vuln.get("cve_id"),
                        "due_date": vuln.get("due_date"),
                        "required_action": vuln.get("required_action"),
                        "priority": "overdue" if vuln.get("is_overdue", False) else "pending",
                        "days_remaining": vuln.get("days_remaining", 0),
                    }
                )

        # Sort by due date
        timeline.sort(key=lambda x: x.get("due_date", "9999-12-31"))

        return timeline

    def render_html(self, report: CISAComplianceReport) -> str:
        """
        Render report as HTML.

        Args:
            report: Compliance report

        Returns:
            HTML report string
        """
        # Simple HTML template
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>CISA Compliance Report - {report.organization}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #003366; }}
                h2 {{ color: #005599; border-bottom: 2px solid #005599; padding-bottom: 5px; }}
                .score {{ font-size: 48px; font-weight: bold; color: #00aa00; }}
                .metric {{ margin: 10px 0; padding: 10px; background: #f5f5f5; }}
                .critical {{ color: #cc0000; font-weight: bold; }}
                .high {{ color: #ff6600; font-weight: bold; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #003366; color: white; }}
            </style>
        </head>
        <body>
            <h1>CISA Compliance Report</h1>
            <p><strong>Organization:</strong> {report.organization}</p>
            <p><strong>Policy Mode:</strong> {report.policy_mode}</p>
            <p><strong>Generated:</strong> {report.generated_at.strftime('%Y-%m-%d %H:%M:%S UTC')}</p>

            <h2>Executive Summary</h2>
            <div class="score">Compliance Score: {report.executive_summary.get('compliance_score', 0)}%</div>
            <div class="metric"><strong>Risk Level:</strong> {report.executive_summary.get('risk_level', 'Unknown')}</div>
            <div class="metric"><strong>Total KEV Vulnerabilities:</strong> {report.executive_summary.get('total_kev_vulnerabilities', 0)}</div>
            <div class="metric"><strong>Open KEV Vulnerabilities:</strong> <span class="critical">{report.executive_summary.get('open_kev_vulnerabilities', 0)}</span></div>
            <div class="metric"><strong>Overdue Remediations:</strong> <span class="critical">{report.executive_summary.get('overdue_remediations', 0)}</span></div>

            <h2>KEV Vulnerabilities</h2>
            <p>Total: {report.kev_section.get('total_vulnerabilities', 0)}</p>

            <h2>Active CISA Alerts</h2>
            <p>Total Alerts: {report.alerts_section.get('total_alerts', 0)}</p>
            {f'<p class="critical">⚠️ SHIELDS UP ACTIVE</p>' if report.alerts_section.get('shields_up_active') else ''}

            <h2>Compliance Status</h2>
            <div class="metric"><strong>Policy Adherence:</strong> {report.compliance_section.get('policy_adherence', 0)}%</div>
            <div class="metric"><strong>Scan Coverage:</strong> {report.compliance_section.get('scan_coverage', 0)}%</div>

            <h2>Remediation Timeline</h2>
            <p>{len(report.remediation_timeline)} items requiring attention</p>
        </body>
        </html>
        """

        return html

    def render_json(self, report: CISAComplianceReport) -> dict[str, Any]:
        """
        Render report as JSON.

        Args:
            report: Compliance report

        Returns:
            JSON-serializable dictionary
        """
        return {
            "report_id": str(report.report_id),
            "generated_at": report.generated_at.isoformat(),
            "organization": report.organization,
            "policy_mode": report.policy_mode,
            "executive_summary": report.executive_summary,
            "kev_section": report.kev_section,
            "alerts_section": report.alerts_section,
            "compliance_section": report.compliance_section,
            "remediation_timeline": report.remediation_timeline,
        }

    def get_report(self, report_id: UUID) -> Optional[CISAComplianceReport]:
        """Get report by ID."""
        return self._reports.get(report_id)

    def _calculate_risk_level(self, compliance_score: float) -> str:
        """Calculate risk level from compliance score."""
        if compliance_score >= 90:
            return "Low"
        elif compliance_score >= 70:
            return "Medium"
        elif compliance_score >= 50:
            return "High"
        else:
            return "Critical"

    def _generate_recommendations(
        self, kev_vulnerabilities: list[dict[str, Any]], active_alerts: list[dict[str, Any]]
    ) -> list[str]:
        """Generate recommendations based on findings."""
        recommendations = []

        overdue = [v for v in kev_vulnerabilities if v.get("is_overdue", False)]
        if overdue:
            recommendations.append(f"Immediately remediate {len(overdue)} overdue KEV vulnerabilities")

        open_kev = [v for v in kev_vulnerabilities if v.get("status") == "open"]
        if open_kev:
            recommendations.append(f"Address {len(open_kev)} open KEV vulnerabilities before due dates")

        critical_alerts = [a for a in active_alerts if a.get("severity") == "critical"]
        if critical_alerts:
            recommendations.append(f"Review and respond to {len(critical_alerts)} critical CISA alerts")

        return recommendations

    def _group_by_status(self, vulnerabilities: list[dict[str, Any]]) -> dict[str, int]:
        """Group vulnerabilities by status."""
        status_counts = {}
        for vuln in vulnerabilities:
            status = vuln.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        return status_counts

    def _group_by_severity(self, vulnerabilities: list[dict[str, Any]]) -> dict[str, int]:
        """Group vulnerabilities by severity."""
        severity_counts = {}
        for vuln in vulnerabilities:
            severity = vuln.get("severity", "unknown")
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        return severity_counts

    def _group_alerts_by_severity(self, alerts: list[dict[str, Any]]) -> dict[str, int]:
        """Group alerts by severity."""
        severity_counts = {}
        for alert in alerts:
            severity = alert.get("severity", "unknown")
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        return severity_counts
