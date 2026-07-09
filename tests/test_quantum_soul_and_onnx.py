import unittest
import os
import torch
import json
import shutil
from unittest.mock import MagicMock
from adaptiveneuralnetwork.central_nervous_system.soul import Soul
from adaptiveneuralnetwork.central_nervous_system.ecosystem.identity_guard import IdentityGuard
from adaptiveneuralnetwork.central_nervous_system.onnx_bridge import ONNXBridge

class TestQuantumSoulAndONNX(unittest.TestCase):
    def setUp(self):
        # Mock QuantumBridge to avoid real API calls during unit tests
        self.mock_bridge = MagicMock()
        self.mock_bridge.generate_quantum_entropy.return_value = {"quantum_seed": 123456789}
        self.mock_bridge.is_connected = True
        
        # Initialize IdentityGuard
        self.guard = IdentityGuard(owner_name="Błyskawica")
        self.guard.quantum_bridge = self.mock_bridge
        
        # Initialize Soul with mocked guard
        self.soul = Soul(identity_guard=self.guard)
        self.soul.bond_strength = 0.85
        self.soul.philosophical_anchor = "Peace and Cooperation."

    def test_soul_quantum_integrity_verification(self):
        """Tests if the Soul can verify its integrity using the Quantum Bridge."""
        # The verify_quantum_integrity method creates a snapshot and checks for the hash
        is_valid = self.soul.verify_quantum_integrity()
        
        self.assertTrue(is_valid)
        
        # Check if the generated hash exists in the latest snapshot
        last_snapshot = self.soul.identity_guard.snapshots[-1]
        self.assertNotEqual(last_snapshot.get("quantum_entropy_hash"), "not_connected")

    def test_identity_snapshot_consistency(self):
        """Tests if the IdentityGuard creates consistent snapshots."""
        dummy_net = torch.nn.Linear(1, 1)
        snapshot = self.guard.capture_snapshot(
            neural_network=dummy_net,
            quantum_bridge=self.mock_bridge,
            metadata={"test": "true"}
        )
        
        self.assertEqual(snapshot["owner"], "Błyskawica")
        self.assertNotEqual(snapshot.get("quantum_entropy_hash"), "not_connected")

    def test_onnx_bridge_export(self):
        """Tests the ONNX crystallization process with a dummy model."""
        output_dir = "tests/temp_exports"
        bridge = ONNXBridge(output_dir=output_dir)
        
        # Create a simple dummy model
        class SimpleModel(torch.nn.Module):
            def __init__(self):
                super().__init__()
                self.fc = torch.nn.Linear(10, 2)
            def forward(self, x):
                return self.fc(x)
        
        model = SimpleModel()
        input_sample = torch.randn(1, 10)
        
        export_path = bridge.export_crystallized_core(model, input_sample, "test_model")
        
        self.assertIsNotNone(export_path)
        self.assertTrue(os.path.exists(export_path))
        
        # Verify integrity
        self.assertTrue(bridge.verify_onnx_integrity(export_path))
        
        # Test Cryptographic Signing & Verification
        sig_path = bridge.sign_crystallized_core(export_path)
        self.assertIsNotNone(sig_path)
        self.assertTrue(os.path.exists(sig_path))
        
        # Verify valid signature
        self.assertTrue(bridge.verify_crystallized_core_signature(export_path, sig_path))
        
        # Verify invalid signature or modified file
        with open(export_path, "ab") as f:
            f.write(b"tamper")
        self.assertFalse(bridge.verify_crystallized_core_signature(export_path, sig_path))
        
        # Cleanup
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)

    def test_soul_save_load_with_identity(self):
        """Tests saving and loading the Soul with identity markers."""
        test_path = "tests/temp_soul.json"
        self.soul.save(test_path)
        
        new_soul = Soul()
        new_soul.load(test_path)
        
        self.assertEqual(new_soul.user_name, self.soul.user_name)
        self.assertEqual(new_soul.bond_strength, self.soul.bond_strength)
        
        # Cleanup
        if os.path.exists(test_path):
            os.remove(test_path)

    def test_soul_multiuser_capping_and_damping(self):
        """Verify multi-user capping (0.45) and Architect damping logic."""
        # 1. Test Architect (Andrzej) - should grow up to 1.0 but damped
        self.soul.set_active_user("Andrzej")
        self.soul.bond_strength = 0.5
        
        # Strengthen bond
        self.soul.strengthen_bond(0.1)
        # Expected new bond = 0.5 + 0.1 * (1.0 - 0.5 * 0.4) = 0.5 + 0.1 * 0.8 = 0.58
        self.assertAlmostEqual(self.soul.bond_strength, 0.58)
        
        # Verify it can grow close to 1.0
        self.soul.bond_strength = 0.98
        self.soul.strengthen_bond(0.1)
        self.assertLessEqual(self.soul.bond_strength, 1.0)
        self.assertGreater(self.soul.bond_strength, 0.98)

        # 2. Test Other User (e.g. John) - should be capped at 0.45
        self.soul.set_active_user("John")
        self.assertEqual(self.soul.bond_strength, 0.1) # Default initial bond
        
        # Boost John's bond repeatedly
        for _ in range(50):
            self.soul.strengthen_bond(0.1)
            
        # john's bond should be strictly capped at 0.45
        self.assertEqual(self.soul.bond_strength, 0.45)

        # 3. Switch back to Architect and verify different bond strength persists
        self.soul.set_active_user("Andrzej")
        self.assertNotEqual(self.soul.bond_strength, 0.45)

if __name__ == '__main__':
    unittest.main()
