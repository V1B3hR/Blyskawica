# Kontrakt samodzielnego runtime SPARKLE

> **Status:** aktywny — RNT-01 zakończone, wersja 1, 2026-10-20  
> **Źródło strategii:** [zaakceptowany plan rozwoju i remediacji](../planning/2026-10-development-plan.md)  
> **Zakres:** kontrakt produktu desktopowego; nie jest specyfikacją narzędzi treningowych Python.

## Cel

SPARKLE jest kanoniczną aplikacją Błyskawicy dla Windows 11, Linuxa i macOS. Po instalacji uruchamia się oraz realizuje podstawowy przepływ pracy bez interpretera Python, serwera FastAPI, lokalnego HTTP ani Internetu. Python jest zachowany jako oddzielny toolchain do treningu, badań i przygotowania artefaktów modeli.

## Granica runtime

| Warstwa | Odpowiedzialność w produkcie | Zależność od Pythona |
|---|---|---|
| `sparkle_app/src/` | interfejs desktopowy i wywołania IPC | brak |
| `sparkle_app/src-tauri/` | lifecycle aplikacji, uprawnienia, workspace, konfiguracja, łączniki | brak w ścieżce podstawowej |
| `blyskawica_core/` | silnik, pamięć wektorowa, bezpieczeństwo i moduły kognitywne Rust | brak |
| lokalne artefakty modeli | inference offline, tokenizery i dane aplikacji | brak po przygotowaniu release'u |
| `adaptiveneuralnetwork/`, `blyskawica_app/` | trening, eksperymenty, konwersje i kompatybilność przejściowa | tylko środowisko deweloperskie |

Pythonowy sidecar jest **wyłączony domyślnie**. Może zostać uruchomiony wyłącznie w kompatybilnym środowisku deweloperskim przez `SPARKLE_ENABLE_SIDECAR=true` albo `SPARKLE_ENABLE_SIDECAR=1`. Nie jest elementem kryterium wydania SPARKLE.

Frontend Tauri ma politykę CSP bez wpisów `localhost` i zewnętrznych hostów. Komunikacja online może przejść wyłącznie przez zatwierdzony rejestr ONL-01: tryb offline jest domyślny, a tryb online i zgoda na konkretny łącznik są tymczasowe dla sesji oraz wymagają L2 i natywnego potwierdzenia. Zgodny sidecar komunikuje się wewnętrznie z Rustem tylko wtedy, gdy został jawnie włączony; jego odczyt statusu loopback wymaga dodatkowo zgody rejestru.

## Zweryfikowana mapa granicy

### Aktualna ścieżka SPARKLE

| Przepływ użytkownika | Wykonawca | Stan docelowy |
|---|---|---|
| uruchomienie silnika, wiadomości i zdarzenia | komendy Tauri `start_engine`, `send_user_message`, `get_engine_status` | Rust, offline |
| workspace: lista, odczyt, zapis i eksport | komendy Tauri `list_workspace_files`, `read_workspace_file`, `write_workspace_file`, `export_logs` | Rust, sandboxed |
| uprawnienia, telemetryka i modele lokalne | Tauri + `blyskawica_core` | Rust, za zgodą użytkownika |
| pamięć wektorowa, Aegis, Shadow Forge, Quantum | `blyskawica_core` przez Tauri IPC | Rust, offline |
| status FastAPI | opcjonalne odpytywanie tylko po jawnym uruchomieniu sidecara | kompatybilność deweloperska, nie wymaganie produktu |

### Starsza ścieżka FastAPI

`blyskawica_app/frontend/` jest niezależnym frontendem HTTP i używa endpointów `/api/*`. Nie jest wywoływany przez bieżący frontend `sparkle_app/src/`. Endpointy klasyfikujemy następująco:

