"""
Global Attack Surface Intelligence Module

Organization-wide reconnaissance and multi-cloud asset discovery capabilities.
Implements ROADMAP 5.0 Section V.15: Global Attack Surface Intelligence.
"""

from .cloud_discovery import CloudAsset, CloudAssetDiscovery, CloudProvider
from .digital_twin import DigitalTwin, TwinAsset
from .organization_scanner import OrganizationScanner, OrganizationScope
from .risk_mapping import OrganizationRiskMapper, RiskMap
from .shadow_it_detector import ShadowITDetector, ShadowITFinding

__all__ = [
    "OrganizationScanner",
    "OrganizationScope",
    "CloudAssetDiscovery",
    "CloudProvider",
    "CloudAsset",
    "ShadowITDetector",
    "ShadowITFinding",
    "OrganizationRiskMapper",
    "RiskMap",
    "DigitalTwin",
    "TwinAsset",
]
