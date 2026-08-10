"""Core components of the Nethical safety governance system."""

# Phase 7 components
from .anomaly_detector import (
    AnomalyAlert,
    AnomalyDriftMonitor,
    AnomalyType,
    DistributionDriftDetector,
    DriftMetrics,
    DriftSeverity,
    SequenceAnomalyDetector,
)

# Phase 4 components
from .audit_merkle import AuditChunk, MerkleAnchor, MerkleNode
from .correlation_engine import CorrelationEngine, CorrelationMatch
from .embedding_config import (
    EmbeddingConfig,
    EmbeddingProviderType,
    EnsembleStrategy,
    ProviderConfig,
    load_embedding_config,
)

# Vector/Embedding support
from .embedding_engine import (
    EmbeddingEngine,
    EmbeddingProvider,
    EmbeddingResult,
    HuggingFaceEmbeddingProvider,
    OpenAIEmbeddingProvider,
    SimpleEmbeddingProvider,
    cosine_similarity,
)
from .ethical_drift_reporter import CohortProfile, EthicalDriftReport, EthicalDriftReporter
from .ethical_taxonomy import EthicalDimension, EthicalTag, EthicalTaxonomy, ViolationTagging
from .fairness_sampler import FairnessSampler, Sample, SamplingJob, SamplingStrategy
from .feedback_finetuning import (
    ActionLawPair,
    FeedbackEntry,
    FeedbackLogger,
    FeedbackSource,
    FeedbackType,
)

# Fundamental Laws - Ethical Backbone
from .fundamental_laws import (
    FUNDAMENTAL_LAWS,
    FundamentalLaw,
    FundamentalLawsRegistry,
    LawCategory,
    get_fundamental_laws,
)

# Phase 8 components
from .human_feedback import (
    EscalationCase,
    EscalationQueue,
    FeedbackTag,
    HumanFeedback,
    ReviewPriority,
    ReviewStatus,
    SLAMetrics,
)

# Unified Integration (All Phases)
from .integrated_governance import IntegratedGovernance

# Kill Switch Protocol - Emergency Override System
from .kill_switch import (
    ActuatorRecord,
    ActuatorSevering,
    ActuatorState,
    AgentRecord,
    AuditLogEntry,
    CommandType,
    ConnectionType,
    CryptoSignedCommands,
    GlobalKillSwitch,
    HardwareIsolation,
    IsolationLevel,
    KeyType,
    KillSwitchCallback,
    KillSwitchConfig,
    KillSwitchProtocol,
    KillSwitchResult,
    ShutdownMode,
    SignedCommand,
)

# Phase 6 components
from .ml_blended_risk import BlendedDecision, BlendingMetrics, MLBlendedRiskEngine, RiskZone

# Phase 5 components
from .ml_shadow import MLModelType, MLShadowClassifier, ShadowMetrics, ShadowPrediction
from .multimodal_embeddings import (
    Modality,
    ModalityDetector,
    MultiModalEmbeddingEngine,
    MultiModalEmbeddingResult,
    MultiModalInput,
)

# Phase 9 components
from .optimization import (
    ABTestingFramework,
    AdaptiveThresholdTuner,
    ConfigStatus,
    Configuration,
    MultiObjectiveOptimizer,
    OptimizationObjective,
    OptimizationTechnique,
    OutcomeRecord,
    PerformanceMetrics,
    PromotionGate,
)
from .performance_optimizer import DetectorMetrics, DetectorTier, PerformanceOptimizer
from .phase3_integration import Phase3IntegratedGovernance
from .phase4_integration import Phase4IntegratedGovernance

# Phase 8-9 Integration
from .phase89_integration import Phase89IntegratedGovernance

# Phase 5-7 Integration
from .phase567_integration import Phase567IntegratedGovernance

# F2: Detector & Policy Extensibility
from .plugin_interface import (
    DetectorPlugin,
    PluginManager,
    PluginMetadata,
    PluginStatus,
    get_plugin_manager,
)
from .policy_diff import ChangeType, PolicyChange, PolicyDiffAuditor, PolicyDiffResult, RiskLevel
from .policy_dsl import (
    Policy,
    PolicyAction,
    PolicyEngine,
    PolicyParser,
    PolicyRule,
    RuleEvaluator,
    RuleSeverity,
    get_policy_engine,
)
from .quarantine import HardwareIsolationLevel, QuarantineManager, QuarantinePolicy, QuarantineReason, QuarantineStatus

# Phase 1: Security & Governance
from .rbac import (
    AccessDeniedError,
    Permission,
    RBACManager,
    Role,
    get_rbac_manager,
    require_permission,
    require_role,
    set_rbac_manager,
)
from .risk_engine import RiskEngine, RiskProfile, RiskTier
from .semantic_benchmark import (
    BenchmarkResult,
    BenchmarkTestCase,
    SemanticAccuracyBenchmark,
)
from .semantic_mapper import (
    ActionEmbedding,
    PolicyVector,
    SemanticMapper,
    SemanticPrimitive,
)
from .semantic_primitives import (
    PRIMITIVE_KEYWORDS,
    EnhancedPrimitiveDetector,
)
from .sla_monitor import SLABreach, SLAMonitor, SLAStatus, SLATarget

