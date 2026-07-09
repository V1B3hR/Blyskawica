import unittest
from experiments.quantum_integration.quantum_teleportation import run_quantum_teleportation

class TestQuantumTeleportation(unittest.TestCase):
    def test_quantum_teleportation_execution(self):
        """Verify that run_quantum_teleportation executes successfully and returns the correct dictionary format."""
        res = run_quantum_teleportation(use_gli=False)
        self.assertIsInstance(res, dict)
        self.assertIn("backend", res)
        self.assertIn("raw_counts", res)
        self.assertIn("final_counts", res)
        self.assertIn("theta", res)
        self.assertIn("seed", res)
        
        self.assertIsInstance(res["theta"], float)
        self.assertIsInstance(res["seed"], int)
        self.assertIsInstance(res["raw_counts"], dict)
        self.assertIsInstance(res["final_counts"], dict)
        
        # Verify shots sum to 100
        total_shots = sum(res["raw_counts"].values())
        self.assertEqual(total_shots, 100)

    def test_quantum_teleportation_gli_stabilization(self):
        """Verify that GLI filtering works on teleportation results and produces valid normalized counts."""
        res_with_gli = run_quantum_teleportation(use_gli=True)
        res_no_gli = run_quantum_teleportation(use_gli=False)
        
        # Both should sum to exactly 100 shots
        total_shots_gli = sum(res_with_gli["final_counts"].values())
        total_shots_no_gli = sum(res_no_gli["final_counts"].values())
        
        self.assertEqual(total_shots_gli, 100)
        self.assertEqual(total_shots_no_gli, 100)
        
        # Check that count keys are present
        self.assertIn("0", res_with_gli["final_counts"])
        self.assertIn("1", res_with_gli["final_counts"])

if __name__ == "__main__":
    unittest.main()
