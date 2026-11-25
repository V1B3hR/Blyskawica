# Kontrakt łączników online SPARKLE

**Status:** rozpoczęto 2026-10-22 (ONL-01). Ten dokument opisuje stan potwierdzony przez `sparkle_app/src-tauri/src/lib.rs`; nie jest obietnicą dostępności usług zdalnych.

## Zasady obowiązujące obecnie

1. SPARKLE startuje w trybie offline.
2. Włączenie trybu online wymaga poziomu Workspace (L2) i natywnego potwierdzenia. Sam przełącznik nie wysyła danych.
3. Każdy działający łącznik wymaga osobnej zgody po włączeniu trybu online. Zgoda pokazuje cel i zakres danych przed potwierdzeniem.
4. Zgody są przechowywane wyłącznie w pamięci procesu. Są kasowane po wyłączeniu trybu online i po zakończeniu aplikacji.
5. Na platformach bez wdrożonego natywnego potwierdzenia aplikacja odmawia awansu i zgody. Przenośny interfejs potwierdzeń należy do RNT-03.

## Rejestr i transport

| Identyfikator | Cel | Zakres danych | Stan |
|---|---|---|---|
| `legacy_sidecar_status` | `http://127.0.0.1:8000/api/system_status` | żądanie GET bez treści użytkownika; odpowiedź może zawierać metryki legacy | jedyny działający transport Tauri; wymaga `SPARKLE_ENABLE_SIDECAR=1/true`, trybu online i osobnej zgody |
| `internet_search` | dostawca wyszukiwania nie jest skonfigurowany | nic nie jest wysyłane | brak transportu; nie można aktywować |
| `cloud_backup` | dostawca kopii nie jest skonfigurowany | nic nie jest wysyłane | brak transportu; nie można aktywować |
| `nethical_docking` | integracja Nethical nie jest skonfigurowana | nic nie jest wysyłane; zakres nie został zaprojektowany | brak transportu; nie można aktywować |

Tryb offline i brak zgody na `legacy_sidecar_status` blokują odczyt statusu sidecara przez Tauri. Rejestr nie uruchamia transportu dla zdalnych wpisów i nie jest zgodą na przyszłe, inne dane niż opisane w aktualnym wpisie.

Legacy FastAPI ma osobny, historyczny mechanizm auto-dockingu Nethical. Od 2026-10-22 jest on domyślnie wyłączony i uruchomi się tylko po ustawieniu `BLYSKAWICA_ENABLE_NETHICAL_AUTO_DOCK=1` albo `true` przed startem tego procesu. Ten opt-in nie jest jeszcze połączony z rejestrem desktopowym; nie wolno traktować go jako wdrożonej zgody per integracja.

## Granice

- Kontrakt kontroluje wywołania wykonywane przez proces Tauri. Legacy auto-docking Nethical jest osobno fail-closed przez zmienną środowiskową, ale niezależnie uruchomiony proces legacy lub program zewnętrzny nadal nie podlega sesyjnej zgodzie desktopowej.
- `SPARKLE_ENABLE_SIDECAR` pozostaje osobnym, deweloperskim opt-inem; nie jest domyślnym elementem wydania desktopowego.
- CSP frontendu nadal nie zezwala na połączenia HTTP/WebSocket z hostami zewnętrznymi ani `localhost`; wszystkie przyszłe transporty wymagają jawnej implementacji po stronie Rust i testów.
- Wyszukiwanie, backup i Nethical nie otrzymują jeszcze danych użytkownika, workspace, eksportów ani sekretów.

## Weryfikacja i następne kroki

`sparkle_app/tests/frontend-security.test.mjs` sprawdza, że stan początkowy jest offline, wyłączenie trybu kasuje zgody, a jedyny odczyt loopback jest warunkowany bramką zgody. Test nie zastępuje testu wykonawczego transportu na każdej platformie.

Przed dodaniem dowolnego transportu zdalnego należy:

1. zdefiniować konkretny dostawca, endpoint, typ danych, limit rozmiaru i retencję;
2. dodać łącznik jako domyślnie nieaktywny oraz dokładny komunikat zgody;
3. wymusić bramkę rejestru bezpośrednio przed wywołaniem sieciowym;
4. dodać testy braku połączenia w trybie offline i bez zgody oraz test kontraktu danych;
5. zweryfikować zachowanie na Windows, Linuxie i macOS.
