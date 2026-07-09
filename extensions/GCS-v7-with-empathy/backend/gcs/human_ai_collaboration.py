"""
human_ai_collaboration.py - Human-AI Collaboration Framework Implementation

Implements Phase 9 technical and ethical objectives:
- Collaborative decision-making systems
- Anomaly detection and response protocols  
- Confirmation procedure automation
- Performance monitoring dashboards
- Collaborative ethics enforcement mechanisms
- Human override and appeal systems
- Ethical anomaly detection protocols
- Transparency in collaborative decisions
"""

import logging
import time
import threading
from typing import Dict, List, Tuple, Any, Optional, Callable, Set
from dataclasses import dataclass, field
from .types import (
    Intent, Action, ActionType, SafetyLevel, 
    CollaborationMode, ConfirmationLevel, AnomalyType, CollaborationContext
)
from .ethical_constraint_engine import EthicalConstraintEngine, EthicalAssessment
from .ethical_decision_api import EthicalDecisionAPI, DecisionComplexity, StakeholderType


@dataclass 
class CollaborativeDecision:
    """Represents a collaborative decision"""
    decision_id: str
    context: CollaborationContext
    problem_description: str
    proposed_action: Action
    human_input: Optional[str] = None
    ai_recommendation: Optional[str] = None
    final_decision: Optional[str] = None
    rationale: Optional[str] = None
    confirmation_level: ConfirmationLevel = ConfirmationLevel.EXPLICIT
    stakeholder_approval: Dict[str, bool] = field(default_factory=dict)
    ethical_assessment: Optional[EthicalAssessment] = None
    timestamp: float = field(default_factory=time.time)
    execution_status: str = "pending"


@dataclass
class CollaborationAnomaly:
    """Represents an anomaly in human-AI collaboration"""
    anomaly_id: str
    anomaly_type: AnomalyType
    severity: SafetyLevel
    description: str
    detected_at: float
    context: CollaborationContext
    detection_confidence: float
    recommended_actions: List[str] = field(default_factory=list)
    human_notified: bool = False
    resolved: bool = False
    resolution_actions: List[str] = field(default_factory=list)


