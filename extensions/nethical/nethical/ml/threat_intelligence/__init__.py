"""
Threat Intelligence and Predictive Detection Module.

This module implements Phase 5: Detection Omniscience capabilities including:
- Threat intelligence integration from multiple sources
- Predictive modeling for attack anticipation
- Proactive hardening based on threat predictions

Phase: 5 - Detection Omniscience
Status: Active
"""

from .predictive_modeling import (
    AttackPrediction,
    PredictiveModeler,
    ThreatEvolutionModel,
)
from .proactive_hardening import (
    HardeningAction,
    HardeningPriority,
    ProactiveHardener,
)
from .threat_feed_integration import (
    ThreatFeedIntegrator,
    ThreatIntelligence,
    ThreatSeverity,
    ThreatSource,
)

__all__ = [
    "ThreatFeedIntegrator",
    "ThreatSource",
    "ThreatIntelligence",
    "ThreatSeverity",
    "PredictiveModeler",
    "AttackPrediction",
    "ThreatEvolutionModel",
    "ProactiveHardener",
    "HardeningAction",
    "HardeningPriority",
]
