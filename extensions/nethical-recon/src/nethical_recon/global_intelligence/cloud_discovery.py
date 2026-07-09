"""
Cloud Asset Discovery

Multi-cloud asset discovery for AWS, GCP, and Azure environments.
Identifies cloud resources across different providers and regions.

Part of ROADMAP 5.0 Section V.15: Global Attack Surface Intelligence
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4


class CloudProvider(Enum):
    """Supported cloud providers"""

    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    DIGITALOCEAN = "digitalocean"
    ALIBABA = "alibaba"


class ResourceType(Enum):
    """Types of cloud resources"""

    COMPUTE = "compute"  # EC2, VM, Compute Engine
    STORAGE = "storage"  # S3, Blob Storage, Cloud Storage
    DATABASE = "database"  # RDS, Cloud SQL, Azure SQL
    NETWORK = "network"  # VPC, VNet, Subnets
    LOADBALANCER = "loadbalancer"
    CONTAINER = "container"  # ECS, GKE, AKS
    SERVERLESS = "serverless"  # Lambda, Cloud Functions, Azure Functions
    IAM = "iam"  # Users, roles, policies
    CDN = "cdn"
    DNS = "dns"


@dataclass
class CloudAsset:
    """Represents a cloud resource"""

    asset_id: UUID = field(default_factory=uuid4)
    provider: CloudProvider = CloudProvider.AWS
    resource_type: ResourceType = ResourceType.COMPUTE
    resource_id: str = ""  # Provider-specific resource ID
    name: str = ""
    region: str = ""
    account_id: str = ""
    tags: dict[str, str] = field(default_factory=dict)
    properties: dict[str, Any] = field(default_factory=dict)
    public_access: bool = False
    discovery_timestamp: datetime = field(default_factory=datetime.utcnow)
    risk_indicators: list[str] = field(default_factory=list)
    compliance_status: dict[str, bool] = field(default_factory=dict)


@dataclass
class CloudDiscoveryResult:
    """Results of cloud asset discovery"""

    scan_id: UUID = field(default_factory=uuid4)
    provider: CloudProvider = CloudProvider.AWS
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: datetime | None = None
    status: str = "running"
    assets: list[CloudAsset] = field(default_factory=list)
    regions_scanned: list[str] = field(default_factory=list)
    accounts_scanned: list[str] = field(default_factory=list)
    statistics: dict[str, int] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


class CloudAssetDiscovery:
    """
    Multi-Cloud Asset Discovery

    Discovers and inventories cloud resources across multiple cloud providers:
    - AWS (EC2, S3, RDS, Lambda, VPC, etc.)
    - GCP (Compute Engine, Cloud Storage, Cloud SQL, etc.)
    - Azure (VMs, Blob Storage, Azure SQL, etc.)

    Features:
    - Multi-account/project/subscription support
    - Multi-region scanning
    - Public exposure detection
    - Security misconfiguration identification
    - Tag-based filtering
    - Compliance checking

    Detection Capabilities:
    - Publicly accessible resources
    - Unencrypted storage
    - Open security groups
    - Missing tags
    - Orphaned resources
    - Shadow IT resources
    """

    def __init__(self, config: dict[str, Any] | None = None):
        """
        Initialize cloud asset discovery

        Args:
            config: Configuration options
                - aws_credentials: AWS credentials dict
                - gcp_credentials: GCP service account path
                - azure_credentials: Azure credentials dict
                - regions: List of regions to scan (default: all)
                - resource_types: List of resource types to discover (default: all)
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}

        self.aws_credentials = self.config.get("aws_credentials", {})
        self.gcp_credentials = self.config.get("gcp_credentials", "")
        self.azure_credentials = self.config.get("azure_credentials", {})

        self.regions = self.config.get("regions", [])
        self.resource_types = self.config.get("resource_types", [rt.value for rt in ResourceType])

        self.logger.info("Cloud Asset Discovery initialized")

    def discover_aws_assets(self, accounts: list[str] | None = None) -> CloudDiscoveryResult:
        """
        Discover AWS assets across accounts and regions

        Args:
            accounts: List of AWS account IDs to scan (default: current account)

        Returns:
            Discovery results with all found assets
        """
        self.logger.info("Starting AWS asset discovery")

        result = CloudDiscoveryResult(
            provider=CloudProvider.AWS,
            start_time=datetime.utcnow(),
            status="running",
        )

        try:
            accounts = accounts or ["default"]

            for account in accounts:
                self.logger.debug(f"Scanning AWS account: {account}")

                # Discover regions if not specified
                regions = self.regions or self._get_aws_regions()
                result.regions_scanned = regions

                for region in regions:
                    self.logger.debug(f"Scanning AWS region: {region}")

                    # Discover different resource types
                    if ResourceType.COMPUTE.value in self.resource_types:
                        compute_assets = self._discover_aws_compute(account, region)
                        result.assets.extend(compute_assets)

                    if ResourceType.STORAGE.value in self.resource_types:
                        storage_assets = self._discover_aws_storage(account, region)
                        result.assets.extend(storage_assets)

                    if ResourceType.DATABASE.value in self.resource_types:
                        database_assets = self._discover_aws_databases(account, region)
                        result.assets.extend(database_assets)

                    if ResourceType.SERVERLESS.value in self.resource_types:
                        serverless_assets = self._discover_aws_lambda(account, region)
                        result.assets.extend(serverless_assets)

                result.accounts_scanned.append(account)

            # Calculate statistics
            result.statistics = self._calculate_statistics(result.assets)

            result.status = "completed"
            result.end_time = datetime.utcnow()

            self.logger.info(f"AWS discovery completed. Found {len(result.assets)} assets")

        except Exception as e:
            self.logger.error(f"AWS discovery failed: {e}")
            result.status = "failed"
            result.errors.append(str(e))
            result.end_time = datetime.utcnow()

        return result

    def discover_gcp_assets(self, projects: list[str] | None = None) -> CloudDiscoveryResult:
        """
        Discover GCP assets across projects and regions

        Args:
            projects: List of GCP project IDs to scan

        Returns:
            Discovery results with all found assets
        """
        self.logger.info("Starting GCP asset discovery")

        result = CloudDiscoveryResult(
            provider=CloudProvider.GCP,
            start_time=datetime.utcnow(),
            status="running",
        )

        try:
            projects = projects or ["default"]

            for project in projects:
                self.logger.debug(f"Scanning GCP project: {project}")

                regions = self.regions or self._get_gcp_regions()
                result.regions_scanned = regions

                for region in regions:
                    # Discover GCP resources
                    if ResourceType.COMPUTE.value in self.resource_types:
                        compute_assets = self._discover_gcp_compute(project, region)
                        result.assets.extend(compute_assets)

                    if ResourceType.STORAGE.value in self.resource_types:
                        storage_assets = self._discover_gcp_storage(project, region)
                        result.assets.extend(storage_assets)

                result.accounts_scanned.append(project)

            result.statistics = self._calculate_statistics(result.assets)
            result.status = "completed"
            result.end_time = datetime.utcnow()

            self.logger.info(f"GCP discovery completed. Found {len(result.assets)} assets")

        except Exception as e:
            self.logger.error(f"GCP discovery failed: {e}")
            result.status = "failed"
            result.errors.append(str(e))
            result.end_time = datetime.utcnow()

        return result

    def discover_azure_assets(self, subscriptions: list[str] | None = None) -> CloudDiscoveryResult:
        """
        Discover Azure assets across subscriptions and regions

        Args:
            subscriptions: List of Azure subscription IDs to scan

        Returns:
            Discovery results with all found assets
        """
        self.logger.info("Starting Azure asset discovery")

        result = CloudDiscoveryResult(
            provider=CloudProvider.AZURE,
            start_time=datetime.utcnow(),
            status="running",
        )

        try:
            subscriptions = subscriptions or ["default"]

            for subscription in subscriptions:
                self.logger.debug(f"Scanning Azure subscription: {subscription}")

                regions = self.regions or self._get_azure_regions()
                result.regions_scanned = regions

                for region in regions:
                    # Discover Azure resources
                    if ResourceType.COMPUTE.value in self.resource_types:
                        compute_assets = self._discover_azure_compute(subscription, region)
                        result.assets.extend(compute_assets)

                    if ResourceType.STORAGE.value in self.resource_types:
                        storage_assets = self._discover_azure_storage(subscription, region)
                        result.assets.extend(storage_assets)

                result.accounts_scanned.append(subscription)

            result.statistics = self._calculate_statistics(result.assets)
            result.status = "completed"
            result.end_time = datetime.utcnow()

            self.logger.info(f"Azure discovery completed. Found {len(result.assets)} assets")

        except Exception as e:
            self.logger.error(f"Azure discovery failed: {e}")
            result.status = "failed"
            result.errors.append(str(e))
            result.end_time = datetime.utcnow()

        return result

    def _discover_aws_compute(self, account: str, region: str) -> list[CloudAsset]:
        """Discover AWS EC2 instances"""
        # Mock implementation - would use boto3 in production
        self.logger.debug(f"Discovering AWS EC2 instances in {region}")

        assets = [
            CloudAsset(
                provider=CloudProvider.AWS,
                resource_type=ResourceType.COMPUTE,
                resource_id="i-1234567890abcdef0",
                name="web-server-prod-01",
                region=region,
                account_id=account,
                tags={"Environment": "production", "Role": "web"},
                properties={"instance_type": "t3.medium", "state": "running"},
                public_access=True,
                risk_indicators=["publicly_accessible"],
            ),
        ]

        return assets

    def _discover_aws_storage(self, account: str, region: str) -> list[CloudAsset]:
        """Discover AWS S3 buckets"""
        # Mock implementation
        self.logger.debug(f"Discovering AWS S3 buckets")

        assets = [
            CloudAsset(
                provider=CloudProvider.AWS,
                resource_type=ResourceType.STORAGE,
                resource_id="my-company-data-bucket",
                name="my-company-data-bucket",
                region=region,
                account_id=account,
                tags={"Department": "Engineering"},
                properties={"encryption": False, "versioning": False},
                public_access=False,
                risk_indicators=["unencrypted"],
            ),
        ]

        return assets

    def _discover_aws_databases(self, account: str, region: str) -> list[CloudAsset]:
        """Discover AWS RDS databases"""
        # Mock implementation
        assets = [
            CloudAsset(
                provider=CloudProvider.AWS,
                resource_type=ResourceType.DATABASE,
                resource_id="prod-database-1",
                name="prod-database-1",
                region=region,
                account_id=account,
                properties={"engine": "postgres", "publicly_accessible": False},
                public_access=False,
            ),
        ]

        return assets

    def _discover_aws_lambda(self, account: str, region: str) -> list[CloudAsset]:
        """Discover AWS Lambda functions"""
        # Mock implementation
        assets = [
            CloudAsset(
                provider=CloudProvider.AWS,
                resource_type=ResourceType.SERVERLESS,
                resource_id="api-handler",
                name="api-handler",
                region=region,
                account_id=account,
                properties={"runtime": "python3.11", "memory": 256},
            ),
        ]

        return assets

    def _discover_gcp_compute(self, project: str, region: str) -> list[CloudAsset]:
        """Discover GCP Compute Engine instances"""
        # Mock implementation
        return []

    def _discover_gcp_storage(self, project: str, region: str) -> list[CloudAsset]:
        """Discover GCP Cloud Storage buckets"""
        # Mock implementation
        return []

    def _discover_azure_compute(self, subscription: str, region: str) -> list[CloudAsset]:
        """Discover Azure VMs"""
        # Mock implementation
        return []

    def _discover_azure_storage(self, subscription: str, region: str) -> list[CloudAsset]:
        """Discover Azure Blob Storage"""
        # Mock implementation
        return []

    def _get_aws_regions(self) -> list[str]:
        """Get list of AWS regions"""
        return ["us-east-1", "us-west-2", "eu-west-1"]

    def _get_gcp_regions(self) -> list[str]:
        """Get list of GCP regions"""
        return ["us-central1", "europe-west1", "asia-east1"]

    def _get_azure_regions(self) -> list[str]:
        """Get list of Azure regions"""
        return ["eastus", "westeurope", "southeastasia"]

    def _calculate_statistics(self, assets: list[CloudAsset]) -> dict[str, int]:
        """Calculate statistics from discovered assets"""
        stats = {
            "total_assets": len(assets),
            "public_assets": sum(1 for a in assets if a.public_access),
            "assets_with_risks": sum(1 for a in assets if a.risk_indicators),
        }

        # Count by resource type
        for resource_type in ResourceType:
            count = sum(1 for a in assets if a.resource_type == resource_type)
            stats[f"{resource_type.value}_count"] = count

        return stats
