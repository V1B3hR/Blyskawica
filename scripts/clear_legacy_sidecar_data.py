"""Explicit cleanup for data owned by the optional legacy Python sidecar."""

from __future__ import annotations

import argparse
import stat
import sys
from pathlib import Path

from blyskawica_app.backend.retention_policy import legacy_sidecar_data_paths

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def remove_regular_tree(path: Path) -> int:
    """Remove a regular file or directory tree without following symbolic links."""
    try:
        metadata = path.lstat()
    except FileNotFoundError:
        return 0

    if stat.S_ISLNK(metadata.st_mode):
        raise ValueError(f"Refusing to remove symbolic link: {path}")
    if stat.S_ISREG(metadata.st_mode):
        path.unlink()
        return 1
    if not stat.S_ISDIR(metadata.st_mode):
        raise ValueError(f"Refusing to remove unsupported filesystem entry: {path}")

    removed_count = 0
    for child in path.iterdir():
        removed_count += remove_regular_tree(child)
    path.rmdir()
    return removed_count + 1


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Remove only data owned by the optional legacy Blyskawica sidecar.",
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        default=PROJECT_ROOT,
        help="Repository workspace that contains blyskawica_app (default: this repository).",
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Required acknowledgement for this irreversible operation.",
    )
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    if not arguments.confirm:
        print("Refusing to delete data without --confirm.", file=sys.stderr)
        return 2

    workspace_root = arguments.workspace.resolve()
    expected_application_root = (workspace_root / "blyskawica_app").resolve()
    if not expected_application_root.is_dir():
        print("Refusing to delete: workspace does not contain blyskawica_app.", file=sys.stderr)
        return 2

    removed_count = 0
    try:
        for data_path in legacy_sidecar_data_paths(workspace_root):
            resolved_parent = data_path.parent.resolve()
            if expected_application_root not in (resolved_parent, *resolved_parent.parents):
                raise ValueError("Refusing to delete a path outside blyskawica_app.")
            removed_count += remove_regular_tree(data_path)
    except (OSError, ValueError) as error:
        print(f"Legacy sidecar cleanup failed: {error}", file=sys.stderr)
        return 1

    print(f"Removed {removed_count} legacy sidecar filesystem entries.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
