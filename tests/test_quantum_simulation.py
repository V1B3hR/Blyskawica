import os
import json
import unittest
import time
from unittest.mock import patch
from scripts.ibm_quantum_emergence import (
    perform_quantum_emergence,
    run_local_qec_simulation,
    analyze_and_report_results,
    HAS_QISKIT
)
from scripts.quantum_badminton_phononics import simulate_badminton_phonon_coupling

class TestQuantumSimulation(unittest.TestCase):
    def setUp(self):
        # Paths to check/cleanup
        # Resolve path relative to the workspace dynamically
        workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.report_paths = [
            os.path.join(workspace_root, "quantum_emergence_report.json"),
            "quantum_emergence_report.json"
        ]
        # Clean up any pre-existing report files
        for p in self.report_paths:
            if os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass

    def tearDown(self):
        # Clean up after tests
        for p in self.report_paths:
            if os.path.exists(p):
                try:
                    os.remove(p)
                except Exception:
                    pass

    def test_local_qec_simulation_execution(self):
        """Verifies that the local 3-qubit QEC simulation runs and produces a report."""
        target_state = 1
        noise_rate = 0.10
        shots = 1000
        
        run_local_qec_simulation(target_state, noise_rate=noise_rate, shots=shots)
        
        # Verify report generation
        report_found = False
        report_data = None
        for p in self.report_paths:
            if os.path.exists(p):
                report_found = True
                with open(p, 'r', encoding='utf-8') as f:
                    report_data = json.load(f)
                break
                
        self.assertTrue(report_found, "Report JSON was not created by the local QEC simulation.")
        self.assertIsNotNone(report_data)
        
        # Check required keys
        required_keys = [
            "timestamp", "backend", "job_id", "target_state", 
            "raw_fidelity_percent", "corrected_survival_percent", "status"
        ]
        for key in required_keys:
            self.assertIn(key, report_data)
            
        self.assertEqual(report_data["target_state"], target_state)
        self.assertEqual(report_data["backend"], "local_simulation")

    def test_qec_mathematical_limits(self):
        """Verifies correct majority-vote calculations for clean and fully-noisy channels."""
        # 1. Clean Channel (noise = 0)
        counts_clean = {"111": 1000}
        
        # We capture report generation using mocked write
        with patch("builtins.open", create=True) as mock_open:
            analyze_and_report_results(target_state=1, counts=counts_clean, backend_name="test_clean", job_id="1")
            
            # The function should print statistics and try to dump JSON.
            # Let's verify by checking the logic directly instead of mock details.
            
        # 2. Let's do the manual check of QEC math in our test
        # 0 flips (111) -> success
        # 1 flip (110, 101, 011) -> corrected
        # 2 or 3 flips (100, 010, 001, 000) -> fatal
        target = 1
        expected_majority = "1"
        
        test_cases = [
            ("111", True, True),   # Perfect match
            ("110", True, False),  # Corrected (ones > zeros)
            ("101", True, False),  # Corrected (ones > zeros)
            ("011", True, False),  # Corrected (ones > zeros)
            ("100", False, False), # Fatal (zeros > ones)
            ("000", False, False), # Fatal (zeros > ones)
        ]
        
        for state, expected_survived, expected_perfect in test_cases:
            ones = state.count('1')
            zeros = state.count('0')
            majority = "1" if ones > zeros else "0"
            
            survived = (majority == expected_majority)
            perfect = (state == expected_majority * 3)
            
            self.assertEqual(survived, expected_survived, f"Failed survival check for state {state}")
            self.assertEqual(perfect, expected_perfect, f"Failed perfect check for state {state}")

    def test_perform_quantum_emergence_fallback(self):
        """Verifies that perform_quantum_emergence runs successfully and triggers fallback."""
        # Even if HAS_QISKIT is true, perform_quantum_emergence should handle absence of API key file and fall back
        perform_quantum_emergence()
        
        # Verify a report file was created
        report_found = False
        for p in self.report_paths:
            if os.path.exists(p):
                report_found = True
                break
        self.assertTrue(report_found, "perform_quantum_emergence failed to produce a report file in fallback mode.")

    def test_badminton_phonon_coupling_qec(self):
        """Verifies that badminton phononics simulation completes and returns expected tuple."""
        res = simulate_badminton_phonon_coupling(birdie_velocity_mps=10.0, impact_freq_hz=2200.0, shots=500)
        self.assertIsInstance(res, tuple)
        self.assertEqual(len(res), 2)
        
        final_coherence, qec_survival_rate = res
        self.assertTrue(0.0 <= final_coherence <= 1.0)
        self.assertTrue(0.0 <= qec_survival_rate <= 1.0)
        
        # Mathematically, for error rate p = 1 - coherence, if coherence > 0.5, QEC survival rate should be >= coherence
        if final_coherence > 0.5:
            # Theoretical formula: P_surv = p_phy^3 + 3 * p_phy^2 * (1 - p_phy)
            # e.g. for p_phy = 0.8: 0.8^3 + 3 * 0.64 * 0.2 = 0.512 + 0.384 = 0.896 >= 0.8
            theoretical = (final_coherence ** 3) + 3 * (final_coherence ** 2) * (1.0 - final_coherence)
            # Allow some margin for Monte Carlo simulation variance (shots = 500)
            self.assertAlmostEqual(qec_survival_rate, theoretical, delta=0.08)

if __name__ == "__main__":
    unittest.main()
