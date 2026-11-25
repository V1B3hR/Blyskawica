from blyskawica_app.backend.permission_policy import (
    permission_change_requires_consent,
    permission_elevation_message,
)


def test_permission_elevation_requires_consent() -> None:
    assert permission_change_requires_consent(1, 3)
    assert permission_elevation_message(3) == (
        "Błyskawica wymaga pełnego dostępu do systemu operacyjnego "
        "(Poziom 3). Czy chcesz zezwolić na tę operację?"
    )


def test_permission_reduction_does_not_require_consent() -> None:
    assert not permission_change_requires_consent(3, 1)
