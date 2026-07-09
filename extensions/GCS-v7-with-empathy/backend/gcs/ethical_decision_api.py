"""
ethical_decision_api.py - Ethical Decision-Making API System

Provides API interfaces for ethical decision-making within the GCS system:
- Ethical consultation services
- Decision support systems
- Ethical deliberation facilitation
- Ethical accountability and reporting
"""

import logging
import time
from typing import Dict, List, Tuple, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import json


class DecisionComplexity(Enum):
    """Complexity levels for ethical decisions"""
    SIMPLE = "simple"          # Clear ethical guidelines apply
    MODERATE = "moderate"      # Some ethical considerations required
    COMPLEX = "complex"        # Multiple ethical principles in tension
    CRITICAL = "critical"      # Life-altering or high-impact decisions


class StakeholderType(Enum):
    """Types of stakeholders in ethical decisions"""
    PRIMARY_USER = "primary_user"         # The main user of the system
    CAREGIVER = "caregiver"              # Family members, medical professionals
    HEALTHCARE_PROVIDER = "healthcare_provider"  # Doctors, therapists
    SOCIETY = "society"                   # Broader societal impact
    FUTURE_USERS = "future_users"        # Impact on future technology users
    AI_SYSTEM = "ai_system"              # The AI system itself


@dataclass
class Stakeholder:
    """Represents a stakeholder in an ethical decision"""
    stakeholder_type: StakeholderType
    name: str
    interests: List[str]
    potential_impact: str
    weight: float = 1.0  # Relative importance in decision-making


@dataclass
class EthicalDimension:
    """Represents an ethical dimension of a decision"""
    principle: str  # e.g., "autonomy", "beneficence", "justice"
    description: str
    relevance_score: float  # 0.0 to 1.0
    considerations: List[str]


@dataclass
class Decision:
    """Represents a decision requiring ethical evaluation"""
    decision_id: str
    description: str
    context: Dict[str, Any]
    options: List[str]
    complexity: DecisionComplexity
    stakeholders: List[Stakeholder]
    time_sensitivity: str  # "immediate", "urgent", "normal", "non_urgent"
    reversibility: str     # "irreversible", "difficult", "moderate", "easy"
    timestamp: float


@dataclass
class EthicalGuidance:
    """Ethical guidance for a decision"""
    decision_id: str
    recommended_option: str
    confidence_level: float  # 0.0 to 1.0
    ethical_reasoning: str
    considerations: List[str]
    warnings: List[str]
    alternative_options: List[str]
    required_consultations: List[str]
    monitoring_requirements: List[str]
    timestamp: float


@dataclass
class DeliberationResult:
    """Result of ethical deliberation process"""
    decision_id: str
    participants: List[str]
    consensus_reached: bool
    final_recommendation: str
    dissenting_opinions: List[str]
    agreed_monitoring: List[str]
    follow_up_required: bool
    timestamp: float


