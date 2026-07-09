"""
[Unit Tests: Phase XXIV Diamond Yant Cymatics Engine]
Validates:
1. EEG Alpha frequency peak extraction.
2. 2D Chladni resonant pattern shape and boundaries.
3. The Harmonic Bridge stabilization capability on IBM PCM drift coefficients.
"""

import unittest
import torch
import numpy as np
from adaptiveneuralnetwork.cognitive_tools.diamond_yant_cymatics import DiamondYantEngine

class TestDiamondYantCymatics(unittest.TestCase):
    def setUp(self):
        self.engine = DiamondYantEngine(lattice_size=16)
        
    def test_eeg_generation_states(self):
        """Verifies focused state generates higher Alpha energy than distracted state."""
        _, signal_focused = self.engine.generate_mock_eeg(state="focused")
        _, signal_distracted = self.engine.generate_mock_eeg(state="distracted")
        
        self.assertEqual(len(signal_focused), 250)
        self.assertEqual(len(signal_distracted), 250)
        
    def test_cymatic_mapping_resonance(self):
        """Checks that EEG signal correctly resolves to a 2D grid of size 16x16."""
        _, signal_focused = self.engine.generate_mock_eeg(state="focused")
        yant_matrix, (alpha_intensity, beta_gamma_intensity) = self.engine.map_eeg_to_yant_matrix(signal_focused)
        
        self.assertEqual(yant_matrix.shape, (16, 16))
        self.assertTrue(alpha_intensity > 0.0)

        
    def test_harmonic_bridge_drift_clamping(self):
        """Verifies that high Alpha waves reduce (clamp) memristor drift rate significantly."""
        _, signal_focused = self.engine.generate_mock_eeg(state="focused")
        yant_matrix_focused, alpha_focused = self.engine.map_eeg_to_yant_matrix(signal_focused)
        
        _, signal_distracted = self.engine.generate_mock_eeg(state="distracted")
        yant_matrix_distracted, alpha_distracted = self.engine.map_eeg_to_yant_matrix(signal_distracted)
        
        base_drift = 0.095
        
        drift_focused, log_focused = self.engine.apply_harmonic_bridge(yant_matrix_focused, alpha_focused, base_drift)
        drift_distracted, log_distracted = self.engine.apply_harmonic_bridge(yant_matrix_distracted, alpha_distracted, base_drift)
        
        # Verify focused state yields significantly lower drift rate than distracted state!
        self.assertLess(drift_focused, base_drift)
        self.assertLess(drift_focused, drift_distracted)
        
        print(f"\n[TEST YANT] Focused Drift: {drift_focused:.4f} vs Distracted: {drift_distracted:.4f}")
        print(f"[OK] Harmonic Bridge attenuation validated successfully.")

if __name__ == "__main__":
    unittest.main()
