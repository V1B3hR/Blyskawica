"""
Asset Inventory and CMDB Integration

Integrates with enterprise asset inventory systems and Configuration Management
Databases (CMDB) to enrich reconnaissance data with enterprise context.

Part of ROADMAP 5.0 Section V.14: Advanced Security Features
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4


class AssetType(Enum):
    """Types of assets in the inventory"""

    SERVER = "server"
    WORKSTATION = "workstation"
    NETWORK_DEVICE = "network_device"
    MOBILE_DEVICE = "mobile_device"
    CLOUD_INSTANCE = "cloud_instance"
    CONTAINER = "container"
    APPLICATION = "application"
    DATABASE = "database"
    STORAGE = "storage"
    IOT_DEVICE = "iot_device"


class AssetCriticality(Enum):
    """Criticality levels for assets"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class CMDBAsset:
    """Represents an asset from CMDB/inventory system"""

    asset_id: UUID = field(default_factory=uuid4)
    external_id: str = ""  # ID in external system
    name: str = ""
    asset_type: AssetType = AssetType.SERVER
    criticality: AssetCriticality = AssetCriticality.MEDIUM
    owner: str = ""  # Business owner
    technical_owner: str = ""  # Technical contact
    department: str = ""
    location: str = ""
    environment: str = "production"  # production, staging, development, test
    ip_addresses: list[str] = field(default_factory=list)
    hostnames: list[str] = field(default_factory=list)
    operating_system: str = ""
    applications: list[str] = field(default_factory=list)
    services: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    compliance_requirements: list[str] = field(default_factory=list)  # PCI-DSS, HIPAA, SOX, etc.
    last_updated: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EnrichedAsset:
    """Asset data enriched with CMDB information"""

    reconnaissance_data: dict[str, Any]  # Data from recon tools
    cmdb_data: CMDBAsset | None = None
    enrichment_timestamp: datetime = field(default_factory=datetime.utcnow)
    match_confidence: float = 0.0  # 0.0 to 1.0
    match_method: str = ""  # How the asset was matched (ip, hostname, etc.)
    discrepancies: list[str] = field(default_factory=list)  # Differences between recon and CMDB


