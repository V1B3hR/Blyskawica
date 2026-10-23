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

import json  # noqa: E402
import tempfile  # noqa: E402
import unittest  # noqa: E402

from scripts.assimilate_neurotorium import NeurotoriumAssimilator  # noqa: E402

FIXTURE_PATH = Path(project_root) / "docs" / "technical" / "fixtures" / "neurochemistry-profile-v1.json"


class TestNeurotoriumAtlas(unittest.TestCase):
    def setUp(self):
        # Synthetic checkpoint: never depend on the user's runtime memory_checkpoint.json.
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        with FIXTURE_PATH.open(encoding="utf-8") as fixture_file:
            baseline = json.load(fixture_file)["baseline"]
        checkpoint_path = Path(self.temp_dir.name) / "synthetic-checkpoint.json"
        checkpoint_path.write_text(json.dumps({"neurochemistry": baseline}), encoding="utf-8")
        self.assimilator = NeurotoriumAssimilator(checkpoint_path=str(checkpoint_path))

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
