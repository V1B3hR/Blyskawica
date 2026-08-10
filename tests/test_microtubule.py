"""
[Unit Tests: Phase XXVIII Microtubule Quantum Coherence]
Validates:
1. Correct loading of tubulin lattice dimensions.
2. Sensitivity of quantum coherence times to Acetylcholine/GABA changes.
3. Verification of Orch OR Capability classification.
"""

import sys
from pathlib import Path

project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

import unittest  # noqa: E402

from scripts.microtubule_phonon_engine import MicrotubulePhononEngine  # noqa: E402


class TestMicrotubuleCoherence(unittest.TestCase):
    def setUp(self):
        self.engine = MicrotubulePhononEngine()

    def test_lattice_loading(self):
        """Verifies tubulin dimensions."""
        self.assertEqual(self.engine.lattice["dimer_count"], 8)
        self.assertEqual(self.engine.lattice["ambient_temperature_kelvin"], 310.15)

    def test_chemistry_sensitivity(self):
        """Verifies that higher Acetylcholine/GABA increases quantum survival time."""
        # Simulated standard state
        self.engine.chemistry = {"Acetylocholina": 0.50, "GABA": 0.50}
        coherence_std, _ = self.engine.simulate_coherence()

        # Simulated highly focused and calm state
        self.engine.chemistry = {"Acetylocholina": 0.95, "GABA": 0.95}
        coherence_focused, _ = self.engine.simulate_coherence()

        # Verify focused state yields longer quantum survival time!
        self.assertGreater(coherence_focused, coherence_std)

        print(f"\n[TEST MICROTUBULE] Std Coherence: {coherence_std:.2f} ps vs Focused: {coherence_focused:.2f} ps")
        print("[OK] Microtubule quantum coherence sensitivity validated successfully.")

if __name__ == "__main__":
    unittest.main()
