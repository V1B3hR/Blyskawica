import os
import unittest
import time
from unittest.mock import MagicMock
from adaptiveneuralnetwork.central_nervous_system.intelligence.quantum_watchdog import (
    QuantumIntegrityWatchdog,
    WatchdogConfig,
    IntegritySnapshot
)

class TestQuantumWatchdog(unittest.TestCase):
    def setUp(self):
        # Use a temporary vault file to avoid overwriting production integrity logs
        workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.temp_vault = os.path.join(workspace_root, "test_integrity_vault.json")
        if os.path.exists(self.temp_vault):
            try:
                os.remove(self.temp_vault)
            except Exception:
                pass

        self.config = WatchdogConfig(
            n_qubits=4,
            vault_path=self.temp_vault,
            drift_sigma_threshold=2.0
        )
        self.identity_guard_mock = MagicMock()
        self.watchdog = QuantumIntegrityWatchdog(
            config=self.config,
            identity_guard=self.identity_guard_mock
        )

    def tearDown(self):
        if os.path.exists(self.temp_vault):
            try:
                os.remove(self.temp_vault)
            except Exception:
                pass

    def test_classical_fallback_drift_generation(self):
        """Verify that the classical fallback simulates dynamic expectation values and computes drift."""
        # Force offline/fallback mode by clearing service connection
        self.watchdog.service = None
        
        # Run three audits to build history (drift metrics require at least 3 historical runs)
        snap1 = self.watchdog.run_single_audit()
        snap2 = self.watchdog.run_single_audit()
        snap3 = self.watchdog.run_single_audit()
        
        # Verify basic properties
        self.assertEqual(snap1.backend, "simulated_fallback")
        self.assertEqual(len(snap1.expectation_vector), 4)
        self.assertNotEqual(snap1.expectation_vector, [0.0] * 4)
        
        # Verify that successive runs update history and build drift measurements
        self.assertEqual(len(self.watchdog.history), 3)
        self.assertTrue(os.path.exists(self.temp_vault))
        
        # Run a 4th audit and verify we calculate some drift metric
        snap4 = self.watchdog.run_single_audit()
        self.assertIsInstance(snap4.drift_sigma, float)

    def test_gli_damps_simulated_noise_spikes(self):
        """Verify that GLI handles moderate/transient noise spikes and keeps DEFCON at 2."""
        # 1. Establish a stable history of close to 0.0 values
        self.watchdog.history = [
            IntegritySnapshot(time.time(), "sim", "1", [0.01, 0.01, 0.01, 0.01], "fp", 1),
            IntegritySnapshot(time.time(), "sim", "2", [-0.01, -0.01, -0.01, -0.01], "fp2", 1),
            IntegritySnapshot(time.time(), "sim", "3", [0.0, 0.0, 0.0, 0.0], "fp3", 1),
        ]
        
        # 2. Mock a transient spike (hum) in run_single_audit by overriding run_circuit logic
        # Here we simulate an audit returning [0.08, 0.08, 0.08, 0.08] (hum offset)
        # Without GLI, a spike of 0.08 relative to mean=0, std=0.01 yields a huge sigma drift of ~8σ.
        # But with GLI (isolation_ratio=0.05), the hum [0.08, 0.08, 0.08, 0.08] will have
        # mean=0.08. Since input_signal - hum = 0, the noise_mask selects all elements, shunting them to Ground.
        # The GLI stabilized signal will be close to 0.0, keeping stabilized_drift low.
        
        # We manually inject the vector and run the calculation part of run_single_audit:
        evs = [0.08, 0.08, 0.08, 0.08]
        
        # Run the audit logic using the internal steps
        raw_drift = self.watchdog._compute_drift(evs)
        
        # Verify raw drift is high (above threshold of 2.0)
        self.assertGreater(raw_drift, self.config.drift_sigma_threshold)
        
        # Stabilize with GLI
        import torch
        evs_tensor = torch.tensor(evs, dtype=torch.float32).unsqueeze(0)
        stabilized_tensor = self.watchdog.gli(evs_tensor).squeeze(0)
        stabilized_evs = stabilized_tensor.tolist()
        stabilized_drift = self.watchdog._compute_drift(stabilized_evs)
        
        # Verify GLI successfully isolated and damped the hum
        self.assertLess(stabilized_drift, self.config.drift_sigma_threshold)
        
        # Verify the DEFCON logic resolves to DEFCON 2 (WATCH) instead of 3/4
        # (This matches the logic inside run_single_audit)
        raw_anomaly = raw_drift > self.config.drift_sigma_threshold
        stabilized_anomaly = stabilized_drift > self.config.drift_sigma_threshold
        
        if stabilized_anomaly:
            defcon = 3
        elif raw_anomaly:
            defcon = 2
        else:
            defcon = 1
            
        self.assertEqual(defcon, 2, "GLI did not clamp the transient hum spike to DEFCON 2!")

    def test_gli_severe_drift_escalation(self):
        """Verify that severe drift (non-uniform/massive) still escalates to DEFCON 4."""
        self.watchdog.history = [
            IntegritySnapshot(time.time(), "sim", "1", [0.0, 0.0, 0.0, 0.0], "fp", 1),
            IntegritySnapshot(time.time(), "sim", "2", [0.0, 0.0, 0.0, 0.0], "fp2", 1),
            IntegritySnapshot(time.time(), "sim", "3", [0.0, 0.0, 0.0, 0.0], "fp3", 1),
        ]
        
        # A massive non-uniform drift that cannot be isolated as uniform hum
        # e.g., one qubit is completely stuck or flipped
        evs = [0.99, -0.99, 0.99, -0.99]
        
        # Compute stabilized
        import torch
        evs_tensor = torch.tensor(evs, dtype=torch.float32).unsqueeze(0)
        stabilized_tensor = self.watchdog.gli(evs_tensor).squeeze(0)
        stabilized_evs = stabilized_tensor.tolist()
        stabilized_drift = self.watchdog._compute_drift(stabilized_evs)
        
        # Verify stabilized drift is still extremely high (exceeds threshold * 2)
        self.assertGreater(stabilized_drift, self.config.drift_sigma_threshold * 2)
        
        # Verify it resolves to DEFCON 4
        raw_drift = self.watchdog._compute_drift(evs)
        raw_anomaly = raw_drift > self.config.drift_sigma_threshold
        stabilized_anomaly = stabilized_drift > self.config.drift_sigma_threshold
        
        if stabilized_anomaly:
            if stabilized_drift > self.config.drift_sigma_threshold * 2:
                defcon = 4
            else:
                defcon = 3
        elif raw_anomaly:
            defcon = 2
        else:
            defcon = 1
            
        self.assertEqual(defcon, 4, "GLI incorrectly suppressed a severe, non-uniform system compromise!")

    def test_watchdog_thread_control(self):
        """Verify starting and stopping the continuous audit thread runs cleanly."""
        self.watchdog.config.check_interval_sec = 1  # Fast check interval
        self.watchdog.start_continuous()
        self.assertTrue(self.watchdog._thread.is_alive())
        
        # Let it run for a short moment
        time.sleep(0.5)
        self.watchdog.stop()
        self.watchdog._thread.join(timeout=2.0)
        self.assertFalse(self.watchdog._thread.is_alive())

if __name__ == "__main__":
    unittest.main()
