"""
Dynamic Attack Registry for Nethical

This module implements Phase 4 Dynamic Attack Registry capability
for automatic registration and deprecation of attack vectors.

Components:
- AutoRegistration: Automatically register new attack patterns
- AutoDeprecation: Automatically deprecate unused attack vectors
- RegistryManager: Manages the dynamic attack registry lifecycle

Phase 4 Objective: Self-updating detection with minimal human intervention

Author: Nethical Core Team
Version: 1.0.0
"""

from .auto_deprecation import (
    ArchiveStatus,
    AutoDeprecation,
    DeprecationCandidate,
    DeprecationReason,
)
from .auto_registration import (
    AttackPattern,
    AutoRegistration,
    RegistrationStage,
    ValidationResult,
)
from .registry_manager import (
    RegistryHealth,
    RegistryManager,
)

__all__ = [
    "AutoRegistration",
    "RegistrationStage",
    "ValidationResult",
    "AttackPattern",
    "AutoDeprecation",
    "DeprecationReason",
    "ArchiveStatus",
    "DeprecationCandidate",
    "RegistryManager",
    "RegistryHealth",
]
