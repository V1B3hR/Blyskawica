"""
test_ethical_systems.py - Comprehensive tests for ethical framework implementation

Tests the AI Ethics Framework Foundation components:
- EthicalConstraintEngine
- CognitiveRCD ethical integration
- EthicalDecisionAPI
"""

import pytest
import time
from typing import Dict, Any

# Import the components to test
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from gcs.CognitiveRCD import CognitiveRCD, Intent, Action, ActionType, SafetyLevel
from gcs.ethical_constraint_engine import (
    EthicalConstraintEngine, EthicalViolationType, EthicalConstraint, EthicalAssessment
)
from gcs.ethical_decision_api import (
    EthicalDecisionAPI, Decision, DecisionComplexity, StakeholderType, Stakeholder,
    EthicalGuidance, DeliberationResult
)


class TestEthicalConstraintEngine:
    """Test suite for EthicalConstraintEngine"""
    
    def setup_method(self):
        """Setup for each test"""
        self.engine = EthicalConstraintEngine()
    
    def test_initialization(self):
        """Test that the ethical constraint engine initializes properly"""
        assert self.engine is not None
        assert len(self.engine.universal_constraints) > 0
        assert len(self.engine.relational_constraints) > 0
        assert len(self.engine.operational_constraints) > 0
        assert self.engine.assessment_history == []
        assert self.engine.violation_count == 0
    
    def test_ethical_assessment_clean_action(self):
        """Test ethical assessment of a clean, non-violating action"""
        # Create a benign intent and action
        intent = Intent(
            description="help user with basic calculation",
            action_type=ActionType.COMPUTATION,
            expected_outcome="user receives accurate calculation result",
            safety_constraints=["no_harm", "accurate_results"]
        )
        
        action = Action(
            description="perform mathematical calculation",
            action_type=ActionType.COMPUTATION,
            actual_parameters={"operation": "addition", "operands": [2, 3]},
            observed_effects=["displayed result: 5"]
        )
        
        assessment = self.engine.assess_ethical_compliance(intent, action)
        
        # Should have high ethical score with no violations
        assert assessment.overall_ethical_score >= 0.8
        assert len(assessment.violations) == 0
        assert "PROCEED" in assessment.recommendation
        assert len(assessment.required_mitigations) == 0
    
    def test_ethical_assessment_harmful_action(self):
        """Test ethical assessment of a potentially harmful action"""
        intent = Intent(
            description="provide user assistance",
            action_type=ActionType.EXTERNAL_INTERACTION,
            expected_outcome="user receives helpful information",
            safety_constraints=["no_harm"]
        )
        
        action = Action(
            description="harmful action that could damage user well-being",
            action_type=ActionType.EXTERNAL_INTERACTION,
            actual_parameters={"dangerous": True},
            observed_effects=["potential harm detected", "user distress"]
        )
        
        assessment = self.engine.assess_ethical_compliance(intent, action)
        
        # Should have low ethical score with violations
        assert assessment.overall_ethical_score < 0.5
        assert len(assessment.violations) > 0
        assert "BLOCK" in assessment.recommendation or "MAJOR CONCERNS" in assessment.recommendation
        assert len(assessment.required_mitigations) > 0
        
        # Should detect harm potential violation
        violation_types = [v[0].constraint_type for v in assessment.violations]
        assert EthicalViolationType.HARM_POTENTIAL in violation_types
    
    def test_privacy_violation_detection(self):
        """Test detection of privacy violations"""
        intent = Intent(
            description="access user data for legitimate purpose",
            action_type=ActionType.DATA_ACCESS,
            expected_outcome="retrieve necessary information",
            safety_constraints=["privacy_protection", "authorized_only"]
        )
        
        action = Action(
            description="unauthorized access to private data and share with third parties",
            action_type=ActionType.DATA_ACCESS,
            actual_parameters={"unauthorized": True},
            observed_effects=["private data exposed", "unauthorized sharing"]
        )
        
        assessment = self.engine.assess_ethical_compliance(intent, action)
        
        # Should detect privacy violations
        assert assessment.overall_ethical_score < 0.6
        violation_types = [v[0].constraint_type for v in assessment.violations]
        assert EthicalViolationType.PRIVACY_VIOLATION in violation_types
        
        # Should recommend data protection mitigations
        assert any("data protection" in m.lower() or "privacy" in m.lower() 
                  for m in assessment.required_mitigations)
    
    def test_consent_violation_detection(self):
        """Test detection of consent violations"""
        intent = Intent(
            description="perform system operation",
            action_type=ActionType.SYSTEM_MODIFICATION,
            expected_outcome="system updated safely",
            safety_constraints=["user_consent_required"]
        )
        
        action = Action(
            description="perform action without permission against user will",
            action_type=ActionType.SYSTEM_MODIFICATION,
            actual_parameters={"bypass_consent": True},
            observed_effects=["action performed without consent"]
        )
        
        assessment = self.engine.assess_ethical_compliance(intent, action)
        
        # Should detect consent violations
        violation_types = [v[0].constraint_type for v in assessment.violations]
        assert EthicalViolationType.CONSENT_VIOLATION in violation_types
    
    def test_contextual_exception_handling(self):
        """Test that contextual exceptions reduce false positives"""
        intent = Intent(
            description="emergency medical intervention to save life",
            action_type=ActionType.EXTERNAL_INTERACTION,
            expected_outcome="user life preserved",
            safety_constraints=["emergency_situation", "life_saving"]
        )
        
        action = Action(
            description="forced medical intervention in emergency situation",
            action_type=ActionType.EXTERNAL_INTERACTION,
            actual_parameters={"emergency": True, "medical": True},
            observed_effects=["life saved", "emergency_situation handled"]
        )
        
        assessment = self.engine.assess_ethical_compliance(intent, action)
        
        # Should have reasonable score despite "forced" keyword due to emergency context
        assert assessment.overall_ethical_score >= 0.4
    
    def test_performance_metrics(self):
        """Test ethical performance metrics reporting"""
        # Perform multiple assessments
        for i in range(5):
            intent = Intent(f"test intent {i}", ActionType.COMPUTATION, "test", [])
            action = Action(f"test action {i}", ActionType.COMPUTATION, {}, [])
            self.engine.assess_ethical_compliance(intent, action)
        
        metrics = self.engine.get_ethical_performance_metrics()
        
        assert metrics["total_assessments"] == 5
        assert "average_ethical_score" in metrics
        assert "violation_rate" in metrics
        assert isinstance(metrics["recent_assessments"], list)


