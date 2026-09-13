import os
import sys
import unittest
import numpy as np

# Test the Diamond Yant Cymatics and Quantum Logic in Python
from adaptiveneuralnetwork.cognitive_tools.diamond_yant_cymatics import DiamondYantEngine

class TestQuantumAndCymatics(unittest.TestCase):
    def setUp(self):
        self.engine = DiamondYantEngine(lattice_size=16)

    def test_eeg_mapping_and_chladni_matrix(self):
        t, signal = self.engine.generate_mock_eeg(duration_sec=0.5, state="focused")
        self.assertEqual(len(signal), 125)
        
        yant_matrix, (alpha, beta_gamma) = self.engine.map_eeg_to_yant_matrix(signal)
        self.assertEqual(yant_matrix.shape, (16, 16))
        self.assertGreater(alpha, 0.0)
        print(f"✓ Cymatics Test Passed: Alpha Intensity = {alpha:.4f}, Lattice Shape = {yant_matrix.shape}")

    def test_harmonic_bridge(self):
        t, signal = self.engine.generate_mock_eeg(duration_sec=0.5, state="focused")
        yant_matrix, spectral = self.engine.map_eeg_to_yant_matrix(signal)
        compensated, state = self.engine.apply_harmonic_bridge(yant_matrix, spectral, base_ibm_drift=0.05)
        self.assertIn("drift_variance", state)
        print(f"✓ Harmonic Bridge Test Passed: Stabilized Drift = {state['drift_variance']:.6f}")

if __name__ == "__main__":
    unittest.main()