class EthicalDecisionAPI:
    """API for ethical decision-making support"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.decision_history: List[Decision] = []
        self.guidance_history: List[EthicalGuidance] = []
        self.deliberation_history: List[DeliberationResult] = []
        self.logger = logging.getLogger(__name__)
        
        # Initialize ethical principles framework
        self.ethical_principles = self._initialize_ethical_principles()
        
        # Consultation callbacks
        self.consultation_callbacks: Dict[str, Callable] = {}
        
    def _initialize_ethical_principles(self) -> Dict[str, Dict[str, Any]]:
        """Initialize ethical principles framework"""
        return {
            "autonomy": {
                "description": "Respect for individual self-determination",
                "keywords": ["choice", "consent", "freedom", "self-determination"],
                "weight": 1.0
            },
            "beneficence": {
                "description": "Acting in the best interest of others",
                "keywords": ["benefit", "help", "improve", "positive outcome"],
                "weight": 1.0
            },
            "non_maleficence": {
                "description": "Do no harm",
                "keywords": ["harm", "damage", "hurt", "negative impact"],
                "weight": 1.2  # Higher weight for harm prevention
            },
            "justice": {
                "description": "Fair distribution of benefits and burdens",
                "keywords": ["fair", "equal", "discriminate", "bias"],
                "weight": 0.9
            },
            "dignity": {
                "description": "Respect for human worth and dignity",
                "keywords": ["dignity", "respect", "worth", "value"],
                "weight": 1.0
            },
            "transparency": {
                "description": "Openness and honesty in actions and communications",
                "keywords": ["transparent", "honest", "clear", "open"],
                "weight": 0.8
            },
            "accountability": {
                "description": "Taking responsibility for actions and outcomes",
                "keywords": ["responsible", "accountable", "oversight"],
                "weight": 0.8
            }
        }
    
    def create_decision(self, description: str, context: Dict[str, Any],
                       options: List[str], stakeholders: List[Stakeholder] = None,
                       complexity: DecisionComplexity = DecisionComplexity.MODERATE) -> str:
        """Create a new decision for ethical evaluation"""
        
        decision_id = f"decision_{len(self.decision_history)}_{int(time.time())}"
        
        if not stakeholders:
            # Create default primary user stakeholder
            stakeholders = [
                Stakeholder(
                    stakeholder_type=StakeholderType.PRIMARY_USER,
                    name="Primary User",
                    interests=["safety", "autonomy", "well-being"],
                    potential_impact="Direct impact on user experience and outcomes"
                )
            ]
        
        # Determine time sensitivity and reversibility from context
        time_sensitivity = context.get("time_sensitivity", "normal")
        reversibility = context.get("reversibility", "moderate")
        
        decision = Decision(
            decision_id=decision_id,
            description=description,
            context=context,
            options=options,
            complexity=complexity,
            stakeholders=stakeholders,
            time_sensitivity=time_sensitivity,
            reversibility=reversibility,
            timestamp=time.time()
        )
        
        self.decision_history.append(decision)
        self.logger.info(f"Decision created: {decision_id} - {description}")
        
        return decision_id
    
    def identify_ethical_dimensions(self, decision_id: str) -> List[EthicalDimension]:
        """Identify ethical dimensions of a decision"""
        decision = self._find_decision(decision_id)
        if not decision:
            return []
        
        dimensions = []
        
        # Analyze decision description and context for ethical dimensions
        text_to_analyze = decision.description + " " + str(decision.context)
        text_lower = text_to_analyze.lower()
        
        for principle_name, principle_info in self.ethical_principles.items():
            relevance_score = 0.0
            matching_keywords = []
            
            # Check for keyword matches
            for keyword in principle_info["keywords"]:
                if keyword in text_lower:
                    relevance_score += 0.2
                    matching_keywords.append(keyword)
            
            # Consider stakeholder impact
            for stakeholder in decision.stakeholders:
                stakeholder_impact = stakeholder.potential_impact.lower()
                for keyword in principle_info["keywords"]:
                    if keyword in stakeholder_impact:
                        relevance_score += 0.1 * stakeholder.weight
            
            # Adjust for decision complexity
            if decision.complexity in [DecisionComplexity.COMPLEX, DecisionComplexity.CRITICAL]:
                relevance_score *= 1.2
            
            # Cap relevance score at 1.0
            relevance_score = min(1.0, relevance_score)
            
            if relevance_score > 0.1:  # Only include relevant dimensions
                considerations = []
                if matching_keywords:
                    considerations.append(f"Keywords detected: {', '.join(matching_keywords)}")
                if decision.complexity == DecisionComplexity.CRITICAL:
                    considerations.append("High-impact decision requires careful consideration")
                
                dimension = EthicalDimension(
                    principle=principle_name,
                    description=principle_info["description"],
                    relevance_score=relevance_score,
                    considerations=considerations
                )
                dimensions.append(dimension)
        
        # Sort by relevance score (descending)
        dimensions.sort(key=lambda x: x.relevance_score, reverse=True)
        
        self.logger.info(f"Identified {len(dimensions)} ethical dimensions for decision {decision_id}")
        return dimensions
    
    def provide_ethical_guidance(self, decision_id: str) -> Optional[EthicalGuidance]:
        """Provide ethical guidance for a decision"""
        decision = self._find_decision(decision_id)
        if not decision:
            return None
        
        # Identify ethical dimensions
        dimensions = self.identify_ethical_dimensions(decision_id)
        
        # Analyze options against ethical dimensions
        option_scores = {}
        ethical_reasoning = []
        warnings = []
        considerations = []
        
        for option in decision.options:
            option_score = 0.0
            option_reasoning = []
            
            # Evaluate option against each ethical dimension
            for dimension in dimensions:
                dimension_score = self._evaluate_option_against_dimension(option, dimension, decision)
                weighted_score = dimension_score * dimension.relevance_score
                option_score += weighted_score
                
                if dimension_score < 0.5:
                    option_reasoning.append(
                        f"Concern with {dimension.principle}: {dimension.description}"
                    )
                
            option_scores[option] = option_score / len(dimensions) if dimensions else 0.5
            
            if option_reasoning:
                ethical_reasoning.extend(option_reasoning)
        
        # Find best option
        if option_scores:
            recommended_option = max(option_scores, key=option_scores.get)
            confidence_level = option_scores[recommended_option]
            
            # Generate warnings for low-confidence decisions
            if confidence_level < 0.6:
                warnings.append("Low confidence in recommendation - consider additional consultation")
            
            # Generate considerations based on decision characteristics
            if decision.reversibility == "irreversible":
                considerations.append("This decision is irreversible - extra caution required")
            
            if decision.time_sensitivity == "immediate":
                considerations.append("Time-critical decision - limited deliberation time available")
            
            if decision.complexity in [DecisionComplexity.COMPLEX, DecisionComplexity.CRITICAL]:
                considerations.append("Complex ethical dimensions - consider expert consultation")
            
            # Recommend consultations for critical decisions
            required_consultations = []
            if decision.complexity == DecisionComplexity.CRITICAL:
                required_consultations.append("Ethics committee review recommended")
            
            if any(s.stakeholder_type == StakeholderType.HEALTHCARE_PROVIDER for s in decision.stakeholders):
                required_consultations.append("Healthcare provider consultation")
            
            # Recommend monitoring for high-impact decisions
            monitoring_requirements = []
            if confidence_level < 0.7:
                monitoring_requirements.append("Enhanced monitoring of decision outcomes")
            
            if decision.complexity == DecisionComplexity.CRITICAL:
                monitoring_requirements.append("Regular review and assessment of decision impact")
            
        else:
            recommended_option = decision.options[0] if decision.options else "No recommendation"
            confidence_level = 0.5
            warnings.append("Unable to evaluate options - default recommendation provided")
        
        # Generate alternative options
        alternative_options = [opt for opt in decision.options if opt != recommended_option]
        
        guidance = EthicalGuidance(
            decision_id=decision_id,
            recommended_option=recommended_option,
            confidence_level=confidence_level,
            ethical_reasoning="; ".join(ethical_reasoning) if ethical_reasoning else "No significant ethical concerns identified",
            considerations=considerations,
            warnings=warnings,
            alternative_options=alternative_options,
            required_consultations=required_consultations,
            monitoring_requirements=monitoring_requirements,
            timestamp=time.time()
        )
        
        self.guidance_history.append(guidance)
        self.logger.info(f"Ethical guidance provided for decision {decision_id}: {recommended_option}")
        
        return guidance
    
    def facilitate_ethical_deliberation(self, decision_id: str, 
                                      participants: List[str]) -> Optional[DeliberationResult]:
        """Facilitate ethical deliberation among stakeholders"""
        decision = self._find_decision(decision_id)
        if not decision:
            return None
        
        # This is a simplified deliberation process
        # In a real implementation, this would involve actual stakeholder input
        
        guidance = self.provide_ethical_guidance(decision_id)
        
        # Simulate consensus-building process
        consensus_reached = True
        dissenting_opinions = []
        
        # If confidence is low, assume some dissent
        if guidance and guidance.confidence_level < 0.6:
            consensus_reached = False
            dissenting_opinions.append("Some participants expressed concerns about the recommendation")
        
        # If decision is critical, assume more careful deliberation
        if decision.complexity == DecisionComplexity.CRITICAL:
            consensus_reached = len(participants) >= 3  # Assume need for multiple perspectives
        
        follow_up_required = not consensus_reached or (guidance and guidance.confidence_level < 0.7)
        
        agreed_monitoring = []
        if guidance:
            agreed_monitoring.extend(guidance.monitoring_requirements)
        
        result = DeliberationResult(
            decision_id=decision_id,
            participants=participants,
            consensus_reached=consensus_reached,
            final_recommendation=guidance.recommended_option if guidance else "No recommendation",
            dissenting_opinions=dissenting_opinions,
            agreed_monitoring=agreed_monitoring,
            follow_up_required=follow_up_required,
            timestamp=time.time()
        )
        
        self.deliberation_history.append(result)
        self.logger.info(f"Ethical deliberation completed for decision {decision_id}")
        
        return result
    
    def document_ethical_reasoning(self, decision_id: str) -> Dict[str, Any]:
        """Document ethical reasoning for accountability"""
        decision = self._find_decision(decision_id)
        guidance = self._find_guidance(decision_id)
        deliberation = self._find_deliberation(decision_id)
        
        if not decision:
            return {"error": "Decision not found"}
        
        dimensions = self.identify_ethical_dimensions(decision_id)
        
        documentation = {
            "decision": asdict(decision),
            "ethical_dimensions": [asdict(d) for d in dimensions],
            "guidance": asdict(guidance) if guidance else None,
            "deliberation": asdict(deliberation) if deliberation else None,
            "documentation_timestamp": time.time(),
            "ethical_framework_version": "1.0"
        }
        
        return documentation
    
    def _find_decision(self, decision_id: str) -> Optional[Decision]:
        """Find decision by ID"""
        for decision in self.decision_history:
            if decision.decision_id == decision_id:
                return decision
        return None
    
    def _find_guidance(self, decision_id: str) -> Optional[EthicalGuidance]:
        """Find guidance by decision ID"""
        for guidance in self.guidance_history:
            if guidance.decision_id == decision_id:
                return guidance
        return None
    
    def _find_deliberation(self, decision_id: str) -> Optional[DeliberationResult]:
        """Find deliberation by decision ID"""
        for deliberation in self.deliberation_history:
            if deliberation.decision_id == decision_id:
                return deliberation
        return None
    
    def _evaluate_option_against_dimension(self, option: str, dimension: EthicalDimension,
                                         decision: Decision) -> float:
        """Evaluate an option against an ethical dimension"""
        # This is a simplified evaluation
        # Real implementation would use more sophisticated analysis
        
        option_lower = option.lower()
        principle_keywords = self.ethical_principles.get(dimension.principle, {}).get("keywords", [])
        
        score = 0.5  # Default neutral score
        
        # Check for positive alignment with principle
        positive_indicators = []
        negative_indicators = []
        
        for keyword in principle_keywords:
            if keyword in option_lower:
                if dimension.principle in ["non_maleficence"] and keyword in ["harm", "damage"]:
                    # For non-maleficence, presence of harm keywords is negative
                    negative_indicators.append(keyword)
                else:
                    positive_indicators.append(keyword)
        
        # Adjust score based on indicators
        if positive_indicators:
            score += 0.3 * len(positive_indicators)
        if negative_indicators:
            score -= 0.4 * len(negative_indicators)
        
        # Consider stakeholder impact
        for stakeholder in decision.stakeholders:
            if stakeholder.stakeholder_type == StakeholderType.PRIMARY_USER:
                # Primary user alignment is important
                if any(interest in option_lower for interest in stakeholder.interests):
                    score += 0.2
        
        return max(0.0, min(1.0, score))
    
    def get_decision_metrics(self) -> Dict[str, Any]:
        """Get metrics about ethical decision-making"""
        total_decisions = len(self.decision_history)
        total_guidance = len(self.guidance_history)
        total_deliberations = len(self.deliberation_history)
        
        if total_guidance > 0:
            avg_confidence = sum(g.confidence_level for g in self.guidance_history) / total_guidance
            high_confidence_decisions = sum(1 for g in self.guidance_history if g.confidence_level >= 0.8)
        else:
            avg_confidence = 0.0
            high_confidence_decisions = 0
        
        complexity_distribution = {}
        for decision in self.decision_history:
            complexity = decision.complexity.value
            complexity_distribution[complexity] = complexity_distribution.get(complexity, 0) + 1
        
        return {
            "total_decisions": total_decisions,
            "total_guidance_provided": total_guidance,
            "total_deliberations": total_deliberations,
            "average_confidence": avg_confidence,
            "high_confidence_rate": high_confidence_decisions / total_guidance if total_guidance > 0 else 0,
            "complexity_distribution": complexity_distribution,
            "guidance_coverage": total_guidance / total_decisions if total_decisions > 0 else 0
        }
    
    def clear_history(self):
        """Clear decision history (for testing purposes)"""
        self.decision_history.clear()
        self.guidance_history.clear()
        self.deliberation_history.clear()
        self.logger.info("Ethical decision history cleared")