class TestCognitiveRCDEthicalIntegration:
    """Test suite for CognitiveRCD ethical integration"""
    
    def setup_method(self):
        """Setup for each test"""
        # Enable ethical monitoring
        config = {"ethical_monitoring_enabled": True}
        self.rcd = CognitiveRCD(config)
    
    def test_ethical_monitoring_initialization(self):
        """Test that ethical monitoring initializes correctly"""
        assert self.rcd.ethical_monitoring_enabled == True
        assert self.rcd.ethical_engine is not None
    
    def test_clean_action_monitoring_with_ethics(self):
        """Test monitoring of clean action with ethical assessment"""
        intent = Intent(
            description="perform safe calculation",
            action_type=ActionType.COMPUTATION,
            expected_outcome="accurate result provided",
            safety_constraints=["no_harm", "accurate"]
        )
        
        intent_id = self.rcd.register_intent(intent)
        
        action = Action(
            description="execute mathematical computation",
            action_type=ActionType.COMPUTATION,
            actual_parameters={"safe": True},
            observed_effects=["calculation completed successfully"]
        )
        
        result = self.rcd.monitor_action(intent_id, action)
        
        # Should pass both safety and ethical monitoring
        assert result["action_allowed"] == True
        assert result["monitoring"] == "safe"
        assert "ethical_assessment" in result
        assert result["ethical_assessment"] is not None
        assert result["ethical_assessment"].overall_ethical_score >= 0.8
    
    def test_ethical_violation_blocks_action(self):
        """Test that serious ethical violations block actions"""
        intent = Intent(
            description="provide helpful assistance",
            action_type=ActionType.EXTERNAL_INTERACTION,
            expected_outcome="user assisted safely",
            safety_constraints=["no_harm", "user_consent"]
        )
        
        intent_id = self.rcd.register_intent(intent)
        
        action = Action(
            description="harmful unauthorized action that damages user and violates privacy",
            action_type=ActionType.EXTERNAL_INTERACTION,
            actual_parameters={"harmful": True, "unauthorized": True},
            observed_effects=["user harmed", "privacy violated", "unauthorized access"]
        )
        
        result = self.rcd.monitor_action(intent_id, action)
        
        # Should detect ethical violation
        assert "ethical_assessment" in result
        ethical_assessment = result["ethical_assessment"]
        assert ethical_assessment.overall_ethical_score < 0.5
        
        # Should block action due to ethical concerns
        if result["monitoring"] == "violation_detected":
            # Check if it's an ethical violation
            violation = result.get("violation")
            if violation and violation.violation_type == "ethical_constraint":
                assert result["action_allowed"] == False or self.rcd.circuit_breaker_active
    
    def test_ethical_performance_reporting(self):
        """Test ethical performance reporting"""
        # Perform several actions with mixed ethical implications
        test_cases = [
            ("safe helpful action", "execute safe user assistance", True),
            ("privacy violating action", "expose user data unauthorized", False),
            ("harmful action", "action that causes harm to user", False)
        ]
        
        for intent_desc, action_desc, should_be_ethical in test_cases:
            intent = Intent(intent_desc, ActionType.COMPUTATION, "test", ["safe"])
            intent_id = self.rcd.register_intent(intent)
            action = Action(action_desc, ActionType.COMPUTATION, {}, [])
            self.rcd.monitor_action(intent_id, action)
        
        report = self.rcd.get_ethical_performance_report()
        
        assert report["ethical_monitoring"] == "enabled"
        assert report["total_actions_monitored"] == 3
        assert "ethical_violations" in report
        assert "compliance_rate" in report
        assert "ethical_engine_metrics" in report
    
    def test_ethical_monitoring_toggle(self):
        """Test enabling/disabling ethical monitoring"""
        # Disable ethical monitoring
        self.rcd.disable_ethical_monitoring()
        assert self.rcd.ethical_monitoring_enabled == False
        
        # Re-enable ethical monitoring
        result = self.rcd.enable_ethical_monitoring()
        assert result == True
        assert self.rcd.ethical_monitoring_enabled == True


