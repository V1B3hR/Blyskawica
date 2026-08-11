# Package init for security

from .attestation import (
    AttestationErrorCodes,
    NoopAttestation,
    TrustedAttestation,
    compute_measurements_digest,
    normalize_attestation_result,
    register_attestation_provider,
    select_attestation_provider,
)

try:
    from .auth import (
        APIKey,
        AuthManager,
        InvalidTokenError,
        TokenExpiredError,
        TokenPayload,
        TokenType,
    )
except ModuleNotFoundError as e:
    # Defensive: PyJWT dependency missing error explanation
    if e.name == "jwt":
        raise ImportError(
            "PyJWT library required for authentication. "
            "Please install by running: pip install PyJWT"
        ) from e
    raise

# Adaptive Guardian - Intelligent Throttling Security System
from .adaptive_guardian import (
    AdaptiveGuardian,
    MetricRecord,
    clear_lockdown,
    get_guardian,
    get_mode,
    get_status,
    monitored,
    record_metric,
    trigger_lockdown,
)

# Phase 2: Advanced Anomaly Detection
from .anomaly_detection import (
    AdvancedAnomalyDetectionEngine,
    AnomalyDetectionResult,
    AnomalyType,
    APTBehavioralDetector,
    GraphRelationshipAnalyzer,
    InsiderThreatDetector,
    LSTMSequenceDetector,
    TransformerContextAnalyzer,
)

# Phase 3: Enhanced Audit Logging
from .audit_logging import (
    AuditBlockchain,
    AuditEvent,
    AuditEventType,
    AuditSeverity,
    BlockchainBlock,
    ChainOfCustodyManager,
    DigitalSignature,
    EnhancedAuditLogger,
    ForensicAnalyzer,
    TimestampAuthority,
)

# Phase 1: Military-Grade Security Enhancements
from .authentication import (
    AuthCredentials,
    AuthResult,
    ClearanceLevel,
    LDAPConnector,
    MilitaryGradeAuthProvider,
    MultiFactorAuthEngine,
    PKICertificateValidator,
    SecureSessionManager,
)

# Phase 3: Compliance & Audit Framework
from .compliance import (
    ComplianceControl,
    ComplianceEvidence,
    ComplianceFramework,
    ComplianceReport,
    ComplianceReportGenerator,
    ComplianceStatus,
    ControlSeverity,
    EvidenceCollector,
    FedRAMPMonitor,
    HIPAAComplianceValidator,
    NIST80053ControlMapper,
)
from .encryption import (
    EncryptedData,
    EncryptionAlgorithm,
    HSMConfig,
    KeyManagementService,
    KeyRotationPolicy,
    MilitaryGradeEncryption,
)
from .guardian_modes import GuardianMode, ModeConfig, TripwireSensitivity

# Phase 5: Hardware Security Module (HSM) Integration
from .hsm import (
    AWSCloudHSMProvider,
    AzureDedicatedHSMProvider,
    BaseHSMProvider,
    GoogleCloudHSMProvider,
    HSMAbstractionLayer,
    HSMKeyInfo,
    HSMOperationResult,
    HSMOperationStatus,
    HSMProvider,
    KeyAlgorithm,
    KeyCeremonyConfig,
    KeyCeremonyManager,
    KeyCeremonyRecord,
    KeyUsage,
    SoftwareHSMProvider,
    ThalesLunaProvider,
    YubiHSMProvider,
    create_hsm_provider,
)
from .hsm import (
    HSMConfig as HSMAbstractionConfig,
)
from .input_validation import (
    AdversarialInputDefense,
    BehavioralAnalyzer,
    SemanticAnomalyDetector,
    ThreatIntelligenceDB,
    ThreatLevel,
    ValidationResult,
)
from .mfa import (
    InvalidMFACodeError,
    MFAManager,
    MFAMethod,
    MFARequiredError,
    MFASetup,
    get_mfa_manager,
    set_mfa_manager,
)

# Regulatory Compliance Framework (EU AI Act, UK Law, US Standards)
from .regulatory_compliance import (
    AIRiskLevel,
    ControlCategory,
    EUAIActCompliance,
    RegulatoryFramework,
    RegulatoryMapping,
    RegulatoryMappingGenerator,
    RegulatoryRequirement,
    UKLawCompliance,
    USStandardsCompliance,
    generate_regulatory_mapping_table,
)
from .regulatory_compliance import (
    ComplianceStatus as RegulatoryComplianceStatus,
)

# Phase 4: Secret Management
from .secret_management import (
    DynamicSecretGenerator,
    Secret,
    SecretManagementSystem,
    SecretRotationManager,
    SecretRotationPolicy,
    SecretScanner,
    SecretType,
    VaultConfig,
    VaultIntegration,
)

# Phase 2: SOC Integration
from .soc_integration import (
    AlertingEngine,
    AlertSeverity,
    ForensicCollector,
    Incident,
    IncidentManager,
    IncidentStatus,
    SIEMConnector,
    SIEMEvent,
    SIEMFormat,
    SOCIntegrationHub,
    ThreatHuntingEngine,
)
from .sso import (
    SAMLConfig,
    SSOConfig,
    SSOError,
    SSOManager,
    SSOProvider,
    get_sso_manager,
    set_sso_manager,
)
from .track_analyzer import ThreatAnalysis, TrackAnalyzer
from .tripwires import TripwireAlert, Tripwires
from .watchdog import Watchdog, WatchdogAlert

