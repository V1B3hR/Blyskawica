"""
CISA Category Mapping

Maps security findings to CISA categories, severity levels, and guidance.
Aligns risk scoring with CISA framework.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class CISACategory(Enum):
    """CISA service and function categories."""

    VULNERABILITY_MANAGEMENT = "vulnerability_management"
    THREAT_HUNTING = "threat_hunting"
    INCIDENT_RESPONSE = "incident_response"
    ASSET_MANAGEMENT = "asset_management"
    NETWORK_SECURITY = "network_security"
    ENDPOINT_SECURITY = "endpoint_security"
    CLOUD_SECURITY = "cloud_security"
    EMAIL_SECURITY = "email_security"
    WEB_SECURITY = "web_security"
    DATA_PROTECTION = "data_protection"


class CISASeverityLevel(Enum):
    """CISA severity levels."""

    CRITICAL = "critical"  # 90-100
    HIGH = "high"  # 70-89
    MEDIUM = "medium"  # 40-69
    LOW = "low"  # 0-39


class CriticalInfrastructureSector(Enum):
    """16 critical infrastructure sectors defined by CISA."""

    CHEMICAL = "chemical"
    COMMERCIAL_FACILITIES = "commercial_facilities"
    COMMUNICATIONS = "communications"
    CRITICAL_MANUFACTURING = "critical_manufacturing"
    DAMS = "dams"
    DEFENSE_INDUSTRIAL_BASE = "defense_industrial_base"
    EMERGENCY_SERVICES = "emergency_services"
    ENERGY = "energy"
    FINANCIAL_SERVICES = "financial_services"
    FOOD_AND_AGRICULTURE = "food_and_agriculture"
    GOVERNMENT_FACILITIES = "government_facilities"
    HEALTHCARE = "healthcare"
    INFORMATION_TECHNOLOGY = "information_technology"
    NUCLEAR = "nuclear"
    TRANSPORTATION = "transportation"
    WATER = "water"


@dataclass
class CISAMapping:
    """CISA category mapping for a finding."""

    finding_id: str
    cisa_category: CISACategory
    cisa_severity: CISASeverityLevel
    cisa_recommendation: str
    sector: Optional[CriticalInfrastructureSector] = None


class CISACategoryMapper:
    """
    CISA Category Mapper.

    Maps security findings to CISA categories and guidelines.

    Features:
    - Category classification
    - Severity alignment
    - Recommendation mapping
    - Critical infrastructure sector identification
    - Coverage analysis
    """

    def __init__(self):
        """Initialize CISA category mapper."""
        self._category_rules = self._load_category_rules()
        self._monitored_categories: set[CISACategory] = set()

    def _load_category_rules(self) -> dict[str, CISACategory]:
        """Load category classification rules."""
        return {
            "vulnerability": CISACategory.VULNERABILITY_MANAGEMENT,
            "cve": CISACategory.VULNERABILITY_MANAGEMENT,
            "kev": CISACategory.VULNERABILITY_MANAGEMENT,
            "patch": CISACategory.VULNERABILITY_MANAGEMENT,
            "threat": CISACategory.THREAT_HUNTING,
            "malware": CISACategory.THREAT_HUNTING,
            "ioc": CISACategory.THREAT_HUNTING,
            "incident": CISACategory.INCIDENT_RESPONSE,
            "breach": CISACategory.INCIDENT_RESPONSE,
            "compromise": CISACategory.INCIDENT_RESPONSE,
            "asset": CISACategory.ASSET_MANAGEMENT,
            "inventory": CISACategory.ASSET_MANAGEMENT,
            "network": CISACategory.NETWORK_SECURITY,
            "firewall": CISACategory.NETWORK_SECURITY,
            "port": CISACategory.NETWORK_SECURITY,
            "endpoint": CISACategory.ENDPOINT_SECURITY,
            "host": CISACategory.ENDPOINT_SECURITY,
            "cloud": CISACategory.CLOUD_SECURITY,
            "aws": CISACategory.CLOUD_SECURITY,
            "azure": CISACategory.CLOUD_SECURITY,
            "gcp": CISACategory.CLOUD_SECURITY,
            "email": CISACategory.EMAIL_SECURITY,
            "smtp": CISACategory.EMAIL_SECURITY,
            "phishing": CISACategory.EMAIL_SECURITY,
            "web": CISACategory.WEB_SECURITY,
            "http": CISACategory.WEB_SECURITY,
            "https": CISACategory.WEB_SECURITY,
            "ssl": CISACategory.WEB_SECURITY,
            "tls": CISACategory.WEB_SECURITY,
            "data": CISACategory.DATA_PROTECTION,
            "encryption": CISACategory.DATA_PROTECTION,
            "backup": CISACategory.DATA_PROTECTION,
        }

    def map_finding(
        self,
        finding_id: str,
        finding_type: str,
        risk_score: float,
        description: str = "",
    ) -> CISAMapping:
        """
        Map finding to CISA categories.

        Args:
            finding_id: Finding identifier
            finding_type: Type of finding
            risk_score: Risk score (0-100)
            description: Finding description

        Returns:
            CISA mapping
        """
        # Determine category
        category = self._classify_category(finding_type, description)

        # Map severity
        severity = self._map_severity(risk_score)

        # Generate recommendation
        recommendation = self._generate_recommendation(category, severity)

        # Create mapping
        mapping = CISAMapping(
            finding_id=finding_id,
            cisa_category=category,
            cisa_severity=severity,
            cisa_recommendation=recommendation,
        )

        # Track monitored categories
        self._monitored_categories.add(category)

        return mapping

    def _classify_category(self, finding_type: str, description: str) -> CISACategory:
        """Classify finding into CISA category."""
        finding_type_lower = finding_type.lower()
        description_lower = description.lower()

        # Check finding type first
        for keyword, category in self._category_rules.items():
            if keyword in finding_type_lower:
                return category

        # Check description
        for keyword, category in self._category_rules.items():
            if keyword in description_lower:
                return category

        # Default to vulnerability management
        return CISACategory.VULNERABILITY_MANAGEMENT

    def _map_severity(self, risk_score: float) -> CISASeverityLevel:
        """
        Map risk score to CISA severity level.

        CISA Severity Mapping:
        - Critical: 90-100
        - High: 70-89
        - Medium: 40-69
        - Low: 0-39
        """
        if risk_score >= 90:
            return CISASeverityLevel.CRITICAL
        elif risk_score >= 70:
            return CISASeverityLevel.HIGH
        elif risk_score >= 40:
            return CISASeverityLevel.MEDIUM
        else:
            return CISASeverityLevel.LOW

    def _generate_recommendation(self, category: CISACategory, severity: CISASeverityLevel) -> str:
        """Generate CISA-aligned recommendation."""
        recommendations = {
            CISACategory.VULNERABILITY_MANAGEMENT: {
                CISASeverityLevel.CRITICAL: "Immediately patch or mitigate. Check CISA KEV catalog.",
                CISASeverityLevel.HIGH: "Prioritize patching within organizational SLA.",
                CISASeverityLevel.MEDIUM: "Schedule patching in next maintenance window.",
                CISASeverityLevel.LOW: "Monitor and patch per regular schedule.",
            },
            CISACategory.THREAT_HUNTING: {
                CISASeverityLevel.CRITICAL: "Initiate incident response procedures immediately.",
                CISASeverityLevel.HIGH: "Investigate threat indicators and contain if necessary.",
                CISASeverityLevel.MEDIUM: "Monitor threat activity and update defenses.",
                CISASeverityLevel.LOW: "Log for future correlation and analysis.",
            },
            CISACategory.NETWORK_SECURITY: {
                CISASeverityLevel.CRITICAL: "Isolate affected systems and review firewall rules.",
                CISASeverityLevel.HIGH: "Update network security controls and monitor traffic.",
                CISASeverityLevel.MEDIUM: "Review network segmentation and access controls.",
                CISASeverityLevel.LOW: "Document for next security review.",
            },
        }

        # Get specific recommendation or use default
        category_recs = recommendations.get(
            category,
            {
                CISASeverityLevel.CRITICAL: "Take immediate action per CISA guidelines.",
                CISASeverityLevel.HIGH: "Address promptly per CISA best practices.",
                CISASeverityLevel.MEDIUM: "Review and remediate per CISA recommendations.",
                CISASeverityLevel.LOW: "Monitor per CISA guidance.",
            },
        )

        return category_recs.get(severity, "Follow CISA guidelines for remediation.")

    def get_coverage_report(self) -> dict[str, Any]:
        """
        Get CISA coverage report.

        Shows which CISA-recommended areas are being monitored.

        Returns:
            Coverage report with monitored categories and gaps
        """
        all_categories = set(CISACategory)
        monitored = self._monitored_categories
        gaps = all_categories - monitored

        coverage_percentage = (len(monitored) / len(all_categories)) * 100 if all_categories else 0

        return {
            "total_categories": len(all_categories),
            "monitored_categories": len(monitored),
            "coverage_percentage": round(coverage_percentage, 2),
            "monitored": [cat.value for cat in monitored],
            "gaps": [cat.value for cat in gaps],
            "recommendations": self._generate_coverage_recommendations(gaps),
        }

    def _generate_coverage_recommendations(self, gaps: set[CISACategory]) -> list[str]:
        """Generate recommendations for coverage gaps."""
        recommendations = []

        gap_descriptions = {
            CISACategory.VULNERABILITY_MANAGEMENT: "Implement vulnerability scanning and KEV monitoring",
            CISACategory.THREAT_HUNTING: "Deploy threat intelligence and hunting capabilities",
            CISACategory.INCIDENT_RESPONSE: "Establish incident response procedures and monitoring",
            CISACategory.ASSET_MANAGEMENT: "Implement asset discovery and inventory management",
            CISACategory.NETWORK_SECURITY: "Deploy network monitoring and security controls",
            CISACategory.ENDPOINT_SECURITY: "Implement endpoint detection and response",
            CISACategory.CLOUD_SECURITY: "Deploy cloud security posture management",
            CISACategory.EMAIL_SECURITY: "Implement email security gateway and monitoring",
            CISACategory.WEB_SECURITY: "Deploy web application firewall and scanning",
            CISACategory.DATA_PROTECTION: "Implement data loss prevention and encryption",
        }

        for gap in gaps:
            if gap in gap_descriptions:
                recommendations.append(gap_descriptions[gap])

        return recommendations
