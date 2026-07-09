"""
PostgreSQL Store Implementation
Enterprise-grade relational database for team deployments
"""

import json
from typing import Any

from .base_store import BaseStore, StoreBackend

try:
    import psycopg2
    from psycopg2 import sql
    from psycopg2.extras import RealDictCursor

    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False


class PostgreSQLStore(BaseStore):
    """
    PostgreSQL implementation of the stain database

    Ideal for:
    - Team deployments with multiple users
    - Advanced SQL features (JSON, full-text search)
    - High reliability and ACID compliance
    - Horizontal scalability with replication

    Requires: psycopg2 or psycopg2-binary package
    """

    def __init__(self, config: dict[str, Any]):
        """
        Initialize PostgreSQL store

        Args:
            config: Configuration dictionary with keys:
                - host: Database host (default: localhost)
                - port: Database port (default: 5432)
                - database: Database name
                - user: Database user
                - password: Database password
        """
        super().__init__(config)
        self.backend_type = StoreBackend.POSTGRESQL

        if not PSYCOPG2_AVAILABLE:
            raise ImportError(
                "psycopg2 is required for PostgreSQL support. " "Install with: pip install psycopg2-binary"
            )

        self.connection = None
        self.cursor = None

    def connect(self) -> bool:
        """Establish connection to PostgreSQL database"""
        try:
            self.connection = psycopg2.connect(
                host=self.config.get("host", "localhost"),
                port=self.config.get("port", 5432),
                database=self.config.get("database"),
                user=self.config.get("user"),
                password=self.config.get("password"),
            )
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            self.connected = True
            return True
        except psycopg2.Error as e:
            print(f"PostgreSQL connection error: {e}")
            self.connected = False
            return False

    def disconnect(self) -> bool:
        """Close connection to PostgreSQL database"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
            self.connected = False
            return True
        except psycopg2.Error as e:
            print(f"PostgreSQL disconnection error: {e}")
            return False

    def initialize_schema(self) -> bool:
        """Initialize PostgreSQL schema"""
        try:
            # Create stains table with JSONB for efficient JSON storage
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS stains (
                    tag_id TEXT PRIMARY KEY,
                    marker_type TEXT NOT NULL,
                    color TEXT NOT NULL,
                    timestamp_first_seen TIMESTAMP NOT NULL,
                    timestamp_last_seen TIMESTAMP NOT NULL,
                    hit_count INTEGER DEFAULT 1,
                    weapon_used TEXT NOT NULL,
                    target_data JSONB NOT NULL,
                    forest_location JSONB,
                    threat_score REAL NOT NULL,
                    confidence REAL NOT NULL,
                    evidence JSONB,
                    linked_tags JSONB,
                    hunter_notes TEXT,
                    detected_by TEXT,
                    status TEXT DEFAULT 'ACTIVE_THREAT',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create indexes for common queries
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_marker_type ON stains(marker_type)
            """)
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_color ON stains(color)
            """)
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_threat_score ON stains(threat_score)
            """)
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_status ON stains(status)
            """)
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp ON stains(timestamp_first_seen)
            """)

            # Create GIN index for JSONB columns (fast JSON queries)
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_target_gin ON stains USING GIN (target_data)
            """)

            # Create full-text search index
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_text_search 
                ON stains USING GIN (to_tsvector('english', 
                    COALESCE(tag_id, '') || ' ' || 
                    COALESCE(marker_type, '') || ' ' || 
                    COALESCE(hunter_notes, '')
                ))
            """)

            self.connection.commit()
            return True
        except psycopg2.Error as e:
            print(f"Schema initialization error: {e}")
            self.connection.rollback()
            return False

    def save_stain(self, stain: dict[str, Any]) -> bool:
        """Save a stain to PostgreSQL database"""
        try:
            stain_data = stain.get("stain", {})

            self.cursor.execute(
                """
                INSERT INTO stains (
                    tag_id, marker_type, color, timestamp_first_seen, timestamp_last_seen,
                    hit_count, weapon_used, target_data, forest_location,
                    threat_score, confidence, evidence, linked_tags,
                    hunter_notes, detected_by, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (tag_id) DO UPDATE SET
                    hit_count = stains.hit_count + 1,
                    timestamp_last_seen = EXCLUDED.timestamp_last_seen,
                    updated_at = CURRENT_TIMESTAMP
            """,
                (
                    stain.get("tag_id"),
                    stain.get("marker_type"),
                    stain.get("color"),
                    stain.get("timestamp_first_seen"),
                    stain.get("timestamp_last_seen"),
                    stain.get("hit_count", 1),
                    stain.get("weapon_used"),
                    json.dumps(stain.get("target", {})),
                    json.dumps(stain.get("forest_location", {})),
                    stain_data.get("threat_score", 0.0),
                    stain_data.get("confidence", 0.0),
                    json.dumps(stain_data.get("evidence", [])),
                    json.dumps(stain_data.get("linked_tags", [])),
                    stain.get("hunter_notes", ""),
                    stain.get("detected_by", ""),
                    stain.get("status", "ACTIVE_THREAT"),
                ),
            )

            self.connection.commit()
            return True
        except psycopg2.Error as e:
            print(f"Save stain error: {e}")
            self.connection.rollback()
            return False

    def get_stain(self, tag_id: str) -> dict[str, Any] | None:
        """Retrieve a stain by tag ID"""
        try:
            self.cursor.execute("SELECT * FROM stains WHERE tag_id = %s", (tag_id,))
            row = self.cursor.fetchone()
            if row:
                return self._row_to_dict(row)
            return None
        except psycopg2.Error as e:
            print(f"Get stain error: {e}")
            return None

    def get_all_stains(self, limit: int | None = None, offset: int = 0) -> list[dict[str, Any]]:
        """Retrieve all stains with pagination"""
        try:
            query = "SELECT * FROM stains ORDER BY timestamp_first_seen DESC"
            if limit:
                query += f" LIMIT {limit} OFFSET {offset}"

            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]
        except psycopg2.Error as e:
            print(f"Get all stains error: {e}")
            return []

    def get_stains_by_type(self, marker_type: str, limit: int | None = None) -> list[dict[str, Any]]:
        """Retrieve stains filtered by marker type"""
        try:
            query = "SELECT * FROM stains WHERE marker_type = %s ORDER BY timestamp_first_seen DESC"
            if limit:
                query += f" LIMIT {limit}"

            self.cursor.execute(query, (marker_type,))
            rows = self.cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]
        except psycopg2.Error as e:
            print(f"Get stains by type error: {e}")
            return []

    def get_stains_by_color(self, color: str, limit: int | None = None) -> list[dict[str, Any]]:
        """Retrieve stains filtered by color"""
        try:
            query = "SELECT * FROM stains WHERE color = %s ORDER BY timestamp_first_seen DESC"
            if limit:
                query += f" LIMIT {limit}"

            self.cursor.execute(query, (color,))
            rows = self.cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]
        except psycopg2.Error as e:
            print(f"Get stains by color error: {e}")
            return []

    def get_stains_by_ip(self, ip: str) -> list[dict[str, Any]]:
        """Retrieve stains associated with an IP address"""
        try:
            # Use JSONB containment operator
            self.cursor.execute(
                "SELECT * FROM stains WHERE target_data @> %s ORDER BY timestamp_first_seen DESC",
                (json.dumps({"ip": ip}),),
            )
            rows = self.cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]
        except psycopg2.Error as e:
            print(f"Get stains by IP error: {e}")
            return []

    def get_stains_by_threat_score(self, min_score: float, max_score: float = 10.0) -> list[dict[str, Any]]:
        """Retrieve stains within a threat score range"""
        try:
            self.cursor.execute(
                "SELECT * FROM stains WHERE threat_score BETWEEN %s AND %s ORDER BY threat_score DESC",
                (min_score, max_score),
            )
            rows = self.cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]
        except psycopg2.Error as e:
            print(f"Get stains by threat score error: {e}")
            return []

    def update_stain(self, tag_id: str, updates: dict[str, Any]) -> bool:
        """Update an existing stain"""
        try:
            # Whitelist of allowed column names to prevent SQL injection
            allowed_columns = {
                "marker_type",
                "color",
                "timestamp_first_seen",
                "timestamp_last_seen",
                "hit_count",
                "weapon_used",
                "threat_score",
                "confidence",
                "hunter_notes",
                "detected_by",
                "status",
            }

            set_clauses = []
            values = []

            for key, value in updates.items():
                if key == "target":
                    set_clauses.append("target_data = %s")
                    values.append(json.dumps(value))
                elif key == "forest_location":
                    set_clauses.append("forest_location = %s")
                    values.append(json.dumps(value))
                elif key == "evidence":
                    set_clauses.append("evidence = %s")
                    values.append(json.dumps(value))
                elif key == "linked_tags":
                    set_clauses.append("linked_tags = %s")
                    values.append(json.dumps(value))
                elif key == "stain":
                    # Handle nested stain data with column whitelist
                    for sub_key, sub_value in value.items():
                        if sub_key in allowed_columns:
                            set_clauses.append(f"{sub_key} = %s")
                            values.append(sub_value)
                elif key in allowed_columns:
                    set_clauses.append(f"{key} = %s")
                    values.append(value)

            if not set_clauses:
                return False

            values.append(tag_id)
            query = f"UPDATE stains SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP WHERE tag_id = %s"

            self.cursor.execute(query, values)
            self.connection.commit()
            return self.cursor.rowcount > 0
        except psycopg2.Error as e:
            print(f"Update stain error: {e}")
            self.connection.rollback()
            return False

    def delete_stain(self, tag_id: str) -> bool:
        """Delete a stain from the database"""
        try:
            self.cursor.execute("DELETE FROM stains WHERE tag_id = %s", (tag_id,))
            self.connection.commit()
            return self.cursor.rowcount > 0
        except psycopg2.Error as e:
            print(f"Delete stain error: {e}")
            self.connection.rollback()
            return False

    def search_stains(self, query: str, fields: list[str] | None = None) -> list[dict[str, Any]]:
        """Search for stains using PostgreSQL full-text search"""
        try:
            # Use full-text search
            self.cursor.execute(
                """
                SELECT * FROM stains 
                WHERE to_tsvector('english', 
                    COALESCE(tag_id, '') || ' ' || 
                    COALESCE(marker_type, '') || ' ' || 
                    COALESCE(hunter_notes, '')
                ) @@ plainto_tsquery('english', %s)
                ORDER BY timestamp_first_seen DESC
            """,
                (query,),
            )

            rows = self.cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]
        except psycopg2.Error as e:
            print(f"Search stains error: {e}")
            return []

    def count_stains(self, filters: dict[str, Any] | None = None) -> int:
        """Count stains with optional filters"""
        try:
            if not filters:
                self.cursor.execute("SELECT COUNT(*) FROM stains")
            else:
                where_clauses = []
                values = []
                for key, value in filters.items():
                    where_clauses.append(f"{key} = %s")
                    values.append(value)

                query = f"SELECT COUNT(*) FROM stains WHERE {' AND '.join(where_clauses)}"
                self.cursor.execute(query, values)

            return self.cursor.fetchone()["count"]
        except psycopg2.Error as e:
            print(f"Count stains error: {e}")
            return 0

    def get_statistics(self) -> dict[str, Any]:
        """Get database statistics"""
        try:
            stats = {}

            # Total stains
            self.cursor.execute("SELECT COUNT(*) as count FROM stains")
            stats["total_stains"] = self.cursor.fetchone()["count"]

            # Stains by type
            self.cursor.execute("SELECT marker_type, COUNT(*) as count FROM stains GROUP BY marker_type")
            stats["stains_by_type"] = {row["marker_type"]: row["count"] for row in self.cursor.fetchall()}

            # Stains by color
            self.cursor.execute("SELECT color, COUNT(*) as count FROM stains GROUP BY color")
            stats["stains_by_color"] = {row["color"]: row["count"] for row in self.cursor.fetchall()}

            # Stains by status
            self.cursor.execute("SELECT status, COUNT(*) as count FROM stains GROUP BY status")
            stats["stains_by_status"] = {row["status"]: row["count"] for row in self.cursor.fetchall()}

            # Average threat score
            self.cursor.execute("SELECT AVG(threat_score) as avg_score FROM stains")
            stats["avg_threat_score"] = round(self.cursor.fetchone()["avg_score"] or 0.0, 2)

            # High threat stains
            self.cursor.execute("SELECT COUNT(*) as count FROM stains WHERE threat_score >= 8.0")
            stats["high_threat_count"] = self.cursor.fetchone()["count"]

            return stats
        except psycopg2.Error as e:
            print(f"Get statistics error: {e}")
            return {}

    def _row_to_dict(self, row: dict[str, Any]) -> dict[str, Any]:
        """Convert PostgreSQL row to stain dictionary"""
        return {
            "tag_id": row["tag_id"],
            "marker_type": row["marker_type"],
            "color": row["color"],
            "timestamp_first_seen": row["timestamp_first_seen"].isoformat() if row["timestamp_first_seen"] else None,
            "timestamp_last_seen": row["timestamp_last_seen"].isoformat() if row["timestamp_last_seen"] else None,
            "hit_count": row["hit_count"],
            "weapon_used": row["weapon_used"],
            "target": row["target_data"] if isinstance(row["target_data"], dict) else json.loads(row["target_data"]),
            "forest_location": (
                row["forest_location"]
                if isinstance(row["forest_location"], dict)
                else (json.loads(row["forest_location"]) if row["forest_location"] else {})
            ),
            "stain": {
                "threat_score": float(row["threat_score"]),
                "confidence": float(row["confidence"]),
                "evidence": (
                    row["evidence"]
                    if isinstance(row["evidence"], list)
                    else (json.loads(row["evidence"]) if row["evidence"] else [])
                ),
                "linked_tags": (
                    row["linked_tags"]
                    if isinstance(row["linked_tags"], list)
                    else (json.loads(row["linked_tags"]) if row["linked_tags"] else [])
                ),
            },
            "hunter_notes": row["hunter_notes"],
            "detected_by": row["detected_by"],
            "status": row["status"],
        }
