"""
Nanobots - Automated Response System

🤖 NANOBOTY - SYSTEM AUTOMATYCZNEJ ODPOWIEDZI
The immune system of Nethical Recon - autonomous agents that respond to threats.

Modules:
- base: Base nanobot classes and enums
- swarm: Nanobot swarm manager
- actions: Nanobot action implementations
- rules: Rules engine and hybrid decision logic
- learning: Adaptive learning components
"""

from .actions.alert import AlertLevel, AlertNanobot

# Actions
from .actions.block_ip import IPBlockerNanobot
from .actions.enumerate import EnumeratorNanobot
from .actions.forest_patrol import ForestPatrolNanobot
from .actions.honeypot import HoneypotNanobot
from .actions.rate_limit import RateLimiterNanobot
from .actions.threat_hunt import ThreatHunterNanobot
from .base import ActionResult, ActionStatus, ActionType, BaseNanobot, NanobotMode
from .learning.anomaly_ml import SimpleMLAnomalyDetector

# Learning
from .learning.baseline import BaselineLearner

# Rules
from .rules.engine import Rule, RuleCondition, RuleOperator, RulesEngine
from .rules.hybrid_mode import DecisionMode, HybridDecisionMaker
from .swarm import NanobotSwarm

# New features
from .ml_prediction import MLThreatPredictor, ThreatPredictionModel, ThreatFeatures
from .adaptive_behavior import AdaptiveBehavior, BehaviorProfile
from .swarm_coordination import SwarmCoordinator, SwarmRole

__all__ = [
    # Base
    "BaseNanobot",
    "NanobotMode",
    "ActionType",
    "ActionStatus",
    "ActionResult",
    # Swarm
    "NanobotSwarm",
    # Actions - Defensive
    "IPBlockerNanobot",
    "RateLimiterNanobot",
    "HoneypotNanobot",
    "AlertNanobot",
    "AlertLevel",
    # Actions - Scout
    "EnumeratorNanobot",
    "ForestPatrolNanobot",
    "ThreatHunterNanobot",
    # Rules
    "RulesEngine",
    "Rule",
    "RuleCondition",
    "RuleOperator",
    "HybridDecisionMaker",
    "DecisionMode",
    # Learning
    "BaselineLearner",
    "SimpleMLAnomalyDetector",
    # New features
    "MLThreatPredictor",
    "ThreatPredictionModel",
    "ThreatFeatures",
    "AdaptiveBehavior",
    "BehaviorProfile",
    "SwarmCoordinator",
    "SwarmRole",
]


# Version
__version__ = "1.0.0"
