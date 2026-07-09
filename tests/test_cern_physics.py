import unittest
import numpy as np
import math
from scripts.cern_quantum_learning import (
    SubatomicCollisionSimulator,
    TokamakMHDSolver,
    simulate_learning
)

class TestCernPhysics(unittest.TestCase):
    def setUp(self):
        self.collision_sim = SubatomicCollisionSimulator(magnetic_field_tesla=3.8)
        self.tokamak = TokamakMHDSolver(num_grid_points=30, B_toroidal=5.3)

    def test_breit_wigner_sampling(self):
        """Tests that Breit-Wigner samples group around the resonance peak."""
        mean = 91.18
        gamma = 2.49
        samples = [self.collision_sim.sample_breit_wigner(mean, gamma) for _ in range(500)]
        
        # Mean of Breit-Wigner samples should be close to nominal mean
        # (Breit-Wigner has heavy tails, so we filter out outliers for standard mean verification)
        filtered_samples = [s for s in samples if abs(s - mean) < 5 * gamma]
        self.assertGreater(len(filtered_samples), 400)
        self.assertAlmostEqual(np.mean(filtered_samples), mean, delta=0.5)

    def test_bethe_bloch_energy_loss(self):
        """Tests that Bethe-Bloch energy loss values are physically reasonable."""
        m_muon = 0.1056
        
        # Test positive energy loss for different momenta
        loss_low = self.collision_sim.simulate_bethe_bloch(momentum_gev=0.04, mass_gev=m_muon)
        loss_high = self.collision_sim.simulate_bethe_bloch(momentum_gev=2.0, mass_gev=m_muon)
        
        self.assertGreater(loss_low, 0.0)
        self.assertGreater(loss_high, 0.0)
        
        # Low momentum (near ionization peak) typically loses more energy than high momentum (minimum ionizing)
        self.assertGreater(loss_low, loss_high)
        
        # Boundary checks
        self.assertEqual(self.collision_sim.simulate_bethe_bloch(0.0, m_muon), 0.0)
        self.assertEqual(self.collision_sim.simulate_bethe_bloch(-5.0, m_muon), 0.0)

    def test_collision_event_reconstruction(self):
        """Tests Z and Higgs boson decay simulation and tracking."""
        res_z = self.collision_sim.run_collision_event("Z")
        required_keys = [
            "true_mass", "reconstructed_mass", "muon1_pt", "muon2_pt",
            "muon1_loss", "muon2_loss", "muon1_radius", "muon2_radius"
        ]
        for key in required_keys:
            self.assertIn(key, res_z)
            
        # Z mass should be physically bounded
        self.assertTrue(70.0 < res_z["true_mass"] < 110.0)
        self.assertTrue(60.0 < res_z["reconstructed_mass"] < 120.0)
        self.assertTrue(res_z["muon1_pt"] > 0.0)
        self.assertTrue(res_z["muon1_radius"] > 0.0)

        # Higgs mass should also be bounded
        res_h = self.collision_sim.run_collision_event("Higgs")
        self.assertTrue(110.0 < res_h["true_mass"] < 140.0)
        self.assertTrue(100.0 < res_h["reconstructed_mass"] < 150.0)

    def test_tokamak_safety_factor_profile(self):
        """Tests that safety factor q(r) increases radially from center to edge."""
        q = self.tokamak.compute_safety_factor()
        self.assertEqual(len(q), 30)
        
        # In a standard tokamak, q increases from the magnetic axis to the plasma boundary
        self.assertGreater(q[-1], q[0])
        # Central q should be around 1.0 - 1.5, edge q should be higher (e.g. > 3.0)
        self.assertTrue(0.5 < q[0] < 2.0)
        self.assertTrue(q[-1] > 2.5)

    def test_tokamak_mhd_diffusion_loop(self):
        """Tests poloidal magnetic field diffusion over simulation steps."""
        initial_B_theta = self.tokamak.B_theta.copy()
        
        # Step diffusion multiple times
        for _ in range(50):
            self.tokamak.step_diffusion(dt=0.01)
            
        # Magnetic field profile should diffuse and change
        self.assertFalse(np.array_equal(self.tokamak.B_theta, initial_B_theta))
        self.assertEqual(self.tokamak.B_theta[0], 0.0)  # Boundary condition preserved

    def test_tearing_mode_and_disruption(self):
        """Tests that tearing modes grow and trigger plasma disruptions."""
        # 1. Initially, no disruption
        disrupted, _ = self.tokamak.check_disruption()
        self.assertFalse(disrupted)
        
        # 2. Force tearing mode growth
        # Increase resistivity and tearing mode index to force fast disruption
        self.tokamak.delta_prime_0 = 15.0
        self.tokamak.eta.fill(1e-7)  # Stable resistivity
        self.tokamak.w_sat = 0.40    # Set saturation above disruption limit
        
        for _ in range(200):
            self.tokamak.step_rutherford_growth(dt=0.1)
            
        disrupted_after_growth, reason = self.tokamak.check_disruption()
        self.assertTrue(disrupted_after_growth)
        self.assertIn("Major Disruption", reason)

    def test_simulate_learning_run(self):
        """Tests that the main simulate_learning function runs successfully in fast_mode."""
        try:
            simulate_learning(fast_mode=True)
        except Exception as e:
            self.fail(f"simulate_learning failed in fast_mode: {e}")

if __name__ == "__main__":
    unittest.main()
