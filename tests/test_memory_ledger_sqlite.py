import os
import sqlite3
import tempfile
import unittest

from adaptiveneuralnetwork.immune_system import MemoryLedger


class TestMemoryLedgerSQLite(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_ledger.db")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_sqlite_initialization_and_genesis(self):
        """Verify that memory_ledger table is initialized and genesis block is saved."""
        ledger = MemoryLedger(db_path=self.db_path)  # noqa: F841

        # Verify db file exists
        self.assertTrue(os.path.exists(self.db_path))

        # Verify tables and genesis entry exists in DB
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='memory_ledger';")
        self.assertIsNotNone(cursor.fetchone())

        cursor.execute("SELECT index_val, text, prev_hash FROM memory_ledger;")
        row = cursor.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[0], 0)
        self.assertEqual(row[1], "Genesis Core Knowledge")
        self.assertEqual(row[2], "0" * 64)
        conn.close()

    def test_validation_with_persisted_history(self):
        """Verify memory ledger correctly loads history from DB and performs drift detection."""
        # 1. Instantiate ledger, append a block
        ledger1 = MemoryLedger(drift_threshold=0.65, db_path=self.db_path)

        vector_a = [1.0, 0.0, 0.0, 0.0]
        appended1 = ledger1.validate_and_append(
            vector_id=10,
            text="First observation",
            vector=vector_a,
            historical_vectors=[],  # Will be ignored since it loads from db
            signature="SIG1"
        )
        self.assertTrue(appended1)
        self.assertEqual(len(ledger1.chain), 2)

        # 2. Re-instantiate ledger (simulating restart)
        ledger2 = MemoryLedger(drift_threshold=0.65, db_path=self.db_path)
        self.assertEqual(len(ledger2.chain), 2)

        # 3. Try to append matching vector (should pass)
        vector_match = [0.99, 0.0, 0.0, 0.0]
        appended_match = ledger2.validate_and_append(
            vector_id=11,
            text="Matching observation",
            vector=vector_match,
            historical_vectors=[],
            signature="SIG2"
        )
        self.assertTrue(appended_match)

        # 4. Try to append drifting vector (should fail due to cosine distance > 0.65 w.r.t loaded history)
        vector_drift = [0.0, 1.0, 0.0, 0.0]
        appended_drift = ledger2.validate_and_append(
            vector_id=12,
            text="Drifting observation",
            vector=vector_drift,
            historical_vectors=[],
            signature="SIG3"
        )
        self.assertFalse(appended_drift)

if __name__ == "__main__":
    unittest.main()
