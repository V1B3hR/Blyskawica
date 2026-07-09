"""
types.py - Common Type Definitions for GCS System

Centralized type definitions used across multiple GCS modules:
- Safety and action type enumerations
- Collaboration context and mode definitions
- Confirmation level enumerations
- Core action and intent data structures
- Anomaly type definitions
"""

import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class SafetyLevel(Enum):
    """Safety alert levels"""
    SAFE = "safe"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class ActionType(Enum):
    """Types of actions that can be monitored"""
    COMPUTATION = "computation"
    COMMUNICATION = "communication"
    SYSTEM_MODIFICATION = "system_modification"
    DATA_ACCESS = "data_access"
    EXTERNAL_INTERACTION = "external_interaction"


class CollaborationMode(Enum):
    """Modes of human-AI collaboration"""
    HUMAN_AUTONOMOUS = "human_autonomous"       # Human makes decisions independently
    AI_ASSISTED = "ai_assisted"                 # AI provides assistance to human decisions
    COLLABORATIVE = "collaborative"             # Joint human-AI decision making
    AI_AUTONOMOUS = "ai_autonomous"             # AI operates autonomously with human oversight
    EMERGENCY_OVERRIDE = "emergency_override"   # Emergency human override of AI actions


class ConfirmationLevel(Enum):
    """Levels of confirmation required for actions"""
    NONE = 0           # No confirmation required
    IMPLICIT = 1       # Brief display with timeout for objection
    EXPLICIT = 2       # Clear yes/no confirmation required
    ENHANCED = 3       # Detailed confirmation with alternatives
    CRITICAL = 4       # Multi-step confirmation with cooling-off period


class AnomalyType(Enum):
    """Types of collaborative anomalies"""
    PERFORMANCE_DEGRADATION = "performance_degradation"
    COMMUNICATION_BREAKDOWN = "communication_breakdown"
    DECISION_INCONSISTENCY = "decision_inconsistency"
    ETHICAL_ANOMALY = "ethical_anomaly"
    SAFETY_ANOMALY = "safety_anomaly"
    TRUST_EROSION = "trust_erosion"
    BEHAVIORAL_ANOMALY = "behavioral_anomaly"


@dataclass
class Intent:
    """Represents an agent's stated intent"""
    description: str
    action_type: ActionType
    expected_outcome: str
    safety_constraints: List[str]
    confidence: float = 1.0
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


@dataclass
class Action:
    """Represents an actual action being performed"""
    description: str
    action_type: ActionType
    actual_parameters: Dict[str, Any]
    observed_effects: List[str]
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


@dataclass
class CollaborationContext:
    """Context information for collaborative interactions"""
    user_id: str
    session_id: str
    collaboration_mode: CollaborationMode
    trust_level: float  # 0.0 to 1.0
    urgency_level: int  # 1-5, 5 being most urgent
    domain: str
    stakeholders: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
