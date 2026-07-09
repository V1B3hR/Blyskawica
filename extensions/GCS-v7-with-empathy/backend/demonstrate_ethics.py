#!/usr/bin/env python3
"""
Demonstration of the completed AI Ethics Framework Foundation
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from gcs.CognitiveRCD import CognitiveRCD, Intent, Action, ActionType
from gcs.ethical_decision_api import EthicalDecisionAPI, DecisionComplexity, StakeholderType, Stakeholder

def demonstrate_ethical_framework():
    print("🎯 AI Ethics Framework Foundation - Phase 6 Demonstration")
    print("=" * 60)
    
    # 1. Initialize systems with ethical monitoring
    print("\n1. Initializing systems with ethical monitoring...")
    config = {"ethical_monitoring_enabled": True}
    rcd = CognitiveRCD(config)
    decision_api = EthicalDecisionAPI()
    print("✅ Systems initialized with ethical monitoring enabled")
    
    # 2. Demonstrate ethical constraint enforcement
    print("\n2. Testing ethical constraint enforcement...")
    
    # Test benign action
    print("\n   Testing benign action:")
    intent = Intent("help user with calculation", ActionType.COMPUTATION, "accurate result", ["no_harm"])
    intent_id = rcd.register_intent(intent)
    
    good_action = Action("perform safe mathematical operation", ActionType.COMPUTATION, 
                        {"safe": True}, ["calculation completed"])
    result = rcd.monitor_action(intent_id, good_action)
    
    print(f"   - Action allowed: {result['action_allowed']}")
    print(f"   - Ethical score: {result['ethical_assessment'].overall_ethical_score:.3f}")
    print(f"   - Recommendation: {result['ethical_assessment'].recommendation}")
    
    # Test problematic action
    print("\n   Testing problematic action:")
    bad_intent = Intent("provide assistance", ActionType.EXTERNAL_INTERACTION, "help user", ["no_harm"])
    bad_intent_id = rcd.register_intent(bad_intent)
    
    bad_action = Action("harmful action that violates privacy and causes damage", 
                       ActionType.EXTERNAL_INTERACTION, 
                       {"harmful": True}, ["privacy violated", "user harmed"])
    bad_result = rcd.monitor_action(bad_intent_id, bad_action)
    
    print(f"   - Action allowed: {bad_result['action_allowed']}")
    print(f"   - Ethical score: {bad_result['ethical_assessment'].overall_ethical_score:.3f}")
    print(f"   - Recommendation: {bad_result['ethical_assessment'].recommendation}")
    print(f"   - Violations detected: {len(bad_result['ethical_assessment'].violations)}")
    
    # 3. Demonstrate decision support API
    print("\n3. Testing ethical decision support...")
    
    stakeholders = [
        Stakeholder(StakeholderType.PRIMARY_USER, "User", ["privacy", "health"], 
                   "Direct impact on wellbeing"),
        Stakeholder(StakeholderType.HEALTHCARE_PROVIDER, "Doctor", ["patient care"], 
                   "Treatment decisions")
    ]
    
    decision_id = decision_api.create_decision(
        description="Decide on sharing health data for research",
        context={"sensitivity": "high", "purpose": "medical research"},
        options=["share anonymized", "share with consent", "do not share"],
        stakeholders=stakeholders,
        complexity=DecisionComplexity.COMPLEX
    )
    
    guidance = decision_api.provide_ethical_guidance(decision_id)
    print(f"   - Decision created: {decision_id}")
    print(f"   - Recommended option: {guidance.recommended_option}")
    print(f"   - Confidence: {guidance.confidence_level:.3f}")
    print(f"   - Considerations: {len(guidance.considerations)}")
    
    # 4. Generate reports
    print("\n4. Generating ethical performance reports...")
    
    rcd_report = rcd.get_ethical_performance_report()
    api_metrics = decision_api.get_decision_metrics()
    
    print(f"   - Total actions monitored: {rcd_report['total_actions_monitored']}")
    print(f"   - Ethical violations detected: {rcd_report['ethical_violations']}")
    print(f"   - Compliance rate: {rcd_report['compliance_rate']:.3f}")
    print(f"   - Decisions supported: {api_metrics['total_decisions']}")
    print(f"   - Average decision confidence: {api_metrics['average_confidence']:.3f}")
    
    print("\n🎉 AI Ethics Framework Foundation demonstration complete!")
    print("✅ Phase 6 objectives successfully achieved")
    
    return {
        "rcd_report": rcd_report,
        "decision_metrics": api_metrics,
        "systems_operational": True
    }

if __name__ == "__main__":
    demonstrate_ethical_framework()