class HumanAICollaborationFramework:
    """
    Core framework for human-AI collaboration in GCS system.
    
    Implements collaborative decision-making, anomaly detection,
    confirmation procedures, and ethical enforcement.
    """
    
    def __init__(self, ethical_engine: EthicalConstraintEngine, 
                 ethical_api: EthicalDecisionAPI):
        """Initialize the collaboration framework"""
        self.logger = logging.getLogger(__name__)
        self.ethical_engine = ethical_engine
        self.ethical_api = ethical_api
        
        # Core collaboration state
        self.active_decisions: Dict[str, CollaborativeDecision] = {}
        self.collaboration_history: List[CollaborativeDecision] = []
        self.detected_anomalies: List[CollaborationAnomaly] = []
        self.user_trust_levels: Dict[str, float] = {}
        
        # Configuration
        self.default_collaboration_mode = CollaborationMode.AI_ASSISTED
        self.anomaly_detection_enabled = True
        self.performance_monitoring_enabled = True
        
        # Event callbacks
        self.decision_callbacks: List[Callable] = []
        self.anomaly_callbacks: List[Callable] = []
        self.confirmation_callbacks: List[Callable] = []
        
        # Threading for async operations
        self.monitor_thread = None
        self.shutdown_flag = threading.Event()
        
        self.logger.info("Human-AI Collaboration Framework initialized")

    def start_monitoring(self):
        """Start background monitoring for anomalies and performance"""
        if self.monitor_thread is None or not self.monitor_thread.is_alive():
            self.shutdown_flag.clear()
            self.monitor_thread = threading.Thread(target=self._monitoring_loop)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            self.logger.info("Collaboration monitoring started")

    def stop_monitoring(self):
        """Stop background monitoring"""
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.shutdown_flag.set()
            self.monitor_thread.join(timeout=5.0)
            self.logger.info("Collaboration monitoring stopped")

    def initiate_collaborative_decision(self, context: CollaborationContext,
                                      problem_description: str,
                                      proposed_action: Action) -> str:
        """
        Initiate a collaborative decision-making process
        
        Args:
            context: Collaboration context
            problem_description: Description of the problem/decision
            proposed_action: Proposed action to take
            
        Returns:
            Decision ID for tracking
        """
        decision_id = f"decision_{int(time.time() * 1000)}"
        
        # Determine appropriate confirmation level
        confirmation_level = self._determine_confirmation_level(
            proposed_action, context
        )
        
        # Create collaborative decision
        decision = CollaborativeDecision(
            decision_id=decision_id,
            context=context,
            problem_description=problem_description,
            proposed_action=proposed_action,
            confirmation_level=confirmation_level
        )
        
        # Perform ethical assessment
        decision.ethical_assessment = self._perform_ethical_assessment(
            proposed_action, context
        )
        
        # Generate AI recommendation
        decision.ai_recommendation = self._generate_ai_recommendation(
            decision, context
        )
        
        # Store active decision
        self.active_decisions[decision_id] = decision
        
        # Trigger callbacks
        self._trigger_decision_callbacks(decision)
        
        self.logger.info(f"Collaborative decision initiated: {decision_id}")
        return decision_id

    def provide_human_input(self, decision_id: str, human_input: str,
                          confirmation: bool = True) -> bool:
        """
        Provide human input for a collaborative decision
        
        Args:
            decision_id: ID of the decision
            human_input: Human's input/feedback
            confirmation: Whether human confirms the action
            
        Returns:
            Whether input was successfully processed
        """
        if decision_id not in self.active_decisions:
            self.logger.warning(f"Decision {decision_id} not found")
            return False
            
        decision = self.active_decisions[decision_id]
        decision.human_input = human_input
        
        if confirmation:
            decision.final_decision = self._synthesize_decision(decision)
            decision.execution_status = "approved"
        else:
            decision.execution_status = "rejected"
            
        # Move to history
        self.collaboration_history.append(decision)
        del self.active_decisions[decision_id]
        
        # Update trust level based on interaction
        self._update_trust_level(decision)
        
        self.logger.info(f"Human input processed for decision {decision_id}")
        return True

    def detect_collaboration_anomaly(self, context: CollaborationContext,
                                   anomaly_data: Dict[str, Any]) -> Optional[str]:
        """
        Detect anomalies in collaborative interactions
        
        Args:
            context: Current collaboration context
            anomaly_data: Data for anomaly detection
            
        Returns:
            Anomaly ID if detected, None otherwise
        """
        anomaly_type, confidence = self._analyze_anomaly_data(anomaly_data, context)
        
        if confidence > 0.7:  # Anomaly threshold
            anomaly_id = f"anomaly_{int(time.time() * 1000)}"
            
            anomaly = CollaborationAnomaly(
                anomaly_id=anomaly_id,
                anomaly_type=anomaly_type,
                severity=self._determine_anomaly_severity(anomaly_type, confidence),
                description=f"Detected {anomaly_type.value} with confidence {confidence:.2f}",
                detected_at=time.time(),
                context=context,
                detection_confidence=confidence,
                recommended_actions=self._generate_anomaly_response_actions(anomaly_type)
            )
            
            self.detected_anomalies.append(anomaly)
            
            # Trigger callbacks
            self._trigger_anomaly_callbacks(anomaly)
            
            # Auto-respond to critical anomalies
            if anomaly.severity in [SafetyLevel.CRITICAL, SafetyLevel.EMERGENCY]:
                self._handle_critical_anomaly(anomaly)
                
            self.logger.warning(f"Collaboration anomaly detected: {anomaly_id}")
            return anomaly_id
            
        return None

    def request_human_override(self, context: CollaborationContext,
                             override_reason: str) -> bool:
        """
        Request human override of AI decision
        
        Args:
            context: Collaboration context
            override_reason: Reason for override request
            
        Returns:
            Whether override was granted
        """
        override_request = {
            "context": context,
            "reason": override_reason,
            "timestamp": time.time(),
            "urgency": context.urgency_level
        }
        
        # For now, log the override request
        # In a real system, this would trigger UI notifications
        self.logger.critical(f"Human override requested: {override_reason}")
        
        # Simulate human response based on urgency
        if context.urgency_level >= 4:
            self.logger.info("Override granted due to high urgency")
            return True
        else:
            self.logger.info("Override request logged for review")
            return False

    def get_collaboration_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for collaboration"""
        total_decisions = len(self.collaboration_history)
        
        if total_decisions == 0:
            return {"total_decisions": 0, "metrics": "No decisions processed yet"}
        
        approved_decisions = len([d for d in self.collaboration_history 
                                if d.execution_status == "approved"])
        
        anomaly_count = len(self.detected_anomalies)
        resolved_anomalies = len([a for a in self.detected_anomalies if a.resolved])
        
        avg_trust_level = (sum(self.user_trust_levels.values()) / 
                          len(self.user_trust_levels)) if self.user_trust_levels else 0.0
        
        return {
            "total_decisions": total_decisions,
            "approved_decisions": approved_decisions,
            "approval_rate": approved_decisions / total_decisions,
            "anomaly_count": anomaly_count,
            "anomaly_resolution_rate": resolved_anomalies / anomaly_count if anomaly_count > 0 else 1.0,
            "average_trust_level": avg_trust_level,
            "active_decisions": len(self.active_decisions),
            "collaboration_effectiveness": self._calculate_collaboration_effectiveness()
        }

    # Private helper methods
    
    def _determine_confirmation_level(self, action: Action, 
                                    context: CollaborationContext) -> ConfirmationLevel:
        """Determine appropriate confirmation level for an action"""
        # Base level on action type and risk
        if action.action_type == ActionType.SYSTEM_MODIFICATION:
            base_level = ConfirmationLevel.ENHANCED
        elif action.action_type == ActionType.EXTERNAL_INTERACTION:
            base_level = ConfirmationLevel.EXPLICIT
        else:
            base_level = ConfirmationLevel.IMPLICIT
            
        # Adjust based on trust level
        trust_level = self.user_trust_levels.get(context.user_id, 0.5)
        if trust_level < 0.3:
            base_level = ConfirmationLevel(min(base_level.value + 1, 4))
        elif trust_level > 0.8:
            base_level = ConfirmationLevel(max(base_level.value - 1, 0))
            
        return base_level

    def _perform_ethical_assessment(self, action: Action, 
                                  context: CollaborationContext) -> EthicalAssessment:
        """Perform ethical assessment of proposed action"""
        # Create intent from action for ethical engine
        intent = Intent(
            description=f"Collaborative action: {action.description}",
            action_type=action.action_type,
            expected_outcome="Beneficial collaborative outcome",
            safety_constraints=context.constraints
        )
        
        return self.ethical_engine.assess_ethical_compliance(intent, action)

    def _generate_ai_recommendation(self, decision: CollaborativeDecision,
                                  context: CollaborationContext) -> str:
        """Generate AI recommendation for decision"""
        ethical_score = decision.ethical_assessment.overall_ethical_score if decision.ethical_assessment else 0.5
        
        if ethical_score > 0.8:
            return f"Recommend proceeding with {decision.proposed_action.description}. High ethical compliance."
        elif ethical_score > 0.6:
            return f"Recommend proceeding with {decision.proposed_action.description} with caution."
        else:
            return f"Recommend reconsidering {decision.proposed_action.description}. Ethical concerns detected."

    def _synthesize_decision(self, decision: CollaborativeDecision) -> str:
        """Synthesize final decision from human and AI input"""
        return f"Collaborative decision: {decision.human_input} (incorporating AI recommendation: {decision.ai_recommendation})"

    def _update_trust_level(self, decision: CollaborativeDecision):
        """Update trust level based on decision outcome"""
        user_id = decision.context.user_id
        current_trust = self.user_trust_levels.get(user_id, 0.5)
        
        # Adjust trust based on decision outcome
        if decision.execution_status == "approved":
            trust_adjustment = 0.05
        elif decision.execution_status == "rejected":
            trust_adjustment = -0.02
        else:
            trust_adjustment = 0.0
            
        new_trust = max(0.0, min(1.0, current_trust + trust_adjustment))
        self.user_trust_levels[user_id] = new_trust

    def _analyze_anomaly_data(self, anomaly_data: Dict[str, Any],
                            context: CollaborationContext) -> Tuple[AnomalyType, float]:
        """Analyze data for anomaly detection"""
        # Simple heuristic-based anomaly detection
        # In a real system, this would use ML models
        
        if "response_time" in anomaly_data:
            if anomaly_data["response_time"] > 5.0:
                return AnomalyType.PERFORMANCE_DEGRADATION, 0.8
                
        if "communication_failures" in anomaly_data:
            if anomaly_data["communication_failures"] > 3:
                return AnomalyType.COMMUNICATION_BREAKDOWN, 0.9
                
        if "trust_score_drop" in anomaly_data:
            if anomaly_data["trust_score_drop"] > 0.3:
                return AnomalyType.TRUST_EROSION, 0.7
                
        return AnomalyType.BEHAVIORAL_ANOMALY, 0.3

    def _determine_anomaly_severity(self, anomaly_type: AnomalyType, 
                                  confidence: float) -> SafetyLevel:
        """Determine severity of detected anomaly"""
        if anomaly_type in [AnomalyType.SAFETY_ANOMALY, AnomalyType.ETHICAL_ANOMALY]:
            return SafetyLevel.CRITICAL if confidence > 0.8 else SafetyLevel.WARNING
        elif anomaly_type == AnomalyType.COMMUNICATION_BREAKDOWN:
            return SafetyLevel.WARNING
        else:
            return SafetyLevel.WARNING if confidence > 0.8 else SafetyLevel.SAFE

    def _generate_anomaly_response_actions(self, anomaly_type: AnomalyType) -> List[str]:
        """Generate recommended response actions for anomaly"""
        actions_map = {
            AnomalyType.PERFORMANCE_DEGRADATION: [
                "Check system resources",
                "Restart affected components",
                "Reduce processing load"
            ],
            AnomalyType.COMMUNICATION_BREAKDOWN: [
                "Verify communication channels",
                "Restart communication subsystem",
                "Switch to backup communication method"
            ],
            AnomalyType.ETHICAL_ANOMALY: [
                "Halt current operation",
                "Request human review",
                "Apply ethical constraints"
            ],
            AnomalyType.TRUST_EROSION: [
                "Increase transparency",
                "Request human feedback",
                "Review recent decisions"
            ]
        }
        
        return actions_map.get(anomaly_type, ["Monitor situation", "Log for review"])

    def _handle_critical_anomaly(self, anomaly: CollaborationAnomaly):
        """Handle critical anomalies automatically"""
        self.logger.critical(f"Handling critical anomaly: {anomaly.anomaly_id}")
        
        # Execute recommended actions
        for action in anomaly.recommended_actions:
            self.logger.info(f"Executing anomaly response: {action}")
            
        # Mark as notified (in real system, would trigger UI notification)
        anomaly.human_notified = True

    def _calculate_collaboration_effectiveness(self) -> float:
        """Calculate overall collaboration effectiveness score"""
        if not self.collaboration_history:
            return 0.5  # Neutral score with no data
            
        # Simple effectiveness calculation based on approvals and trust
        approval_rate = len([d for d in self.collaboration_history 
                           if d.execution_status == "approved"]) / len(self.collaboration_history)
        
        avg_trust = (sum(self.user_trust_levels.values()) / 
                    len(self.user_trust_levels)) if self.user_trust_levels else 0.5
        
        return (approval_rate * 0.6) + (avg_trust * 0.4)

    def _monitoring_loop(self):
        """Background monitoring loop for anomalies and performance"""
        while not self.shutdown_flag.is_set():
            try:
                # Check for stale decisions
                current_time = time.time()
                for decision_id, decision in list(self.active_decisions.items()):
                    if current_time - decision.timestamp > 300:  # 5 minutes timeout
                        self.logger.warning(f"Decision {decision_id} timed out")
                        decision.execution_status = "timeout"
                        self.collaboration_history.append(decision)
                        del self.active_decisions[decision_id]
                
                # Monitor for performance anomalies
                if len(self.active_decisions) > 10:
                    context = CollaborationContext(
                        user_id="system",
                        session_id="monitoring",
                        collaboration_mode=CollaborationMode.AI_AUTONOMOUS,
                        trust_level=1.0,
                        urgency_level=2,
                        domain="system_monitoring"
                    )
                    self.detect_collaboration_anomaly(context, {
                        "active_decisions_overflow": len(self.active_decisions)
                    })
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}", exc_info=True)
                time.sleep(60)  # Wait longer if error

    def _trigger_decision_callbacks(self, decision: CollaborativeDecision):
        """Trigger registered decision callbacks"""
        for callback in self.decision_callbacks:
            try:
                callback(decision)
            except Exception as e:
                self.logger.error(f"Error in decision callback: {e}")

    def _trigger_anomaly_callbacks(self, anomaly: CollaborationAnomaly):
        """Trigger registered anomaly callbacks"""
        for callback in self.anomaly_callbacks:
            try:
                callback(anomaly)
            except Exception as e:
                self.logger.error(f"Error in anomaly callback: {e}")

    # Public callback registration methods
    
    def register_decision_callback(self, callback: Callable):
        """Register callback for decision events"""
        self.decision_callbacks.append(callback)
        
    def register_anomaly_callback(self, callback: Callable):
        """Register callback for anomaly events"""
        self.anomaly_callbacks.append(callback)
        
    def register_confirmation_callback(self, callback: Callable):
        """Register callback for confirmation events"""  
        self.confirmation_callbacks.append(callback)

    def shutdown(self):
        """Shutdown the collaboration framework"""
        self.stop_monitoring()
        self.logger.info("Human-AI Collaboration Framework shutdown complete")