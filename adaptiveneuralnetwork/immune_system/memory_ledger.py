import hashlib
import logging
import math
import time

logger = logging.getLogger(__name__)

class MemoryLedgerEntry:
    def __init__(self, index: int, timestamp: float, vector_id: int, text: str, prev_hash: str, signature: str = ""):
        self.index = index
        self.timestamp = timestamp
        self.vector_id = vector_id
        self.text = text
        self.prev_hash = prev_hash
        self.signature = signature
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        data = f"{self.index}{self.timestamp}{self.vector_id}{self.text}{self.prev_hash}{self.signature}"
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "vector_id": self.vector_id,
            "text": self.text,
            "prev_hash": self.prev_hash,
            "signature": self.signature,
            "hash": self.hash
        }

class MemoryLedger:
    def __init__(self, drift_threshold: float = 0.65, db_path: str = None):
        self.chain: list[MemoryLedgerEntry] = []
        self.drift_threshold = drift_threshold
        self.db_path = db_path

        if self.db_path:
            self._init_db()
            self._load_chain_from_db()

        # Genesis block setup
        if not self.chain:
            self._create_genesis_block()
            if self.db_path:
                self._save_entry_to_db(self.chain[0])

    def _init_db(self):
        try:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memory_ledger (
                    index_val INTEGER PRIMARY KEY,
                    timestamp REAL,
                    vector_id INTEGER,
                    text TEXT,
                    prev_hash TEXT,
                    signature TEXT,
                    hash TEXT,
                    vector_json TEXT
                )
            """)
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"[MEMORY LEDGER] SQLite initialization error: {e}")

    def _load_chain_from_db(self):
        try:
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT index_val, timestamp, vector_id, text, prev_hash, signature, hash FROM memory_ledger ORDER BY index_val ASC")
            rows = cursor.fetchall()
            conn.close()

            for row in rows:
                entry = MemoryLedgerEntry(
                    index=row[0],
                    timestamp=row[1],
                    vector_id=row[2],
                    text=row[3],
                    prev_hash=row[4],
                    signature=row[5]
                )
                entry.hash = row[6]
                self.chain.append(entry)

            if self.chain:
                logger.info(f"[MEMORY LEDGER] Loaded {len(self.chain)} entries from SQLite database.")
        except Exception as e:
            logger.error(f"[MEMORY LEDGER] Error loading chain from SQLite: {e}")

    def _save_entry_to_db(self, entry: MemoryLedgerEntry, vector: list[float] = None):
        try:
            import json
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            vector_json = json.dumps(vector) if vector is not None else "[]"
            cursor.execute(
                "INSERT OR REPLACE INTO memory_ledger (index_val, timestamp, vector_id, text, prev_hash, signature, hash, vector_json) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (entry.index, entry.timestamp, entry.vector_id, entry.text, entry.prev_hash, entry.signature, entry.hash, vector_json)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"[MEMORY LEDGER] Error saving entry to SQLite: {e}")

    def _get_all_vectors_from_db(self) -> list[list[float]]:
        try:
            import json
            import sqlite3
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT vector_json FROM memory_ledger ORDER BY index_val ASC")
            rows = cursor.fetchall()
            conn.close()

            vectors = []
            for row in rows:
                try:
                    vec = json.loads(row[0])
                    if vec:
                        vectors.append([float(x) for x in vec])
                except Exception:
                    continue
            return vectors
        except Exception as e:
            logger.error(f"[MEMORY LEDGER] Error retrieving vectors from SQLite: {e}")
            return []

    def _create_genesis_block(self):
        genesis = MemoryLedgerEntry(
            index=0,
            timestamp=time.time(),
            vector_id=0,
            text="Genesis Core Knowledge",
            prev_hash="0" * 64,
            signature="SYSTEM_INIT_SIG"
        )
        self.chain.append(genesis)

    def verify_chain_integrity(self) -> bool:
        """Weryfikuje poprawność całego łańcucha skrótów kryptograficznych."""
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            prev = self.chain[i-1]
            if current.prev_hash != prev.hash:
                logger.error(f"[MEMORY LEDGER] Łańcuch przerwany na indeksie {i}: niezgodność prev_hash!")
                return False
            if current.hash != current.calculate_hash():
                logger.error(f"[MEMORY LEDGER] Łańcuch przerwany na indeksie {i}: naruszenie integralności bloku!")
                return False
        return True

    def validate_and_append(self, vector_id: int, text: str, vector: list[float], historical_vectors: list[list[float]], signature: str = "") -> bool:
        """
        Waliduje wektor wejściowy, sprawdza dryf semantyczny (dystans cosinusowy) i dodaje wpis do rejestru.
        """
        # Jeśli mamy bazę, pobierz rzeczywiste historyczne wektory z SQLite
        if self.db_path:
            db_vectors = self._get_all_vectors_from_db()
            if db_vectors:
                historical_vectors = db_vectors

        # 1. Obliczenie dystansu cosinusowego (pure Python)
        if historical_vectors:
            def dot_product(v1, v2):
                return sum(a * b for a, b in zip(v1, v2))  # noqa: B905

            def magnitude(v):
                return math.sqrt(sum(a * a for a in v))

            max_similarity = -1.0
            for hist_vec in historical_vectors:
                mag_a = magnitude(vector)
                mag_b = magnitude(hist_vec)
                if mag_a == 0 or mag_b == 0:
                    similarity = 0.0
                else:
                    similarity = dot_product(vector, hist_vec) / (mag_a * mag_b)

                if similarity > max_similarity:
                    max_similarity = similarity

            cosine_distance = 1.0 - max_similarity

            if cosine_distance > self.drift_threshold:
                logger.warning(
                    f"[MEMORY LEDGER] 🚨 Zablokowano konsolidację z powodu dryfu semantycznego! "
                    f"Dystans: {cosine_distance:.4f} > próg: {self.drift_threshold:.4f}. Wektor skierowany do kwarantanny."
                )
                return False

        # 2. Rejestracja w blockchain-style ledger
        prev_hash = self.chain[-1].hash
        new_entry = MemoryLedgerEntry(
            index=len(self.chain),
            timestamp=time.time(),
            vector_id=vector_id,
            text=text,
            prev_hash=prev_hash,
            signature=signature
        )
        self.chain.append(new_entry)

        # Zapis do bazy danych SQLite
        if self.db_path:
            self._save_entry_to_db(new_entry, vector)

        logger.info(f"[MEMORY LEDGER] Dodano wpis: ID={vector_id}, Hash={new_entry.hash[:8]}")
        return True
