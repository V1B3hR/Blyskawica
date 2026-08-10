"""
Edge Decision Engine Module

Ultra-low latency governance for edge deployment.
Designed for autonomous vehicles, robots, and real-time systems.

Target: <10ms p99 latency
Mode: Offline-first with sync

Components:
- EdgeGovernor: Core edge governance engine
- PolicyCache: In-memory policy cache with LRU eviction
- FastDetector: Lightweight detectors for edge deployment
- SafeDefaults: Fail-safe default decisions
- PredictiveEngine: Pre-computation for predicted actions
- OfflineFallback: Graceful degradation when disconnected
- TPM: Trusted Platform Module integration for edge security
"""

from .circuit_breaker import CircuitBreaker, CircuitState
from .context_fingerprint import ContextFingerprint, compute_fingerprint
from .decision_queue import DecisionQueue, QueuedDecision
from .fast_detector import DetectionResult, FastDetector
from .local_governor import DecisionType, EdgeDecision, EdgeGovernor
from .network_monitor import ConnectionStatus, NetworkMonitor
from .offline_fallback import OfflineFallback, OfflineMode
from .pattern_profiler import ActionPattern, PatternProfiler
from .policy_cache import CachedPolicy, PolicyCache
from .predictive_engine import PredictionProfile, PredictiveEngine
from .safe_defaults import DefaultDecision, SafeDefaults
from .sync_manager import SyncManager, SyncStatus

# Phase 5: TPM Integration for Edge Security
from .tpm import (
    AttestationQuote,
    AttestationResult,
    AttestationStatus,
    BootState,
    EdgeSecurityManager,
    HardwareTPM,
    PCRBank,
    PCRValue,
    PlatformMeasurement,
    RemoteAttestation,
    SecureBootConfig,
    SecureBootVerifier,
    SoftwareTPM,
    TPMConfig,
    TPMInterface,
    TPMStatus,
    TPMVersion,
    create_tpm_interface,
)

__all__ = [
    # Core
    "EdgeGovernor",
    "EdgeDecision",
    "DecisionType",
    # Policy
    "PolicyCache",
    "CachedPolicy",
    # Detection
    "FastDetector",
    "DetectionResult",
    # Defaults
    "SafeDefaults",
    "DefaultDecision",
    # Prediction
    "PredictiveEngine",
    "PredictionProfile",
    "ContextFingerprint",
    "compute_fingerprint",
    "PatternProfiler",
    "ActionPattern",
    # Offline
    "OfflineFallback",
    "OfflineMode",
    "NetworkMonitor",
    "ConnectionStatus",
    "DecisionQueue",
    "QueuedDecision",
    "SyncManager",
    "SyncStatus",
    # Circuit Breaker
    "CircuitBreaker",
    "CircuitState",
    # Phase 5: TPM Integration
    "TPMVersion",
    "TPMStatus",
    "AttestationStatus",
    "BootState",
    "PCRBank",
    "PCRValue",
    "PlatformMeasurement",
    "AttestationQuote",
    "AttestationResult",
    "TPMConfig",
    "SecureBootConfig",
    "TPMInterface",
    "SoftwareTPM",
    "HardwareTPM",
    "RemoteAttestation",
    "SecureBootVerifier",
    "EdgeSecurityManager",
    "create_tpm_interface",
]