__all__ = [
    # Fundamental Laws - Ethical Backbone
    "LawCategory",
    "FundamentalLaw",
    "FundamentalLawsRegistry",
    "FUNDAMENTAL_LAWS",
    "get_fundamental_laws",
    # Phase 3
    "RiskEngine",
    "RiskTier",
    "RiskProfile",
    "CorrelationEngine",
    "CorrelationMatch",
    "FairnessSampler",
    "Sample",
    "SamplingJob",
    "SamplingStrategy",
    "EthicalDriftReporter",
    "EthicalDriftReport",
    "CohortProfile",
    "PerformanceOptimizer",
    "DetectorTier",
    "DetectorMetrics",
    "Phase3IntegratedGovernance",
    # Phase 4
    "MerkleAnchor",
    "AuditChunk",
    "MerkleNode",
    "PolicyDiffAuditor",
    "PolicyDiffResult",
    "PolicyChange",
    "ChangeType",
    "RiskLevel",
    "QuarantineManager",
    "QuarantineReason",
    "QuarantineStatus",
    "QuarantinePolicy",
    "HardwareIsolationLevel",
    "EthicalTaxonomy",
    "EthicalTag",
    "ViolationTagging",
    "EthicalDimension",
    "SLAMonitor",
    "SLAStatus",
    "SLATarget",
    "SLABreach",
    "Phase4IntegratedGovernance",
    # Kill Switch Protocol
    "ShutdownMode",
    "CommandType",
    "KeyType",
    "ConnectionType",
    "IsolationLevel",
    "ActuatorState",
    "KillSwitchConfig",
    "AgentRecord",
    "ActuatorRecord",
    "SignedCommand",
    "AuditLogEntry",
    "KillSwitchResult",
    "KillSwitchCallback",
    "GlobalKillSwitch",
    "ActuatorSevering",
    "CryptoSignedCommands",
    "HardwareIsolation",
    "KillSwitchProtocol",
    # Phase 5
    "MLShadowClassifier",
    "ShadowPrediction",
    "ShadowMetrics",
    "MLModelType",
    # Phase 6
    "MLBlendedRiskEngine",
    "BlendedDecision",
    "BlendingMetrics",
    "RiskZone",
    # Phase 7
    "AnomalyDriftMonitor",
    "SequenceAnomalyDetector",
    "DistributionDriftDetector",
    "AnomalyAlert",
    "AnomalyType",
    "DriftSeverity",
    "DriftMetrics",
    # Phase 5-7 Integration
    "Phase567IntegratedGovernance",
    # Phase 8
    "EscalationQueue",
    "FeedbackTag",
    "ReviewStatus",
    "ReviewPriority",
    "HumanFeedback",
    "EscalationCase",
    "SLAMetrics",
    # Phase 9
    "MultiObjectiveOptimizer",
    "Configuration",
    "PerformanceMetrics",
    "OptimizationObjective",
    "OptimizationTechnique",
    "ConfigStatus",
    "PromotionGate",
    "AdaptiveThresholdTuner",
    "ABTestingFramework",
    "OutcomeRecord",
    # Phase 8-9 Integration
    "Phase89IntegratedGovernance",
    # Unified Integration (All Phases)
    "IntegratedGovernance",
    # Vector/Embedding support
    "EmbeddingEngine",
    "EmbeddingProvider",
    "EmbeddingResult",
    "SimpleEmbeddingProvider",
    "OpenAIEmbeddingProvider",
    "HuggingFaceEmbeddingProvider",
    "cosine_similarity",
    "EmbeddingConfig",
    "ProviderConfig",
    "EmbeddingProviderType",
    "EnsembleStrategy",
    "load_embedding_config",
    "SemanticMapper",
    "SemanticPrimitive",
    "PolicyVector",
    "ActionEmbedding",
    "EnhancedPrimitiveDetector",
    "PRIMITIVE_KEYWORDS",
    "MultiModalEmbeddingEngine",
    "MultiModalInput",
    "MultiModalEmbeddingResult",
    "Modality",
    "ModalityDetector",
    "FeedbackLogger",
    "FeedbackEntry",
    "ActionLawPair",
    "FeedbackType",
    "FeedbackSource",
    "SemanticAccuracyBenchmark",
    "BenchmarkTestCase",
    "BenchmarkResult",
    # F2: Detector & Policy Extensibility
    "DetectorPlugin",
    "PluginManager",
    "PluginMetadata",
    "PluginStatus",
    "get_plugin_manager",
    "Policy",
    "PolicyAction",
    "PolicyEngine",
    "PolicyParser",
    "PolicyRule",
    "RuleEvaluator",
    "RuleSeverity",
    "get_policy_engine",
    # Phase 1: Security & Governance
    "Role",
    "Permission",
    "RBACManager",
    "AccessDeniedError",
    "require_role",
    "require_permission",
    "get_rbac_manager",
    "set_rbac_manager",
]
