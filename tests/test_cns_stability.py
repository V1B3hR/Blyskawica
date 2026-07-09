import unittest
import torch
from adaptiveneuralnetwork.central_nervous_system.cognitive_hygiene import NeuromodulationState, CRAEngine
from adaptiveneuralnetwork.central_nervous_system.global_workspace import GlobalWorkspaceBus

class TestCNSStability(unittest.TestCase):
    def test_global_workspace_stabilization(self):
        """Verify that GlobalWorkspaceBus broadcasts signals and applies GLI to incoming salient info."""
        bus = GlobalWorkspaceBus(workspace_dim=64, salience_threshold=0.5)
        
        # Test baseline state
        self.assertEqual(bus.workspace_state.shape, (64,))
        self.assertEqual(bus.workspace_state.sum().item(), 0.0)
        
        # Broadcast a highly salient signal
        signal = torch.ones(2, 64) * 2.0
        out_state = bus.broadcast(signal)
        
        # State should be updated (non-zero)
        self.assertEqual(out_state.shape, (64,))
        self.assertNotEqual(out_state.sum().item(), 0.0)
        
        # Verify GLI has shunted some noise energy (potential > 0.0)
        potential = bus.gli.ground.ground_potential.item()
        self.assertGreater(potential, 0.0)

    def test_neurochemistry_stabilization(self):
        """Verify that NeuromodulationState dynamically filters extreme hormonal spikes via GLI."""
        state = NeuromodulationState()
        
        # Force a massive, chaotic dopamine/cortisol spike (representing hyper-arousal and stress)
        state.dopamine.fill_(2.5)
        state.cortisol.fill_(3.0)
        state.adrenaline.fill_(3.0)
        
        # Run stabilization
        state.stabilize_neurochemistry()
        
        # Verify that the values have been damped and clamped to healthy boundaries
        self.assertLessEqual(state.dopamine.item(), 2.0)
        self.assertLessEqual(state.cortisol.item(), 2.0)
        self.assertLessEqual(state.adrenaline.item(), 2.0)
        
        # Verify GLI ground potential registered the shunt
        self.assertGreater(state.gli.ground.ground_potential.item(), 0.0)

    def test_sleep_cycle_execution(self):
        """Verify that the sleep-cycle updates execute without AttributeError and reset stress hormones."""
        state = NeuromodulationState()
        
        # Simulate high stress baseline
        state.cortisol.fill_(1.5)
        state.adrenaline.fill_(1.2)
        state.melatonin.fill_(0.1)
        state.serotonin.fill_(1.0)
        state.gaba.fill_(0.5)
        
        # Run sleep cycle (duration=8.0 hours)
        state.update(8.0, "sleep")
        
        # Check that cortisol/adrenaline dropped, melatonin/serotonin/GABA rose
        self.assertLess(state.cortisol.item(), 1.5)
        self.assertLess(state.adrenaline.item(), 1.2)
        self.assertGreater(state.melatonin.item(), 0.1)
        self.assertGreater(state.serotonin.item(), 1.0)
        self.assertGreater(state.gaba.item(), 0.5)

if __name__ == "__main__":
    unittest.main()