# Phase 4: Zero Trust Architecture
from .zero_trust import (
    ContinuousAuthEngine,
    DeviceHealthCheck,
    DeviceHealthStatus,
    NetworkSegment,
    PolicyEnforcer,
    ServiceMeshConfig,
    TrustLevel,
    ZeroTrustController,
)

__all__ = [
    # Attestation
    "NoopAttestation",
    "TrustedAttestation",
    "select_attestation_provider",
    "normalize_attestation_result",
    "AttestationErrorCodes",
    "register_attestation_provider",
    "compute_measurements_digest",
    # Authentication
    "AuthManager",
    "TokenPayload",
    "TokenType",
    "APIKey",
    "TokenExpiredError",
    "InvalidTokenError",
    # Multi-Factor Authentication
    "MFAMethod",
    "MFASetup",
    "MFAManager",
    "MFARequiredError",
    "InvalidMFACodeError",
    "get_mfa_manager",
    "set_mfa_manager",
    # Single Sign-On
    "SSOProvider",
    "SSOConfig",
    "SAMLConfig",
    "SSOManager",
    "SSOError",
    "get_sso_manager",
    "set_sso_manager",
    # Phase 1: Military-Grade Authentication
    "AuthCredentials",
    "AuthResult",
    "ClearanceLevel",
    "PKICertificateValidator",
    "MultiFactorAuthEngine",
    "SecureSessionManager",
    "LDAPConnector",
    "MilitaryGradeAuthProvider",
    # Phase 1: Encryption
    "EncryptionAlgorithm",
    "KeyRotationPolicy",
    "HSMConfig",
    "EncryptedData",
    "MilitaryGradeEncryption",
    "KeyManagementService",
    # Phase 1: Input Validation
    "ValidationResult",
    "ThreatLevel",
    "SemanticAnomalyDetector",
    "ThreatIntelligenceDB",
    "BehavioralAnalyzer",
    "AdversarialInputDefense",
    # Phase 2: Advanced Anomaly Detection
    "AnomalyType",
    "AnomalyDetectionResult",
    "LSTMSequenceDetector",
    "TransformerContextAnalyzer",
    "GraphRelationshipAnalyzer",
    "InsiderThreatDetector",
    "APTBehavioralDetector",
    "AdvancedAnomalyDetectionEngine",
    # Phase 2: SOC Integration
    "SIEMFormat",
    "AlertSeverity",
    "IncidentStatus",
    "SIEMEvent",
    "Incident",
    "SIEMConnector",
    "IncidentManager",
    "ThreatHuntingEngine",
    "AlertingEngine",
    "ForensicCollector",
    "SOCIntegrationHub",
    # Phase 3: Compliance Framework
    "ComplianceFramework",
    "ComplianceStatus",
    "ControlSeverity",
    "ComplianceControl",
    "ComplianceEvidence",
    "ComplianceReport",
    "NIST80053ControlMapper",
    "HIPAAComplianceValidator",
    "FedRAMPMonitor",
    "ComplianceReportGenerator",
    "EvidenceCollector",
    # Phase 3: Audit Logging
    "AuditEvent",
    "AuditEventType",
    "AuditSeverity",
    "BlockchainBlock",
    "TimestampAuthority",
    "DigitalSignature",
    "AuditBlockchain",
    "ForensicAnalyzer",
    "ChainOfCustodyManager",
    "EnhancedAuditLogger",
    # Phase 4: Zero Trust Architecture
    "TrustLevel",
    "DeviceHealthStatus",
    "NetworkSegment",
    "ServiceMeshConfig",
    "DeviceHealthCheck",
    "PolicyEnforcer",
    "ContinuousAuthEngine",
    "ZeroTrustController",
    # Phase 4: Secret Management
    "SecretType",
    "SecretRotationPolicy",
    "VaultConfig",
    "Secret",
    "SecretScanner",
    "DynamicSecretGenerator",
    "SecretRotationManager",
    "VaultIntegration",
    "SecretManagementSystem",
    # Regulatory Compliance Framework
    "AIRiskLevel",
    "RegulatoryFramework",
    "RegulatoryComplianceStatus",
    "ControlCategory",
    "RegulatoryRequirement",
    "RegulatoryMapping",
    "EUAIActCompliance",
    "UKLawCompliance",
    "USStandardsCompliance",
    "RegulatoryMappingGenerator",
    "generate_regulatory_mapping_table",
    # Phase 5: HSM Integration
    "HSMProvider",
    "KeyAlgorithm",
    "KeyUsage",
    "HSMOperationStatus",
    "HSMKeyInfo",
    "HSMAbstractionConfig",
    "HSMOperationResult",
    "KeyCeremonyConfig",
    "KeyCeremonyRecord",
    "BaseHSMProvider",
    "AWSCloudHSMProvider",
    "AzureDedicatedHSMProvider",
    "GoogleCloudHSMProvider",
    "YubiHSMProvider",
    "ThalesLunaProvider",
    "SoftwareHSMProvider",
    "HSMAbstractionLayer",
    "KeyCeremonyManager",
    "create_hsm_provider",
    # Adaptive Guardian - Intelligent Throttling Security System
    "AdaptiveGuardian",
    "GuardianMode",
    "get_guardian",
    "record_metric",
    "trigger_lockdown",
    "clear_lockdown",
    "get_mode",
    "get_status",
    "monitored",
    "TripwireAlert",
    "ThreatAnalysis",
    "WatchdogAlert",
]
