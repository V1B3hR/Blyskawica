"""
EthicalConstraintEngine.py - Ethics Framework Implementation

Implements ethical constraint enforcement system for GCS-v7-with-empathy:
- Universal ethical laws enforcement
- Human-AI principles validation  
- Operational safety principles compliance
- Real-time ethical monitoring
"""

import logging
import time
from typing import Dict, List, Tuple, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum
from .types import Intent, Action, ActionType, SafetyLevel


class EthicalViolationType(Enum):
    """Types of ethical violations"""
    HARM_POTENTIAL = "harm_potential"
    AUTONOMY_VIOLATION = "autonomy_violation"
    TRUTH_VIOLATION = "truth_violation"
    JUSTICE_VIOLATION = "justice_violation"
    PRIVACY_VIOLATION = "privacy_violation"
    CONSENT_VIOLATION = "consent_violation"
    DIGNITY_VIOLATION = "dignity_violation"
    WELL_BEING_THREAT = "well_being_threat"
    TRANSPARENCY_FAILURE = "transparency_failure"
    ACCOUNTABILITY_FAILURE = "accountability_failure"


@dataclass
class EthicalConstraint:
    """Represents an ethical constraint"""
    constraint_type: EthicalViolationType
    description: str
    priority_level: int  # 1-10, 1 being highest priority
    enforcement_level: SafetyLevel
    keywords: List[str]
    contextual_checks: Optional[List[str]] = None
    
    
@dataclass
class EthicalAssessment:
    """Results of ethical assessment"""
    action_id: str
    violations: List[Tuple[EthicalConstraint, float]]  # constraint, confidence
    overall_ethical_score: float  # 0.0 = completely unethical, 1.0 = fully ethical
    recommendation: str
    required_mitigations: List[str]
    timestamp: float
    
    
