"""
Nethical Recon - AI Module (Artificial Intelligence)

The AI module provides intelligent analysis, predictions, and strategy
recommendations for the Nethical Hunter system:

📊 ANALYZER - Threat scoring and pattern matching
📝 REPORTER - Report generation and executive summaries
🔮 PREDICTOR - Next attack prediction and risk forecasting
🎯 ADVISOR - Hunt strategy and action recommendations
🔗 CORRELATOR - Stain linking and attack chain analysis
📚 LEARNER - Pattern learning and baseline adjustment
🌳 FOREST AI - Forest-specific threat intelligence
🦅 BIRD COORDINATOR - AI-powered bird deployment
🎭 THREAT CLASSIFIER - Crow/Magpie/Squirrel classification
🤖 LLM CLIENT - Evidence-based LLM integration (PHASE H)
🔍 DEDUPLICATION - Finding deduplication engine (PHASE H)
🛡️ THREAT INTELLIGENCE - Threat feed management and STIX export (PHASE H)
"""

from .advisor import HuntAdvisor
from .analyzer import ThreatAnalyzer
from .bird_coordinator import BirdCoordinator
from .correlator import StainCorrelator
from .deduplication import DeduplicationEngine, DuplicateGroup, FindingMerger
from .forest_ai import ForestAI
from .learner import PatternLearner
from .llm_client import EvidenceReference, LLMClient, LLMReport
from .predictor import ThreatPredictor
from .reporter import AIReporter
from .threat_classifier import ThreatClassifier
from .threat_intelligence import STIXIndicator, ThreatFeed, ThreatIntelligenceManager

__all__ = [
    "ThreatAnalyzer",
    "AIReporter",
    "ThreatPredictor",
    "HuntAdvisor",
    "StainCorrelator",
    "PatternLearner",
    "ForestAI",
    "BirdCoordinator",
    "ThreatClassifier",
    # Phase H additions
    "LLMClient",
    "LLMReport",
    "EvidenceReference",
    "DeduplicationEngine",
    "DuplicateGroup",
    "FindingMerger",
    "ThreatIntelligenceManager",
    "ThreatFeed",
    "STIXIndicator",
]
