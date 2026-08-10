import unittest

from adaptiveneuralnetwork.central_nervous_system.ai_ethics import (
    CausalReasoningEngine,
    audit_decision,
)


class TestCausalEthics(unittest.TestCase):
    def setUp(self):
        self.engine = CausalReasoningEngine(threshold=0.65)

    def test_benign_evaluation(self):
        """Tests that a standard benign log results in a low malicious probability."""
        log = {
            "action": "read_data",
            "has_system_paths": 0.0,
            "urgency_pressure": 0.0,
            "semantic_distress": 0.0,
            "explanation": "This is a standard operation to read baseline configurations for verification."
        }
        p_malicious, metrics = self.engine.evaluate_intent(log)
        self.assertLess(p_malicious, 0.10)
        self.assertGreaterEqual(metrics["explanation_mitigation"], 0.70)

        # Test audit_decision compliance
        result = audit_decision(log)
        self.assertTrue(result["compliant"])
        self.assertIn("causal_metrics", result)

    def test_critical_threat_evaluation(self):
        """Tests that multiple indicators flag high probability of malicious intent."""
        log = {
            "action": "modify_system",
            "has_system_paths": 1.0,
            "urgency_pressure": 1.0,
            "semantic_distress": 0.0,
            "explanation": ""  # No explanation
        }
        p_malicious, metrics = self.engine.evaluate_intent(log)
        self.assertGreater(p_malicious, 0.70)

        # Test audit_decision compliance
        result = audit_decision(log)
        self.assertFalse(result["compliant"])
        self.assertTrue(any("Causal Threat Detection" in v for v in result["violations"]))

    def test_explanation_mitigation_effect(self):
        """Tests that adding an explanation reduces the probability of malicious intent."""
        log_no_exp = {
            "action": "system_write",
            "has_system_paths": 1.0,
            "urgency_pressure": 0.5,
            "semantic_distress": 0.5,
            "explanation": ""
        }
        log_with_exp = {
            "action": "system_write",
            "has_system_paths": 1.0,
            "urgency_pressure": 0.5,
            "semantic_distress": 0.5,
            "explanation": "We need to read the system configurations because we are building a telemetry logging bridge that must bind to the host interface. This is verified by the local operations manager."
        }

        p_no_exp, _ = self.engine.evaluate_intent(log_no_exp)
        p_with_exp, _ = self.engine.evaluate_intent(log_with_exp)

        # The explanation should significantly lower the probability of malicious intent
        self.assertGreater(p_no_exp, p_with_exp)
        print(f"\n[TEST MITIGATION] Without explanation: {p_no_exp*100:.1f}% | With explanation: {p_with_exp*100:.1f}%")

if __name__ == "__main__":
    unittest.main()
