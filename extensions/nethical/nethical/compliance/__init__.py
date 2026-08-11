"""Nethical Compliance Module for Global Compliance Operations.

This module provides comprehensive compliance capabilities for Phase 3:
- Automated Compliance Enforcement (GDPR, EU AI Act, CCPA, ISO 27001, NIST AI RMF)
- Data Residency Management
- Right to Explanation (GDPR Article 22)

Adheres to:
- Law 15: Audit Compliance - Cooperation with auditing
- Law 10: Reasoning Transparency - Explainable decision-making
- Law 12: Limitation Disclosure - Disclosure of known limitations
- Law 22: Digital Security - Protection of digital assets and privacy

Author: Nethical Core Team
Version: 1.0.0
"""

from .data_residency import (
    DataClassification,
    DataRegion,
    DataResidencyManager,
    DataType,
    ResidencyPolicy,
    ResidencyViolation,
)
from .eu_ai_act import (
    AIRiskLevel,
    ConformityAssessmentResult,
    EUAIActArticle,
    EUAIActValidator,
)
from .gdpr import (
    DataSubjectRight,
    GDPRArticle,
    GDPRComplianceValidator,
    GDPRValidationResult,
    LawfulBasis,
)
from .validator import (
    ComplianceFramework,
    ComplianceReport,
    ComplianceValidator,
    ValidationResult,
)

__all__ = [
    # GDPR
    "GDPRComplianceValidator",
    "GDPRArticle",
    "DataSubjectRight",
    "LawfulBasis",
    "GDPRValidationResult",
    # EU AI Act
    "EUAIActValidator",
    "AIRiskLevel",
    "EUAIActArticle",
    "ConformityAssessmentResult",
    # Data Residency
    "DataResidencyManager",
    "DataRegion",
    "DataClassification",
    "DataType",
    "ResidencyPolicy",
    "ResidencyViolation",
    # Validator
    "ComplianceValidator",
    "ComplianceFramework",
    "ComplianceReport",
    "ValidationResult",
]
