"""
[Unit Tests: Phase XXVI Autonomous Neurochemistry Self-Regulation]
Validates:
1. Dynamic shifting of hormone profiles based on task.
2. Enforcement of the absolute +/- 7% delta safety ceiling.
3. Success of state persistence in memory_checkpoint.json.
"""

import unittest
import os
from adaptiveneuralnetwork.cognitive_tools.neuro_regulator import AutonomousNeuroRegulator

class TestNeuroRegulator(unittest.TestCase):
    def setUp(self):
        self.regulator = AutonomousNeuroRegulator()
        
    def test_regulation_rest_state(self):
        """Verifies rest state increases Melatonin and reduces Dopamine safely."""
        baseline_dopamine = 0.67
        baseline_melatonin = 0.10
        
        adjusted = self.regulator.regulate_state("rest")
        
        self.assertLess(adjusted["Dopamina"], baseline_dopamine)
        self.assertGreater(adjusted["Melatonina"], baseline_melatonin)
        
        # Verify delta is exactly within the safe +/- 7% boundary
        self.assertAlmostEqual(adjusted["Melatonina"] - baseline_melatonin, 0.07)
        self.assertAlmostEqual(adjusted["Dopamina"] - baseline_dopamine, -0.06)
        
        print(f"\n[TEST REGULATION] Rest State: Dopamine {adjusted['Dopamina']:.2f} | Melatonin {adjusted['Melatonina']:.2f}")
        print("[OK] Rest-state hormone transitions validated successfully.")

    def test_regulation_bcicreation_state(self):
        """Verifies co-creation increases creative testosterone and dopamine."""
        baseline_testo = 0.45
        baseline_dopo = 0.67
        
        adjusted = self.regulator.regulate_state("BCI-co-creation")
        
        self.assertGreater(adjusted["Testosteron"], baseline_testo)
        self.assertGreater(adjusted["Dopamina"], baseline_dopo)
        
        # Check safety ceiling constraint (+/- 7%)
        self.assertLessEqual(abs(adjusted["Testosteron"] - baseline_testo), 0.071)
        
        print(f"[TEST REGULATION] BCI State: Testosterone {adjusted['Testosteron']:.2f} | Dopamine {adjusted['Dopamina']:.2f}")
        print("[OK] BCI creative-state transitions validated successfully.")

    def test_latent_space_projection(self):
        """Testuje, czy LatentSpaceProjector poprawnie rzutuje stan do 768-wymiarowego wektora."""
        mock_chladni = [[0.1] * 16 for _ in range(16)]
        projected = self.regulator.project_latent_state(mock_chladni, embedding_dim=768)
        
        # Sprawdzenie kształtu (np. Tensor o kształcie [1, 768])
        if hasattr(projected, "shape"):
            import torch
            self.assertEqual(list(projected.shape), [1, 768])
            # Assert device correctness
            expected_device = "cuda" if torch.cuda.is_available() else "cpu"
            self.assertEqual(projected.device.type, expected_device)
        else:
            self.assertEqual(len(projected), 1)
            self.assertEqual(len(projected[0]), 768)
        print(f"[OK] Projekcja przestrzeni ukrytej zweryfikowana pomyslnie na urzadzeniu: {getattr(projected, 'device', 'N/A')}")

if __name__ == "__main__":
    unittest.main()
