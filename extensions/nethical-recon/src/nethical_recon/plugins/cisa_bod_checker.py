"""
CISA BOD (Binding Operational Directive) Checker Plugin

Checks compliance with CISA Binding Operational Directives for federal agencies.
Supports BOD 22-01, BOD 23-01, and BOD 18-01.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class BODDirective(Enum):
    """CISA Binding Operational Directives."""

    BOD_22_01 = "bod_22_01"  # Reducing Significant Risk of Known Exploited Vulnerabilities
    BOD_23_01 = "bod_23_01"  # Improving Asset Visibility and Vulnerability Detection
    BOD_18_01 = "bod_18_01"  # Enhance Email and Web Security


@dataclass
class BODCheckResult:
    """Result of BOD compliance check."""

    directive: BODDirective
    compliant: bool
    compliance_percentage: float
    findings: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)


class CISABODChecker:
    """
    CISA BOD Compliance Checker.

    Checks compliance with CISA Binding Operational Directives.

    Supported Directives:
    - BOD 22-01: KEV vulnerability remediation
    - BOD 23-01: Asset inventory and vulnerability detection
    - BOD 18-01: Email and web security (DMARC, HTTPS, HSTS)
    """

    def __init__(self, kev_client: Any = None):
        """
        Initialize BOD checker.

        Args:
            kev_client: CISA KEV client for BOD 22-01 checks
        """
        self.kev_client = kev_client

    def check_bod_22_01(self, vulnerabilities: list[dict[str, Any]]) -> BODCheckResult:
        """
        Check compliance with BOD 22-01.

        BOD 22-01 requires federal agencies to remediate KEV vulnerabilities
        within specified timeframes.

        Args:
            vulnerabilities: List of vulnerabilities with CVE IDs

        Returns:
            BOD 22-01 compliance result
        """
        logger.info("Checking BOD 22-01 compliance")

        if not self.kev_client:
            return BODCheckResult(
                directive=BOD_22_01,
                compliant=False,
                compliance_percentage=0.0,
                findings=["KEV client not available"],
                recommendations=["Configure CISA KEV client for BOD 22-01 compliance"],
            )

        # Extract CVE IDs
        cve_ids = []
        for vuln in vulnerabilities:
            if "cve_id" in vuln:
                cve_ids.append(vuln["cve_id"])

        # Check which vulnerabilities are KEV
        kev_vulns = []
        for cve_id in cve_ids:
            if self.kev_client.is_kev(cve_id):
                kev_entry = self.kev_client.get_kev_entry(cve_id)
                kev_vulns.append({"cve_id": cve_id, "kev_entry": kev_entry})

        # Check status of KEV vulnerabilities
        total_kev = len(kev_vulns)
        remediated_kev = 0
        overdue_kev = []

        for kev_vuln in kev_vulns:
            # In a real implementation, check if vulnerability is remediated
            # For now, assume vulnerability status from input
            vuln_status = next(
                (v.get("status", "open") for v in vulnerabilities if v.get("cve_id") == kev_vuln["cve_id"]),
                "open",
            )

            if vuln_status in ["remediated", "mitigated", "closed"]:
                remediated_kev += 1
            else:
                # Check if overdue
                kev_entry = kev_vuln["kev_entry"]
                if kev_entry and kev_entry.due_date:
                    try:
                        due_date = datetime.fromisoformat(kev_entry.due_date)
                        if datetime.now() > due_date:
                            overdue_kev.append(kev_vuln["cve_id"])
                    except ValueError:
                        pass

        # Calculate compliance
        compliance_percentage = (remediated_kev / total_kev * 100) if total_kev > 0 else 100.0
        compliant = compliance_percentage >= 95.0 and len(overdue_kev) == 0

        findings = []
        recommendations = []

        findings.append(f"Total KEV vulnerabilities: {total_kev}")
        findings.append(f"Remediated: {remediated_kev}")
        findings.append(f"Open: {total_kev - remediated_kev}")

        if overdue_kev:
            findings.append(f"⚠️ Overdue remediations: {len(overdue_kev)}")
            recommendations.append(f"Immediately remediate {len(overdue_kev)} overdue KEV vulnerabilities")

        if not compliant:
            recommendations.append("Increase remediation efforts to achieve 95%+ KEV compliance")

        return BODCheckResult(
            directive=BODDirective.BOD_22_01,
            compliant=compliant,
            compliance_percentage=round(compliance_percentage, 2),
            findings=findings,
            recommendations=recommendations,
            details={
                "total_kev": total_kev,
                "remediated": remediated_kev,
                "open": total_kev - remediated_kev,
                "overdue": len(overdue_kev),
                "overdue_cves": overdue_kev,
            },
        )

    def check_bod_23_01(self, assets: list[dict[str, Any]], scan_coverage: float) -> BODCheckResult:
        """
        Check compliance with BOD 23-01.

        BOD 23-01 requires asset inventory completeness and vulnerability
        detection coverage.

        Args:
            assets: List of discovered assets
            scan_coverage: Vulnerability scan coverage percentage (0-100)

        Returns:
            BOD 23-01 compliance result
        """
        logger.info("Checking BOD 23-01 compliance")

        total_assets = len(assets)
        inventoried_assets = len([a for a in assets if a.get("inventoried", False)])
        scanned_assets = len([a for a in assets if a.get("last_scan")])

        # Asset inventory completeness (should be 100%)
        inventory_percentage = (inventoried_assets / total_assets * 100) if total_assets > 0 else 0.0

        # Vulnerability detection coverage (should be >= 95%)
        detection_percentage = scan_coverage

        # Overall compliance (both criteria must be met)
        compliant = inventory_percentage >= 100.0 and detection_percentage >= 95.0

        findings = []
        recommendations = []

        findings.append(f"Total assets: {total_assets}")
        findings.append(f"Inventoried assets: {inventoried_assets} ({inventory_percentage:.1f}%)")
        findings.append(f"Scanned assets: {scanned_assets}")
        findings.append(f"Vulnerability detection coverage: {detection_percentage:.1f}%")

        if inventory_percentage < 100.0:
            findings.append(f"⚠️ Asset inventory incomplete: {total_assets - inventoried_assets} assets missing")
            recommendations.append("Complete asset inventory for all discovered assets")

        if detection_percentage < 95.0:
            findings.append(f"⚠️ Vulnerability detection coverage below 95%")
            recommendations.append("Expand vulnerability scanning to achieve 95%+ coverage")

        return BODCheckResult(
            directive=BODDirective.BOD_23_01,
            compliant=compliant,
            compliance_percentage=round(min(inventory_percentage, detection_percentage), 2),
            findings=findings,
            recommendations=recommendations,
            details={
                "total_assets": total_assets,
                "inventoried_assets": inventoried_assets,
                "inventory_percentage": inventory_percentage,
                "detection_percentage": detection_percentage,
            },
        )

    def check_bod_18_01(self, email_config: dict[str, Any], web_config: dict[str, Any]) -> BODCheckResult:
        """
        Check compliance with BOD 18-01.

        BOD 18-01 requires:
        - Email: DMARC, SPF, DKIM
        - Web: HTTPS enforcement, HSTS

        Args:
            email_config: Email security configuration
            web_config: Web security configuration

        Returns:
            BOD 18-01 compliance result
        """
        logger.info("Checking BOD 18-01 compliance")

        findings = []
        recommendations = []
        issues = []

        # Email security checks
        has_dmarc = email_config.get("dmarc", False)
        has_spf = email_config.get("spf", False)
        has_dkim = email_config.get("dkim", False)

        if not has_dmarc:
            issues.append("DMARC not configured")
            recommendations.append("Implement DMARC for email domain")
        else:
            findings.append("✓ DMARC configured")

        if not has_spf:
            issues.append("SPF not configured")
            recommendations.append("Implement SPF for email domain")
        else:
            findings.append("✓ SPF configured")

        if not has_dkim:
            issues.append("DKIM not configured")
            recommendations.append("Implement DKIM for email domain")
        else:
            findings.append("✓ DKIM configured")

        # Web security checks
        has_https = web_config.get("https_enforced", False)
        has_hsts = web_config.get("hsts", False)

        if not has_https:
            issues.append("HTTPS not enforced")
            recommendations.append("Enforce HTTPS for all web services")
        else:
            findings.append("✓ HTTPS enforced")

        if not has_hsts:
            issues.append("HSTS not configured")
            recommendations.append("Implement HSTS header for web services")
        else:
            findings.append("✓ HSTS configured")

        # Calculate compliance
        total_checks = 5
        passed_checks = sum([has_dmarc, has_spf, has_dkim, has_https, has_hsts])
        compliance_percentage = (passed_checks / total_checks) * 100
        compliant = compliance_percentage >= 100.0

        if issues:
            findings.append(f"⚠️ {len(issues)} compliance issues found")

        return BODCheckResult(
            directive=BODDirective.BOD_18_01,
            compliant=compliant,
            compliance_percentage=round(compliance_percentage, 2),
            findings=findings,
            recommendations=recommendations,
            details={
                "email_security": {
                    "dmarc": has_dmarc,
                    "spf": has_spf,
                    "dkim": has_dkim,
                },
                "web_security": {
                    "https_enforced": has_https,
                    "hsts": has_hsts,
                },
                "issues": issues,
            },
        )

    def check_all(
        self,
        vulnerabilities: list[dict[str, Any]],
        assets: list[dict[str, Any]],
        scan_coverage: float,
        email_config: dict[str, Any],
        web_config: dict[str, Any],
    ) -> dict[str, BODCheckResult]:
        """
        Check all BOD directives.

        Args:
            vulnerabilities: List of vulnerabilities
            assets: List of assets
            scan_coverage: Scan coverage percentage
            email_config: Email configuration
            web_config: Web configuration

        Returns:
            Dictionary of BOD results
        """
        return {
            "bod_22_01": self.check_bod_22_01(vulnerabilities),
            "bod_23_01": self.check_bod_23_01(assets, scan_coverage),
            "bod_18_01": self.check_bod_18_01(email_config, web_config),
        }
