"""
Global Attack Surface Intelligence Module

Organization-wide reconnaissance and multi-cloud asset discovery capabilities.
Implements ROADMAP 5.0 Section V.15: Global Attack Surface Intelligence.
"""

from .organization_scanner import OrganizationScanner, OrganizationScope
from .cloud_discovery import CloudAssetDiscovery, CloudProvider, CloudAsset
from .shadow_it_detector import ShadowITDetector, ShadowITFinding
from .risk_mapping import OrganizationRiskMapper, RiskMap
from .digital_twin import DigitalTwin, TwinAsset

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
