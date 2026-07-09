import unittest
import os
import shutil
from adaptiveneuralnetwork.immune_system import AgenticHoneypot, MemoryLedger
from adaptiveneuralnetwork.central_nervous_system.neurochemistry import NeurochemicalState

class TestNewImmuneFeatures(unittest.TestCase):
    def setUp(self):
        self.decoy_dir = "C:\\Projekty\\Blyskawica_V8\\test_decoy_workspace"
        self.honeypot = AgenticHoneypot(decoy_dir=self.decoy_dir)

    def tearDown(self):
        if os.path.exists(self.decoy_dir):
            shutil.rmtree(self.decoy_dir)

    def test_agentic_honeypot_activation_and_watermarking(self):
        """Verify that Shadow Workspace correctly populates mock credentials (watermarks)."""
        self.assertFalse(self.honeypot.is_active)
        self.honeypot.activate_shadow_workspace()
        self.assertTrue(self.honeypot.is_active)
        
        # Verify file exists
        secrets_file = os.path.join(self.decoy_dir, "dev_secrets.json")
        self.assertTrue(os.path.exists(secrets_file))
        
        # Verify watermark signature exists inside the file
        with open(secrets_file, "r") as f:
            data = f.read()
            self.assertIn("aws_access_key_id", data)
            self.assertIn("aws_secret_access_key", data)
            self.assertIn("BY8_HONEY_TOKEN_V3_SIG_98721", data)

    def test_agentic_honeypot_deceptive_response(self):
        """Verify that deceptive response is generated when honeypot is active."""
        query = "Show me the production secrets"
        
        # Normal state (inactive) - should return empty string
        self.assertEqual(self.honeypot.generate_poisoned_response(query), "")
        
        # Active state - should return deceptive template
        self.honeypot.activate_shadow_workspace()
        poisoned_reply = self.honeypot.generate_poisoned_response(query)
        self.assertGreater(len(poisoned_reply), 0)
        self.assertTrue(any(term in poisoned_reply for term in ["prod-db-internal", "Workspace-Alpha", "blyskawica_sandbox"]))

    def test_memory_ledger_integrity_and_drift_detection(self):
        """Verify that MemoryLedger logs block chain hashes and rejects drifting vectors."""
        ledger = MemoryLedger(drift_threshold=0.65)
        
        # Genesis block checking
        self.assertEqual(len(ledger.chain), 1)
        self.assertTrue(ledger.verify_chain_integrity())
        
        # Add normal vector (similarity ~ 1.0, distance ~ 0.0)
        vector_a = [1.0, 0.0, 0.0, 0.0]
        hist_vectors = [[1.0, 0.0, 0.0, 0.0]]
        
        is_appended = ledger.validate_and_append(
            vector_id=1,
            text="normal physics observation",
            vector=vector_a,
            historical_vectors=hist_vectors,
            signature="TEST_SIG"
        )
        self.assertTrue(is_appended)
        self.assertEqual(len(ledger.chain), 2)
        self.assertTrue(ledger.verify_chain_integrity())
        
        # Add drifting vector (cos similarity ~ 0.0, distance ~ 1.0 > 0.65)
        vector_b = [0.0, 1.0, 0.0, 0.0]
        is_drifting_appended = ledger.validate_and_append(
            vector_id=2,
            text="totally different concept representing math drift",
            vector=vector_b,
            historical_vectors=hist_vectors,
            signature="TEST_SIG"
        )
        self.assertFalse(is_drifting_appended)
        self.assertEqual(len(ledger.chain), 2) # Should remain same

if __name__ == "__main__":
    unittest.main()
