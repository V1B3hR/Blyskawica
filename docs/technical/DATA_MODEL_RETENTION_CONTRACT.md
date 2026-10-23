# Kontrakt modelu danych i retencji SPARKLE

> **Status:** aktywny — pierwszy wycinek PRIV-01, 2026-10-22; inwentaryzacja metadanych wdrożona 2026-10-22  
> **Źródło strategii:** [plan rozwoju i remediacji](../planning/2026-10-development-plan.md)  
> **Zakres:** desktopowy runtime SPARKLE oraz zgodny, deweloperski sidecar Python. Dokument nie jest deklaracją gotowości wydaniowej ani pełnego szyfrowania danych w spoczynku.

## Cel i granice

Kontrakt klasyfikuje lokalne dane, aby eksport, retencja i usuwanie były projektowane jawnie. Opisuje wyłącznie ścieżki widoczne w kodzie; nie odczytywano lokalnych cache, baz, vaultów ani snapshotów użytkownika.

SPARKLE uruchamia sidecar Python tylko po jawnym opt-in. Jego SQLite i pliki pamięci są więc ścieżką zgodności deweloperskiej, ale nadal mogą zawierać dane wymagające ochrony.

## Aktualna klasyfikacja

| Klasa | Dane i obecna lokalizacja | Dostęp / ochrona w kodzie | Retencja i ograniczenie |
|---|---|---|---|
| R0 — artefakty aplikacji | generowany `mock_weights.bin` w katalogu danych aplikacji | nie zawiera danych użytkownika; tworzony przez `start_engine` | odtwarzalny; osobne usunięcie wymaga L2 i natywnego potwierdzenia |
| R1 — workspace i eksporty | pliki workspace, eksporty sesji i `sparkle_app_activity.log` | operacje plikowe i eksport wymagają L2; eksport HTML koduje pola sesji | zawartość zależy od użytkownika; usuwanie odbywa się obecnie przez workspace, bez polityki czasowej |
| R2 — pamięć pochodna | indeks HNSW, WAL, suma kontrolna i kopia `.prev` w `app_data_dir/db` | lokalna trwałość i integralność, lecz brak szyfrowania w spoczynku lub powierzchni usuwania/eksportu | może utrwalać reprezentacje pochodne z przyszłych interakcji; retencja nie jest jeszcze zdefiniowana |
| R3 — dane zgodności sidecara | `blyskawica_memory.db`: cache wyszukiwania, BLOB metadanych i JSON snapshotów; `media_storage/*`: pliki wysłane do legacy API | SQLite WAL zapewnia odporność zapisu, nie szyfrowanie całej bazy; Windows DPAPI może chronić pojedyncze wartości, a fallback poza Windowsem zwraca bajty bez szyfrowania. Legacy upload wymaga tokenu sesyjnego, odmawia linku symbolicznego i przyjmuje maks. 25 MiB przez plik tymczasowy | brak potwierdzonego limitu retencji lub interfejsu usunięcia; ścieżka tylko deweloperska |
| R4 — sekrety | pojedyncze pliki `identity_vault/*.enc` w katalogu danych aplikacji | zapis i odczyt wymagają L3; obecna implementacja wywołuje natywną ochronę sekretu | brak przenośnego kontraktu sejfu i sterowanego retencją usuwania; nie wolno deklarować ochrony na wszystkich platformach |

## Obecne właściwości, których nie wolno rozszerzać marketingowo

- SQLite `WAL` i `synchronous=FULL` zapewniają trwałość oraz spójność zapisu, nie szyfrowanie tabel `search_cache` ani `cognitive_snapshots`.
- Szyfrowanie pojedynczej wartości DPAPI nie oznacza szyfrowania całego magazynu; fallback Pythona poza Windowsem pozostawia dane niezaszyfrowane.
- Lokalny indeks HNSW weryfikuje integralność przez WAL, SHA-256 i `.prev`, ale nie ma potwierdzonego szyfrowania, okresu retencji ani interfejsu „usuń moje dane”.
- Eksport sesji i logów jest funkcją kontrolowaną przez użytkownika na L2, lecz zapisuje dane do wskazanego workspace. Użytkownik powinien traktować takie pliki jak własne dane lokalne.
- Legacy upload mediów ma tymczasowy limit 25 MiB dla pojedynczego pliku, ale nie ma jeszcze ustalonej retencji, limitu całkowitej pojemności ani kontrolowanego przez użytkownika usuwania. To nie jest deklaracja ochrony danych w spoczynku.

## Minimalny kontrakt docelowy

Przed zamknięciem PRIV-01 każda klasa R1–R4 musi mieć:

1. widoczny opis lokalizacji, celu i klasy danych;
2. jawny export oraz usunięcie z potwierdzeniem użytkownika;
3. ograniczenie retencji albo udokumentowane uzasadnienie braku automatycznego usuwania;
4. test regresji dla granicy uprawnień i usuwania;
5. decyzję o szyfrowaniu w spoczynku oraz o odzyskiwaniu klucza na Windows, Linuxie i macOS.

Żadna funkcja online nie może otrzymać danych R1–R4 przed rejestrem łączników ONL-01, opisem zakresu danych i zgodą użytkownika.

## Kolejność wdrożenia

1. **Częściowo wdrożono 2026-10-22:** Rust/Tauri udostępnia w opcjach inwentaryzację klas R0–R4 bez odczytu treści plików. Wymaga L2; ścieżki danych aplikacji i szczegóły R4 są ujawniane dopiero na L3. Rekurencyjny pomiar rozmiaru ma limit 10&nbsp;000 wpisów, a niepełny wynik jest oznaczony w UI. R3 pozostaje opisem ścieżki zgodności sidecara, bez odczytu przez runtime.
2. **Rozpoczęto 2026-10-22:** osobna operacja usuwa wyłącznie odtwarzalny R0 `mock_weights.bin` po L2 i natywnym potwierdzeniu; odmawia usunięcia katalogu lub linku. Zaprojektować osobne, potwierdzane operacje usuwania dla workspace, indeksu HNSW, cache sidecara i vaultu; nie łączyć ich z automatycznym czyszczeniem.
3. Ustalić retencję i bezpieczny eksport dla każdego magazynu, a następnie dodać testy.
4. Zastąpić Windows-only założenia sejfu kontraktem platformowym RNT-03 przed deklaracją ochrony sekretów na Linuxie i macOS.
5. Dopiero po powyższych krokach podjąć decyzję o migracji lub usunięciu legacy SQLite i JSON snapshotów.

## Powiązane dokumenty

- [SEC-02 — inwentaryzacja artefaktów Git](../audit/SEC-02_TRACKED_DATA_INVENTORY.md)
- [Polityka zarządzania danymi treningowymi](../DATA_GOVERNANCE.md)
- [Kontrakt samodzielnego runtime SPARKLE](SPARKLE_RUNTIME_CONTRACT.md)
