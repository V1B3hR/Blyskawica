import os
import unittest
import torch
import numpy as np
from adaptiveneuralnetwork.central_nervous_system.intelligence.quantum_intuition import QuantumIntuition, _QUANTUM_AVAILABLE

class TestQuantumAsynchronousStabilization(unittest.TestCase):
    def setUp(self):
        self.qi = QuantumIntuition()

    def test_asynchronous_phase_resolution(self):
        """Verify that update_asynchronous_phases executes and returns float lists."""
        target_angles = [1.0, 1.5, 2.0, 2.5, 3.0]
        phases = self.qi.update_asynchronous_phases(target_angles, dt=1.0)
        
        self.assertIsInstance(phases, list)
        self.assertEqual(len(phases), self.qi.NUM_QUBITS)
        for val in phases:
            self.assertIsInstance(val, float)

    def test_gli_dampening_of_oscillations(self):
        """Verify that GLI dampens wild oscillations and converges to stable values."""
        # We simulate a chaotic limit cycle (wildly alternating input signal)
        # and feed it repeatedly into update_asynchronous_phases.
        # With GLI active, the output trajectory should converge/dampen.
        
        amplitude_history = []
        
        # Step through 50 iterations of alternating signals (representing a chaotic feedback loop)
        for step in range(50):
            # Alternating stimulus: 2.0 on odd steps, -2.0 on even steps
            target = [2.0 if step % 2 == 0 else -2.0] * self.qi.NUM_QUBITS
            phases = self.qi.update_asynchronous_phases(target, dt=0.5)
            # Calculate the magnitude of the current phases
            amplitude = np.mean(np.abs(phases))
            amplitude_history.append(amplitude)

        # Check that the GLI successfully shunted the feedback energy.
        # The final amplitudes in the second half of the run should be significantly
        # lower or more stable than the initial steps due to uziemienie (VirtualGround).
        initial_mean = np.mean(amplitude_history[:10])
        final_mean = np.mean(amplitude_history[-10:])
        
        print(f"\n[GLI Verification] Initial mean amplitude: {initial_mean:.4f}")
        print(f"[GLI Verification] Final mean amplitude: {final_mean:.4f}")
        
        # Verify that the average amplitude is stabilized/damped (final < initial)
        self.assertLess(final_mean, initial_mean, "Ground Loop Isolator failed to dampen dynamic feedback loop energy.")

    @unittest.skipUnless(_QUANTUM_AVAILABLE, "Qiskit is not available")
    def test_circuit_compilation_with_asynchronous_phases(self):
        """Verify that the quantum circuit compiles cleanly with the updated phase angles."""
        from qiskit import QuantumCircuit
        
        qc = self.qi._build_circuit("Should we contact CERN QTI?")
        self.assertIsInstance(qc, QuantumCircuit)
        self.assertEqual(qc.num_qubits, self.qi.NUM_QUBITS)

if __name__ == "__main__":
    unittest.main()