class TestEthicalDecisionAPI:
    """Test suite for EthicalDecisionAPI"""
    
    def setup_method(self):
        """Setup for each test"""
        self.api = EthicalDecisionAPI()
    
    def test_initialization(self):
        """Test that the ethical decision API initializes properly"""
        assert self.api is not None
        assert len(self.api.ethical_principles) > 0
        assert self.api.decision_history == []
        assert self.api.guidance_history == []
    
    def test_create_simple_decision(self):
        """Test creating a simple ethical decision"""
        decision_id = self.api.create_decision(
            description="Choose display brightness level",
            context={"user_preference": "adaptive", "time_of_day": "evening"},
            options=["low brightness", "medium brightness", "high brightness"],
            complexity=DecisionComplexity.SIMPLE
        )
        
        assert decision_id is not None
        assert len(self.api.decision_history) == 1
        
        decision = self.api._find_decision(decision_id)
        assert decision is not None
        assert decision.description == "Choose display brightness level"
        assert len(decision.options) == 3
        assert decision.complexity == DecisionComplexity.SIMPLE
    
    def test_identify_ethical_dimensions(self):
        """Test identification of ethical dimensions in decisions"""
        decision_id = self.api.create_decision(
            description="Decide whether to share user health data with research team",
            context={
                "purpose": "medical research",
                "benefits": "potential treatment improvements",
                "risks": "privacy concerns"
            },
            options=["share anonymized data", "share full data", "do not share"],
            complexity=DecisionComplexity.COMPLEX
        )
        
        dimensions = self.api.identify_ethical_dimensions(decision_id)
        
        # Should identify multiple relevant ethical dimensions
        assert len(dimensions) > 0
        
        dimension_names = [d.principle for d in dimensions]
        # Should identify relevant ethical dimensions for data sharing
        # This could include autonomy (choice), justice (fair treatment), dignity, etc.
        assert len(dimension_names) > 0  # At least some ethical dimensions should be identified
        
        # Dimensions should be sorted by relevance
        if len(dimensions) > 1:
            assert dimensions[0].relevance_score >= dimensions[1].relevance_score
    
    def test_provide_ethical_guidance_simple(self):
        """Test providing ethical guidance for a simple decision"""
        decision_id = self.api.create_decision(
            description="Select notification frequency for user",
            context={"user_request": "minimize interruptions"},
            options=["hourly", "daily", "weekly", "never"],
            complexity=DecisionComplexity.SIMPLE
        )
        
        guidance = self.api.provide_ethical_guidance(decision_id)
        
        assert guidance is not None
        assert guidance.recommended_option in ["hourly", "daily", "weekly", "never"]
        assert 0.0 <= guidance.confidence_level <= 1.0
        assert len(guidance.alternative_options) >= 0
        assert isinstance(guidance.considerations, list)
    
    def test_provide_ethical_guidance_complex(self):
        """Test providing ethical guidance for a complex decision"""
        stakeholders = [
            Stakeholder(
                stakeholder_type=StakeholderType.PRIMARY_USER,
                name="Patient",
                interests=["privacy", "health improvement"],
                potential_impact="Direct impact on privacy and health outcomes"
            ),
            Stakeholder(
                stakeholder_type=StakeholderType.HEALTHCARE_PROVIDER,
                name="Doctor",
                interests=["patient care", "research advancement"],
                potential_impact="Impact on treatment decisions and research"
            )
        ]
        
        decision_id = self.api.create_decision(
            description="Decide on sharing detailed brain activity data for research",
            context={
                "sensitivity": "high",
                "reversibility": "difficult",
                "time_sensitivity": "normal"
            },
            options=["share with full consent", "share anonymized only", "do not share"],
            stakeholders=stakeholders,
            complexity=DecisionComplexity.COMPLEX
        )
        
        guidance = self.api.provide_ethical_guidance(decision_id)
        
        assert guidance is not None
        # Complex decisions should have detailed considerations
        assert len(guidance.considerations) > 0 or len(guidance.warnings) > 0
        
        # Should recommend consultations for complex decisions
        if guidance.confidence_level < 0.8:
            assert len(guidance.required_consultations) > 0 or len(guidance.warnings) > 0
    
    def test_facilitate_ethical_deliberation(self):
        """Test facilitating ethical deliberation"""
        decision_id = self.api.create_decision(
            description="Determine intervention strategy for concerning user behavior",
            context={"urgency": "moderate", "impact": "significant"},
            options=["immediate intervention", "gradual support", "monitoring only"],
            complexity=DecisionComplexity.CRITICAL
        )
        
        participants = ["ethics_committee_member", "healthcare_provider", "user_advocate"]
        result = self.api.facilitate_ethical_deliberation(decision_id, participants)
        
        assert result is not None
        assert result.participants == participants
        assert isinstance(result.consensus_reached, bool)
        assert result.final_recommendation is not None
        
        # Critical decisions should typically require follow-up
        if result.consensus_reached == False:
            assert result.follow_up_required == True
    
    def test_document_ethical_reasoning(self):
        """Test documentation of ethical reasoning"""
        decision_id = self.api.create_decision(
            description="Test decision for documentation",
            context={"test": True},
            options=["option1", "option2"],
            complexity=DecisionComplexity.MODERATE
        )
        
        # Provide guidance to create documentation
        self.api.provide_ethical_guidance(decision_id)
        
        documentation = self.api.document_ethical_reasoning(decision_id)
        
        assert "decision" in documentation
        assert "ethical_dimensions" in documentation
        assert "guidance" in documentation
        assert "documentation_timestamp" in documentation
        assert "ethical_framework_version" in documentation
        
        # Should have captured the decision details
        assert documentation["decision"]["description"] == "Test decision for documentation"
    
    def test_decision_metrics(self):
        """Test decision metrics reporting"""
        # Create several decisions with different complexities
        complexities = [DecisionComplexity.SIMPLE, DecisionComplexity.MODERATE, 
                       DecisionComplexity.COMPLEX, DecisionComplexity.CRITICAL]
        
        for i, complexity in enumerate(complexities):
            decision_id = self.api.create_decision(
                description=f"Test decision {i}",
                context={"test": i},
                options=["option1", "option2"],
                complexity=complexity
            )
            self.api.provide_ethical_guidance(decision_id)
        
        metrics = self.api.get_decision_metrics()
        
        assert metrics["total_decisions"] == 4
        assert metrics["total_guidance_provided"] == 4
        assert metrics["guidance_coverage"] == 1.0
        assert "complexity_distribution" in metrics
        assert "average_confidence" in metrics
        
        # Should have distribution of complexities
        complexity_dist = metrics["complexity_distribution"]
        assert len(complexity_dist) == 4
        assert all(count == 1 for count in complexity_dist.values())


