# ADR 0002: Samodzielny runtime Rust dla SPARKLE

## Stan

**ZAAKCEPTOWANE — 2026-10-20**

## Kontekst

ADR 0001 ustanowił Tauri jako jedyną powłokę użytkownika, ale zachował uruchamiany w tle Python/FastAPI jako część ścieżki aplikacyjnej. Powoduje to różne stany pomiędzy systemami, lokalny port HTTP i niemożność wiarygodnego zadeklarowania samodzielnego działania offline.

## Decyzja

SPARKLE ma własny, samodzielny runtime Rust/Tauri. Standardowy start nie uruchamia Pythona, FastAPI ani sidecara i nie wymaga Internetu. Python pozostaje toolchainem do treningu, eksperymentów, konwersji modeli oraz przejściowej kompatybilności deweloperskiej.

Sidecar można uruchomić tylko przez jawną zmienną `SPARKLE_ENABLE_SIDECAR=true` lub `SPARKLE_ENABLE_SIDECAR=1`. Nie należy dodawać nowych funkcji produktu wyłącznie do endpointów FastAPI.

Tryb online będzie osobnym, opcjonalnym mechanizmem łączników z widoczną zgodą użytkownika. Nie może być zależnością startu, inference lokalnego, workspace ani pamięci.

## Konsekwencje

- część ADR 0001 dotycząca stałego, tła FastAPI jest zastąpiona przez niniejszą decyzję;
- frontend `blyskawica_app/frontend` i endpointy `/api/*` są ścieżką legacy/deweloperską, aż do jawnego wycofania;
- wymagane są przenośne abstrakcje systemowe dla Windows 11, Linuxa i macOS;
- release SPARKLE musi przejść test uruchomienia bez Pythona i bez ruchu sieciowego w trybie offline.

## Powiązania

- [ADR 0001: Single Shell Decision](0001-single-shell-decision.md)
- [Kontrakt samodzielnego runtime SPARKLE](../technical/SPARKLE_RUNTIME_CONTRACT.md)
- [Zaakceptowany plan rozwoju](../planning/2026-10-development-plan.md)
