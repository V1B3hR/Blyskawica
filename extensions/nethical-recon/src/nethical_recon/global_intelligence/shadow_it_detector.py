"""
Shadow IT Detector

Identifies unauthorized cloud resources and services (Shadow IT) that are not
registered in the official asset inventory or CMDB.

Part of ROADMAP 5.0 Section V.15: Global Attack Surface Intelligence
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4


class ShadowITType(Enum):
    """Types of Shadow IT resources"""

    UNAUTHORIZED_CLOUD = "unauthorized_cloud"
    UNMANAGED_SERVICE = "unmanaged_service"
    PERSONAL_ACCOUNT = "personal_account"
    UNAPPROVED_SOFTWARE = "unapproved_software"
    UNKNOWN_SUBDOMAIN = "unknown_subdomain"
    UNREGISTERED_DEVICE = "unregistered_device"


@dataclass
class ShadowITFinding:
    """Represents a Shadow IT discovery"""

    finding_id: UUID = field(default_factory=uuid4)
    shadow_it_type: ShadowITType = ShadowITType.UNAUTHORIZED_CLOUD
    resource_identifier: str = ""
    discovery_method: str = ""
    discovery_timestamp: datetime = field(default_factory=datetime.utcnow)
    severity: str = "medium"  # low, medium, high, critical
    confidence: float = 0.7
    description: str = ""
    evidence: list[str] = field(default_factory=list)
    risk_factors: list[str] = field(default_factory=list)
    recommended_actions: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class ShadowITDetector:
    """
    Shadow IT Detector

    Identifies unauthorized IT resources and services:
    - Unauthorized cloud accounts and resources
    - Unmanaged SaaS applications
    - Personal cloud storage usage
    - Unregistered subdomains
    - Unmanaged devices on the network

    Detection Methods:
    - Compare discovered assets with CMDB
    - Cloud provider API enumeration
    - DNS and certificate analysis
    - Network traffic analysis
    - User behavior monitoring
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """
        Initialize Shadow IT detector

        Args:
            config: Configuration options
                - authorized_cloud_accounts: List of authorized cloud account IDs
                - authorized_domains: List of authorized domain patterns
                - min_confidence_threshold: Minimum confidence to report (default: 0.6)
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}

        self.authorized_cloud_accounts = self.config.get("authorized_cloud_accounts", [])
        self.authorized_domains = self.config.get("authorized_domains", [])
        self.min_confidence_threshold = self.config.get("min_confidence_threshold", 0.6)

        self.logger.info("Shadow IT Detector initialized")

    def detect_shadow_cloud(
        self, discovered_assets: list[dict[str, Any]], cmdb_assets: list[dict[str, Any]]
    ) -> list[ShadowITFinding]:
        """
        Detect shadow cloud resources by comparing discovered assets with CMDB

        Args:
            discovered_assets: Assets found during reconnaissance
            cmdb_assets: Assets registered in CMDB

        Returns:
            List of Shadow IT findings
        """
        self.logger.info(f"Analyzing {len(discovered_assets)} assets for Shadow IT")

        findings = []
        cmdb_identifiers = {asset.get("identifier", "") for asset in cmdb_assets}

        for asset in discovered_assets:
            asset_id = asset.get("identifier", "")
            asset_type = asset.get("asset_type", "")

            # Check if asset is in CMDB
            if asset_id not in cmdb_identifiers:
                # Potential Shadow IT
                finding = self._analyze_unauthorized_asset(asset)

                if finding and finding.confidence >= self.min_confidence_threshold:
                    findings.append(finding)

        self.logger.info(f"Detected {len(findings)} potential Shadow IT resources")

        return findings

    def detect_unauthorized_subdomains(
        self, discovered_subdomains: list[str], authorized_patterns: list[str] | None = None
    ) -> list[ShadowITFinding]:
        """
        Detect unauthorized subdomains not matching approved patterns

        Args:
            discovered_subdomains: List of discovered subdomains
            authorized_patterns: List of authorized subdomain patterns

        Returns:
            List of Shadow IT findings for unauthorized subdomains
        """
        patterns = authorized_patterns or self.authorized_domains
        findings = []

        for subdomain in discovered_subdomains:
            # Check if subdomain matches any authorized pattern
            is_authorized = any(self._matches_pattern(subdomain, pattern) for pattern in patterns)

            if not is_authorized:
                finding = ShadowITFinding(
                    shadow_it_type=ShadowITType.UNKNOWN_SUBDOMAIN,
                    resource_identifier=subdomain,
                    discovery_method="subdomain_enumeration",
                    severity="medium",
                    confidence=0.8,
                    description=f"Unauthorized subdomain detected: {subdomain}",
                    evidence=[f"Subdomain not matching authorized patterns"],
                    risk_factors=[
                        "Potential data exfiltration channel",
                        "Unmonitored security posture",
                        "Compliance violation",
                    ],
                    recommended_actions=[
                        "Verify subdomain ownership",
                        "Assess security configuration",
                        "Add to asset inventory if legitimate",
                        "Decommission if unauthorized",
                    ],
                )

                findings.append(finding)

        return findings

    def _analyze_unauthorized_asset(self, asset: dict[str, Any]) -> ShadowITFinding | None:
        """Analyze an asset for Shadow IT indicators"""
        asset_id = asset.get("identifier", "")
        asset_type = asset.get("asset_type", "")

        # Determine Shadow IT type
        if "cloud" in asset_type.lower():
            shadow_type = ShadowITType.UNAUTHORIZED_CLOUD
        elif "service" in asset_type.lower():
            shadow_type = ShadowITType.UNMANAGED_SERVICE
        else:
            shadow_type = ShadowITType.UNAUTHORIZED_CLOUD

        # Calculate confidence
        confidence = 0.7

        # Check for high-confidence indicators
        if asset.get("discovery_method") == "cloud_api":
            confidence += 0.2

        # Determine severity
        severity = "medium"
        risk_factors = ["Unmanaged security configuration", "No compliance oversight"]

        if "production" in str(asset.get("properties", {})).lower():
            severity = "high"
            risk_factors.append("Production environment exposure")

        if asset.get("public_access", False):
            severity = "high"
            risk_factors.append("Public internet access")
            confidence += 0.1

        finding = ShadowITFinding(
            shadow_it_type=shadow_type,
            resource_identifier=asset_id,
            discovery_method=asset.get("discovery_method", "unknown"),
            severity=severity,
            confidence=min(1.0, confidence),
            description=f"Unauthorized {asset_type} detected: {asset_id}",
            evidence=[f"Not found in asset inventory", f"Discovered via {asset.get('discovery_method', 'scan')}"],
            risk_factors=risk_factors,
            recommended_actions=[
                "Verify resource ownership and purpose",
                "Assess security configuration and compliance",
                "Add to inventory if legitimate",
                "Decommission if unauthorized",
                "Implement approval workflow for new resources",
            ],
        )

        return finding

    def _matches_pattern(self, subdomain: str, pattern: str) -> bool:
        """Check if subdomain matches an authorized pattern"""
        # Simple pattern matching (would use regex in production)
        if "*" in pattern:
            # Wildcard pattern
            prefix = pattern.split("*")[0]
            return subdomain.startswith(prefix)

        return subdomain == pattern or subdomain.endswith(f".{pattern}")
