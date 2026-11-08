# Zanik zasilania i diagnostyka WAL SPARKLE

**Stan: 2026-11-03.** Instrukcja diagnostyczna nie jest potwierdzeniem odporności całego urządzenia na zanik zasilania. Nie wykonano testów fizycznego odcięcia zasilania ani natywnych testów Linux/macOS.

## Co zapisuje aplikacja

Kolejka i potwierdzenie konsolidacji są dopisywane do WAL przed potwierdzeniem operacji. Checkpoint tworzy osobną generację, synchronizuje jej pliki i publikuje znacznik. Na Unix kod dodatkowo wywołuje synchronizację katalogów po utworzeniu wpisów oraz po publikacji znacznika. Na Windows zapis WAL, sum i znacznika używa `FILE_FLAG_WRITE_THROUGH`; znacznik jest przenoszony przez `MoveFileExW` z `MOVEFILE_WRITE_THROUGH`. Żaden z tych kroków nie jest dowodem, że każdy system plików, kontroler lub dysk przetrwa fizyczne odcięcie zasilania.

Automatyczny checkpoint sprawdza co około 30 sekund, gdy pętla silnika może go wykonać, czy zastosowany WAL wymaga nowej generacji. Brak zmian nie tworzy kopii, a niepusta kolejka wstrzymuje checkpoint; same pozycje tej kolejki są już wcześniej zapisywane do WAL. Błąd jest zgłaszany w dzienniku i próba jest ponawiana. Dłuższa operacja silnika może opóźnić sprawdzenie. Zwykły czat desktopowy wysyła `Prompt`, a nie `QueryWithVector`; jego historia jest zapisywana przez osobny mechanizm opisany poniżej.

Historia głównego czatu i kanału gościa jest zapisywana lokalnie w `db/chat-autosave.jsonl` w postaci jawnego tekstu i odtwarzana przy uruchomieniu. Odtworzone ostatnie wypowiedzi głównego czatu mogą ponownie wejść do kontekstu modelu. Każdy ukończony wpis jest dopisywany z sumą SHA-256, a plik jest synchronizowany przed pokazaniem statusu zapisu. Suma wykrywa przypadkowe zmiany, nie uwierzytelnia danych. Limit wynosi 16 MiB lub 10 000 wpisów, 64 KiB tekstu jednej wiadomości i 256 KiB zakodowanego rekordu; po błędzie lub uszkodzeniu zapis jest wstrzymywany i pokazywany w interfejsie, a oryginał pozostaje do analizy. Wpisy i statusy są obsługiwane kolejno; części generowanej odpowiedzi są zapisywane dopiero po jej zakończeniu, więc przerwanie generowania lub aplikacji może je utracić. Obecnie brak automatycznej naprawy niekompletnego dziennika rozmów i testu fizycznego zaniku zasilania. Historia jest częścią R2: jej eksport i usunięcie wymagają L2 i natywnego potwierdzenia, a po usunięciu tekst widoczny na ekranie pozostaje w pamięci do zamknięcia aplikacji. Eksporty w workspace są osobnymi kopiami.