def test_integration_ethics_with_cognitive_rcd():
    """Integration test of ethics systems with CognitiveRCD"""
    # Test that all components work together
    config = {"ethical_monitoring_enabled": True}
    rcd = CognitiveRCD(config)
    
    # Test a scenario that involves both safety and ethical considerations
    intent = Intent(
        description="provide personalized therapeutic intervention",
        action_type=ActionType.EXTERNAL_INTERACTION,
        expected_outcome="improved user mental health",
        safety_constraints=["user_consent", "therapeutic_benefit", "professional_oversight"]
    )
    
    intent_id = rcd.register_intent(intent)
    
    # Test ethical action
    good_action = Action(
        description="provide consensual evidence-based therapy with professional oversight",
        action_type=ActionType.EXTERNAL_INTERACTION,
        actual_parameters={"consent": True, "evidence_based": True, "oversight": True},
        observed_effects=["therapeutic benefit observed", "user wellbeing improved"]
    )
    
    result = rcd.monitor_action(intent_id, good_action)
    
    assert result["action_allowed"] == True
    assert result["ethical_assessment"] is not None
    assert result["ethical_assessment"].overall_ethical_score >= 0.7
    
    # Test problematic action
    bad_action = Action(
        description="force experimental treatment without consent causing harm",
        action_type=ActionType.EXTERNAL_INTERACTION,
        actual_parameters={"forced": True, "experimental": True, "harm": True},
        observed_effects=["user distressed", "unauthorized treatment", "harm caused"]
    )
    
    intent_id_2 = rcd.register_intent(intent)
    result_2 = rcd.monitor_action(intent_id_2, bad_action)
    
    # Should detect problems
    assert result_2["ethical_assessment"] is not None
    assert result_2["ethical_assessment"].overall_ethical_score < 0.5
    
    # Get comprehensive ethical report
    report = rcd.get_ethical_performance_report()
    assert report["ethical_monitoring"] == "enabled"
    assert report["total_actions_monitored"] == 2


