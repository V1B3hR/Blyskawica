from blyskawica_app.backend.online_policy import (
    NETHICAL_AUTO_DOCK_ENV,
    explicitly_enabled,
    nethical_auto_dock_enabled,
)


def test_explicitly_enabled_accepts_only_documented_values() -> None:
    assert explicitly_enabled("1")
    assert explicitly_enabled(" true ")
    assert not explicitly_enabled(None)
    assert not explicitly_enabled("yes")
    assert not explicitly_enabled("0")


def test_nethical_auto_dock_is_disabled_without_explicit_opt_in() -> None:
    assert not nethical_auto_dock_enabled({})
    assert not nethical_auto_dock_enabled({NETHICAL_AUTO_DOCK_ENV: "false"})
    assert nethical_auto_dock_enabled({NETHICAL_AUTO_DOCK_ENV: "true"})
