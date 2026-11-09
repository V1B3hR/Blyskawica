"""Retention boundaries for the optional legacy sidecar."""

from pathlib import Path

LEGACY_DATABASE_FILENAMES = (
    "blyskawica_memory.db",
    "blyskawica_memory.db-shm",
    "blyskawica_memory.db-wal",
)


def legacy_sidecar_data_paths(workspace_root: Path) -> tuple[Path, ...]:
    """Return only the data paths owned by the optional legacy sidecar."""
    application_root = workspace_root / "blyskawica_app"
    memory_directory = application_root / "memory"
    database_paths = tuple(memory_directory / filename for filename in LEGACY_DATABASE_FILENAMES)
    return (*database_paths, application_root / "media_storage")
