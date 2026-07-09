"""
Executive PDF Report Generator
Creates professional PDF reports for executives and stakeholders
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID


@dataclass
class ExecutiveReportConfig:
    """Configuration for executive reports"""

    organization_name: str
    logo_path: str | None
    include_charts: bool
    include_recommendations: bool
    include_risk_matrix: bool


@dataclass
class ExecutiveSummary:
    """Executive summary data"""

    report_id: UUID
    title: str
    period_start: datetime
    period_end: datetime
    total_findings: int
    critical_findings: int
    high_findings: int
    medium_findings: int
    low_findings: int
    risk_score: float
    key_findings: list[str]
    recommendations: list[str]
    trends: dict[str, Any]


class ExecutiveReportGenerator:
    """
    Generates executive-level PDF reports

    Features:
    - Professional formatting
    - Charts and visualizations
    - Risk matrices
    - Trend analysis
    - Recommendations
    """

    def __init__(self, config: ExecutiveReportConfig):
        """Initialize report generator"""
        self.config = config

    def generate_report(self, summary: ExecutiveSummary, findings: list[dict[str, Any]]) -> str:
        """
        Generate executive PDF report

        Args:
            summary: Executive summary data
            findings: List of findings to include

        Returns:
            Path to generated PDF file
        """
        # In production, use reportlab or similar library
        report_content = self._generate_html_report(summary, findings)

        # Simulate PDF generation
        pdf_path = f"/tmp/executive_report_{summary.report_id}.pdf"
        return pdf_path

    def _generate_html_report(self, summary: ExecutiveSummary, findings: list[dict[str, Any]]) -> str:
        """Generate HTML report (intermediate format)"""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{summary.title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #2c3e50; }}
        .summary {{ background: #ecf0f1; padding: 20px; margin: 20px 0; }}
        .metric {{ display: inline-block; margin: 10px 20px; }}
        .critical {{ color: #e74c3c; font-weight: bold; }}
        .high {{ color: #e67e22; font-weight: bold; }}
        .medium {{ color: #f39c12; }}
        .low {{ color: #3498db; }}
        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #34495e; color: white; }}
    </style>
</head>
<body>
    <h1>{summary.title}</h1>
    <p><strong>Organization:</strong> {self.config.organization_name}</p>
    <p><strong>Report Period:</strong> {summary.period_start.strftime('%Y-%m-%d')} to {summary.period_end.strftime('%Y-%m-%d')}</p>
    
    <div class="summary">
        <h2>Executive Summary</h2>
        <div class="metric">
            <strong>Total Findings:</strong> {summary.total_findings}
        </div>
        <div class="metric critical">
            <strong>Critical:</strong> {summary.critical_findings}
        </div>
        <div class="metric high">
            <strong>High:</strong> {summary.high_findings}
        </div>
        <div class="metric medium">
            <strong>Medium:</strong> {summary.medium_findings}
        </div>
        <div class="metric low">
            <strong>Low:</strong> {summary.low_findings}
        </div>
        <div class="metric">
            <strong>Risk Score:</strong> {summary.risk_score:.1f}/10
        </div>
    </div>
    
    <h2>Key Findings</h2>
    <ul>
"""

        for finding in summary.key_findings:
            html += f"        <li>{finding}</li>\n"

        html += """
    </ul>
    
    <h2>Recommendations</h2>
    <ol>
"""

        for rec in summary.recommendations:
            html += f"        <li>{rec}</li>\n"

        html += """
    </ol>
    
    <h2>Detailed Findings</h2>
    <table>
        <tr>
            <th>Severity</th>
            <th>Finding</th>
            <th>Asset</th>
            <th>Status</th>
        </tr>
"""

        for finding in findings[:20]:  # Limit to top 20
            severity = finding.get("severity", "MEDIUM")
            severity_class = severity.lower()
            html += f"""
        <tr>
            <td class="{severity_class}">{severity}</td>
            <td>{finding.get('title', 'Unknown')}</td>
            <td>{finding.get('asset', 'N/A')}</td>
            <td>{finding.get('status', 'Open')}</td>
        </tr>
"""

        html += """
    </table>
</body>
</html>
"""
        return html

    def generate_risk_matrix(self, findings: list[dict[str, Any]]) -> dict[str, Any]:
        """Generate risk matrix data"""
        matrix = {
            "critical": {"count": 0, "percentage": 0.0},
            "high": {"count": 0, "percentage": 0.0},
            "medium": {"count": 0, "percentage": 0.0},
            "low": {"count": 0, "percentage": 0.0},
        }

        total = len(findings)
        if total == 0:
            return matrix

        for finding in findings:
            severity = finding.get("severity", "MEDIUM").lower()
            if severity in matrix:
                matrix[severity]["count"] += 1

        for severity in matrix:
            matrix[severity]["percentage"] = (matrix[severity]["count"] / total) * 100

        return matrix

    def generate_summary(
        self, findings: list[dict[str, Any]], period_start: datetime, period_end: datetime
    ) -> ExecutiveSummary:
        """Generate executive summary from findings"""
        from uuid import uuid4

        # Count by severity
        critical = sum(1 for f in findings if f.get("severity") == "CRITICAL")
        high = sum(1 for f in findings if f.get("severity") == "HIGH")
        medium = sum(1 for f in findings if f.get("severity") == "MEDIUM")
        low = sum(1 for f in findings if f.get("severity") == "LOW")

        # Calculate risk score
        risk_score = (critical * 10 + high * 7 + medium * 4 + low * 1) / max(len(findings), 1)
        risk_score = min(risk_score, 10.0)

        # Extract key findings (top 5 by severity)
        sorted_findings = sorted(
            findings,
            key=lambda f: {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}.get(f.get("severity", "LOW"), 0),
            reverse=True,
        )
        key_findings = [f"{f.get('severity')}: {f.get('title', 'Unknown')}" for f in sorted_findings[:5]]

        # Generate recommendations
        recommendations = self._generate_recommendations(findings)

        return ExecutiveSummary(
            report_id=uuid4(),
            title=f"Security Assessment Report",
            period_start=period_start,
            period_end=period_end,
            total_findings=len(findings),
            critical_findings=critical,
            high_findings=high,
            medium_findings=medium,
            low_findings=low,
            risk_score=risk_score,
            key_findings=key_findings,
            recommendations=recommendations,
            trends={},
        )

    def _generate_recommendations(self, findings: list[dict[str, Any]]) -> list[str]:
        """Generate recommendations based on findings"""
        recommendations = []

        # Count findings by type
        finding_types: dict[str, int] = {}
        for finding in findings:
            ftype = finding.get("type", "unknown")
            finding_types[ftype] = finding_types.get(ftype, 0) + 1

        # Top recommendations
        if finding_types.get("vulnerability", 0) > 0:
            recommendations.append("Implement a regular vulnerability scanning and patching program")

        if finding_types.get("misconfiguration", 0) > 0:
            recommendations.append("Review and harden system configurations according to security baselines")

        if finding_types.get("exposed_service", 0) > 0:
            recommendations.append("Reduce attack surface by disabling unnecessary services")

        recommendations.append("Implement continuous security monitoring")
        recommendations.append("Conduct regular security awareness training")

        return recommendations[:5]
