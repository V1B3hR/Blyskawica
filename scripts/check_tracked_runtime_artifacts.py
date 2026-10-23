"""Fail CI if user-specific runtime state is added to the Git index."""

from __future__ import annotations

import subprocess
import sys
from collections.abc import Iterable

EXACT_RUNTIME_ARTIFACTS = {
    "decoy_workspace/dev_secrets.json",
    "data/cognitive_defense/episodic_memory_vault.json",
    "integrity_vault.json",
    "memory_checkpoint.json",
    "memory_checkpoint.json.bak",
    "memory_checkpoint.json.tmp",
    "blyskawica_app/memory/offline_search_cache.db",
}
RUNTIME_PREFIXES = (
    "identity_vault/",
    "blyskawica_app/memory/snapshots/",
    "blyskawica_app/memory/user_identity",
)


def find_runtime_artifact_violations(paths: Iterable[str]) -> list[str]:
    return sorted(
        path
        for path in paths
        if path in EXACT_RUNTIME_ARTIFACTS or path.startswith(RUNTIME_PREFIXES)
    )


def main() -> int:
    tracked = subprocess.run(
        ["git", "ls-files", "-z"],
        check=True,
        capture_output=True,
    ).stdout.decode("utf-8").split("\0")
    violations = find_runtime_artifact_violations(tracked)
    if not violations:
        return 0

    print("Runtime state or potential secrets must not be tracked by Git:", file=sys.stderr)
    print("\n".join(f"- {path}" for path in violations), file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