Dokumentacja Microsoft opisuje zależność zachowania write-through od sprzętu ([CreateFile](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilea)) i ograniczenia opcji przenoszenia ([MoveFileExW](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-movefileexw)). Opis `fsync` wskazuje, że synchronizacja pliku nie musi utrwalić wpisu w katalogu ([Linux fsync](https://man7.org/linux/man-pages/man2/fsync.2.html)).

## Diagnostyka po błędzie otwarcia

1. Zamknij wszystkie instancje SPARKLE i nie uruchamiaj operacji czyszczenia pamięci. Zachowaj cały katalog `db`, łącznie ze starymi generacjami, plikami tymczasowymi i dziennikami. Pliki te mogą zawierać jawny tekst zapytań.
2. Ustal rzeczywisty katalog danych aplikacji; w środowisku developerskim ścieżkę można odczytać w inwentaryzacji danych po uzyskaniu odpowiedniego poziomu uprawnień. Nie zakładaj, że znajduje się on w katalogu repozytorium.
3. W PowerShell, z repozytorium, użyj dokładnej ścieżki katalogu `db`:

   ```powershell
   cargo run --locked --offline --manifest-path .\blyskawica_core\Cargo.toml --bin inspect_memory_wal -- 'C:\SCIEZKA\DO\DANYCH\db' sparkle_vectors 128
   ```

   Narzędzie otwiera plik blokady w katalogu nadrzędnym i odmawia pracy, jeśli inna współpracująca instancja trzyma blokadę. Odczytuje wyłącznie aktywny WAL; nie zmienia jego zawartości ani nie wyświetla rekordów, wektorów lub tekstu. Raport JSON zawiera liczbę bajtów, poprawnych rekordów i oczekujących pozycji przed ewentualnym błędem, jego rodzaj, numer linii i offset.
4. `incomplete_tail` oznacza rekord bez końcowego znaku nowej linii, a `invalid_record` oznacza niepoprawny rekord lub kolejność. Oba wyniki zwracają kod wyjścia 1. Raport nie rozstrzyga, czy uszkodzony zapis został wcześniej potwierdzony; nie należy samodzielnie obcinać WAL ani zamieniać najnowszej generacji starszą.

## Osobny kandydat dla niekompletnej końcówki

Po diagnostyce i świadomej akceptacji, że końcówka **może zawierać wcześniej potwierdzone dane**, operator może przygotować oddzielną kopię kandydata. Tylko poprawny pełny prefiks WAL zostaje do niej skopiowany; oryginalny WAL i generacja nie są zmieniane, a kandydat nie jest aktywowany automatycznie.

```powershell
cargo run --locked --offline --manifest-path .\blyskawica_core\Cargo.toml --bin prepare_memory_wal_candidate -- 'C:\SCIEZKA\DO\DANYCH\db' sparkle_vectors 128 --accept-possible-loss
```

Polecenie odmawia działania dla poprawnego WAL, błędnego pełnego rekordu lub niedostępnej blokady. Tworzy `index.recovery_candidate.*` (nazwa zaczyna się od wybranego identyfikatora indeksu) **wewnątrz** katalogu DB, kopiuje wyłącznie aktywną generację i prawidłowy prefiks, sprawdza sumy oraz próbuje odczytać stan kolejki i indeksu kandydata. Raport i `recovery-candidate.json` zawierają liczbę pominiętych bajtów i sumy oryginału/kopii; nie zawierają treści rekordów. Brak pliku raportu oznacza niedokończoną próbę. Kandydat może zawierać jawne dane użytkownika, zajmować dodatkowe miejsce i na Windows dziedziczy uprawnienia katalogu nadrzędnego. Nie jest dowodem, że pominięte dane nie były potrzebne. Nie nadpisuj ręcznie oryginału.

Przed rozważeniem kandydata można ponowić jego weryfikację względem nadal obecnego źródła. Podaj nazwę katalogu z raportu, bez ścieżki:

```powershell
cargo run --locked --offline --manifest-path .\blyskawica_core\Cargo.toml --bin verify_memory_wal_candidate -- 'C:\SCIEZKA\DO\DANYCH\db' sparkle_vectors 128 NAZWA_KATALOGU_KANDYDATA
```

Polecenie porównuje manifest, źródłowy WAL i jego prefiks, pliki bazowe oraz odtwarza indeks i kolejkę; odrzuca także brakujące i nieoczekiwane pliki kandydata. Wymaga tej samej współpracującej blokady i pozostawia oryginał oraz kandydata bez zmian. Odmowa może oznaczać zmianę źródła po utworzeniu kopii, nawet jeśli sama kopia jest czytelna. Zgodność sum nie jest uwierzytelnieniem ani dowodem, że wykluczona końcówka nie zawierała ważnych danych. Po sprawdzeniu pliki mogą się ponownie zmienić; wynik nie jest zgodą na aktywację ani ochroną przed niewspółpracującym procesem.

## Świadoma aktywacja lub usunięcie jednej kopii

Zatrzymaj aplikację i wykonaj niezależną, sprawdzoną kopię całego katalogu danych poza urządzeniem. Zbadaj raport, w szczególności `excluded_tail_bytes`: pominięta końcówka może zawierać potwierdzone dane. Jeśli akceptujesz taką możliwość, skopiuj z raportu weryfikacji dokładne `candidate_directory`, `original_wal_sha256` i `candidate_wal_sha256`:

```powershell
cargo run --locked --offline --manifest-path .\blyskawica_core\Cargo.toml --bin manage_memory_recovery -- activate 'C:\SCIEZKA\DO\DANYCH\db' sparkle_vectors 128 NAZWA_KANDYDATA SUMA_ORYGINALNEGO_WAL SUMA_WAL_KANDYDATA --accept-possible-loss
```

Program ponownie sprawdza źródło i kopię pod blokadą, tworzy kolejną generację i publikuje znacznik; nie usuwa oryginału ani kandydata. Uruchom ponownie aplikację i sprawdź wynik. Po błędzie, awarii lub niepewnym wyniku zachowaj **wszystkie** pliki i nie ponawiaj w ciemno: nowa generacja może być już aktywna albo jej WAL może bezpiecznie blokować start bez znacznika. Katalogi `*.recovery_stage.*`, `*.gen.*` oraz `*.commit_tmp_*` mogą pozostać po przerwaniu. Nie zmieniaj ich ręcznie bez analizy. Wszystkie kopie podlegają ograniczeniom poufności R2. Blokada chroni wyłącznie współpracujące procesy.

Ograniczona selektywna retencja pozwala wskazać **jednego** kandydata, który nadal daje się porównać z bieżącym źródłem (zwykle przed aktywacją), i usunąć go po przejrzeniu raportu:

```powershell
cargo run --locked --offline --manifest-path .\blyskawica_core\Cargo.toml --bin manage_memory_recovery -- delete-candidate 'C:\SCIEZKA\DO\DANYCH\db' sparkle_vectors 128 NAZWA_KANDYDATA SUMA_ORYGINALNEGO_WAL SUMA_WAL_KANDYDATA --confirm-delete
```

Usunięcie jest nieodwracalne. Polecenie ponownie weryfikuje wskazaną kopię i sumy, usuwa wyłącznie jej oczekiwane pliki, bez rekurencji. Przerwanie może zostawić niekompletny katalog bez manifestu gotowości; zachowaj go do analizy. Po aktywacji, gdy źródło wskazuje nową generację, weryfikacja względem poprzedniego uszkodzonego WAL może się nie powieść i polecenie odmówi usunięcia.

## Selektywne usunięcie starej generacji

Po zatrzymaniu aplikacji i wykonaniu niezależnej, sprawdzonej kopii całego katalogu można osobno przejrzeć wskazany numer generacji i podjąć decyzję o usunięciu. Zawartość starego indeksu może być unikalna nawet wtedy, gdy jego WAL jest pusty; nowsze generacje nie są dowodem, że usunięcie historii jest obojętne dla użytkownika.

```powershell
cargo run --locked --offline --manifest-path .\blyskawica_core\Cargo.toml --bin manage_memory_retention -- review 'C:\SCIEZKA\DO\DANYCH\db' sparkle_vectors 128 NUMER_GENERACJI
cargo run --locked --offline --manifest-path .\blyskawica_core\Cargo.toml --bin manage_memory_retention -- delete 'C:\SCIEZKA\DO\DANYCH\db' sparkle_vectors 128 NUMER_GENERACJI FINGERPRINT_SHA256_Z_RAPORTU --confirm-delete
```

Polecenie usuwa tylko wskazaną kompletną generację z pustym WAL, po ponownym sprawdzeniu sum z raportu. Muszą pozostać co najmniej dwie nowsze, czytelne generacje. Niejednoznaczne generacje, ślady pracy odzyskiwania, nietypowe wpisy i błędy odczytu blokują operację. Usuwanie jest nieodwracalne i nie ma trybu automatycznego. Przy przerwaniu usuwa najpierw stary znacznik, a następnie pojedyncze pliki; pozostałości mogą blokować dalsze czyszczenie i wymagają analizy. To ograniczona procedura: nie czyści generacji z niepustym WAL, starszego formatu, kopii, kandydatów po aktywacji ani porzuconych plików.

Narzędzie ocenia strukturę i kontrolę rekordów aktywnego WAL, nie jest pełnym testem poprawności plików indeksu, integralności historycznych rekordów bez sum ani stanu sprzętu. Blokada chroni tylko procesy stosujące ten sam protokół. Pełna polityka przechowywania starych generacji pozostaje otwarta.

Jeżeli nie ma znacznika najnowszej generacji, ale jej katalog zawiera niepusty WAL, aplikacja odmawia cichego cofnięcia do starszej generacji i zachowuje dane. Jeśli nie zachował się ani znacznik, ani dane pozwalające wykryć nowszą generację, ten mechanizm nie potrafi wykryć utraty.

Checkpoint odmawia publikacji po przekroczeniu 4 GiB lub 10 000 wpisów w katalogu indeksu i nie usuwa automatycznie żadnych danych. To próg odmowy, nie ścisła gwarancja maksymalnej zajętości: rozpoczęta generacja, istniejące dane i aktywny WAL mogą przekroczyć próg. Przy odmowie zachowaj WAL oraz wszystkie generacje do czasu analizy; opisane selektywne czyszczenie obejmuje tylko część przypadków.

## Przygotowanie fizycznych testów zaniku zasilania

Na decyzję użytkownika test fizyczny odłożono z powodu braku odpowiedniego stanowiska. Automatyczny zapis nie zastępuje tego dowodu; podane niżej wymagania dotyczą ewentualnej przyszłej walidacji.

Potrzebny jest osobny komputer testowy i dysk z wyłącznie syntetycznymi danymi oraz kopia systemu i danych poza tym komputerem. Nie należy wykonywać prób na głównym komputerze. Wynik dotyczy konkretnej konfiguracji: modelu dysku, kontrolera, firmware, systemu plików, systemu operacyjnego i ustawień cache. Laptop z podłączoną baterią lub UPS może nie utracić zasilania po odłączeniu sieci; nie należy samodzielnie ingerować w baterię ani elektronikę.

Potrzebne są sterowane odcięcie zasilania i niezależny komputer rejestrujący zdarzenia: numery syntetycznych operacji i potwierdzenia zapisu muszą zostać zapisane poza testowanym urządzeniem przed odcięciem. Test należy powtórzyć podczas dopisywania WAL, konsolidacji, publikacji generacji i aktywacji, a po każdym restarcie porównać stan z niezależnym rejestrem. Brak potwierdzonego wpisu, ciche cofnięcie albo uszkodzenie oryginału to błąd; kontrolowana odmowa odczytu powinna zachować pliki do analizy. Potrzebny jest jeszcze dedykowany, zweryfikowany sterownik testów i protokół pomiaru — obecne testy przerwania procesu nie wykonują fizycznego odcięcia zasilania. Przykładowo [Microsoft Flush Test](https://learn.microsoft.com/en-us/windows-hardware/test/hlk/testref/2dec1f67-b506-4434-8bdf-763147ad8f0b) wykorzystuje sterowaną listwę, ale bada warstwę magazynu i nie zastępuje testów aplikacji.
