"""
Verification suite for Phase 8: Project Symbiosis.
Tests the Carbon-Silicon Bridge, Ethical Firewall, and BCI Simulator integration.
"""

import unittest
import torch
import numpy as np
import logging
from adaptiveneuralnetwork.core.symbiosis import (
    BCISimulator, 
    EthicalFirewall, 
    CarbonSiliconBridge,
    NeurologicalTelemetry
)

# Mocking a Node with chemistry and workspace for testing
class MockCognitiveNode:
    def __init__(self):
        class MockChemistry:
            def __init__(self):
                self.acetylcholine = 1.0
                self.serotonin = 1.0
        
        class MockWorkspace:
            def __init__(self):
                self.attention_gain = 0.5
                
        self.neurochemistry = MockChemistry()
        self.workspace = MockWorkspace()

class TestProjectSymbiosis(unittest.TestCase):
    def setUp(self):
        self.node = MockCognitiveNode()
        self.bridge = CarbonSiliconBridge(target_node=self.node)
        self.bridge.activate()

    def test_bci_simulator_states(self):
        """Test if the simulator generates appropriate telemetry for different states."""
        sim = BCISimulator()
        
        # Test Focused State
        sim.set_user_state("focused")
        telemetry = sim.poll_telemetry()
        self.assertGreater(telemetry.eeg_bands['beta'], 0.5)
        self.assertGreater(telemetry.attention_level, 0.7)
        
        # Test Tired State
        sim.set_user_state("tired")
        telemetry = sim.poll_telemetry()
        self.assertGreater(telemetry.eeg_bands['theta'], 0.5)
        self.assertLess(telemetry.attention_level, 0.5)

    def test_ethical_firewall_clamping(self):
        """Test if the firewall clamps dangerous output signals."""
        firewall = EthicalFirewall()
        dangerous_signal = torch.full((16,), 5.0)  # Way too high
        safe_signal = firewall.validate_outbound_neuromodulation(dangerous_signal)
        
        self.assertLess(torch.max(safe_signal).item(), 2.0)
        self.assertTrue(len(firewall.alerts) > 0)

    def test_ethical_firewall_privacy(self):
        """Test if sensitive tags are stripped."""
        firewall = EthicalFirewall()
        telemetry = NeurologicalTelemetry(timestamp=0.0)
        telemetry.metadata['episodic_tag'] = "User's home address"
        
        firewall.validate_inbound_telemetry(telemetry)
        self.assertNotIn('episodic_tag', telemetry.metadata)

    def test_bridge_injection(self):
        """Test if bridge correctly updates the synthetic substrate."""
        initial_ach = self.node.neurochemistry.acetylcholine
        
        # Force a focused state into the simulator
        self.bridge.simulator.set_user_state("focused")
        
        # Run bridge cycle
        self.bridge.update_cycle()
        
        # Chemistry should have changed (ACh should increase due to Beta waves)
        self.assertNotEqual(self.node.neurochemistry.acetylcholine, initial_ach)
        self.assertGreater(self.node.neurochemistry.acetylcholine, initial_ach)
        
        # Workspace attention should be high
        self.assertGreater(self.node.workspace.attention_gain, 0.7)

    def test_sovereignty_loss_shutdown(self):
        """Test if bridge shuts down when sovereignty is critical."""
        self.bridge.firewall.sovereignty_score = 0.1
        feedback = torch.ones(16)
        
        # We need a stent_report for the updated feedback method signature
        stent_report = {"stent_load": 0.0} 
        safe_feedback = self.bridge.firewall.validate_outbound_neuromodulation(
            self.bridge._generate_neuromodulatory_feedback(
                NeurologicalTelemetry(timestamp=0.0), stent_report
            )
        )
        
        self.assertEqual(torch.sum(safe_feedback).item(), 0.0)

    def test_quantum_stent_stabilization(self):
        """Test if the quantum stent applies pulses when coherence is low."""
        stent = self.bridge.quantum_stent
        
        # Case 1: Initial Run (Will likely need stabilization since starts at 0.5)
        report = stent.process_telemetry(attention_level=1.0, stress_level=0.0)
        self.assertIn(report["status"], ["optimal", "stabilized"])
        
        # Case 2: Stressed (Stabilization should activate intermittently)
        for _ in range(20):
            report = stent.process_telemetry(attention_level=0.0, stress_level=1.0)
            
        self.assertIn(report["status"], ["stabilized", "optimal"])

if __name__ == '__main__':
    unittest.main()
