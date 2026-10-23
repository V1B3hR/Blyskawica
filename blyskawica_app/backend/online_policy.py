"""Pure policy helpers for legacy network integrations."""

from collections.abc import Mapping

NETHICAL_AUTO_DOCK_ENV = "BLYSKAWICA_ENABLE_NETHICAL_AUTO_DOCK"


def explicitly_enabled(value: str | None) -> bool:
    """Return true only for the documented explicit opt-in values."""
    return value is not None and value.strip().lower() in {"1", "true"}


def nethical_auto_dock_enabled(environment: Mapping[str, str]) -> bool:
    """Keep legacy Nethical traffic off unless the operator opts in."""
    return explicitly_enabled(environment.get(NETHICAL_AUTO_DOCK_ENV))
