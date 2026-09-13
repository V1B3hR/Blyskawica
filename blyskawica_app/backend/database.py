"""
[Moduł: Baza Danych SQLite Błyskawicy (database.py)]
Zarządza pamięcią podręczną wyszukiwania, metadanymi tożsamości użytkownika
oraz migawkami kognitywnymi (cognitive snapshots) w bezpiecznym trybie WAL.
"""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("BlyskawicaDatabase")


class BlyskawicaDatabase:
    """Zarządza bazą SQLite dla pamięci, cache i snapshotów Błyskawicy."""

    def __init__(self, db_path: Path | str) -> None:
        self.db_path: Path = Path(db_path)
        self._init_db()

    def _init_db(self) -> None:
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            # Crash-safe SQLite configuration
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=FULL")
            # 1. Search cache
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS search_cache (
                    query TEXT PRIMARY KEY,
                    results_json TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # 2. User metadata (DPAPI encrypted or plain)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_metadata (
                    key TEXT PRIMARY KEY,
                    value BLOB
                )
            """)
            # 3. Cognitive snapshots
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cognitive_snapshots (
                    timestamp TEXT PRIMARY KEY,
                    version TEXT,
                    data_json TEXT
                )
            """)
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Błąd inicjalizacji bazy danych SQLite: {e}")

    def get_metadata(self, key: str) -> Optional[bytes]:
        """Pobiera zaszyfrowane lub surowe metadane dla danego klucza."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM user_metadata WHERE key = ?", (key,))
            row = cursor.fetchone()
            conn.close()
            return row[0] if row else None
        except Exception as e:
            logger.error(f"Błąd odczytu metadata {key} z SQLite: {e}")
            return None

    def set_metadata(self, key: str, value: bytes) -> None:
        """Zapisuje metadane pod zadanym kluczem."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO user_metadata (key, value) VALUES (?, ?)", (key, value))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Błąd zapisu metadata {key} do SQLite: {e}")

    def add_snapshot(self, timestamp: str, version: str, data_json: str) -> None:
        """Dodaje migawkę kognitywną do historii."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO cognitive_snapshots (timestamp, version, data_json) VALUES (?, ?, ?)",
                (timestamp, version, data_json)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Błąd zapisu snapshotu {timestamp} do SQLite: {e}")

    def get_all_snapshots(self) -> List[Dict[str, Any]]:
        """Zwraca listę wszystkich zarejestrowanych snapshotów kognitywnych."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT timestamp, version, data_json FROM cognitive_snapshots ORDER BY timestamp DESC")
            rows = cursor.fetchall()
            conn.close()
            return [{"timestamp": r[0], "version": r[1], "data_json": r[2]} for r in rows]
        except Exception as e:
            logger.error(f"Błąd odczytu snapshotów z SQLite: {e}")
            return []