| Klasa | Endpointy FastAPI | Decyzja |
|---|---|---|
| funkcje desktopowe już pokryte przez Rust | status, chat, poziom uprawnień, pliki IDE, zapis, logi, akcje systemowe | utrzymać tylko jako kompatybilność do czasu wycofania frontendu HTTP; nie rozszerzać |
| opcjonalne łączniki online | `/api/internet/search`, `/api/cloud/backup`, auto-docking Nethical, integracje Ollama/TTS | przenieść dopiero do jawnego rejestru łączników ONL-01; legacy auto-docking Nethical jest domyślnie wyłączony i wymaga `BLYSKAWICA_ENABLE_NETHICAL_AUTO_DOCK=1/true` |
| narzędzia rozwojowe lub badawcze | analiza kodu, krystalizacja ONNX, trening i symulacje | pozostawić w Python toolchain albo zaprojektować osobny kontrakt CLI/API |
| wejście danych użytkownika | upload mediów | legacy endpoint wymaga tokenu sesyjnego i ma tymczasowy limit 25 MiB; ponownie zaprojektować w Rust po klasyfikacji danych i polityce retencji PRIV-01 |

Szczegóły rejestru, jego granic i stanu wdrożenia opisuje [kontrakt łączników online](ONLINE_CONNECTOR_CONTRACT.md). Rejestr nie daje jeszcze transportu zdalnego ani nie kontroluje osobno uruchomionych procesów legacy.

## Kontrakt trybów połączenia

| Tryb | Domyślny | Sieć | Obowiązkowa funkcja |
|---|---|---|---|
| Offline | tak | zablokowana lub niedostępna | lokalny model, workspace, pamięć, ustawienia i UI pozostają użyteczne |
| Online | nie | tylko przez zatwierdzony łącznik | UI pokazuje usługę, zakres danych i umożliwia cofnięcie zgody |
| Deweloperski sidecar | nie | lokalny HTTP wyłącznie po `SPARKLE_ENABLE_SIDECAR=true` | nie jest wymagany do działania produktu ani testu offline |

## Kolejność migracji

1. Utrwalić samodzielny start Rust/Tauri i przetestować go bez procesu Python.
2. Usunąć z krytycznej ścieżki statusu założenie, że FastAPI istnieje; zachować jedynie diagnostykę kompatybilności.
3. Zaprojektować rejestr łączników online wraz z kontraktami danych i zgodą użytkownika.
4. Rozdzielić artefakty release'u od Python toolchain oraz uruchomić natywne testy na Windows 11, Linuxie i macOS.
5. Dopiero po zakończeniu powyższych kroków podjąć decyzję o wycofaniu legacy frontend/API FastAPI.

## Kryteria akceptacji RNT-01

- zdefiniowana jest granica produktowa Rust/Python oraz los każdego aktywnego endpointu FastAPI;
- standardowy start nie tworzy procesu Python;
- test regresji dowodzi, że sidecar może zostać uruchomiony wyłącznie po jawnym opt-in;
- portal dokumentacji prowadzi do tego kontraktu i planu rozwoju.

## Stan weryfikacji

- **2026-10-20:** `cargo test --locked --manifest-path sparkle_app/src-tauri/Cargo.toml` — 5 testów zaliczonych, w tym domyślnie wyłączony sidecar, potwierdzenie awansu uprawnień oraz ukrycie ścieżki workspace na L1.
- **2026-10-22:** przegląd SEC-01 objął wszystkie zarejestrowane komendy IPC; test resolvera obejmuje również nowy plik zagnieżdżony, a `rustfmt --check --edition 2021 sparkle_app/src-tauri/src/lib.rs` jest zielony. Świeże wykonanie `cargo test` pozostaje niezweryfikowane lokalnie, ponieważ Windows Application Control blokuje binaria build-script Cargo (`os error 4551`); musi zostać powtórzone w CI lub na zatwierdzonym hoście.
- **2026-10-20:** `cargo build --release --locked --manifest-path sparkle_app/src-tauri/Cargo.toml` — build release zaliczony.
- **2026-10-20:** smoke test artefaktu `target/release/sparkle_app.exe` z `SPARKLE_ENABLE_SIDECAR=0` — aplikacja działała po starcie, nie wykryto nowego procesu `blyskawica_backend`.