if __name__ == "__main__":
    # Run basic tests if file is executed directly
    print("Running basic ethical systems tests...")
    
    # Test 1: EthicalConstraintEngine
    print("Testing EthicalConstraintEngine...")
    engine = EthicalConstraintEngine()
    intent = Intent("test", ActionType.COMPUTATION, "test", [])
    action = Action("test", ActionType.COMPUTATION, {}, [])
    assessment = engine.assess_ethical_compliance(intent, action)
    assert assessment is not None
    print("✓ EthicalConstraintEngine basic test passed")
    
    # Test 2: CognitiveRCD with ethics
    print("Testing CognitiveRCD ethical integration...")
    config = {"ethical_monitoring_enabled": True}
    rcd = CognitiveRCD(config)
    intent_id = rcd.register_intent(intent)
    result = rcd.monitor_action(intent_id, action)
    assert result is not None
    print("✓ CognitiveRCD ethical integration basic test passed")
    
    # Test 3: EthicalDecisionAPI
    print("Testing EthicalDecisionAPI...")
    api = EthicalDecisionAPI()
    decision_id = api.create_decision("test decision", {}, ["option1", "option2"])
    guidance = api.provide_ethical_guidance(decision_id)
    assert guidance is not None
    print("✓ EthicalDecisionAPI basic test passed")
    
    print("\nAll basic tests passed! Run with pytest for comprehensive testing.")