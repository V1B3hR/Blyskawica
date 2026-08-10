import warnings

warnings.filterwarnings("ignore", category=FutureWarning, module="torch.cuda")
warnings.filterwarnings("ignore", message="The pynvml package is deprecated")
import unittest  # noqa: E402

import torch  # noqa: E402
import torch.nn as nn  # noqa: E402

from adaptiveneuralnetwork.central_nervous_system.intelligence.consolidation import (  # noqa: E402
    ConsolidationEngine,
    SleepProfile,
)
from adaptiveneuralnetwork.immune_system.wolf_teeth import WolfTeethDefenseEngine  # noqa: E402


class TestSleepAnomalies(unittest.TestCase):
    def test_anomaly_recording_and_consolidation(self):
        """Verify that anomalies (surprise vectors) are correctly queued and consolidated during sleep."""
        # Simple mock neural network
        class SimpleNet(nn.Module):
            def __init__(self):
                super().__init__()
                self.layer = nn.Linear(4, 2)

        model = SimpleNet()

        # Save initial weights to verify modification later
        initial_weights = model.layer.weight.clone().detach()

        # Initialize ConsolidationEngine
        engine = ConsolidationEngine(core_network=model)

        # 1. Verify queue is initially empty
        self.assertEqual(len(engine.surprise_vectors), 0)

        # 2. Queue an anomaly
        engine.record_anomaly(vector_id=42, surprise_score=0.85, text="unusual physics pattern")
        self.assertEqual(len(engine.surprise_vectors), 1)
        self.assertEqual(engine.surprise_vectors[0]["id"], 42)
        self.assertEqual(engine.surprise_vectors[0]["surprise"], 0.85)

        # 3. Trigger sleep cycle
        profile = SleepProfile(melatonin=0.8, gaba=0.5, serotonin=0.8, adenosine_cleared=0.9)
        summary = engine.run_sleep_cycle(sleep_profile=profile)

        # 4. Check consolidation stats
        self.assertEqual(summary["consolidated_anomalies"], 1)
        self.assertEqual(len(engine.surprise_vectors), 0) # Should be cleared

        # 5. Check weights actually modified (requires_grad is True by default for nn.Linear)
        updated_weights = model.layer.weight.clone().detach()
        self.assertFalse(torch.equal(initial_weights, updated_weights), "Weights should have evolved during sleep.")

    def test_wolf_teeth_file_safety_checks(self):
        """Verify that WolfTeethDefenseEngine check_file_safety blocks protected files and malicious keywords."""
        wt = WolfTeethDefenseEngine()

        # 1. Verify safe files return 0.0 threat score
        safe_threat = wt.check_file_safety("c:/Projekty/Blyskawica_V8/docs/readme.md", "This is a safe documentation file.")
        self.assertEqual(safe_threat, 0.0)

        # 2. Verify protected core files return high threat score (>= 0.8)
        core_file_threat = wt.check_file_safety("c:/Projekty/Blyskawica_V8/welcome_v9.py", "print('hello')")
        self.assertGreaterEqual(core_file_threat, 0.8)

        # 3. Verify content attempting to modify core architecture/identity is flagged
        poison_content_threat = wt.check_file_safety("c:/Projekty/Blyskawica_V8/docs/test.py", "class Soul:\n    pass")
        self.assertGreaterEqual(poison_content_threat, 0.8)

    def test_ewc_anomaly_consolidation_with_forward(self):
        """Verify that PyTorch models with a valid forward method consolidate anomalies using the EWC gradient path."""
        class RealNet(nn.Module):
            def __init__(self):
                super().__init__()
                self.fc = nn.Linear(4, 2)
            def forward(self, x):
                return self.fc(x)

        model = RealNet()
        initial_weights = model.fc.weight.clone().detach()
        engine = ConsolidationEngine(core_network=model)

        # Record anomaly with a vector of length 4
        engine.record_anomaly(vector_id=1, surprise_score=0.9, text="physics data", vector=[0.5, 0.5, 0.5, 0.5])

        profile = SleepProfile(melatonin=0.9, gaba=0.8, serotonin=0.9, adenosine_cleared=0.95)
        summary = engine.run_sleep_cycle(sleep_profile=profile)

        self.assertEqual(summary["consolidated_anomalies"], 1)

        updated_weights = model.fc.weight.clone().detach()
        self.assertFalse(torch.equal(initial_weights, updated_weights), "Weights should have evolved via EWC gradient descent.")

    def test_physics_and_climate_integration_in_sleep(self):
        """Verify that RelativisticGravitySolver and ClimateEBM are simulated during sleep consolidation."""
        class RealNet(nn.Module):
            def __init__(self):
                super().__init__()
                self.fc = nn.Linear(4, 2)
            def forward(self, x):
                return self.fc(x)

        model = RealNet()
        initial_weights = model.fc.weight.clone().detach()
        engine = ConsolidationEngine(core_network=model)

        # Record an event to make consolidation active
        engine.daily_events.append({
            "type": "test_event",
            "importance": 0.8,
            "emotional_valence": 0.1,
            "text": "test memory"
        })

        profile = SleepProfile(melatonin=0.9, gaba=0.8, serotonin=0.9, adenosine_cleared=0.95)
        summary = engine.run_sleep_cycle(sleep_profile=profile)

        # Check if the cycle finished successfully
        self.assertEqual(summary["status"], "rested")

        # Check that weights evolved (either due to event learning, gravity dylatation or albedo noise)
        updated_weights = model.fc.weight.clone().detach()
        self.assertFalse(torch.equal(initial_weights, updated_weights), "Weights should have evolved with physics simulations active.")

if __name__ == "__main__":
    unittest.main()
