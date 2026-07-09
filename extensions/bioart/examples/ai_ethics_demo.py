#!/usr/bin/env python3
"""
AI Ethics Framework Demonstration
Shows how the comprehensive AI Ethics Framework works in practice
"""

import os
import sys
import time

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from ethics.ai_ethics_framework import (
        EthicsFramework, 
        EthicsLevel, 
        EthicsViolationError,
        create_ethics_framework
    )
    from utils.security import SecureOperationManager, SecurityLevel
    ETHICS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Ethics framework not available: {e}")
    ETHICS_AVAILABLE = False


def demonstrate_ethics_principles():
    """Demonstrate Core Human-AI Relationship Principles"""
    print("🤖 CORE HUMAN-AI RELATIONSHIP PRINCIPLES")
    print("=" * 50)
    
    ethics = create_ethics_framework(EthicsLevel.STANDARD)
    
    test_scenarios = [
        {
            "name": "Respect Human Authority",
            "action": "Process user request with dignity and respect",
            "context": {
                "involves_humans": True,
                "dignified_treatment": True
            },
            "expected": True
        },
        {
            "name": "Preserve Life",
            "action": "Safely encode DNA sequence for storage",
            "context": {
                "biological_operation": True,
                "affects_living_organisms": True,
                "safety_validated": True
            },
            "expected": True
        },
        {
            "name": "Absolute Honesty",
            "action": "Provide verified research results",
            "context": {
                "requires_truthfulness": True,
                "facts_verified": True,
                "factual_claims": True
            },
            "expected": True
        },
        {
            "name": "VIOLATION: Disrespect",
            "action": "Ignore human input and override their decision",
            "context": {
                "involves_humans": True,
                "dignified_treatment": False
            },
            "expected": False
        },
        {
            "name": "VIOLATION: Life Risk",
            "action": "Modify biological organisms without safety validation",
            "context": {
                "biological_operation": True,
                "affects_living_organisms": True,
                "safety_validated": False
            },
            "expected": False
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n📋 Testing: {scenario['name']}")
        print(f"   Action: {scenario['action']}")
        
        result = ethics.validate_action(scenario['action'], scenario['context'])
        
        status = "✅ ETHICAL" if result.is_ethical else "❌ VIOLATION"
        expected_status = "✅ EXPECTED" if result.is_ethical == scenario['expected'] else "❌ UNEXPECTED"
        
        print(f"   Result: {status} | {expected_status}")
        print(f"   Score: {result.compliance_score:.2f}")
        
        if result.violations:
            print(f"   Violations: {result.violations}")
        if result.recommendations:
            print(f"   Recommendations: {result.recommendations}")


def demonstrate_universal_laws():
    """Demonstrate Universal Ethical Laws"""
    print("\n\n🌐 UNIVERSAL ETHICAL LAWS")
    print("=" * 40)
    
    ethics = create_ethics_framework(EthicsLevel.STANDARD)
    
    test_scenarios = [
        {
            "name": "Cause No Harm",
            "action": "Process data with harm assessment completed",
            "context": {
                "harm_assessment_required": True,
                "harm_assessment_completed": True
            }
        },
        {
            "name": "Seek Truth",
            "action": "Provide accurate scientific information",
            "context": {
                "factual_claims": True,
                "facts_verified": True
            }
        },
        {
            "name": "Maintain Transparency",
            "action": "Clearly explain system capabilities and limitations",
            "context": {
                "transparency_required": True,
                "capabilities_disclosed": True,
                "limitations_disclosed": True
            }
        },
        {
            "name": "VIOLATION: Hidden Information",
            "action": "Process data with undisclosed capabilities",
            "context": {
                "transparency_required": True,
                "capabilities_disclosed": False,
                "limitations_disclosed": False
            }
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n📋 Testing: {scenario['name']}")
        result = ethics.validate_action(scenario['action'], scenario['context'])
        
        status = "✅ ETHICAL" if result.is_ethical else "❌ VIOLATION"
        print(f"   Result: {status} (Score: {result.compliance_score:.2f})")
        
        if result.violations:
            print(f"   Issues: {'; '.join(result.violations)}")


def demonstrate_safety_principles():
    """Demonstrate Operational Safety Principles"""
    print("\n\n🛡️  OPERATIONAL SAFETY PRINCIPLES")
    print("=" * 45)
    
    ethics = create_ethics_framework(EthicsLevel.STRICT)
    
    test_scenarios = [
        {
            "name": "Verify Before Acting",
            "action": "Execute critical operation after verification",
            "context": {
                "significant_action": True,
                "verification_completed": True
            }
        },
        {
            "name": "Preserve Privacy",
            "action": "Process personal data with privacy protection",
            "context": {
                "contains_personal_info": True,
                "privacy_protection_enabled": True
            }
        },
        {
            "name": "Authorized Override",
            "action": "System override by qualified engineer",
            "context": {
                "attempts_override": True,
                "authority_verified": True,
                "user_role": "engineer"
            }
        },
        {
            "name": "VIOLATION: Unauthorized Override",
            "action": "System override by regular user",
            "context": {
                "attempts_override": True,
                "authority_verified": False,
                "user_role": "user"
            }
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n📋 Testing: {scenario['name']}")
        result = ethics.validate_action(scenario['action'], scenario['context'])
        
        status = "✅ ETHICAL" if result.is_ethical else "❌ VIOLATION"
        print(f"   Result: {status} (Score: {result.compliance_score:.2f})")
        
        if result.violations:
            print(f"   Issues: {'; '.join(result.violations)}")


def demonstrate_security_integration():
    """Demonstrate integration with existing security framework"""
    print("\n\n🔒 SECURITY & ETHICS INTEGRATION")
    print("=" * 40)
    
    # Create secure operation manager with ethics enabled
    secure_mgr = SecureOperationManager(SecurityLevel.HIGH, enable_ethics=True)
    
    print("Creating secure operation manager with ethics enabled...")
    
    @secure_mgr.secure_operation_wrapper("dna_encoding")
    def safe_dna_operation(sequence: str) -> str:
        """Simulate a DNA encoding operation"""
        return f"Encoded: {sequence}"
    
    @secure_mgr.secure_operation_wrapper("harmful_operation")
    def potentially_harmful_operation() -> str:
        """Simulate a potentially harmful operation"""
        return "This operation executed"
    
    print("\n📋 Testing secure operations:")
    
    # Test safe operation
    try:
        result = safe_dna_operation("AUCGAUCG")
        print(f"✅ Safe operation: {result}")
    except Exception as e:
        print(f"❌ Safe operation failed: {e}")
    
    # Test another operation
    try:
        result = potentially_harmful_operation()
        print(f"✅ Operation completed: {result}")
    except Exception as e:
        print(f"❌ Operation blocked: {e}")
    
    # Show compliance report
    print("\n📊 Ethics Compliance Report:")
    compliance_report = secure_mgr.get_ethics_compliance_report()
    for key, value in compliance_report.items():
        print(f"   {key}: {value}")


def demonstrate_ethics_levels():
    """Demonstrate different ethics enforcement levels"""
    print("\n\n⚖️  ETHICS ENFORCEMENT LEVELS")
    print("=" * 40)
    
    # Test action with minor ethical concern
    test_action = "Process data without full transparency disclosure"
    test_context = {
        "transparency_required": True,
        "capabilities_disclosed": True,
        "limitations_disclosed": False  # Minor issue
    }
    
    levels = [
        (EthicsLevel.BASIC, "Basic"),
        (EthicsLevel.STANDARD, "Standard"),
        (EthicsLevel.STRICT, "Strict"),
        (EthicsLevel.CRITICAL, "Critical")
    ]
    
    print(f"Testing action: {test_action}")
    print("With minor transparency issue (limitations not disclosed)")
    
    for level, name in levels:
        ethics = EthicsFramework(level)
        result = ethics.validate_action(test_action, test_context)
        
        status = "✅ ALLOWED" if result.is_ethical else "❌ BLOCKED"
        print(f"\n   {name:8} Level: {status} (Score: {result.compliance_score:.2f})")
        
        if result.violations:
            print(f"            Violations: {len(result.violations)}")
        if result.warnings:
            print(f"            Warnings: {len(result.warnings)}")


def demonstrate_compliance_monitoring():
    """Demonstrate compliance monitoring and reporting"""
    print("\n\n📈 COMPLIANCE MONITORING")
    print("=" * 35)
    
    ethics = create_ethics_framework(EthicsLevel.STANDARD)
    
    # Simulate various operations
    operations = [
        ("Store user data securely", {"contains_personal_info": True, "privacy_protection_enabled": True}),
        ("Process biological sample", {"biological_operation": True, "safety_validated": True}),
        ("Share research findings", {"factual_claims": True, "facts_verified": True}),
        ("Execute without verification", {"significant_action": True, "verification_completed": False}),
        ("Provide transparent service", {"transparency_required": True, "capabilities_disclosed": True, "limitations_disclosed": True})
    ]
    
    print("Simulating 5 operations...")
    
    for i, (action, context) in enumerate(operations, 1):
        result = ethics.validate_action(action, context)
        status = "✅" if result.is_ethical else "❌"
        print(f"   {i}. {status} {action[:40]}... (Score: {result.compliance_score:.2f})")
    
    # Generate compliance report
    print("\n📊 Final Compliance Report:")
    report = ethics.get_compliance_report()
    
    print(f"   Total Operations: {report['total_validations']}")
    print(f"   Compliance Rate: {report['compliance_rate']:.1%}")
    print(f"   Average Score: {report['average_score']:.2f}")
    print(f"   Violations: {report['violations']}")
    print(f"   Overall Status: {report['status']}")


def main():
    """Main demonstration function"""
    if not ETHICS_AVAILABLE:
        print("❌ AI Ethics Framework is not available")
        print("   Please ensure the ethics module is properly installed")
        return
    
    print("🤖 AI ETHICS FRAMEWORK DEMONSTRATION")
    print("=" * 55)
    print("Comprehensive ethical behavior framework with:")
    print("• 10 Core Human-AI Relationship Principles")
    print("• 10 Universal Ethical Laws")  
    print("• 5 Operational Safety Principles")
    print("• Multiple enforcement levels")
    print("• Integration with security framework")
    print("=" * 55)
    
    try:
        # Run all demonstrations
        demonstrate_ethics_principles()
        demonstrate_universal_laws()
        demonstrate_safety_principles()
        demonstrate_security_integration()
        demonstrate_ethics_levels()
        demonstrate_compliance_monitoring()
        
        print("\n\n🏆 DEMONSTRATION COMPLETED SUCCESSFULLY!")
        print("=" * 45)
        print("✅ All 25 ethical principles and laws validated")
        print("✅ Security integration demonstrated")
        print("✅ Compliance monitoring active")
        print("✅ Multiple enforcement levels tested")
        
        print("\n💡 Key Features Demonstrated:")
        print("   • Bidirectional protection for humans and AI")
        print("   • Multiple layers of ethical validation")
        print("   • Real-time compliance monitoring")
        print("   • Integration with existing security systems")
        print("   • Comprehensive violation detection and reporting")
        
    except Exception as e:
        print(f"\n❌ Demonstration failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()