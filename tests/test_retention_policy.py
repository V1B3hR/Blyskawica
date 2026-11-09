from pathlib import Path

from blyskawica_app.backend.retention_policy import (
    LEGACY_DATABASE_FILENAMES,
    legacy_sidecar_data_paths,
)
from scripts.clear_legacy_sidecar_data import remove_regular_tree


def test_legacy_sidecar_cleanup_targets_only_owned_paths() -> None:
    workspace_root = Path("C:/workspace")

    assert legacy_sidecar_data_paths(workspace_root) == (
        *(workspace_root / "blyskawica_app" / "memory" / filename for filename in LEGACY_DATABASE_FILENAMES),
        workspace_root / "blyskawica_app" / "media_storage",
    )


def test_legacy_sidecar_cleanup_removes_regular_directory_tree(tmp_path: Path) -> None:
    storage_root = tmp_path / "media_storage"
    nested_directory = storage_root / "voices"
    nested_directory.mkdir(parents=True)
    (nested_directory / "sample.mp3").write_bytes(b"audio")

    assert remove_regular_tree(storage_root) == 3
    assert not storage_root.exists()
    assert remove_regular_tree(storage_root) == 0
