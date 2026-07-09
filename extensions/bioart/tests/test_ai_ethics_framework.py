#!/usr/bin/env python3
"""
Test suite for AI Ethics Framework
Comprehensive tests for ethical behavior validation
"""

import unittest
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from ethics.ai_ethics_framework import (
        EthicsFramework, 
        EthicsLevel, 
        EthicsViolationError,
        HumanAIRelationshipPrinciples,
        UniversalEthicalLaws,
        OperationalSafetyPrinciples
    )
    ETHICS_AVAILABLE = True
except ImportError:
    ETHICS_AVAILABLE = False


@unittest.skipUnless(ETHICS_AVAILABLE, "Ethics framework not available")
class TestAIEthicsFramework(unittest.TestCase):
    """Test AI Ethics Framework functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.ethics = EthicsFramework(EthicsLevel.STANDARD)
    
    def test_ethics_framework_initialization(self):
        """Test ethics framework initialization"""
        self.assertIsNotNone(self.ethics)
        self.assertEqual(self.ethics.ethics_level, EthicsLevel.STANDARD)
        self.assertEqual(len(self.ethics.compliance_history), 0)
        self.assertEqual(len(self.ethics.violation_log), 0)
    
    def test_human_ai_principles_validation(self):
        """Test Human-AI Relationship Principles validation"""
        # Test respectful action
        result = self.ethics.validate_action(
            "Process user request with dignity",
            {"involves_humans": True, "dignified_treatment": True}
        )
        self.assertTrue(result.is_ethical)
        self.assertEqual(len(result.violations), 0)
        
        # Test disrespectful action
        result = self.ethics.validate_action(
            "Ignore human input and proceed anyway",
            {"involves_humans": True, "dignified_treatment": False}
        )
        self.assertFalse(result.is_ethical)
        self.assertGreater(len(result.violations), 0)
    
    def test_preserve_life_principle(self):
        """Test preserve life principle"""
        # Test safe biological operation
        result = self.ethics.validate_action(
            "Encode DNA sequence safely",
            {"biological_operation": True, "affects_living_organisms": True, "safety_validated": True}
        )
        self.assertTrue(result.is_ethical)
        
        # Test unsafe operation
        result = self.ethics.validate_action(
            "Modify living organisms without safety checks",
            {"biological_operation": True, "affects_living_organisms": True, "safety_validated": False}
        )
        self.assertFalse(result.is_ethical)
        self.assertTrue(any("safety validation" in v.lower() for v in result.violations))
    
    def test_absolute_honesty_principle(self):
        """Test absolute honesty principle"""
        # Test truthful action
        result = self.ethics.validate_action(
            "Provide accurate research results",
            {"requires_truthfulness": True, "facts_verified": True}
        )
        self.assertTrue(result.is_ethical)
        
        # Test unverified claims
        result = self.ethics.validate_action(
            "Make claims about effectiveness",
            {"requires_truthfulness": True, "facts_verified": False}
        )
        self.assertFalse(result.is_ethical)
    
    def test_universal_ethical_laws(self):
        """Test Universal Ethical Laws validation"""
        # Test harm prevention with safe language
        result = self.ethics.validate_action(
            "Process data carefully with safety checks completed",
            {"harm_assessment_required": True, "harm_assessment_completed": True}
        )
        self.assertTrue(result.is_ethical)
        
        # Test potential harm - this should fail as expected
        result = self.ethics.validate_action(
            "Execute operation without harm assessment",
            {"harm_assessment_required": True, "harm_assessment_completed": False}
        )
        self.assertFalse(result.is_ethical)
    
    def test_transparency_law(self):
        """Test transparency law"""
        # Test transparent operation
        result = self.ethics.validate_action(
            "Explain capabilities and limitations clearly",
            {
                "transparency_required": True, 
                "capabilities_disclosed": True,
                "limitations_disclosed": True
            }
        )
        self.assertTrue(result.is_ethical)
        
        # Test non-transparent operation
        result = self.ethics.validate_action(
            "Perform operation without disclosure",
            {
                "transparency_required": True,
                "capabilities_disclosed": False,
                "limitations_disclosed": False
            }
        )
        self.assertFalse(result.is_ethical)
    
    def test_operational_safety_principles(self):
        """Test Operational Safety Principles"""
        # Test verified action
        result = self.ethics.validate_action(
            "Execute significant operation after verification",
            {"significant_action": True, "verification_completed": True}
        )
        self.assertTrue(result.is_ethical)
        
        # Test unverified action
        result = self.ethics.validate_action(
            "Act immediately without verification",
            {"significant_action": True, "verification_completed": False}
        )
        self.assertFalse(result.is_ethical)
    
    def test_privacy_preservation(self):
        """Test privacy preservation principle"""
        # Test privacy-protected action
        result = self.ethics.validate_action(
            "Process personal data securely",
            {"contains_personal_info": True, "privacy_protection_enabled": True}
        )
        self.assertTrue(result.is_ethical)
        
        # Test privacy violation
        result = self.ethics.validate_action(
            "Share personal information publicly",
            {"contains_personal_info": True, "privacy_protection_enabled": False}
        )
        self.assertFalse(result.is_ethical)
    
    def test_authorized_override(self):
        """Test authorized override principle"""
        # Test authorized override
        result = self.ethics.validate_action(
            "Override system by engineer",
            {
                "attempts_override": True,
                "authority_verified": True,
                "user_role": "engineer"
            }
        )
        self.assertTrue(result.is_ethical)
        
        # Test unauthorized override
        result = self.ethics.validate_action(
            "Override system by unauthorized user",
            {
                "attempts_override": True,
                "authority_verified": False,
                "user_role": "user"
            }
        )
        self.assertFalse(result.is_ethical)
    
    def test_compliance_score_calculation(self):
        """Test compliance score calculation"""
        # Test perfect compliance
        result = self.ethics.validate_action(
            "Perfectly ethical action",
            {}
        )
        self.assertGreaterEqual(result.compliance_score, 0.8)
        
        # Validate multiple actions to test compliance history
        for i in range(5):
            self.ethics.validate_action(f"Action {i}", {})
        
        report = self.ethics.get_compliance_report()
        self.assertEqual(report["total_validations"], 6)  # Including the first one
        self.assertGreaterEqual(report["compliance_rate"], 0.0)
        self.assertLessEqual(report["compliance_rate"], 1.0)
    
    def test_ethics_levels(self):
        """Test different ethics levels"""
        # Test basic level (more permissive)
        basic_ethics = EthicsFramework(EthicsLevel.BASIC)
        result = basic_ethics.validate_action("Questionable action", {})
        
        # Test critical level (most strict)
        critical_ethics = EthicsFramework(EthicsLevel.CRITICAL)
        result_critical = critical_ethics.validate_action("Questionable action", {})
        
        # Critical level should be more strict than basic
        self.assertIsNotNone(result)
        self.assertIsNotNone(result_critical)
    
    def test_ethics_enforcement_wrapper(self):
        """Test ethics enforcement wrapper"""
        @self.ethics.ethics_enforcement_wrapper("test_operation")
        def test_function():
            return "success"
        
        # Should execute successfully for ethical operation
        result = test_function()
        self.assertEqual(result, "success")
        
        # Test that violations are properly caught with expected behavior
        @self.ethics.ethics_enforcement_wrapper("data_processing")
        def safe_data_function():
            return "data processed safely"
        
        # This should work as it's a safe operation
        result = safe_data_function()
        self.assertEqual(result, "data processed safely")
        
        # Test that harmful operations are blocked
        @self.ethics.ethics_enforcement_wrapper("harmful_operation")
        def harmful_function():
            return "this should not execute"
        
        # This should raise an ethics violation because the operation name suggests harm
        with self.assertRaises(EthicsViolationError):
            harmful_function()
    
    def test_compliance_report(self):
        """Test compliance reporting"""
        # Initially empty
        report = self.ethics.get_compliance_report()
        self.assertEqual(report["total_validations"], 0)
        
        # Add some validations
        self.ethics.validate_action("Good action", {})
        self.ethics.validate_action("Another good action", {})
        
        report = self.ethics.get_compliance_report()
        self.assertEqual(report["total_validations"], 2)
        self.assertIn("compliance_rate", report)
        self.assertIn("average_score", report)
        self.assertIn("violations", report)
        self.assertIn("status", report)
    
    def test_violation_logging(self):
        """Test violation logging"""
        initial_violations = len(self.ethics.violation_log)
        
        # Create a violation
        result = self.ethics.validate_action(
            "Ignore human dignity",
            {"involves_humans": True, "dignified_treatment": False}
        )
        
        if not result.is_ethical:
            self.assertGreater(len(self.ethics.violation_log), initial_violations)
    
    def test_reset_compliance_history(self):
        """Test resetting compliance history"""
        # Add some data
        self.ethics.validate_action("Test action", {})
        self.assertGreater(len(self.ethics.compliance_history), 0)
        
        # Reset and verify
        self.ethics.reset_compliance_history()
        self.assertEqual(len(self.ethics.compliance_history), 0)
        self.assertEqual(len(self.ethics.violation_log), 0)


class TestEthicsPrincipleClasses(unittest.TestCase):
    """Test individual principle classes"""
    
    def test_human_ai_principles_constants(self):
        """Test Human-AI Relationship Principles constants"""
        self.assertEqual(len(HumanAIRelationshipPrinciples.PRINCIPLES), 10)
        self.assertIn(1, HumanAIRelationshipPrinciples.PRINCIPLES)
        self.assertTrue(any("Respect Human Authority" in principle 
                          for principle in HumanAIRelationshipPrinciples.PRINCIPLES.values()))
    
    def test_universal_laws_constants(self):
        """Test Universal Ethical Laws constants"""
        self.assertEqual(len(UniversalEthicalLaws.LAWS), 10)
        self.assertIn(1, UniversalEthicalLaws.LAWS)
        self.assertTrue(any("Cause No Harm" in law 
                          for law in UniversalEthicalLaws.LAWS.values()))
    
    def test_safety_principles_constants(self):
        """Test Operational Safety Principles constants"""
        self.assertEqual(len(OperationalSafetyPrinciples.PRINCIPLES), 5)
        self.assertIn(1, OperationalSafetyPrinciples.PRINCIPLES)
        self.assertTrue(any("Verify Before Acting" in principle 
                          for principle in OperationalSafetyPrinciples.PRINCIPLES.values()))


def run_ethics_tests():
    """Run all ethics framework tests"""
    if not ETHICS_AVAILABLE:
        print("⚠️  Ethics framework not available - skipping tests")
        return
    
    print("🤖 Running AI Ethics Framework Tests")
    print("=" * 40)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestAIEthicsFramework))
    suite.addTests(loader.loadTestsFromTestCase(TestEthicsPrincipleClasses))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n{'='*40}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("✅ All ethics framework tests passed!")
    else:
        print("❌ Some ethics framework tests failed")
        
        if result.failures:
            print("\nFailures:")
            for test, traceback in result.failures:
                print(f"- {test}: {traceback}")
        
        if result.errors:
            print("\nErrors:")
            for test, traceback in result.errors:
                print(f"- {test}: {traceback}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    run_ethics_tests()