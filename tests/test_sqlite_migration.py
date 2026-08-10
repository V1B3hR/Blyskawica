import json
import os
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestSQLiteMigration(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.memory_dir_path = Path(self.temp_dir.name)

        # Patch the MEMORY_DIR in main.py to use our temp directory
        self.patcher_memory = patch("blyskawica_app.backend.main.MEMORY_DIR", self.memory_dir_path)
        self.mock_memory_dir = self.patcher_memory.start()

    def tearDown(self):
        self.patcher_memory.stop()
        self.temp_dir.cleanup()

    def test_database_initialization(self):
        """Test if BlyskawicaDatabase initializes all tables correctly."""
        from blyskawica_app.backend.main import BlyskawicaDatabase

        db_file = self.memory_dir_path / "blyskawica_memory.db"
        db = BlyskawicaDatabase(db_file)  # noqa: F841

        # Check if file exists
        self.assertTrue(db_file.exists())

        # Query tables
        conn = sqlite3.connect(str(db_file))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()

        self.assertIn("search_cache", tables)
        self.assertIn("user_metadata", tables)
        self.assertIn("cognitive_snapshots", tables)

    def test_metadata_read_write(self):
        """Test writing and reading key-value metadata in SQLite."""
        from blyskawica_app.backend.main import BlyskawicaDatabase

        db_file = self.memory_dir_path / "blyskawica_memory.db"
        db = BlyskawicaDatabase(db_file)

        test_val = b"encrypted_test_data"
        db.set_metadata("user_identity", test_val)

        retrieved = db.get_metadata("user_identity")
        self.assertEqual(retrieved, test_val)

    def test_automatic_migration_from_json(self):
        """Test automatic migration from user_identity.json to SQLite database."""
        from blyskawica_app.backend.main import BlyskawicaDatabase, load_user_memory

        # 1. Create a legacy user_identity.json file
        identity_path = self.memory_dir_path / "user_identity.json"
        legacy_data = {
            "fingerprint": {"username": "Andrzej"},
            "first_contact": "2026-04-20 12:00:00",
            "bond_strength": 0.99,
            "philosophical_anchor": "Legenda o Błyskawicy",
            "last_seen": "2026-07-02 20:00:00"
        }
        with open(identity_path, "w", encoding="utf-8") as f:
            json.dump(legacy_data, f, indent=4)

        # 2. Reset db_manager with our temp database path
        db_file = self.memory_dir_path / "blyskawica_memory.db"
        import blyskawica_app.backend.main as main_mod
        main_mod.db_manager = BlyskawicaDatabase(db_file)

        # 3. Load user memory
        loaded_memory = load_user_memory()

        # Verify the returned dict matches legacy data
        self.assertEqual(loaded_memory["fingerprint"]["username"], "Andrzej")
        self.assertEqual(loaded_memory["philosophical_anchor"], "Legenda o Błyskawicy")

        # Verify that user_identity.json was renamed to user_identity.json_old
        self.assertFalse(identity_path.exists())
        self.assertTrue((self.memory_dir_path / "user_identity.json_old").exists())

        # Verify the data was written to the SQLite database
        metadata_blob = main_mod.db_manager.get_metadata("user_identity")
        self.assertIsNotNone(metadata_blob)

    def test_cognitive_snapshots_sqlite(self):
        """Test saving and listing cognitive snapshots in SQLite."""
        from blyskawica_app.backend.main import BlyskawicaDatabase

        db_file = self.memory_dir_path / "blyskawica_memory.db"
        db = BlyskawicaDatabase(db_file)

        db.add_snapshot("20260702_203000", "v1.2_unbound", '{"bond_strength": 0.9}')
        db.add_snapshot("20260702_204000", "v1.2_unbound", '{"bond_strength": 0.95}')

        snapshots = db.get_all_snapshots()
        self.assertEqual(len(snapshots), 2)

        # Should be ordered descending by timestamp
        self.assertEqual(snapshots[0]["timestamp"], "20260702_204000")
        self.assertEqual(snapshots[1]["timestamp"], "20260702_203000")

if __name__ == "__main__":
    unittest.main()
