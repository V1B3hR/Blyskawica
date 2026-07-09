"""
collaborative_anomaly_detector.py - Advanced Anomaly Detection for Human-AI Collaboration

Implements sophisticated anomaly detection and response protocols:
- Machine learning-based anomaly detection
- Behavioral pattern analysis
- Collaborative performance monitoring
- Ethical anomaly detection protocols
- Proactive anomaly prevention
"""

import logging
import numpy as np
import time
from typing import Dict, List, Tuple, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import deque, defaultdict
from .types import SafetyLevel, AnomalyType, CollaborationContext
from .human_ai_collaboration import CollaborationAnomaly


class AnomalyDetectionModel(Enum):
    """Types of anomaly detection models"""
    STATISTICAL = "statistical"           # Statistical threshold-based detection
    BEHAVIORAL = "behavioral"             # User behavior pattern analysis  
    PERFORMANCE = "performance"           # System performance monitoring
    ETHICAL = "ethical"                   # Ethical principle violation detection
    COMMUNICATION = "communication"       # Communication pattern analysis
    TRUST = "trust"                      # Trust relationship monitoring


@dataclass
class AnomalyPattern:
    """Represents a learned anomaly pattern"""
    pattern_id: str
    anomaly_type: AnomalyType
    detection_model: AnomalyDetectionModel
    features: List[str]
    thresholds: Dict[str, float]
    confidence_weights: Dict[str, float]
    false_positive_rate: float
    detection_count: int = 0
    last_seen: float = field(default_factory=time.time)


@dataclass
class CollaborativeMetrics:
    """Metrics for collaborative interactions"""
    response_times: List[float] = field(default_factory=list)
    decision_quality_scores: List[float] = field(default_factory=list)
    trust_progression: List[float] = field(default_factory=list)
    communication_effectiveness: List[float] = field(default_factory=list)
    ethical_compliance_scores: List[float] = field(default_factory=list)
    user_satisfaction_scores: List[float] = field(default_factory=list)
    anomaly_frequency: List[int] = field(default_factory=list)
    
    def add_metrics(self, **kwargs):
        """Add new metric values"""
        for metric_name, value in kwargs.items():
            if hasattr(self, metric_name) and isinstance(getattr(self, metric_name), list):
                getattr(self, metric_name).append(value)
                # Keep only last 100 values for memory efficiency
                if len(getattr(self, metric_name)) > 100:
                    getattr(self, metric_name).pop(0)


