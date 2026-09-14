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

    def __init__(self, db_path: Path | str, timeout: float = 15.0) -> None:
        self.db_path: Path = Path(db_path)
        self.timeout: float = timeout
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Zwraca nowe połączenie SQLite ze skonfigurowanym timeoutem współbieżności."""
        return sqlite3.connect(str(self.db_path), timeout=self.timeout)

    def _init_db(self) -> None:
        conn = None
        try:
            conn = self._get_connection()
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
        except Exception as e:
            logger.error(f"Błąd inicjalizacji bazy danych SQLite: {e}")
        finally:
            if conn:
                conn.close()

    def get_metadata(self, key: str) -> Optional[bytes]:
        """Pobiera zaszyfrowane lub surowe metadane dla danego klucza."""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM user_metadata WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row[0] if row else None
        except Exception as e:
            logger.error(f"Błąd odczytu metadata {key} z SQLite: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def set_metadata(self, key: str, value: bytes) -> None:
        """Zapisuje metadane pod zadanym kluczem."""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO user_metadata (key, value) VALUES (?, ?)", (key, value))
            conn.commit()
        except Exception as e:
            logger.error(f"Błąd zapisu metadata {key} do SQLite: {e}")
        finally:
            if conn:
                conn.close()

    def add_snapshot(self, timestamp: str, version: str, data_json: str) -> None:
        """Dodaje migawkę kognitywną do historii."""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO cognitive_snapshots (timestamp, version, data_json) VALUES (?, ?, ?)",
                (timestamp, version, data_json)
            )
            conn.commit()
        except Exception as e:
            logger.error(f"Błąd zapisu snapshotu {timestamp} do SQLite: {e}")
        finally:
            if conn:
                conn.close()

    def get_all_snapshots(self) -> List[Dict[str, Any]]:
        """Zwraca listę wszystkich zarejestrowanych snapshotów kognitywnych."""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT timestamp, version, data_json FROM cognitive_snapshots ORDER BY timestamp DESC")
            rows = cursor.fetchall()
            return [{"timestamp": r[0], "version": r[1], "data_json": r[2]} for r in rows]
        except Exception as e:
            logger.error(f"Błąd odczytu snapshotów z SQLite: {e}")
            return []
        finally:
            if conn:
                conn.close()
