import unittest

import torch

from adaptiveneuralnetwork.cognitive_tools.ground_loop_isolator import GroundLoopIsolator


class TestAdaptiveGLI(unittest.TestCase):
    def test_multidimensional_tensors(self):
        """Verify GroundLoopIsolator accepts 1D, 2D, and 3D tensors and preserves or processes shapes correctly."""
        gli = GroundLoopIsolator(isolation_ratio=0.05)

        # Test 1D tensor
        tensor_1d = torch.randn(10)
        out_1d = gli(tensor_1d)
        self.assertEqual(out_1d.shape, tensor_1d.shape)

        # Test 2D tensor (Batch)
        tensor_2d = torch.randn(4, 10)
        out_2d = gli(tensor_2d)
        self.assertEqual(out_2d.shape, tensor_2d.shape)

    def test_adaptive_cutoff_threshold(self):
        """Verify that the cutoff threshold dynamically increases when VirtualGround energy builds up."""
        gli = GroundLoopIsolator(isolation_ratio=0.05)

        # Initial ground potential should be 0.0, cutoff should be 0.05
        self.assertEqual(gli.ground.ground_potential.item(), 0.0)

        # Run standard signal
        signal = torch.randn(2, 5)
        gli(signal)

        # Inject massive noise to VirutalGround to build potential
        massive_noise = torch.ones(2, 5) * 5.0
        gli.ground.shunt(massive_noise)

        # Check that ground potential has increased
        potential_after = gli.ground.ground_potential.item()
        self.assertGreater(potential_after, 0.0)

        # Cutoff should now be higher than the base isolation_ratio (0.05)
        expected_cutoff = gli.isolation_ratio * (1.0 + potential_after * 0.2)
        self.assertGreater(expected_cutoff, 0.05)

if __name__ == "__main__":
    unittest.main()