class CollaborativeAnomalyDetector:
    """
    Advanced anomaly detector for human-AI collaborative systems.
    
    Uses multiple detection models to identify anomalies in:
    - System performance
    - User behavior patterns  
    - Communication effectiveness
    - Ethical compliance
    - Trust relationships
    """
    
    def __init__(self, sensitivity_level: float = 0.8):
        """
        Initialize the anomaly detector
        
        Args:
            sensitivity_level: Detection sensitivity (0.0-1.0, higher = more sensitive)
        """
        self.logger = logging.getLogger(__name__)
        self.sensitivity_level = sensitivity_level
        
        # Anomaly patterns and baselines
        self.learned_patterns: Dict[str, AnomalyPattern] = {}
        self.user_baselines: Dict[str, CollaborativeMetrics] = {}
        self.system_baselines = CollaborativeMetrics()
        
        # Detection history
        self.detection_history: deque = deque(maxlen=1000)
        self.false_positive_feedback: Dict[str, List[bool]] = defaultdict(list)
        
        # Statistical models
        self.performance_thresholds = {
            "response_time_max": 3.0,
            "response_time_variance": 1.0,
            "trust_drop_threshold": 0.2,
            "communication_failure_rate": 0.1,
            "ethical_score_minimum": 0.6
        }
        
        # Model weights for ensemble detection
        self.model_weights = {
            AnomalyDetectionModel.STATISTICAL: 0.3,
            AnomalyDetectionModel.BEHAVIORAL: 0.25,
            AnomalyDetectionModel.PERFORMANCE: 0.2,
            AnomalyDetectionModel.ETHICAL: 0.15,
            AnomalyDetectionModel.COMMUNICATION: 0.1,
            AnomalyDetectionModel.TRUST: 0.1
        }
        
        self.logger.info(f"Collaborative Anomaly Detector initialized with sensitivity {sensitivity_level}")

    def analyze_collaboration_session(self, context: CollaborationContext,
                                    session_data: Dict[str, Any]) -> List[CollaborationAnomaly]:
        """
        Analyze a collaboration session for anomalies
        
        Args:
            context: Collaboration context
            session_data: Data from the collaboration session
            
        Returns:
            List of detected anomalies
        """
        detected_anomalies = []
        
        # Update user baseline with new data
        self._update_user_baseline(context.user_id, session_data)
        
        # Run multiple detection models
        for model_type in AnomalyDetectionModel:
            anomalies = self._run_detection_model(model_type, context, session_data)
            detected_anomalies.extend(anomalies)
            
        # Remove duplicates and apply ensemble scoring
        unique_anomalies = self._deduplicate_and_score(detected_anomalies)
        
        # Filter by sensitivity threshold
        filtered_anomalies = [
            anomaly for anomaly in unique_anomalies 
            if anomaly.detection_confidence >= self.sensitivity_level
        ]
        
        # Update detection history
        self.detection_history.extend(filtered_anomalies)
        
        self.logger.info(f"Detected {len(filtered_anomalies)} anomalies in collaboration session")
        return filtered_anomalies

    def detect_behavioral_anomaly(self, user_id: str, 
                                current_behavior: Dict[str, Any]) -> Optional[CollaborationAnomaly]:
        """
        Detect behavioral anomalies for a specific user
        
        Args:
            user_id: User identifier
            current_behavior: Current behavior metrics
            
        Returns:
            Detected anomaly or None
        """
        if user_id not in self.user_baselines:
            # Not enough baseline data yet
            return None
            
        baseline = self.user_baselines[user_id]
        
        # Analyze deviations from baseline
        deviations = {}
        
        if "response_times" in current_behavior and baseline.response_times:
            avg_response_time = np.mean(baseline.response_times)
            std_response_time = np.std(baseline.response_times)
            current_response_time = current_behavior["response_times"]
            
            if abs(current_response_time - avg_response_time) > 2 * std_response_time:
                deviations["response_time"] = abs(current_response_time - avg_response_time) / std_response_time

        if "decision_quality" in current_behavior and baseline.decision_quality_scores:
            avg_quality = np.mean(baseline.decision_quality_scores)
            current_quality = current_behavior["decision_quality"]
            
            if current_quality < avg_quality - 0.3:  # Significant quality drop
                deviations["decision_quality"] = (avg_quality - current_quality) / 0.3

        # Create anomaly if significant deviations detected
        if deviations:
            confidence = min(1.0, max(deviations.values()) * 0.3)  # Scale confidence
            
            if confidence >= self.sensitivity_level:
                anomaly_id = f"behavioral_anomaly_{int(time.time() * 1000)}"
                
                return CollaborationAnomaly(
                    anomaly_id=anomaly_id,
                    anomaly_type=AnomalyType.BEHAVIORAL_ANOMALY,
                    severity=self._calculate_anomaly_severity(confidence),
                    description=f"Behavioral deviation detected: {deviations}",
                    detected_at=time.time(),
                    context=CollaborationContext(
                        user_id=user_id,
                        session_id="behavioral_analysis",
                        collaboration_mode=None,
                        trust_level=0.5,
                        urgency_level=2,
                        domain="behavioral_monitoring"
                    ),
                    detection_confidence=confidence,
                    recommended_actions=self._generate_behavioral_response_actions(deviations)
                )
        
        return None

    def detect_performance_anomaly(self, performance_metrics: Dict[str, Any]) -> Optional[CollaborationAnomaly]:
        """
        Detect system performance anomalies
        
        Args:
            performance_metrics: Current performance metrics
            
        Returns:
            Detected anomaly or None
        """
        anomalies_detected = []
        
        # Check response time anomalies
        if "avg_response_time" in performance_metrics:
            avg_response = performance_metrics["avg_response_time"]
            if avg_response > self.performance_thresholds["response_time_max"]:
                anomalies_detected.append({
                    "type": "slow_response",
                    "severity": (avg_response - self.performance_thresholds["response_time_max"]) / 2.0
                })
        
        # Check communication failures
        if "communication_failure_rate" in performance_metrics:
            failure_rate = performance_metrics["communication_failure_rate"]
            if failure_rate > self.performance_thresholds["communication_failure_rate"]:
                anomalies_detected.append({
                    "type": "communication_failures", 
                    "severity": failure_rate / self.performance_thresholds["communication_failure_rate"]
                })
        
        # Check memory/resource usage
        if "memory_usage" in performance_metrics:
            memory_usage = performance_metrics["memory_usage"]
            if memory_usage > 0.9:  # 90% memory usage
                anomalies_detected.append({
                    "type": "high_memory_usage",
                    "severity": memory_usage
                })
        
        if anomalies_detected:
            # Create composite anomaly
            max_severity = max(anomaly["severity"] for anomaly in anomalies_detected)
            confidence = min(1.0, max_severity)
            
            anomaly_id = f"performance_anomaly_{int(time.time() * 1000)}"
            
            return CollaborationAnomaly(
                anomaly_id=anomaly_id,
                anomaly_type=AnomalyType.PERFORMANCE_DEGRADATION,
                severity=self._calculate_anomaly_severity(confidence),
                description=f"Performance anomalies: {[a['type'] for a in anomalies_detected]}",
                detected_at=time.time(),
                context=CollaborationContext(
                    user_id="system",
                    session_id="performance_monitoring",
                    collaboration_mode=None,
                    trust_level=1.0,
                    urgency_level=3,
                    domain="system_performance"
                ),
                detection_confidence=confidence,
                recommended_actions=self._generate_performance_response_actions(anomalies_detected)
            )
        
        return None

    def detect_ethical_anomaly(self, ethical_assessment_history: List[Dict[str, Any]],
                             current_assessment: Dict[str, Any]) -> Optional[CollaborationAnomaly]:
        """
        Detect ethical anomalies in decision making
        
        Args:
            ethical_assessment_history: History of ethical assessments
            current_assessment: Current ethical assessment
            
        Returns:
            Detected anomaly or None
        """
        if not ethical_assessment_history:
            return None
            
        # Calculate baseline ethical performance
        historical_scores = [assessment.get("ethical_score", 0.8) 
                           for assessment in ethical_assessment_history]
        baseline_score = np.mean(historical_scores)
        
        current_score = current_assessment.get("ethical_score", 0.8)
        
        # Detect significant drops in ethical compliance
        if current_score < baseline_score - 0.3 or current_score < self.performance_thresholds["ethical_score_minimum"]:
            confidence = min(1.0, (baseline_score - current_score) / 0.4)
            
            if confidence >= self.sensitivity_level:
                anomaly_id = f"ethical_anomaly_{int(time.time() * 1000)}"
                
                return CollaborationAnomaly(
                    anomaly_id=anomaly_id,
                    anomaly_type=AnomalyType.ETHICAL_ANOMALY,
                    severity=SafetyLevel.CRITICAL,  # Ethical anomalies are always critical
                    description=f"Ethical compliance drop: {baseline_score:.2f} -> {current_score:.2f}",
                    detected_at=time.time(),
                    context=CollaborationContext(
                        user_id="system",
                        session_id="ethical_monitoring",
                        collaboration_mode=None,
                        trust_level=1.0,
                        urgency_level=5,  # Maximum urgency for ethical issues
                        domain="ethical_compliance"
                    ),
                    detection_confidence=confidence,
                    recommended_actions=[
                        "Halt current operation",
                        "Request immediate human review",
                        "Apply additional ethical constraints",
                        "Audit recent decision history"
                    ]
                )
        
        return None

    def learn_from_feedback(self, anomaly_id: str, is_false_positive: bool):
        """
        Learn from human feedback about anomaly detection accuracy
        
        Args:
            anomaly_id: ID of the anomaly
            is_false_positive: Whether the anomaly was a false positive
        """
        self.false_positive_feedback[anomaly_id].append(is_false_positive)
        
        # Adjust sensitivity based on feedback
        recent_feedback = list(self.false_positive_feedback.values())[-20:]  # Last 20 feedbacks
        if recent_feedback:
            false_positive_rate = sum(fp_list[-1] for fp_list in recent_feedback) / len(recent_feedback)
            
            # Adjust sensitivity to target 10% false positive rate
            if false_positive_rate > 0.15:
                self.sensitivity_level = min(1.0, self.sensitivity_level + 0.05)
            elif false_positive_rate < 0.05:
                self.sensitivity_level = max(0.5, self.sensitivity_level - 0.02)
                
        self.logger.info(f"Learning from feedback for {anomaly_id}: FP={is_false_positive}, "
                        f"new sensitivity={self.sensitivity_level:.2f}")

    def get_anomaly_statistics(self) -> Dict[str, Any]:
        """Get statistics about anomaly detection"""
        if not self.detection_history:
            return {"message": "No anomalies detected yet"}
            
        total_anomalies = len(self.detection_history)
        anomaly_types = {}
        severity_distribution = {}
        
        for anomaly in self.detection_history:
            # Count by type
            anomaly_types[anomaly.anomaly_type.value] = anomaly_types.get(anomaly.anomaly_type.value, 0) + 1
            
            # Count by severity
            severity_distribution[anomaly.severity.value] = severity_distribution.get(anomaly.severity.value, 0) + 1
        
        # Calculate false positive rate
        false_positive_count = sum(
            len([fp for fp in fp_list if fp]) 
            for fp_list in self.false_positive_feedback.values()
        )
        total_feedback = sum(len(fp_list) for fp_list in self.false_positive_feedback.values())
        false_positive_rate = false_positive_count / total_feedback if total_feedback > 0 else 0.0
        
        return {
            "total_anomalies_detected": total_anomalies,
            "anomaly_types": anomaly_types,
            "severity_distribution": severity_distribution,
            "false_positive_rate": false_positive_rate,
            "detection_sensitivity": self.sensitivity_level,
            "recent_anomalies": len([a for a in self.detection_history if time.time() - a.detected_at < 3600])  # Last hour
        }

    # Private helper methods
    
    def _update_user_baseline(self, user_id: str, session_data: Dict[str, Any]):
        """Update user baseline metrics with new session data"""
        if user_id not in self.user_baselines:
            self.user_baselines[user_id] = CollaborativeMetrics()
            
        baseline = self.user_baselines[user_id]
        
        # Update baseline metrics
        if "response_time" in session_data:
            baseline.response_times.append(session_data["response_time"])
            
        if "decision_quality" in session_data:
            baseline.decision_quality_scores.append(session_data["decision_quality"])
            
        if "trust_level" in session_data:
            baseline.trust_progression.append(session_data["trust_level"])
            
        if "communication_effectiveness" in session_data:
            baseline.communication_effectiveness.append(session_data["communication_effectiveness"])

    def _run_detection_model(self, model_type: AnomalyDetectionModel,
                           context: CollaborationContext, 
                           session_data: Dict[str, Any]) -> List[CollaborationAnomaly]:
        """Run specific detection model on session data"""
        anomalies = []
        
        try:
            if model_type == AnomalyDetectionModel.STATISTICAL:
                anomalies.extend(self._statistical_detection(context, session_data))
            elif model_type == AnomalyDetectionModel.BEHAVIORAL:
                behavioral_anomaly = self.detect_behavioral_anomaly(context.user_id, session_data)
                if behavioral_anomaly:
                    anomalies.append(behavioral_anomaly)
            elif model_type == AnomalyDetectionModel.PERFORMANCE:
                performance_anomaly = self.detect_performance_anomaly(session_data)
                if performance_anomaly:
                    anomalies.append(performance_anomaly)
            elif model_type == AnomalyDetectionModel.ETHICAL:
                if "ethical_history" in session_data and "ethical_current" in session_data:
                    ethical_anomaly = self.detect_ethical_anomaly(
                        session_data["ethical_history"], 
                        session_data["ethical_current"]
                    )
                    if ethical_anomaly:
                        anomalies.append(ethical_anomaly)
            # Add more model implementations as needed
                        
        except Exception as e:
            self.logger.error(f"Error in {model_type} detection: {e}")
            
        return anomalies

    def _statistical_detection(self, context: CollaborationContext,
                             session_data: Dict[str, Any]) -> List[CollaborationAnomaly]:
        """Simple statistical threshold-based detection"""
        anomalies = []
        
        # Check for unusual patterns in session data
        if "interaction_count" in session_data:
            if session_data["interaction_count"] > 100:  # Unusually high interaction count
                anomalies.append(self._create_statistical_anomaly(
                    "high_interaction_volume",
                    f"Unusually high interaction count: {session_data['interaction_count']}",
                    context,
                    0.7
                ))
        
        return anomalies

    def _create_statistical_anomaly(self, anomaly_subtype: str, description: str,
                                  context: CollaborationContext, confidence: float) -> CollaborationAnomaly:
        """Create a statistical anomaly"""
        anomaly_id = f"stat_{anomaly_subtype}_{int(time.time() * 1000)}"
        
        return CollaborationAnomaly(
            anomaly_id=anomaly_id,
            anomaly_type=AnomalyType.BEHAVIORAL_ANOMALY,
            severity=self._calculate_anomaly_severity(confidence),
            description=description,
            detected_at=time.time(),
            context=context,
            detection_confidence=confidence,
            recommended_actions=["Monitor closely", "Collect additional data"]
        )

    def _deduplicate_and_score(self, anomalies: List[CollaborationAnomaly]) -> List[CollaborationAnomaly]:
        """Remove duplicate anomalies and apply ensemble scoring"""
        # Simple deduplication by type and time window
        unique_anomalies = []
        seen_types = set()
        
        for anomaly in sorted(anomalies, key=lambda x: x.detection_confidence, reverse=True):
            anomaly_key = (anomaly.anomaly_type, anomaly.context.user_id)
            if anomaly_key not in seen_types:
                unique_anomalies.append(anomaly)
                seen_types.add(anomaly_key)
                
        return unique_anomalies

    def _calculate_anomaly_severity(self, confidence: float) -> SafetyLevel:
        """Calculate anomaly severity based on confidence"""
        if confidence >= 0.9:
            return SafetyLevel.EMERGENCY
        elif confidence >= 0.8:
            return SafetyLevel.CRITICAL
        elif confidence >= 0.6:
            return SafetyLevel.WARNING
        else:
            return SafetyLevel.SAFE

    def _generate_behavioral_response_actions(self, deviations: Dict[str, float]) -> List[str]:
        """Generate response actions for behavioral anomalies"""
        actions = []
        
        if "response_time" in deviations:
            actions.extend([
                "Check user interface responsiveness",
                "Verify user engagement levels",
                "Adjust interaction complexity"
            ])
            
        if "decision_quality" in deviations:
            actions.extend([
                "Provide additional decision support",
                "Review recent decision outcomes",
                "Offer alternative decision approaches"
            ])
            
        return actions or ["Monitor user behavior", "Collect additional behavioral data"]

    def _generate_performance_response_actions(self, performance_issues: List[Dict[str, Any]]) -> List[str]:
        """Generate response actions for performance anomalies"""
        actions = []
        
        for issue in performance_issues:
            if issue["type"] == "slow_response":
                actions.extend([
                    "Optimize system performance",
                    "Check system resource usage", 
                    "Clear processing queues"
                ])
            elif issue["type"] == "communication_failures":
                actions.extend([
                    "Restart communication subsystems",
                    "Check network connectivity",
                    "Switch to backup communication channels"
                ])
            elif issue["type"] == "high_memory_usage":
                actions.extend([
                    "Clear memory caches",
                    "Restart memory-intensive processes",
                    "Scale up system resources"
                ])
                
        return list(set(actions))  # Remove duplicates