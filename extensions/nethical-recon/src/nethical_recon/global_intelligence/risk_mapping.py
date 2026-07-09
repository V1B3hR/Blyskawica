"""
Organization Risk Mapping

Creates comprehensive risk maps for entire organizations showing attack surface,
vulnerabilities, and business impact across all assets and infrastructure.

Part of ROADMAP 5.0 Section V.15: Global Attack Surface Intelligence
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4


@dataclass
class RiskZone:
    """Represents a risk zone in the organization"""

    zone_id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: str = ""
    risk_level: str = "medium"  # low, medium, high, critical
    risk_score: float = 0.0  # 0-100
    asset_count: int = 0
    critical_assets: int = 0
    vulnerabilities: list[dict[str, Any]] = field(default_factory=list)
    attack_vectors: list[str] = field(default_factory=list)
    business_impact: str = ""
    mitigation_priority: int = 5  # 1-10, 10 being highest
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RiskMap:
    """Complete risk map for an organization"""

    map_id: UUID = field(default_factory=uuid4)
    organization_name: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    zones: list[RiskZone] = field(default_factory=list)
    overall_risk_score: float = 0.0  # 0-100
    total_assets: int = 0
    high_risk_assets: int = 0
    critical_vulnerabilities: int = 0
    attack_surface_score: float = 0.0  # 0-100
    recommendations: list[str] = field(default_factory=list)
    compliance_gaps: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class OrganizationRiskMapper:
    """
    Organization Risk Mapper

    Creates comprehensive risk maps showing:
    - Attack surface by business unit/department
    - Critical asset exposure
    - Vulnerability distribution
    - Risk zones and hotspots
    - Business impact analysis
    - Compliance gaps

    Features:
    - Multi-dimensional risk scoring
    - Business context integration
    - Asset criticality weighting
    - Threat prioritization
    - Trend analysis
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """
        Initialize organization risk mapper

        Args:
            config: Configuration options
                - risk_weights: Custom weights for risk factors
                - compliance_frameworks: Frameworks to check (PCI-DSS, HIPAA, etc.)
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}

        self.risk_weights = self.config.get(
            "risk_weights",
            {
                "vulnerability": 0.35,
                "exposure": 0.25,
                "criticality": 0.25,
                "compliance": 0.15,
            },
        )

        self.compliance_frameworks = self.config.get("compliance_frameworks", [])

        self.logger.info("Organization Risk Mapper initialized")

    def create_risk_map(
        self,
        assets: list[dict[str, Any]],
        vulnerabilities: list[dict[str, Any]],
        organization_name: str = "Unknown",
    ) -> RiskMap:
        """
        Create comprehensive risk map for organization

        Args:
            assets: List of all organizational assets
            vulnerabilities: List of identified vulnerabilities
            organization_name: Name of the organization

        Returns:
            Complete risk map
        """
        self.logger.info(f"Creating risk map for {organization_name}")

        risk_map = RiskMap(
            organization_name=organization_name,
            total_assets=len(assets),
        )

        # Group assets into risk zones
        zones = self._create_risk_zones(assets, vulnerabilities)
        risk_map.zones = zones

        # Calculate overall metrics
        risk_map.overall_risk_score = self._calculate_overall_risk(zones)
        risk_map.high_risk_assets = sum(1 for asset in assets if self._get_asset_risk(asset) >= 70)
        risk_map.critical_vulnerabilities = sum(1 for vuln in vulnerabilities if vuln.get("severity") == "critical")
        risk_map.attack_surface_score = self._calculate_attack_surface_score(assets)

        # Generate recommendations
        risk_map.recommendations = self._generate_recommendations(risk_map)

        # Identify compliance gaps
        risk_map.compliance_gaps = self._identify_compliance_gaps(assets, vulnerabilities)

        self.logger.info(
            f"Risk map created. Overall risk score: {risk_map.overall_risk_score:.1f}, "
            f"{risk_map.high_risk_assets} high-risk assets"
        )

        return risk_map

    def _create_risk_zones(self, assets: list[dict[str, Any]], vulnerabilities: list[dict[str, Any]]) -> list[RiskZone]:
        """Create risk zones by grouping assets"""
        zones = []

        # Group by department/location/environment
        asset_groups = {}

        for asset in assets:
            # Determine zone (by department, location, or type)
            zone_key = asset.get("department", asset.get("environment", "default"))

            if zone_key not in asset_groups:
                asset_groups[zone_key] = []

            asset_groups[zone_key].append(asset)

        # Create risk zone for each group
        for zone_name, zone_assets in asset_groups.items():
            # Find vulnerabilities for this zone
            zone_vulns = [v for v in vulnerabilities if v.get("asset_id") in [a.get("id") for a in zone_assets]]

            # Calculate zone risk
            zone_risk_score = self._calculate_zone_risk(zone_assets, zone_vulns)

            # Determine risk level
            if zone_risk_score >= 80:
                risk_level = "critical"
            elif zone_risk_score >= 60:
                risk_level = "high"
            elif zone_risk_score >= 40:
                risk_level = "medium"
            else:
                risk_level = "low"

            # Count critical assets
            critical_count = sum(1 for a in zone_assets if a.get("criticality") in ["high", "critical"])

            # Identify attack vectors
            attack_vectors = self._identify_attack_vectors(zone_assets, zone_vulns)

            zone = RiskZone(
                name=zone_name,
                description=f"Risk zone for {zone_name}",
                risk_level=risk_level,
                risk_score=zone_risk_score,
                asset_count=len(zone_assets),
                critical_assets=critical_count,
                vulnerabilities=zone_vulns,
                attack_vectors=attack_vectors,
                business_impact=self._assess_business_impact(zone_assets),
                mitigation_priority=self._calculate_mitigation_priority(zone_risk_score, critical_count),
            )

            zones.append(zone)

        return zones

    def _calculate_zone_risk(self, assets: list[dict[str, Any]], vulnerabilities: list[dict[str, Any]]) -> float:
        """Calculate risk score for a zone"""
        if not assets:
            return 0.0

        # Average asset risk
        asset_risks = [self._get_asset_risk(asset) for asset in assets]
        avg_asset_risk = sum(asset_risks) / len(asset_risks)

        # Vulnerability factor
        vuln_score = min(100, len(vulnerabilities) * 5)

        # Criticality factor
        critical_assets = sum(1 for a in assets if a.get("criticality") in ["high", "critical"])
        criticality_score = (critical_assets / len(assets)) * 100 if assets else 0

        # Weighted score
        risk_score = (
            avg_asset_risk * self.risk_weights["vulnerability"]
            + vuln_score * self.risk_weights["exposure"]
            + criticality_score * self.risk_weights["criticality"]
        )

        return min(100.0, risk_score)

    def _get_asset_risk(self, asset: dict[str, Any]) -> float:
        """Calculate risk score for an individual asset"""
        risk = 0.0

        # Base risk from criticality
        criticality = asset.get("criticality", "medium")
        criticality_scores = {"low": 20, "medium": 40, "high": 70, "critical": 90}
        risk += criticality_scores.get(criticality, 40)

        # Public exposure
        if asset.get("public_access", False):
            risk += 20

        # Missing security controls
        if not asset.get("encryption", True):
            risk += 10

        return min(100.0, risk)

    def _calculate_overall_risk(self, zones: list[RiskZone]) -> float:
        """Calculate overall organization risk score"""
        if not zones:
            return 0.0

        # Weighted average by asset count
        total_assets = sum(z.asset_count for z in zones)
        if total_assets == 0:
            return 0.0

        weighted_risk = sum(z.risk_score * z.asset_count for z in zones)
        return weighted_risk / total_assets

    def _calculate_attack_surface_score(self, assets: list[dict[str, Any]]) -> float:
        """Calculate attack surface score"""
        if not assets:
            return 0.0

        # Count exposed assets
        public_assets = sum(1 for a in assets if a.get("public_access", False))

        # Score based on exposure
        exposure_ratio = public_assets / len(assets)
        return exposure_ratio * 100

    def _identify_attack_vectors(
        self, assets: list[dict[str, Any]], vulnerabilities: list[dict[str, Any]]
    ) -> list[str]:
        """Identify attack vectors for a zone"""
        vectors = set()

        # From vulnerabilities
        for vuln in vulnerabilities:
            vuln_type = vuln.get("type", "")
            if "injection" in vuln_type.lower():
                vectors.add("SQL Injection")
            if "xss" in vuln_type.lower():
                vectors.add("Cross-Site Scripting")
            if "auth" in vuln_type.lower():
                vectors.add("Authentication Bypass")

        # From asset configuration
        for asset in assets:
            if asset.get("public_access", False):
                vectors.add("Public Internet Exposure")

            if not asset.get("encryption", True):
                vectors.add("Unencrypted Data Access")

        return list(vectors)

    def _assess_business_impact(self, assets: list[dict[str, Any]]) -> str:
        """Assess business impact of zone compromise"""
        critical_count = sum(1 for a in assets if a.get("criticality") == "critical")

        if critical_count > len(assets) * 0.5:
            return "Severe - Business critical systems"
        elif critical_count > 0:
            return "High - Contains critical assets"
        else:
            return "Moderate - Standard business impact"

    def _calculate_mitigation_priority(self, risk_score: float, critical_assets: int) -> int:
        """Calculate mitigation priority (1-10)"""
        priority = int(risk_score / 10)  # Base on risk score

        # Boost for critical assets
        if critical_assets > 0:
            priority += 2

        return min(10, max(1, priority))

    def _generate_recommendations(self, risk_map: RiskMap) -> list[str]:
        """Generate recommendations based on risk map"""
        recommendations = []

        if risk_map.overall_risk_score > 70:
            recommendations.append("URGENT: Implement immediate risk reduction measures across organization")

        if risk_map.high_risk_assets > risk_map.total_assets * 0.3:
            recommendations.append("Prioritize remediation of high-risk assets")

        if risk_map.attack_surface_score > 50:
            recommendations.append("Reduce public attack surface through network segmentation")

        if risk_map.critical_vulnerabilities > 10:
            recommendations.append("Accelerate vulnerability patching program")

        # Zone-specific recommendations
        high_risk_zones = [z for z in risk_map.zones if z.risk_level in ["high", "critical"]]
        if high_risk_zones:
            recommendations.append(
                f"Focus on {len(high_risk_zones)} high-risk zones: {', '.join(z.name for z in high_risk_zones[:3])}"
            )

        return recommendations

    def _identify_compliance_gaps(
        self, assets: list[dict[str, Any]], vulnerabilities: list[dict[str, Any]]
    ) -> list[str]:
        """Identify compliance gaps"""
        gaps = []

        # Check for unencrypted sensitive data
        unencrypted = sum(1 for a in assets if not a.get("encryption", False) and a.get("criticality") == "critical")

        if unencrypted > 0:
            gaps.append(f"{unencrypted} critical assets without encryption (PCI-DSS, HIPAA violation)")

        # Check for public databases
        public_dbs = sum(1 for a in assets if a.get("asset_type") == "database" and a.get("public_access", False))

        if public_dbs > 0:
            gaps.append(f"{public_dbs} publicly accessible databases (compliance violation)")

        return gaps