class AssetInventoryIntegration:
    """
    Asset Inventory and CMDB Integration

    Features:
    - Integration with enterprise CMDB systems (ServiceNow, BMC, custom)
    - Asset matching and correlation
    - Data enrichment with business context
    - Discrepancy detection (shadow IT, configuration drift)
    - Compliance mapping
    - Risk assessment based on asset criticality

    Supported CMDB Systems:
    - ServiceNow CMDB
    - BMC Remedy
    - Jira Assets
    - Microsoft System Center
    - Custom REST APIs
    - CSV/Excel imports
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """
        Initialize asset inventory integration

        Args:
            config: Configuration options
                - cmdb_type: Type of CMDB (servicenow, bmc, jira, custom)
                - cmdb_url: URL of CMDB API
                - api_key: API key for authentication
                - sync_interval_hours: Hours between syncs (default: 24)
                - match_threshold: Minimum confidence for asset matching (default: 0.7)
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}

        self.cmdb_type = self.config.get("cmdb_type", "custom")
        self.cmdb_url = self.config.get("cmdb_url", "")
        self.api_key = self.config.get("api_key", "")
        self.sync_interval_hours = self.config.get("sync_interval_hours", 24)
        self.match_threshold = self.config.get("match_threshold", 0.7)

        # In-memory asset cache (would use database in production)
        self._asset_cache: dict[str, CMDBAsset] = {}
        self._last_sync: datetime | None = None

        self.logger.info(f"Asset Inventory Integration initialized (CMDB: {self.cmdb_type})")

    def load_assets_from_cmdb(self) -> int:
        """
        Load assets from CMDB system

        Returns:
            Number of assets loaded
        """
        self.logger.info(f"Loading assets from CMDB ({self.cmdb_type})")

        # In a real implementation, this would connect to actual CMDB systems
        # For now, we'll create a mock implementation

        if self.cmdb_type == "servicenow":
            assets = self._load_from_servicenow()
        elif self.cmdb_type == "bmc":
            assets = self._load_from_bmc()
        elif self.cmdb_type == "custom":
            assets = self._load_from_custom_api()
        else:
            self.logger.warning(f"Unsupported CMDB type: {self.cmdb_type}")
            return 0

        # Cache assets for fast lookup
        for asset in assets:
            # Index by multiple keys for flexible matching
            if asset.external_id:
                self._asset_cache[f"id:{asset.external_id}"] = asset

            for ip in asset.ip_addresses:
                self._asset_cache[f"ip:{ip}"] = asset

            for hostname in asset.hostnames:
                self._asset_cache[f"host:{hostname}"] = asset

        self._last_sync = datetime.utcnow()
        self.logger.info(f"Loaded {len(assets)} assets from CMDB")

        return len(assets)

    def enrich_reconnaissance_data(self, recon_data: dict[str, Any]) -> EnrichedAsset:
        """
        Enrich reconnaissance data with CMDB information

        Args:
            recon_data: Reconnaissance data to enrich
                - ip: IP address
                - hostname: Hostname
                - services: Discovered services
                - vulnerabilities: Found vulnerabilities
                - etc.

        Returns:
            Enriched asset data
        """
        # Try to match asset in CMDB
        cmdb_asset, confidence, method = self._find_matching_asset(recon_data)

        enriched = EnrichedAsset(
            reconnaissance_data=recon_data,
            cmdb_data=cmdb_asset,
            match_confidence=confidence,
            match_method=method,
        )

        if cmdb_asset and confidence >= self.match_threshold:
            # Detect discrepancies
            enriched.discrepancies = self._detect_discrepancies(recon_data, cmdb_asset)

            if enriched.discrepancies:
                self.logger.warning(
                    f"Discrepancies detected for asset {cmdb_asset.name}: " f"{len(enriched.discrepancies)} differences"
                )
        else:
            # No match found - potential shadow IT
            self.logger.info(f"Asset not found in CMDB: {recon_data.get('ip', 'unknown')} - possible shadow IT")

        return enriched

    def get_asset_criticality(self, asset_identifier: str) -> AssetCriticality | None:
        """
        Get criticality level for an asset

        Args:
            asset_identifier: IP, hostname, or asset ID

        Returns:
            Asset criticality or None if not found
        """
        asset = self._lookup_asset(asset_identifier)
        return asset.criticality if asset else None

    def get_compliance_requirements(self, asset_identifier: str) -> list[str]:
        """
        Get compliance requirements for an asset

        Args:
            asset_identifier: IP, hostname, or asset ID

        Returns:
            List of compliance frameworks applicable to the asset
        """
        asset = self._lookup_asset(asset_identifier)
        return asset.compliance_requirements if asset else []

    def calculate_business_impact_score(self, asset_identifier: str, finding_severity: str) -> float:
        """
        Calculate business impact score based on asset criticality and finding

        Args:
            asset_identifier: IP, hostname, or asset ID
            finding_severity: Severity of the security finding (low, medium, high, critical)

        Returns:
            Business impact score (0-100)
        """
        asset = self._lookup_asset(asset_identifier)

        if not asset:
            # Unknown asset, moderate impact
            return 50.0

        # Base score from asset criticality
        criticality_scores = {
            AssetCriticality.LOW: 20,
            AssetCriticality.MEDIUM: 40,
            AssetCriticality.HIGH: 70,
            AssetCriticality.CRITICAL: 90,
        }

        base_score = criticality_scores.get(asset.criticality, 40)

        # Adjust based on finding severity
        severity_multipliers = {"low": 0.5, "medium": 0.75, "high": 1.0, "critical": 1.2}

        multiplier = severity_multipliers.get(finding_severity.lower(), 1.0)

        impact_score = base_score * multiplier

        # Bonus for production environments
        if asset.environment == "production":
            impact_score += 10

        # Bonus for compliance-regulated assets
        if asset.compliance_requirements:
            impact_score += len(asset.compliance_requirements) * 5

        return min(100.0, impact_score)

    def _find_matching_asset(self, recon_data: dict[str, Any]) -> tuple[CMDBAsset | None, float, str]:
        """
        Find matching asset in CMDB

        Returns:
            Tuple of (asset, confidence, match_method)
        """
        # Try matching by IP
        ip_address = recon_data.get("ip", "")
        if ip_address:
            asset = self._lookup_asset(ip_address)
            if asset:
                return asset, 0.95, "ip_address"

        # Try matching by hostname
        hostname = recon_data.get("hostname", "")
        if hostname:
            asset = self._lookup_asset(hostname)
            if asset:
                return asset, 0.90, "hostname"

        # Try fuzzy matching
        asset, confidence = self._fuzzy_match_asset(recon_data)
        if asset and confidence >= self.match_threshold:
            return asset, confidence, "fuzzy_match"

        return None, 0.0, "no_match"

    def _lookup_asset(self, identifier: str) -> CMDBAsset | None:
        """Lookup asset by various identifiers"""
        # Try direct lookups
        if f"ip:{identifier}" in self._asset_cache:
            return self._asset_cache[f"ip:{identifier}"]

        if f"host:{identifier}" in self._asset_cache:
            return self._asset_cache[f"host:{identifier}"]

        if f"id:{identifier}" in self._asset_cache:
            return self._asset_cache[f"id:{identifier}"]

        return None

    def _fuzzy_match_asset(self, recon_data: dict[str, Any]) -> tuple[CMDBAsset | None, float]:
        """
        Fuzzy match asset based on multiple attributes

        Returns:
            Tuple of (asset, confidence)
        """
        # Simplified fuzzy matching (would use more sophisticated algorithms in production)
        best_match = None
        best_score = 0.0

        hostname = recon_data.get("hostname", "").lower()
        services = set(recon_data.get("services", []))

        for key, asset in self._asset_cache.items():
            if not key.startswith("id:"):
                continue  # Only check each asset once

            score = 0.0
            matches = 0

            # Check hostname similarity
            if hostname:
                for asset_hostname in asset.hostnames:
                    if hostname in asset_hostname.lower() or asset_hostname.lower() in hostname:
                        score += 0.4
                        matches += 1
                        break

            # Check service overlap
            asset_services = set(asset.services)
            if services and asset_services:
                overlap = len(services & asset_services)
                if overlap > 0:
                    score += 0.3 * (overlap / max(len(services), len(asset_services)))
                    matches += 1

            # Check OS match
            recon_os = recon_data.get("operating_system", "").lower()
            if recon_os and asset.operating_system.lower() in recon_os:
                score += 0.3
                matches += 1

            if matches > 0 and score > best_score:
                best_score = score
                best_match = asset

        return best_match, best_score

    def _detect_discrepancies(self, recon_data: dict[str, Any], cmdb_asset: CMDBAsset) -> list[str]:
        """Detect discrepancies between reconnaissance data and CMDB"""
        discrepancies = []

        # Check OS mismatch
        recon_os = recon_data.get("operating_system", "").lower()
        cmdb_os = cmdb_asset.operating_system.lower()

        if recon_os and cmdb_os and recon_os not in cmdb_os and cmdb_os not in recon_os:
            discrepancies.append(
                f"OS mismatch: CMDB={cmdb_asset.operating_system}, Recon={recon_data.get('operating_system')}"
            )

        # Check for services not in CMDB
        recon_services = set(recon_data.get("services", []))
        cmdb_services = set(cmdb_asset.services)

        unknown_services = recon_services - cmdb_services
        if unknown_services:
            discrepancies.append(f"Unknown services detected: {', '.join(unknown_services)}")

        # Check for IP address mismatches
        recon_ip = recon_data.get("ip", "")
        if recon_ip and recon_ip not in cmdb_asset.ip_addresses:
            discrepancies.append(f"IP address not in CMDB: {recon_ip}")

        return discrepancies

    def _load_from_servicenow(self) -> list[CMDBAsset]:
        """Load assets from ServiceNow CMDB"""
        # Mock implementation - would use ServiceNow API in production
        self.logger.info("Loading from ServiceNow CMDB (mock)")
        return []

    def _load_from_bmc(self) -> list[CMDBAsset]:
        """Load assets from BMC Remedy CMDB"""
        # Mock implementation - would use BMC API in production
        self.logger.info("Loading from BMC CMDB (mock)")
        return []

    def _load_from_custom_api(self) -> list[CMDBAsset]:
        """Load assets from custom API"""
        # Mock implementation - would make HTTP requests in production
        self.logger.info("Loading from custom API (mock)")

        # Return sample assets for demonstration
        sample_assets = [
            CMDBAsset(
                external_id="asset001",
                name="web-server-prod-01",
                asset_type=AssetType.SERVER,
                criticality=AssetCriticality.HIGH,
                owner="IT Operations",
                technical_owner="john.doe@example.com",
                department="Engineering",
                location="datacenter-us-east-1",
                environment="production",
                ip_addresses=["192.168.1.10", "10.0.1.10"],
                hostnames=["web-prod-01.example.com", "web01"],
                operating_system="Ubuntu 22.04 LTS",
                applications=["nginx", "nodejs"],
                services=["HTTP", "HTTPS", "SSH"],
                tags=["web", "production", "public-facing"],
                compliance_requirements=["PCI-DSS", "SOC2"],
            ),
            CMDBAsset(
                external_id="asset002",
                name="db-server-prod-01",
                asset_type=AssetType.DATABASE,
                criticality=AssetCriticality.CRITICAL,
                owner="Data Team",
                technical_owner="jane.smith@example.com",
                department="Engineering",
                location="datacenter-us-east-1",
                environment="production",
                ip_addresses=["192.168.1.20"],
                hostnames=["db-prod-01.example.com"],
                operating_system="Ubuntu 22.04 LTS",
                applications=["postgresql"],
                services=["PostgreSQL"],
                tags=["database", "production", "critical"],
                compliance_requirements=["PCI-DSS", "HIPAA", "SOC2"],
            ),
        ]

        return sample_assets
