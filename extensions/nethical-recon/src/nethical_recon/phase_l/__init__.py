"""
Phase L: Advanced Features for Nethical Recon
Implements AI-Enhanced Threat Correlation, Collaborative Features,
Cloud-Native Deployment, Compliance & Reporting, and Plugin Marketplace
"""

__version__ = "1.0.0"

from .threat_correlation import AttackChainDetector, MitreAttackMapper, ThreatActorAttributor
from .collaboration import WorkspaceManager, RBACManager, AnnotationManager, IssueExporter
from .cloud_native import KubernetesEnhancer, TerraformGenerator, CloudStorageManager
from .compliance import ExecutiveReportGenerator, ComplianceMapper, TrendAnalyzer
from .marketplace import PluginMarketplace, PluginDevelopmentKit, PluginVerifier

__all__ = [
    # Threat Correlation (L.1)
    "AttackChainDetector",
    "MitreAttackMapper",
    "ThreatActorAttributor",
    # Collaboration (L.2)
    "WorkspaceManager",
    "RBACManager",
    "AnnotationManager",
    "IssueExporter",
    # Cloud Native (L.3)
    "KubernetesEnhancer",
    "TerraformGenerator",
    "CloudStorageManager",
    # Compliance (L.4)
    "ExecutiveReportGenerator",
    "ComplianceMapper",
    "TrendAnalyzer",
    # Marketplace (L.5)
    "PluginMarketplace",
    "PluginDevelopmentKit",
    "PluginVerifier",
]
