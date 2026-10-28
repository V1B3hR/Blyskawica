# Kontrakt modelu danych i retencji SPARKLE

> **Status:** aktywny — inwentaryzacja, kontrolowane usuwanie R0–R4 oraz eksport R2/R4 wdrożone 2026-10-26; eksport/backup i limity całkowite sidecara pozostają otwarte
> **Źródło strategii:** [plan rozwoju i remediacji](../planning/2026-10-development-plan.md)  
> **Zakres:** desktopowy runtime SPARKLE oraz zgodny, deweloperski sidecar Python. Dokument nie jest deklaracją gotowości wydaniowej ani pełnego szyfrowania danych w spoczynku.

## Cel i granice

Kontrakt klasyfikuje lokalne dane, aby eksport, retencja i usuwanie były projektowane jawnie. Opisuje wyłącznie ścieżki widoczne w kodzie; nie odczytywano lokalnych cache, baz, vaultów ani snapshotów użytkownika.

SPARKLE uruchamia sidecar Python tylko po jawnym opt-in. Jego SQLite i pliki pamięci są więc ścieżką zgodności deweloperskiej, ale nadal mogą zawierać dane wymagające ochrony.

## Aktualna klasyfikacja

| Klasa | Dane i obecna lokalizacja | Dostęp / ochrona w kodzie | Retencja i ograniczenie |
|---|---|---|---|
| R0 — artefakty aplikacji | generowany `mock_weights.bin` w katalogu danych aplikacji | nie zawiera danych użytkownika; tworzony przez `start_engine` | odtwarzalny; osobne usunięcie wymaga L2 i natywnego potwierdzenia |
| R1 — workspace i eksporty | pliki workspace, eksporty sesji i `sparkle_app_activity.log` | operacje plikowe i eksport wymagają L2; eksplorator usuwa wyłącznie wybrany zwykły plik po natywnym potwierdzeniu; eksport HTML koduje pola sesji | zawartość zależy od użytkownika; nie ma polityki czasowej ani masowego usuwania katalogów |
| R2 — pamięć pochodna | indeks HNSW, WAL, suma kontrolna i kopia `.prev` w `app_data_dir/db` | lokalna trwałość i integralność, bez potwierdzonego szyfrowania w spoczynku; usunięcie i eksport całego indeksu do workspace wymagają L2 i natywnego potwierdzenia | może utrwalać reprezentacje pochodne; użytkownik może ręcznie usunąć albo wyeksportować cały indeks, bez automatycznej polityki czasowej |
| R3 — dane zgodności sidecara | `blyskawica_memory.db`: cache wyszukiwania, BLOB metadanych i JSON snapshotów; `media_storage/*`: pliki wysłane do legacy API | SQLite WAL zapewnia odporność zapisu, nie szyfrowanie całej bazy; Windows DPAPI może chronić pojedyncze wartości, a fallback poza Windowsem zwraca bajty bez szyfrowania. Legacy upload wymaga tokenu sesyjnego, odmawia linku symbolicznego, przyjmuje maks. 25 MiB przez plik tymczasowy i odmawia przekroczenia 250 MiB całego magazynu | ścieżka wyłącznie deweloperska: po zatrzymaniu sidecara operator może uruchomić `python -m scripts.clear_legacy_sidecar_data --confirm`; skrypt usuwa wyłącznie bazę sidecara, pliki WAL i `media_storage`, odmawiając linków symbolicznych; eksport R3 jest celowo niedozwolony, aby zapobiec niezaszyfrowanym zrzutom danych sidecara |
| R4 — sekrety | pojedyncze pliki `identity_vault/*.enc` w katalogu danych aplikacji | zapis, odczyt, usunięcie i eksport zaszyfrowanej kopii wymagają L3; eksport nie odczytuje wartości jawnej i wymaga natywnego potwierdzenia | użytkownik może usunąć wskazany sekret albo zapisać jego zaszyfrowaną kopię w workspace; nie ma automatycznej polityki czasowej |

## Obecne właściwości, których nie wolno rozszerzać marketingowo

