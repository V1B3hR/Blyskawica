from scripts.check_tracked_runtime_artifacts import find_runtime_artifact_violations


def test_runtime_artifact_guard_blocks_known_sensitive_state() -> None:
    paths = [
        "README.md",
        "identity_vault/local-secret.enc",
        "blyskawica_app/memory/snapshots/session.json",
        "blyskawica_app/memory/user_identity.json",
        "data/cognitive_defense/episodic_memory_vault.json",
    ]

    assert find_runtime_artifact_violations(paths) == [
        "blyskawica_app/memory/snapshots/session.json",
        "blyskawica_app/memory/user_identity.json",
        "data/cognitive_defense/episodic_memory_vault.json",
        "identity_vault/local-secret.enc",
    ]
