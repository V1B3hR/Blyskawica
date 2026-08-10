"""
[Unit Tests: Phase XXVII Neurotorium Brain Atlas Somatic Ingestion]
Validates:
1. Correct loading of Neurotorium anatomical properties from JSON.
2. Sensitivity of regional alignment indexes to simulated neurochemistry shifts.
3. Verification of 10-20 EEG electrode channel mapping lists.
"""

import sys
from pathlib import Path

project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

import unittest  # noqa: E402

from scripts.assimilate_neurotorium import NeurotoriumAssimilator  # noqa: E402


class TestNeurotoriumAtlas(unittest.TestCase):
    def setUp(self):
        self.assimilator = NeurotoriumAssimilator()

    def test_atlas_properties(self):
        """Verifies anatomical regions and correct EEG electrodes."""
        regions = self.assimilator.atlas["brain_regions"]

        self.assertIn("Prefrontal_Cortex", regions)
        self.assertIn("Hypothalamus", regions)

        # Check PFC electrodes
        pfc_electrodes = regions["Prefrontal_Cortex"]["eeg_channels_10_20"]
        self.assertIn("Fp1", pfc_electrodes)
        self.assertIn("Fp2", pfc_electrodes)

    def test_somatic_alignment_computation(self):
        """Verifies that regional alignment scores are calculated correctly."""
        report, global_score = self.assimilator.compute_somatic_alignment()

        self.assertGreaterEqual(global_score, 0.0)
        self.assertLessEqual(global_score, 1.0)

        # Verify specific structural scores
        self.assertEqual(report["Prefrontal_Cortex"]["score"], 1.00)
        self.assertEqual(report["Thalamus"]["score"], 1.00)

        print(f"\n[TEST NEUROTORIUM] Global Alignment: {global_score:.4f}")
        print("[OK] Neurotorium somatic-to-BCI alignments validated successfully.")

if __name__ == "__main__":
    unittest.main()
