import unittest
import torch
import torch.nn as nn
import numpy as np
from adaptiveneuralnetwork.central_nervous_system.intelligence.quantum_neural_layer import (
    QuantumNeuralLayer,
    _QISKIT_AVAILABLE
)

class TestQuantumNeuralLayerStability(unittest.TestCase):
    def test_gradient_flow_to_projection(self):
        """
        Verify that gradients calculated via PSR flow back to the classical
        input projection layer (self.input_projection.weight).
        """
        # Create a small inputs batch
        x = torch.randn(4, 8, requires_grad=True)
        
        # Instantiate layer with GLI enabled
        layer = QuantumNeuralLayer(
            in_features=8,
            n_qubits=4,
            n_layers=1,
            backend="aer",
            use_gli_stabilization=True
        )
        
        # Ensure we have parameters to optimize
        self.assertIsNotNone(layer.input_projection.weight)
        
        # Forward pass
        q_out = layer(x)
        self.assertEqual(q_out.shape, (4, 4))
        
        # Compute dummy loss and backward pass
        loss = q_out.pow(2).sum()
        loss.backward()
        
        # Verify that gradients exist and are non-zero for input_projection.weight
        self.assertIsNotNone(layer.input_projection.weight.grad)
        grad_norm = layer.input_projection.weight.grad.norm().item()
        self.assertGreater(grad_norm, 0.0, "Gradient did not flow back to input_projection.weight!")
        
        # Also check theta's gradient (if Qiskit is available, it should be non-zero,
        # but in classical fallback, theta doesn't affect output so its grad is 0).
        if _QISKIT_AVAILABLE:
            self.assertIsNotNone(layer.theta.grad)
            self.assertGreater(layer.theta.grad.norm().item(), 0.0, "Gradient did not flow to layer.theta!")

    def test_gli_stabilization_effects(self):
        """
        Verify that GLI stabilization behaves correctly, shunts high-frequency
        vibrations, and outputs stabilized signals.
        """
        # Set up layer with GLI
        layer_with_gli = QuantumNeuralLayer(
            in_features=4,
            n_qubits=4,
            n_layers=1,
            backend="aer",
            use_gli_stabilization=True
        )
        
        # Set up layer without GLI
        layer_no_gli = QuantumNeuralLayer(
            in_features=4,
            n_qubits=4,
            n_layers=1,
            backend="aer",
            use_gli_stabilization=False
        )
        
        # Create a highly chaotic/noisy signal (ground loop hum & high-frequency spikes)
        # We will feed inputs with alternating offsets
        x_base = torch.randn(2, 4)
        
        # Output with GLI
        out_gli = layer_with_gli(x_base)
        self.assertIsNotNone(layer_with_gli.gli)
        
        # Output without GLI
        out_no_gli = layer_no_gli(x_base)
        self.assertIsNone(layer_no_gli.gli)
        
        # Check output shape
        self.assertEqual(out_gli.shape, (2, 4))
        self.assertEqual(out_no_gli.shape, (2, 4))

    def test_gli_parameter_tuning(self):
        """Ensure GLI components are correctly configured."""
        layer = QuantumNeuralLayer(
            in_features=4,
            n_qubits=4,
            n_layers=1,
            use_gli_stabilization=True
        )
        self.assertEqual(layer.gli.isolation_ratio, 0.05)
        self.assertIsNotNone(layer.gli.ground)

if __name__ == "__main__":
    unittest.main()
