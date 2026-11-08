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
| R2 — pamięć runtime, kolejka i rozmowy | indeks HNSW, WAL, oczekujące wektory i tekst metadanych zapytań, automatycznie zapisana historia czatu głównego i gościa, znaczniki, kopie oraz starsze generacje w `app_data_dir/db` | WAL i historia zawierają tekst jawny; brak potwierdzonego szyfrowania w spoczynku; usunięcie i eksport całego katalogu wymagają L2 i natywnego potwierdzenia | dane kolejki, rozmowy i historyczne kopie pozostają do jawnego usunięcia całego R2; brak automatycznej polityki retencji |
| R3 — dane zgodności sidecara | `blyskawica_memory.db`: cache wyszukiwania, BLOB metadanych i JSON snapshotów; `media_storage/*`: pliki wysłane do legacy API | SQLite WAL zapewnia odporność zapisu, nie szyfrowanie całej bazy; Windows DPAPI może chronić pojedyncze wartości, a fallback poza Windowsem zwraca bajty bez szyfrowania. Legacy upload wymaga tokenu sesyjnego, odmawia linku symbolicznego, przyjmuje maks. 25 MiB przez plik tymczasowy i odmawia przekroczenia 250 MiB całego magazynu | ścieżka wyłącznie deweloperska: po zatrzymaniu sidecara operator może uruchomić `python -m scripts.clear_legacy_sidecar_data --confirm`; skrypt usuwa wyłącznie bazę sidecara, pliki WAL i `media_storage`, odmawiając linków symbolicznych; eksport R3 jest celowo niedozwolony, aby zapobiec niezaszyfrowanym zrzutom danych sidecara |
| R4 — sekrety | pojedyncze pliki `identity_vault/*.enc` w katalogu danych aplikacji | zapis, odczyt, usunięcie i eksport zaszyfrowanej kopii wymagają L3; eksport nie odczytuje wartości jawnej i wymaga natywnego potwierdzenia | użytkownik może usunąć wskazany sekret albo zapisać jego zaszyfrowaną kopię w workspace; nie ma automatycznej polityki czasowej |

## Obecne właściwości, których nie wolno rozszerzać marketingowo

- SQLite `WAL` i `synchronous=FULL` zapewniają trwałość oraz spójność zapisu, nie szyfrowanie tabel `search_cache` ani `cognitive_snapshots`.
- Szyfrowanie pojedynczej wartości DPAPI nie oznacza szyfrowania całego magazynu; fallback Pythona poza Windowsem pozostawia dane niezaszyfrowane.
- Lokalny indeks HNSW weryfikuje sumy plików i składnię WAL; nowe wpisy WAL mają sumy SHA-256, starsze wpisy pozostają bez nich. Sumy nie uwierzytelniają danych. Kolejka z magazynem trwałym zapisuje wektor i metadane (w tym tekst zapytania) do WAL przed potwierdzeniem przyjęcia; osobny rekord konsolidacji umożliwia odtworzenie stanu po restarcie. Metadane pozycji mają limit 4096 bajtów, kolejka 10 000 pozycji, a WAL 64 MiB; przekroczenie odrzuca zapis. Checkpoint jest wstrzymany, gdy kolejka nie jest pusta. Starsze generacje, dzienniki, kopie `*.backup_*` i porzucone pliki nie są automatycznie usuwane i mogą zawierać jawny tekst; obowiązują progi checkpointu opisane poniżej. Brak potwierdzonej odporności na awarię zasilania i szyfrowania. Najnowsza uszkodzona generacja powoduje błąd zamiast cichego cofnięcia. Użytkownik może usunąć cały indeks wraz z kopiami po L2 i natywnym potwierdzeniu.
- Przed checkpointem i przed publikacją generacji aplikacja sprawdza katalog R2: ponad 4 GiB, ponad 10 000 wpisów, dowiązanie lub błąd skanowania blokuje checkpoint bez usuwania plików. To próg odmowy, nie ścisły limit zajętości: istniejący magazyn, przygotowywana generacja i aktywny WAL mogą go przekroczyć. Operatorskie, selektywne usuwanie po przeglądzie i potwierdzeniu obejmuje tylko kwalifikujące się stare generacje z pustym WAL; zachowuje dwie najnowsze i odmawia niejednoznacznych przypadków. Nie jest pełną polityką retencji ani automatycznym czyszczeniem.
- Przy świadomym przygotowaniu kandydata odzyskania osobny katalog wewnątrz R2 zawiera kopię aktywnego indeksu i prefiksu WAL; może powielać tekst zapytań i zwiększa zajętość. Kandydat nie jest aktywowany automatycznie i nie gwarantuje zachowania pominiętej końcówki. Osobne narzędzie operatorskie pozwala po jawnej akceptacji ryzyka opublikować kopię jako nową generację albo jawnie usunąć jeden nadal weryfikowalny kandydat. Porzucone pliki nie są automatycznie usuwane. Instrukcja i ograniczenia: [diagnostyka WAL](POWER_LOSS_AND_WAL_RECOVERY.md).
- Silnik okresowo ponawia checkpoint zastosowanego WAL; nie tworzy nowej generacji przy braku zmian ani przy niepustej kolejce. Desktop przesyła tekst jako `Prompt`, nie jako `QueryWithVector`; rozmowy zapisuje osobny dziennik `chat-autosave.jsonl`, jawny, ograniczony do 16 MiB/10 000 wpisów i 64 KiB tekstu na wpis. Przy błędzie lub niekompletnym rekordzie odmawia dalszego zapisu; skończone odpowiedzi zapisywane są po zakończeniu, nie w czasie strumieniowania. Historia jest odtwarzana i ostatnie wiadomości czatu mogą wejść do kontekstu modelu. Usunięcie całego R2 usuwa ją po L2 i potwierdzeniu, a eksport R2 może ją ujawnić; ekran może zachować już wyświetlony tekst do zamknięcia. Żaden z mechanizmów nie dowodzi trwałości na fizyczną utratę zasilania.
- Eksport i usuwanie R2 wymagają zatrzymania i faktycznego zakończenia zadania silnika. Współpracujące instancje desktopu używają wspólnej blokady plikowej w katalogu danych aplikacji; inne programy mogą ją pominąć.
- Aktualizacja interfejsu Rust 2026-11-02: trwałe operacje indeksu wymagają blokady powiązanej z katalogiem; indeks zachowuje ją podczas istnienia. Jedna blokada nie może równocześnie zasilać wielu obiektów indeksu. Jest to koordynacja w API, nie systemowa izolacja plików przed innymi programami z uprawnieniami użytkownika. Dedykowany izolowany magazyn i jego testy na Windows pozostają niewdrożone.
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