- SQLite `WAL` i `synchronous=FULL` zapewniają trwałość oraz spójność zapisu, nie szyfrowanie tabel `search_cache` ani `cognitive_snapshots`.
- Szyfrowanie pojedynczej wartości DPAPI nie oznacza szyfrowania całego magazynu; fallback Pythona poza Windowsem pozostawia dane niezaszyfrowane.
- Lokalny indeks HNSW weryfikuje integralność przez WAL, SHA-256 i `.prev`, ale nie ma potwierdzonego szyfrowania ani okresu retencji. Użytkownik może usunąć cały indeks po L2 i natywnym potwierdzeniu.
- Eksport sesji i logów jest funkcją kontrolowaną przez użytkownika na L2, lecz zapisuje dane do wskazanego workspace. Użytkownik powinien traktować takie pliki jak własne dane lokalne.
- Legacy upload mediów ma limit 25 MiB dla pojedynczego pliku i 250 MiB dla całego magazynu. Skan limitu odmawia działania przy linku symbolicznym, błędzie odczytu lub ponad 10 000 wpisów. Usuwanie R3 jest osobnym, potwierdzanym poleceniem deweloperskim po zatrzymaniu sidecara; nie jest dostępne przez HTTP ani desktopowy runtime. To nie jest deklaracja ochrony danych w spoczynku.
- R1, R2 i R4 nie mają automatycznej retencji czasowej, aby nie usuwać danych użytkownika wyłącznie na podstawie wieku. Ich usunięcie lub eksport pozostaje jawną, potwierdzaną akcją użytkownika.

## Minimalny kontrakt docelowy

Przed zamknięciem PRIV-01 każda klasa R1–R4 musi mieć:

1. widoczny opis lokalizacji, celu i klasy danych;
2. jawny export oraz usunięcie z potwierdzeniem użytkownika;
3. ograniczenie retencji albo udokumentowane uzasadnienie braku automatycznego usuwania;
4. test regresji dla granicy uprawnień i usuwania;
5. decyzję o szyfrowaniu w spoczynku oraz o odzyskiwaniu klucza na Windows, Linuxie i macOS.

Żadna funkcja online nie może otrzymać danych R1–R4 przed rejestrem łączników ONL-01, opisem zakresu danych i zgodą użytkownika.

## Stan wdrożenia i dalsza kolejność

1. **Częściowo wdrożono 2026-10-22:** Rust/Tauri udostępnia w opcjach inwentaryzację klas R0–R4 bez odczytu treści plików. Wymaga L2; ścieżki danych aplikacji i szczegóły R4 są ujawniane dopiero na L3. Rekurencyjny pomiar rozmiaru ma limit 10&nbsp;000 wpisów, a niepełny wynik jest oznaczony w UI. R3 pozostaje opisem ścieżki zgodności sidecara, bez odczytu przez runtime.
2. **Rozszerzono 2026-10-26:** eksplorator usuwa wybrany zwykły plik R1, a osobne operacje usuwają R0 `mock_weights.bin`, cały R2 indeks pamięci pochodnej oraz wskazany sekret R4. R0/R1/R2 wymagają L2, R4 wymaga L3; każda operacja wymaga natywnego potwierdzenia. R2 odmawia katalogów zawierających linki symboliczne, nietypowe typy plików lub ponad 10 000 wpisów. Nie łączy się tych operacji z automatycznym czyszczeniem.
3. **Rozszerzono 2026-10-26:** R3 pozostaje poza desktopowym runtime. Po zatrzymaniu opcjonalnego sidecara operator może uruchomić `python -m scripts.clear_legacy_sidecar_data --confirm`; skrypt jest ograniczony do baz SQLite sidecara, ich plików WAL/SHM oraz `media_storage` i odmawia linków symbolicznych.
4. **Zdecydowano 2026-10-26:** Eksport/backup R3 został świadomie odrzucony i zakazany w architekturze. Dane zgodności sidecara (R3) nie posiadają interfejsu eksportu, aby wykluczyć niekontrolowane, niezaszyfrowane kopiowanie baz SQLite i uploadowanych mediów poza środowisko lokalne; jedyną dozwoloną operacją na R3 pozostaje potwierdzane deweloperskie czyszczenie (`clear_legacy_sidecar_data.py --confirm`).
5. Potwierdzić na natywnych Windows, Linux i macOS zachowanie sejfu platformowego oraz odzyskiwanie klucza przed deklaracją gotowości wydaniowej.
6. Dopiero po powyższych krokach podjąć decyzję o migracji lub usunięciu legacy SQLite i JSON snapshotów.

## Powiązane dokumenty

- [SEC-02 — inwentaryzacja artefaktów Git](../audit/SEC-02_TRACKED_DATA_INVENTORY.md)
- [Polityka zarządzania danymi treningowymi](../DATA_GOVERNANCE.md)
- [Kontrakt samodzielnego runtime SPARKLE](SPARKLE_RUNTIME_CONTRACT.md)
