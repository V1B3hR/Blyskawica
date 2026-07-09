"""Database session management and configuration."""

from __future__ import annotations

import os
from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .models import Base


class DatabaseConfig:
    """Database configuration."""

    def __init__(self, database_url: str | None = None):
        """Initialize database configuration.

        Args:
            database_url: Database URL. Defaults to SQLite in current directory.
        """
        self.database_url = database_url or os.getenv("NETHICAL_DATABASE_URL", "sqlite:///./nethical_recon.db")


class Database:
    """Database management class."""

    def __init__(self, config: DatabaseConfig | None = None):
        """Initialize database.

        Args:
            config: Database configuration.
        """
        self.config = config or DatabaseConfig()
        self.engine = create_engine(
            self.config.database_url,
            echo=os.getenv("NETHICAL_DEBUG", "").lower() in ("1", "true", "yes"),
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def create_tables(self) -> None:
        """Create all tables in the database."""
        Base.metadata.create_all(bind=self.engine)

    def drop_tables(self) -> None:
        """Drop all tables in the database."""
        Base.metadata.drop_all(bind=self.engine)

    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        """Provide a transactional scope for database operations.

        Yields:
            Database session.
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


# Global database instance
_db: Database | None = None


def get_database() -> Database:
    """Get or create global database instance.

    Returns:
        Database instance.
    """
    global _db
    if _db is None:
        _db = Database()
    return _db


def init_database(config: DatabaseConfig | None = None) -> Database:
    """Initialize database with optional configuration.

    Args:
        config: Database configuration.

    Returns:
        Initialized database instance.
    """
    global _db
    _db = Database(config)
    _db.create_tables()
    return _db
