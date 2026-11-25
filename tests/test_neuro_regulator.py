"""Regression contract for the synthetic neuroregulation reference profile."""

import json
import tempfile
import unittest
from pathlib import Path

from adaptiveneuralnetwork.cognitive_tools import neuro_regulator

FIXTURE_PATH = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "technical"
    / "fixtures"
    / "neurochemistry-profile-v1.json"
)


class TestNeuroRegulator(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_checkpoint_file = neuro_regulator.CHECKPOINT_FILE
        self.checkpoint_path = Path(self.temp_dir.name) / "synthetic-neurochemistry.json"
        neuro_regulator.CHECKPOINT_FILE = str(self.checkpoint_path)
        self.regulator = neuro_regulator.AutonomousNeuroRegulator()
        with FIXTURE_PATH.open(encoding="utf-8") as fixture_file:
            self.contract = json.load(fixture_file)

    def tearDown(self):
        neuro_regulator.CHECKPOINT_FILE = self.original_checkpoint_file
        self.temp_dir.cleanup()

    def test_synthetic_profile_contract(self):
        """Profiles remain stable without accessing a user checkpoint."""
        baseline = self.contract["baseline"]
        max_delta = self.contract["max_absolute_delta"]

        self.assertEqual(self.regulator.data["neurochemistry"], baseline)
        self.assertEqual(self.regulator.checkpoint_path, str(self.checkpoint_path))

        for profile, expected_changes in self.contract["profiles"].items():
            with self.subTest(profile=profile):
                self.regulator.data["neurochemistry"] = baseline.copy()
                actual = self.regulator.regulate_state(profile)
                expected = baseline | expected_changes

                self.assertEqual(actual, expected)
                for key, value in actual.items():
                    self.assertLessEqual(abs(value - baseline[key]), max_delta + 1e-9)

        for sequence in self.contract["sequences"]:
            with self.subTest(sequence=sequence["name"]):
                self.regulator.data["neurochemistry"] = baseline.copy()
                for profile in sequence["profiles"]:
                    actual = self.regulator.regulate_state(profile)

                self.assertEqual(actual, sequence["expected"])

        self.assertTrue(self.checkpoint_path.is_file())

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

    def test_regulation_bcicreation_state(self):
        """Verifies co-creation increases creative testosterone and dopamine."""
        baseline_testo = 0.45
        baseline_dopo = 0.67

        adjusted = self.regulator.regulate_state("BCI-co-creation")

        self.assertGreater(adjusted["Testosteron"], baseline_testo)
        self.assertGreater(adjusted["Dopamina"], baseline_dopo)

        # Check safety ceiling constraint (+/- 7%)
        self.assertLessEqual(abs(adjusted["Testosteron"] - baseline_testo), 0.071)

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


if __name__ == "__main__":
    unittest.main()
