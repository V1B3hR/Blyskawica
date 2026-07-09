"""
CISA Policy Modes

Pre-defined scanning profiles aligned with CISA recommendations for different
organization types and compliance requirements.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger(__name__)


class CISAPolicyMode(Enum):
    """CISA policy modes for different organization types."""

    CRITICAL_INFRASTRUCTURE = "critical_infrastructure"
    FEDERAL_AGENCY = "federal_agency"
    ENTERPRISE = "enterprise"
    SMALL_BUSINESS = "small_business"


@dataclass
class CISAScanProfile:
    """
    CISA scan profile configuration.

    Defines recommended scanning parameters, tests, and compliance requirements
    for a specific policy mode.
    """

    mode: CISAPolicyMode
    name: str
    description: str
    scan_frequency_days: int
    required_tests: list[str] = field(default_factory=list)
    alert_thresholds: dict[str, Any] = field(default_factory=dict)
    compliance_requirements: list[str] = field(default_factory=list)
    kev_focus: bool = False
    continuous_monitoring: bool = False
    aggressive_scanning: bool = False


class CISAPolicyManager:
    """
    CISA Policy Manager.

    Manages CISA-aligned scanning profiles and policy application.

    Features:
    - Pre-defined profiles for different org types
    - Profile-based scan configuration
    - Compliance tracking
    - Alert threshold management
    """

    def __init__(self):
        """Initialize CISA policy manager."""
        self._profiles = self._load_profiles()
        self._current_mode: CISAPolicyMode = CISAPolicyMode.ENTERPRISE

    def _load_profiles(self) -> dict[CISAPolicyMode, CISAScanProfile]:
        """
        Load pre-defined CISA scan profiles.

        Returns:
            Dictionary of policy modes to scan profiles
        """
        profiles = {
            CISAPolicyMode.CRITICAL_INFRASTRUCTURE: CISAScanProfile(
                mode=CISAPolicyMode.CRITICAL_INFRASTRUCTURE,
                name="Critical Infrastructure",
                description="Aggressive scanning for critical infrastructure sectors",
                scan_frequency_days=1,  # Daily scans
                required_tests=[
                    "vulnerability_scan",
                    "kev_check",
                    "port_scan",
                    "tls_scan",
                    "web_security",
                    "owasp_top_10",
                    "configuration_audit",
                ],
                alert_thresholds={
                    "critical": 0,  # Alert on any critical finding
                    "high": 1,
                    "medium": 5,
                    "kev_immediate": True,
                },
                compliance_requirements=[
                    "CISA KEV Remediation",
                    "NIST CSF",
                    "Sector-Specific Guidelines",
                ],
                kev_focus=True,
                continuous_monitoring=True,
                aggressive_scanning=True,
            ),
            CISAPolicyMode.FEDERAL_AGENCY: CISAScanProfile(
                mode=CISAPolicyMode.FEDERAL_AGENCY,
                name="Federal Agency",
                description="BOD 22-01 compliant scanning for federal agencies",
                scan_frequency_days=1,  # Daily scans
                required_tests=[
                    "vulnerability_scan",
                    "kev_check",
                    "bod_22_01_compliance",
                    "bod_23_01_compliance",
                    "bod_18_01_compliance",
                    "asset_inventory",
                    "email_security",
                    "web_security",
                ],
                alert_thresholds={
                    "critical": 0,
                    "high": 0,
                    "medium": 3,
                    "kev_immediate": True,
                },
                compliance_requirements=[
                    "BOD 22-01",
                    "BOD 23-01",
                    "BOD 18-01",
                    "FISMA",
                    "CISA KEV",
                ],
                kev_focus=True,
                continuous_monitoring=True,
                aggressive_scanning=True,
            ),
            CISAPolicyMode.ENTERPRISE: CISAScanProfile(
                mode=CISAPolicyMode.ENTERPRISE,
                name="Enterprise",
                description="Balanced approach for enterprise organizations",
                scan_frequency_days=7,  # Weekly scans
                required_tests=[
                    "vulnerability_scan",
                    "kev_check",
                    "port_scan",
                    "web_security",
                    "configuration_audit",
                ],
                alert_thresholds={
                    "critical": 1,
                    "high": 3,
                    "medium": 10,
                    "kev_immediate": True,
                },
                compliance_requirements=[
                    "CISA KEV",
                    "OWASP Top 10",
                    "Industry Best Practices",
                ],
                kev_focus=True,
                continuous_monitoring=False,
                aggressive_scanning=False,
            ),
            CISAPolicyMode.SMALL_BUSINESS: CISAScanProfile(
                mode=CISAPolicyMode.SMALL_BUSINESS,
                name="Small Business",
                description="Lightweight scanning for small businesses",
                scan_frequency_days=30,  # Monthly scans
                required_tests=[
                    "vulnerability_scan",
                    "kev_check",
                    "basic_web_security",
                ],
                alert_thresholds={
                    "critical": 3,
                    "high": 5,
                    "medium": 15,
                    "kev_immediate": True,
                },
                compliance_requirements=[
                    "CISA KEV (High Priority)",
                    "Basic Security Hygiene",
                ],
                kev_focus=True,
                continuous_monitoring=False,
                aggressive_scanning=False,
            ),
        }

        return profiles

    def get_profile(self, mode: CISAPolicyMode) -> CISAScanProfile:
        """
        Get scan profile for policy mode.

        Args:
            mode: CISA policy mode

        Returns:
            Scan profile configuration
        """
        return self._profiles[mode]

    def apply_profile(self, mode: CISAPolicyMode) -> dict[str, Any]:
        """
        Apply CISA policy mode.

        Args:
            mode: Policy mode to apply

        Returns:
            Applied configuration
        """
        profile = self.get_profile(mode)
        self._current_mode = mode

        logger.info(f"Applied CISA policy mode: {mode.value}")
        logger.info(f"Scan frequency: every {profile.scan_frequency_days} days")
        logger.info(f"Required tests: {', '.join(profile.required_tests)}")

        return {
            "mode": mode.value,
            "profile": {
                "name": profile.name,
                "description": profile.description,
                "scan_frequency_days": profile.scan_frequency_days,
                "required_tests": profile.required_tests,
                "alert_thresholds": profile.alert_thresholds,
                "compliance_requirements": profile.compliance_requirements,
                "kev_focus": profile.kev_focus,
                "continuous_monitoring": profile.continuous_monitoring,
            },
        }

    def get_current_mode(self) -> CISAPolicyMode:
        """
        Get currently active policy mode.

        Returns:
            Current policy mode
        """
        return self._current_mode

    def get_compliance_requirements(self, mode: Optional[CISAPolicyMode] = None) -> list[str]:
        """
        Get compliance requirements for policy mode.

        Args:
            mode: Policy mode (uses current mode if not specified)

        Returns:
            List of compliance requirements
        """
        mode = mode or self._current_mode
        profile = self.get_profile(mode)
        return profile.compliance_requirements

    def check_scan_frequency(self, mode: Optional[CISAPolicyMode] = None) -> int:
        """
        Get required scan frequency in days.

        Args:
            mode: Policy mode (uses current mode if not specified)

        Returns:
            Scan frequency in days
        """
        mode = mode or self._current_mode
        profile = self.get_profile(mode)
        return profile.scan_frequency_days
