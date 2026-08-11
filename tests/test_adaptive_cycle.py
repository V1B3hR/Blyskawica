import unittest

import torch

from adaptiveneuralnetwork.central_nervous_system.alive_node import AliveLoopNode
from adaptiveneuralnetwork.central_nervous_system.time_manager import get_time_manager


class TestAdaptiveCycle(unittest.TestCase):
    def setUp(self):
        # Reset global time to noon (daytime)
        tm = get_time_manager()
        tm.reset()
        tm.advance_simulation(12) # 12:00

        pos = torch.zeros(3)
        vel = torch.zeros(3)
        self.node = AliveLoopNode(position=pos, velocity=vel, node_id=1, spatial_dims=3)

    def test_polyphasic_sleep_trigger(self):
        """Test that high cognitive load triggers sleep even during the 'day'."""
        # 1. Ensure we are in 'active' phase during 'day'
        self.node.phase = "active"
        self.node.energy = 25.0

        # 2. Simulate baseline status
        self.node.step_phase()
        self.assertEqual(self.node.phase, "inspired")

        # 3. Inject high entropy and noise (simulating intense learning)
        self.node.current_entropy = 1.0
        self.node.gradient_noise = 1.0
        # Fill working memory to reach 1.0 buffer usage
        for i in range(self.node.working_memory.maxlen):
            self.node.working_memory.append(i)

        # 4. Step phase - should trigger micro-sleep
        self.node.step_phase()

        self.assertEqual(self.node.phase, "sleep")
        self.assertEqual(self.node.sleep_stage, "deep")

    def test_learning_window_closing(self):
        """Test that high stress/tiredness closes the learning window."""
        # Force high adenosine
        self.node.neurochemistry.adenosine = 0.9
        self.node.energy = 50.0

        # Window should be closed
        self.assertFalse(self.node.neurochemistry.learning_window_open())

        # Step phase should downgrade from 'inspired' to 'interactive'
        self.node.phase = "inspired"
        self.node.step_phase()
        self.assertEqual(self.node.phase, "interactive")

if __name__ == "__main__":
    unittest.main()
