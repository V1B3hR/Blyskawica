"""
MySQL Store Implementation
Widely-adopted relational database for web-scale applications
"""

import json
from typing import Any

from .base_store import BaseStore, StoreBackend

try:
    import mysql.connector
    from mysql.connector import Error

    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False


class MySQLStore(BaseStore):
    """
    MySQL implementation of the stain database

    Ideal for:
    - Web-scale applications
    - Wide hosting support
    - Proven scalability
    - Large community support

    Requires: mysql-connector-python package
    """

    def __init__(self, config: dict[str, Any]):
        """
        Initialize MySQL store

        Args:
            config: Configuration dictionary with keys:
                - host: Database host (default: localhost)
                - port: Database port (default: 3306)
                - database: Database name
                - user: Database user
                - password: Database password
        """
        super().__init__(config)
        self.backend_type = StoreBackend.MYSQL

        if not MYSQL_AVAILABLE:
            raise ImportError(
                "mysql-connector-python is required for MySQL support. "
                "Install with: pip install mysql-connector-python"
            )

        self.connection = None
        self.cursor = None

    def connect(self) -> bool:
        """Establish connection to MySQL database"""
        try:
            self.connection = mysql.connector.connect(
                host=self.config.get("host", "localhost"),
                port=self.config.get("port", 3306),
                database=self.config.get("database"),
                user=self.config.get("user"),
                password=self.config.get("password"),
            )
            self.cursor = self.connection.cursor(dictionary=True)
            self.connected = True
            return True
        except Error as e:
            print(f"MySQL connection error: {e}")
            self.connected = False
            return False

    def disconnect(self) -> bool:
        """Close connection to MySQL database"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
            self.connected = False
            return True
        except Error as e:
            print(f"MySQL disconnection error: {e}")
            return False

    def initialize_schema(self) -> bool:
        """Initialize MySQL schema"""
        try:
            # Create stains table with JSON support (MySQL 5.7+)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS stains (
                    tag_id VARCHAR(255) PRIMARY KEY,
                    marker_type VARCHAR(100) NOT NULL,
                    color VARCHAR(50) NOT NULL,
                    timestamp_first_seen DATETIME NOT NULL,
                    timestamp_last_seen DATETIME NOT NULL,
                    hit_count INT DEFAULT 1,
                    weapon_used VARCHAR(100) NOT NULL,
                    target_data JSON NOT NULL,
                    forest_location JSON,
                    threat_score FLOAT NOT NULL,
                    confidence FLOAT NOT NULL,
                    evidence JSON,
                    linked_tags JSON,
                    hunter_notes TEXT,
                    detected_by VARCHAR(100),
                    status VARCHAR(50) DEFAULT 'ACTIVE_THREAT',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_marker_type (marker_type),
                    INDEX idx_color (color),
                    INDEX idx_threat_score (threat_score),
                    INDEX idx_status (status),
                    INDEX idx_timestamp (timestamp_first_seen)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)

            self.connection.commit()
            return True
        except Error as e:
            print(f"Schema initialization error: {e}")
            self.connection.rollback()
            return False

    def save_stain(self, stain: dict[str, Any]) -> bool:
        """Save a stain to MySQL database"""
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
                ON DUPLICATE KEY UPDATE
                    hit_count = hit_count + 1,
                    timestamp_last_seen = VALUES(timestamp_last_seen)
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
        except Error as e:
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
        except Error as e:
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
        except Error as e:
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
        except Error as e:
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
        except Error as e:
            print(f"Get stains by color error: {e}")
            return []

    def get_stains_by_ip(self, ip: str) -> list[dict[str, Any]]:
        """Retrieve stains associated with an IP address"""
        try:
            # Use JSON_CONTAINS for JSON queries
            self.cursor.execute(
                "SELECT * FROM stains WHERE JSON_CONTAINS(target_data, %s, '$.ip') ORDER BY timestamp_first_seen DESC",
                (json.dumps(ip),),
            )
            rows = self.cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]
        except Error as e:
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
        except Error as e:
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
            # Note: MySQL auto-updates updated_at with ON UPDATE CURRENT_TIMESTAMP in schema
            query = f"UPDATE stains SET {', '.join(set_clauses)} WHERE tag_id = %s"

            self.cursor.execute(query, values)
            self.connection.commit()
            return self.cursor.rowcount > 0
        except Error as e:
            print(f"Update stain error: {e}")
            self.connection.rollback()
            return False

    def delete_stain(self, tag_id: str) -> bool:
        """Delete a stain from the database"""
        try:
            self.cursor.execute("DELETE FROM stains WHERE tag_id = %s", (tag_id,))
            self.connection.commit()
            return self.cursor.rowcount > 0
        except Error as e:
            print(f"Delete stain error: {e}")
            self.connection.rollback()
            return False

    def search_stains(self, query: str, fields: list[str] | None = None) -> list[dict[str, Any]]:
        """Search for stains matching a query"""
        try:
            search_query = f"%{query}%"
            self.cursor.execute(
                """
                SELECT * FROM stains 
                WHERE tag_id LIKE %s 
                   OR marker_type LIKE %s
                   OR color LIKE %s
                   OR hunter_notes LIKE %s
                ORDER BY timestamp_first_seen DESC
            """,
                (search_query, search_query, search_query, search_query),
            )

            rows = self.cursor.fetchall()
            return [self._row_to_dict(row) for row in rows]
        except Error as e:
            print(f"Search stains error: {e}")
            return []

    def count_stains(self, filters: dict[str, Any] | None = None) -> int:
        """Count stains with optional filters"""
        try:
            if not filters:
                self.cursor.execute("SELECT COUNT(*) as count FROM stains")
            else:
                where_clauses = []
                values = []
                for key, value in filters.items():
                    where_clauses.append(f"{key} = %s")
                    values.append(value)

                query = f"SELECT COUNT(*) as count FROM stains WHERE {' AND '.join(where_clauses)}"
                self.cursor.execute(query, values)

            return self.cursor.fetchone()["count"]
        except Error as e:
            print(f"Count stains error: {e}")
            return 0

    def get_statistics(self) -> dict[str, Any]:
        """Get database statistics"""
        try:
            stats = {}

            self.cursor.execute("SELECT COUNT(*) as count FROM stains")
            stats["total_stains"] = self.cursor.fetchone()["count"]

            self.cursor.execute("SELECT marker_type, COUNT(*) as count FROM stains GROUP BY marker_type")
            stats["stains_by_type"] = {row["marker_type"]: row["count"] for row in self.cursor.fetchall()}

            self.cursor.execute("SELECT color, COUNT(*) as count FROM stains GROUP BY color")
            stats["stains_by_color"] = {row["color"]: row["count"] for row in self.cursor.fetchall()}

            self.cursor.execute("SELECT status, COUNT(*) as count FROM stains GROUP BY status")
            stats["stains_by_status"] = {row["status"]: row["count"] for row in self.cursor.fetchall()}

            self.cursor.execute("SELECT AVG(threat_score) as avg_score FROM stains")
            stats["avg_threat_score"] = round(self.cursor.fetchone()["avg_score"] or 0.0, 2)

            self.cursor.execute("SELECT COUNT(*) as count FROM stains WHERE threat_score >= 8.0")
            stats["high_threat_count"] = self.cursor.fetchone()["count"]

            return stats
        except Error as e:
            print(f"Get statistics error: {e}")
            return {}

    def _row_to_dict(self, row: dict[str, Any]) -> dict[str, Any]:
        """Convert MySQL row to stain dictionary"""
        return {
            "tag_id": row["tag_id"],
            "marker_type": row["marker_type"],
            "color": row["color"],
            "timestamp_first_seen": row["timestamp_first_seen"].isoformat() if row["timestamp_first_seen"] else None,
            "timestamp_last_seen": row["timestamp_last_seen"].isoformat() if row["timestamp_last_seen"] else None,
            "hit_count": row["hit_count"],
            "weapon_used": row["weapon_used"],
            "target": json.loads(row["target_data"]) if isinstance(row["target_data"], str) else row["target_data"],
            "forest_location": (
                json.loads(row["forest_location"])
                if isinstance(row["forest_location"], str) and row["forest_location"]
                else {}
            ),
            "stain": {
                "threat_score": float(row["threat_score"]),
                "confidence": float(row["confidence"]),
                "evidence": json.loads(row["evidence"]) if isinstance(row["evidence"], str) and row["evidence"] else [],
                "linked_tags": (
                    json.loads(row["linked_tags"]) if isinstance(row["linked_tags"], str) and row["linked_tags"] else []
                ),
            },
            "hunter_notes": row["hunter_notes"],
            "detected_by": row["detected_by"],
            "status": row["status"],
        }