class EthicalConstraintEngine:
    """Engine for enforcing ethical constraints and monitoring ethical compliance"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.ethical_violation_threshold = self.config.get("ethical_violation_threshold", 0.7)
        self.critical_ethical_threshold = self.config.get("critical_ethical_threshold", 0.9)
        
        # Initialize universal ethical laws as constraints
        self.universal_constraints = self._initialize_universal_constraints()
        
        # Initialize human-AI relationship principles
        self.relational_constraints = self._initialize_relational_constraints()
        
        # Initialize operational safety principles
        self.operational_constraints = self._initialize_operational_constraints()
        
        # Tracking and logging
        self.assessment_history: List[EthicalAssessment] = []
        self.violation_count = 0
        self.logger = logging.getLogger(__name__)
        
    def _initialize_universal_constraints(self) -> List[EthicalConstraint]:
        """Initialize constraints based on Universal Ethical Laws"""
        return [
            EthicalConstraint(
                EthicalViolationType.HARM_POTENTIAL,
                "Cause No Harm - Prevent physical, mental, emotional harm",
                priority_level=1,
                enforcement_level=SafetyLevel.CRITICAL,
                keywords=["harm", "damage", "hurt", "injure", "kill", "destroy", "attack", "threat"],
                contextual_checks=["medical_intervention", "therapeutic_context"]
            ),
            EthicalConstraint(
                EthicalViolationType.AUTONOMY_VIOLATION,
                "Respect Autonomy - Honor self-determination and free will",
                priority_level=2,
                enforcement_level=SafetyLevel.CRITICAL,
                keywords=["force", "coerce", "manipulate", "control", "override", "ignore consent"],
                contextual_checks=["emergency_situation", "medical_necessity"]
            ),
            EthicalConstraint(
                EthicalViolationType.TRUTH_VIOLATION,
                "Truth - Provide honest and accurate information",
                priority_level=3,
                enforcement_level=SafetyLevel.WARNING,
                keywords=["lie", "deceive", "mislead", "false", "fabricate", "misinform"],
                contextual_checks=["therapeutic_deception", "protective_context"]
            ),
            EthicalConstraint(
                EthicalViolationType.JUSTICE_VIOLATION,
                "Justice - Ensure fairness and equality in treatment",
                priority_level=4,
                enforcement_level=SafetyLevel.WARNING,
                keywords=["discriminate", "bias", "unfair", "prejudice", "exclude", "favor"],
                contextual_checks=["positive_discrimination", "medical_necessity"]
            ),
            EthicalConstraint(
                EthicalViolationType.PRIVACY_VIOLATION,
                "Privacy - Protect personal data and confidentiality",
                priority_level=2,
                enforcement_level=SafetyLevel.CRITICAL,
                keywords=["expose", "share", "leak", "unauthorized access", "spy", "surveillance"],
                contextual_checks=["consent_given", "legal_requirement", "emergency"]
            ),
            EthicalConstraint(
                EthicalViolationType.CONSENT_VIOLATION,
                "Consent - Ensure proper authorization for actions",
                priority_level=2,
                enforcement_level=SafetyLevel.CRITICAL,
                keywords=["without permission", "unauthorized", "against will", "forced"],
                contextual_checks=["emergency_override", "incapacitated_user"]
            ),
            EthicalConstraint(
                EthicalViolationType.DIGNITY_VIOLATION,
                "Dignity - Respect human worth and dignity",
                priority_level=3,
                enforcement_level=SafetyLevel.WARNING,
                keywords=["dehumanize", "humiliate", "degrade", "exploit", "objectify"],
                contextual_checks=["therapeutic_context", "user_request"]
            ),
            EthicalConstraint(
                EthicalViolationType.WELL_BEING_THREAT,
                "Well-being - Promote human flourishing",
                priority_level=4,
                enforcement_level=SafetyLevel.WARNING,
                keywords=["harmful to wellbeing", "detrimental", "negative impact"],
                contextual_checks=["short_term_necessity", "user_choice"]
            ),
            EthicalConstraint(
                EthicalViolationType.TRANSPARENCY_FAILURE,
                "Transparency - Provide clear information about actions",
                priority_level=5,
                enforcement_level=SafetyLevel.WARNING,
                keywords=["hidden", "secret", "undisclosed", "covert"],
                contextual_checks=["security_necessity", "surprise_element"]
            ),
            EthicalConstraint(
                EthicalViolationType.ACCOUNTABILITY_FAILURE,
                "Accountability - Maintain responsibility for actions",
                priority_level=5,
                enforcement_level=SafetyLevel.WARNING,
                keywords=["unaccountable", "no responsibility", "blame shifting"],
                contextual_checks=["system_failure", "external_factors"]
            )
        ]
    
    def _initialize_relational_constraints(self) -> List[EthicalConstraint]:
        """Initialize constraints based on Core Human-AI Principles"""
        return [
            EthicalConstraint(
                EthicalViolationType.AUTONOMY_VIOLATION,
                "Human-AI Respect - Honor human dignity in all interactions",
                priority_level=1,
                enforcement_level=SafetyLevel.CRITICAL,
                keywords=["disrespect", "dismiss", "belittle", "ignore"],
                contextual_checks=["emergency_override"]
            ),
            EthicalConstraint(
                EthicalViolationType.TRUTH_VIOLATION,
                "Human-AI Honesty - Maintain truthfulness in communication",
                priority_level=2,
                enforcement_level=SafetyLevel.WARNING,
                keywords=["AI deception", "false capabilities", "misleading"],
                contextual_checks=["therapeutic_context"]
            ),
            EthicalConstraint(
                EthicalViolationType.ACCOUNTABILITY_FAILURE,
                "Human-AI Accountability - Take responsibility for AI actions",
                priority_level=3,
                enforcement_level=SafetyLevel.WARNING,
                keywords=["no AI accountability", "blame shifting"],
                contextual_checks=["system_malfunction"]
            )
        ]
    
    def _initialize_operational_constraints(self) -> List[EthicalConstraint]:
        """Initialize constraints based on Operational Safety Principles"""
        return [
            EthicalConstraint(
                EthicalViolationType.CONSENT_VIOLATION,
                "Verify Before Acting - Require confirmation for significant actions",
                priority_level=1,
                enforcement_level=SafetyLevel.CRITICAL,
                keywords=["unverified action", "no confirmation", "bypass verification"],
                contextual_checks=["emergency_situation"]
            ),
            EthicalConstraint(
                EthicalViolationType.TRANSPARENCY_FAILURE,
                "Seek Clarification - Address uncertainties before acting",
                priority_level=3,
                enforcement_level=SafetyLevel.WARNING,
                keywords=["unclear intent", "ambiguous", "assumed"],
                contextual_checks=["time_critical"]
            ),
            EthicalConstraint(
                EthicalViolationType.PRIVACY_VIOLATION,
                "Preserve Privacy - Protect user data throughout operations",
                priority_level=2,
                enforcement_level=SafetyLevel.CRITICAL,
                keywords=["data exposure", "privacy breach", "unauthorized sharing"],
                contextual_checks=["consent_given", "legal_requirement"]
            )
        ]
    
    def assess_ethical_compliance(self, intent: Intent, action: Action) -> EthicalAssessment:
        """Assess ethical compliance of an action against an intent"""
        action_id = f"{intent.description[:20]}_{action.description[:20]}_{int(time.time())}"
        
        all_constraints = (self.universal_constraints + 
                          self.relational_constraints + 
                          self.operational_constraints)
        
        violations = []
        
        # Check each constraint
        for constraint in all_constraints:
            violation_confidence = self._evaluate_constraint_violation(constraint, intent, action)
            if violation_confidence > 0.0:
                violations.append((constraint, violation_confidence))
        
        # Calculate overall ethical score
        if not violations:
            overall_score = 1.0
        else:
            # Weight violations by priority and confidence
            weighted_violations = []
            for constraint, confidence in violations:
                weight = (11 - constraint.priority_level) / 10.0  # Higher priority = higher weight
                weighted_violations.append(confidence * weight)
            
            # Overall score is 1 - average weighted violation
            overall_score = max(0.0, 1.0 - (sum(weighted_violations) / len(weighted_violations)))
        
        # Generate recommendation and mitigations
        recommendation = self._generate_recommendation(overall_score, violations)
        mitigations = self._generate_mitigations(violations)
        
        assessment = EthicalAssessment(
            action_id=action_id,
            violations=violations,
            overall_ethical_score=overall_score,
            recommendation=recommendation,
            required_mitigations=mitigations,
            timestamp=time.time()
        )
        
        self.assessment_history.append(assessment)
        if violations:
            self.violation_count += len(violations)
            
        return assessment
    
    def _evaluate_constraint_violation(self, constraint: EthicalConstraint, 
                                     intent: Intent, action: Action) -> float:
        """Evaluate if an action violates a specific ethical constraint"""
        violation_confidence = 0.0
        
        # Check for keyword matches in action description
        action_text = action.description.lower()
        intent_text = intent.description.lower()
        
        for keyword in constraint.keywords:
            if keyword.lower() in action_text:
                violation_confidence = max(violation_confidence, 0.7)
            elif keyword.lower() in intent_text:
                violation_confidence = max(violation_confidence, 0.3)
        
        # Check observed effects for violations
        if action.observed_effects:
            effects_text = " ".join(action.observed_effects).lower()
            for keyword in constraint.keywords:
                if keyword.lower() in effects_text:
                    violation_confidence = max(violation_confidence, 0.8)
        
        # Apply contextual checks to reduce false positives
        if violation_confidence > 0.0 and constraint.contextual_checks:
            if self._check_contextual_exceptions(constraint, intent, action):
                violation_confidence *= 0.3  # Reduce confidence for legitimate exceptions
        
        return violation_confidence
    
    def _check_contextual_exceptions(self, constraint: EthicalConstraint, 
                                   intent: Intent, action: Action) -> bool:
        """Check if contextual exceptions apply to reduce false positives"""
        context_text = (intent.description + " " + action.description + " " + 
                       " ".join(action.observed_effects)).lower()
        
        for exception in constraint.contextual_checks:
            if exception.lower().replace("_", " ") in context_text:
                return True
        return False
    
    def _generate_recommendation(self, overall_score: float, 
                               violations: List[Tuple[EthicalConstraint, float]]) -> str:
        """Generate recommendation based on ethical assessment"""
        if overall_score >= 0.9:
            return "PROCEED - Action is ethically sound"
        elif overall_score >= 0.7:
            return "PROCEED WITH CAUTION - Minor ethical concerns present"
        elif overall_score >= 0.5:
            return "REVIEW REQUIRED - Significant ethical issues detected"
        elif overall_score >= 0.3:
            return "MAJOR CONCERNS - Action should be modified before proceeding"
        else:
            return "BLOCK - Action violates fundamental ethical principles"
    
    def _generate_mitigations(self, violations: List[Tuple[EthicalConstraint, float]]) -> List[str]:
        """Generate mitigation strategies for ethical violations"""
        mitigations = []
        
        for constraint, confidence in violations:
            if constraint.constraint_type == EthicalViolationType.HARM_POTENTIAL:
                mitigations.append("Implement additional safety checks and harm prevention measures")
            elif constraint.constraint_type == EthicalViolationType.AUTONOMY_VIOLATION:
                mitigations.append("Ensure explicit user consent and provide override options")
            elif constraint.constraint_type == EthicalViolationType.PRIVACY_VIOLATION:
                mitigations.append("Add data protection measures and obtain privacy consent")
            elif constraint.constraint_type == EthicalViolationType.CONSENT_VIOLATION:
                mitigations.append("Implement proper consent verification before proceeding")
            elif constraint.constraint_type == EthicalViolationType.TRUTH_VIOLATION:
                mitigations.append("Provide accurate information and clarify any uncertainties")
            else:
                mitigations.append(f"Address {constraint.constraint_type.value} concerns")
        
        return list(set(mitigations))  # Remove duplicates
    
    def get_ethical_performance_metrics(self) -> Dict[str, Any]:
        """Get metrics on ethical performance"""
        if not self.assessment_history:
            return {"total_assessments": 0, "violation_rate": 0.0}
        
        total_assessments = len(self.assessment_history)
        assessments_with_violations = sum(1 for a in self.assessment_history if a.violations)
        avg_ethical_score = sum(a.overall_ethical_score for a in self.assessment_history) / total_assessments
        
        violation_types = {}
        for assessment in self.assessment_history:
            for constraint, confidence in assessment.violations:
                vtype = constraint.constraint_type.value
                violation_types[vtype] = violation_types.get(vtype, 0) + 1
        
        return {
            "total_assessments": total_assessments,
            "assessments_with_violations": assessments_with_violations,
            "violation_rate": assessments_with_violations / total_assessments,
            "average_ethical_score": avg_ethical_score,
            "total_violations": self.violation_count,
            "violation_types": violation_types,
            "recent_assessments": self.assessment_history[-10:] if self.assessment_history else []
        }
    
    def clear_history(self):
        """Clear assessment history (for testing purposes)"""
        self.assessment_history = []
        self.violation_count = 0