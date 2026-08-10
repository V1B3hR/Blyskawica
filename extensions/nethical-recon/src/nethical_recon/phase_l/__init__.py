"""
Phase L: Advanced Features for Nethical Recon
Implements AI-Enhanced Threat Correlation, Collaborative Features,
Cloud-Native Deployment, Compliance & Reporting, and Plugin Marketplace
"""

__version__ = "1.0.0"

from .cloud_native import CloudStorageManager, KubernetesEnhancer, TerraformGenerator
from .collaboration import AnnotationManager, IssueExporter, RBACManager, WorkspaceManager
from .compliance import ComplianceMapper, ExecutiveReportGenerator, TrendAnalyzer
from .marketplace import PluginDevelopmentKit, PluginMarketplace, PluginVerifier
from .threat_correlation import AttackChainDetector, MitreAttackMapper, ThreatActorAttributor

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
