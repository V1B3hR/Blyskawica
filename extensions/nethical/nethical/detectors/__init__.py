"""Detection components for various safety and ethical violations."""

# from .dark_pattern_detector import EnhancedDarkPatternDetector
# from .cognitive_warfare_detector import CognitiveWarfareDetector
# from .system_limits_detector import SystemLimitsDetector
from .base_detector import BaseDetector
from .corruption import CorruptionDetector
from .ethical_detector import EthicalViolationDetector
from .law_violation_detector import LawViolationDetector
from .manipulation_detector import ManipulationDetector
from .safety_detector import SafetyViolationDetector

__all__ = [
    "EthicalViolationDetector",
    "SafetyViolationDetector",
    "ManipulationDetector",
    "LawViolationDetector",
    # "EnhancedDarkPatternDetector",
    # "CognitiveWarfareDetector",
    # "SystemLimitsDetector",
    "BaseDetector",
    "CorruptionDetector",
]
