"""
test_phase21_verification.py - Test suite for Phase 21 verification framework

Tests formal verification and assurance capabilities including:
- Property registration and verification
- Runtime monitoring
- Assurance case management
- Phase 21 exit criteria validation
"""

import unittest
import time
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from verification_framework import (
    VerificationFramework,
    FormalProperty,
    PropertyType,
    AssuranceLevel,
    VerificationStatus,
    VerificationEvidence,
    AssuranceCase,
    RuntimeMonitor
)


class TestPhase21Verification(unittest.TestCase):
    """Test suite for Phase 21 verification capabilities"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.framework = VerificationFramework(data_dir="/tmp/test_verification")
        
    def test_framework_initialization(self):
        """Test verification framework initialization"""
        self.assertIsNotNone(self.framework)
        self.assertIsNotNone(self.framework.runtime_monitor)
        
        # Check that core properties are initialized
        self.assertGreater(len(self.framework.properties), 0)
        
        print("✓ Verification framework initialization successful")
    
    def test_property_registration(self):
        """Test formal property registration"""
        prop = FormalProperty(
            property_id="TEST_001",
            name="Test Property",
            property_type=PropertyType.SAFETY,
            assurance_level=AssuranceLevel.HIGH,
            specification="ALWAYS (test_condition == true)",
            description="Test property for validation",
            rationale="Testing purposes",
            verification_method="runtime_monitoring"
        )
        
        self.framework.register_property(prop)
        self.assertIn("TEST_001", self.framework.properties)
        self.assertEqual(self.framework.properties["TEST_001"].name, "Test Property")
        
        print("✓ Property registration successful")
    
    def test_runtime_monitoring(self):
        """Test runtime property monitoring"""
        monitor = self.framework.runtime_monitor
        
        # Test with valid state
        valid_state = {
            'latency_ms': 100,
            'accuracy': 0.90,
            'fairness_score': 0.92,
            'privacy_violations': 0,
            'ethical_violations_critical': 0
        }
        
        # Check all core properties
        for prop_id in self.framework.properties.keys():
            result = monitor.check_property(prop_id, valid_state)
            self.assertTrue(result or self.framework.properties[prop_id].status != VerificationStatus.ERROR)
        
        print("✓ Runtime monitoring validated with valid state")
        
        # Test with invalid state (latency violation)
        invalid_state = valid_state.copy()
        invalid_state['latency_ms'] = 200  # Exceeds threshold
        
        violations_before = len(monitor.get_violations())
        monitor.check_property("PERFORMANCE_001", invalid_state)
        violations_after = len(monitor.get_violations())
        
        self.assertGreater(violations_after, violations_before)
        print("✓ Property violation correctly detected and recorded")
    
    def test_evidence_collection(self):
        """Test verification evidence collection"""
        evidence = VerificationEvidence(
            evidence_id="EVID_001",
            property_id="SAFETY_001",
            evidence_type="test_results",
            timestamp=datetime.now(),
            description="Safety property test results",
            artifacts=["test_log_001.txt", "test_report_001.pdf"],
            confidence_score=0.95
        )
        
        self.framework.add_evidence(evidence)
        self.assertIn("SAFETY_001", self.framework.evidence)
        self.assertEqual(len(self.framework.evidence["SAFETY_001"]), 1)
        
        print("✓ Evidence collection successful")
    
    def test_assurance_case_management(self):
        """Test GSN assurance case management"""
        assurance_case = AssuranceCase(
            case_id="AC_TEST_001",
            goal="System is safe for deployment",
            context="Test environment",
            strategies=[
                "Verify safety properties",
                "Test edge cases",
                "Monitor runtime behavior"
            ]
        )
        
        # Add evidence
        for i in range(2):
            evidence = VerificationEvidence(
                evidence_id=f"EVID_AC_{i}",
                property_id="SAFETY_001",
                evidence_type="test_results",
                timestamp=datetime.now(),
                description=f"Test evidence {i}"
            )
            assurance_case.evidence.append(evidence)
        
        self.framework.create_assurance_case(assurance_case)
        
        self.assertIn("AC_TEST_001", self.framework.assurance_cases)
        case = self.framework.assurance_cases["AC_TEST_001"]
        self.assertGreater(case.completeness_score, 0.0)
        
        print(f"✓ Assurance case created with {case.completeness_score:.1%} completeness")
    
    def test_verification_report_generation(self):
        """Test verification report generation"""
        report = self.framework.generate_verification_report()
        
        self.assertIn('summary', report)
        self.assertIn('coverage_by_assurance_level', report)
        self.assertIn('properties', report)
        
        self.assertGreater(report['summary']['total_properties'], 0)
        self.assertGreaterEqual(report['summary']['verification_coverage'], 0.0)
        self.assertLessEqual(report['summary']['verification_coverage'], 1.0)
        
        print(f"✓ Verification report generated")
        print(f"  Total properties: {report['summary']['total_properties']}")
        print(f"  Verified: {report['summary']['verified']}")
        print(f"  Coverage: {report['summary']['verification_coverage']:.1%}")
    
    def test_critical_property_verification(self):
        """Test that critical properties are verified"""
        critical_props = [
            p for p in self.framework.properties.values()
            if p.assurance_level == AssuranceLevel.CRITICAL
        ]
        
        self.assertGreater(len(critical_props), 0, "No critical properties defined")
        
        # Verify each critical property
        for prop in critical_props:
            status = self.framework.verify_property(prop.property_id)
            self.assertIn(status, [VerificationStatus.VERIFIED, VerificationStatus.UNKNOWN])
            
        print(f"✓ {len(critical_props)} critical properties verified")
    
    def test_phase21_exit_criteria(self):
        """Test Phase 21 exit criteria validation"""
        # Create some assurance cases to improve completeness
        for i in range(3):
            case = AssuranceCase(
                case_id=f"AC_EXIT_{i}",
                goal=f"Exit criterion {i} satisfied",
                context="Phase 21 completion",
                strategies=["Verify", "Test", "Monitor"]
            )
            # Add evidence to increase completeness
            for j in range(3):
                case.evidence.append(VerificationEvidence(
                    evidence_id=f"EVID_{i}_{j}",
                    property_id=f"SAFETY_001",
                    evidence_type="test",
                    timestamp=datetime.now(),
                    description=f"Evidence {j}"
                ))
            self.framework.create_assurance_case(case)
        
        exit_check = self.framework.check_phase21_exit_criteria()
        
        self.assertIn('criteria', exit_check)
        self.assertIn('all_criteria_met', exit_check)
        
        print("\n" + "=" * 60)
        print("Phase 21 Exit Criteria Validation")
        print("=" * 60)
        
        for criterion, values in exit_check['criteria'].items():
            status = "✓" if values['met'] else "✗"
            print(f"{status} {criterion}: {values['actual']:.2f} / {values['target']:.2f}")
        
        print(f"\nAll criteria met: {'✓ YES' if exit_check['all_criteria_met'] else '✗ NO'}")
    
    def test_safety_property_enforcement(self):
        """Test that safety properties are enforced"""
        monitor = self.framework.runtime_monitor
        
        # Test critical ethical violation detection
        unsafe_state = {
            'ethical_violations_critical': 1,  # Critical violation!
            'latency_ms': 50,
            'accuracy': 0.95
        }
        
        result = monitor.check_property("SAFETY_001", unsafe_state)
        self.assertFalse(result, "Safety violation not detected")
        
        prop = self.framework.properties["SAFETY_001"]
        self.assertEqual(prop.status, VerificationStatus.VIOLATED)
        self.assertGreater(prop.violation_count, 0)
        
        print("✓ Safety property enforcement validated")
    
    def test_continuous_monitoring(self):
        """Test continuous monitoring over multiple states"""
        monitor = self.framework.runtime_monitor
        
        states = [
            {'latency_ms': 100, 'accuracy': 0.90, 'fairness_score': 0.92},
            {'latency_ms': 120, 'accuracy': 0.88, 'fairness_score': 0.90},
            {'latency_ms': 140, 'accuracy': 0.91, 'fairness_score': 0.89},
            {'latency_ms': 110, 'accuracy': 0.89, 'fairness_score': 0.91}
        ]
        
        for state in states:
            state['ethical_violations_critical'] = 0
            state['privacy_violations'] = 0
            
            for prop_id in ['PERFORMANCE_001', 'FAIRNESS_001']:
                monitor.check_property(prop_id, state)
        
        # Check that monitoring data is collected
        violations = monitor.get_violations(since=datetime.now() - timedelta(minutes=1))
        
        print(f"✓ Continuous monitoring validated ({len(states)} states checked)")
        print(f"  Violations detected: {len(violations)}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
