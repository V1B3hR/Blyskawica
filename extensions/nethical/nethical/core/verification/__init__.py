"""
Verification Module.

Provides formal verification and runtime monitoring capabilities
for Nethical's governance and detection systems.
"""

from .detector_verifier import (
    DetectorProperty,
    DetectorVerifier,
    VerificationResult,
    VerificationStatus,
)
from .runtime_monitor import (
    ContractAssertion,
    InvariantType,
    InvariantViolation,
    RuntimeInvariant,
    RuntimeMonitor,
    TemporalProperty,
    ViolationSeverity,
    ensures,
    invariant_check,
    requires,
)

__all__ = [
    # Runtime Monitor
    "InvariantType",
    "ViolationSeverity",
    "InvariantViolation",
    "RuntimeInvariant",
    "TemporalProperty",
    "ContractAssertion",
    "RuntimeMonitor",
    "invariant_check",
    "requires",
    "ensures",
    # Detector Verifier
    "DetectorProperty",
    "VerificationStatus",
    "VerificationResult",
    "DetectorVerifier",
]

