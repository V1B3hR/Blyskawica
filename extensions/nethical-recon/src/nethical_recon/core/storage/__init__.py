"""Storage layer for Nethical Recon.

This module provides SQLAlchemy ORM models, database session management,
and repository pattern for data access.
"""

from __future__ import annotations

from .database import Database, DatabaseConfig, get_database, init_database
from .models import (
    AssetModel,
    Base,
    EvidenceModel,
    FindingModel,
    IOCModel,
    ScanJobModel,
    TargetModel,
    ToolRunModel,
)
from .repository import (
    AssetRepository,
    EvidenceRepository,
    FindingRepository,
    IOCRepository,
    ScanJobRepository,
    TargetRepository,
    ToolRunRepository,
)

__all__ = [
    # Database
    "Database",
    "DatabaseConfig",
    "get_database",
    "init_database",
    # ORM Models
    "Base",
    "TargetModel",
    "ScanJobModel",
    "ToolRunModel",
    "EvidenceModel",
    "FindingModel",
    "AssetModel",
    "IOCModel",
    # Repositories
    "TargetRepository",
    "ScanJobRepository",
    "ToolRunRepository",
    "EvidenceRepository",
    "FindingRepository",
    "AssetRepository",
    "IOCRepository",
]
