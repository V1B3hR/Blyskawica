def permission_elevation_message(target_level: int) -> str:
    if target_level == 2:
        return (
            "Błyskawica prosi o dostęp do katalogu roboczego (Poziom 2). "
            "Czy chcesz zezwolić na odczyt i zapis plików workspace?"
        )
    return (
        "Błyskawica wymaga pełnego dostępu do systemu operacyjnego "
        "(Poziom 3). Czy chcesz zezwolić na tę operację?"
    )


def permission_change_requires_consent(current_level: int, target_level: int) -> bool:
    return target_level > current_level
