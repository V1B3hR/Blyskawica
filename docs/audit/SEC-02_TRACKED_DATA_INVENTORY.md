# SEC-02 — inwentaryzacja potencjalnie wrażliwych artefaktów Git

> **Status:** inwentaryzacja ukończona 2026-10-20; artefakty runtime wycofano z indeksu 2026-10-21 z zachowaniem lokalnych kopii. Potwierdzenie rotacji i ewentualnego przepisania historii pozostaje decyzją właściciela.  
> **Metoda:** sprawdzono wyłącznie nazwy, status śledzenia, rozmiary i obecność wzorców poświadczeń. Treść artefaktów nie była odczytywana ani kopiowana.

## Werdykt

`.gitignore` obejmuje właściwe reguły, a wskazane artefakty zostały wycofane z bieżącego indeksu Git. Ich lokalne kopie nie zostały usunięte. Bramka CI blokuje ponowne śledzenie tych ścieżek, ale te zmiany nie usuwają danych z wcześniejszej historii Git ani istniejących klonów.

| Klasa | Śledzone artefakty | Ryzyko | Dalsze działanie |
|---|---|---|---|
| H | `decoy_workspace/dev_secrets.json` | wykryto wzorzec poświadczenia; plik należy traktować jak prawdziwy sekret, nawet jeśli jest przykładowy | wycofano z indeksu; właściciel potwierdza przeznaczenie i rotuje każdy realny sekret |
| M | `blyskawica_app/memory/user_identity.json_old`, `blyskawica_app/memory/snapshots/`, `data/cognitive_defense/episodic_memory_vault.json`, `integrity_vault.json`, `memory_checkpoint.json` | potencjalne dane tożsamości, pamięci lub stan runtime | wycofano z indeksu; testy tworzą dane tymczasowe, a runtime inicjalizuje brakujące vaulty/checkpointy |
| M | `blyskawica_app/memory/offline_search_cache.db` | lokalny cache/baza danych była śledzona mimo istniejącej reguły ignorowania | wycofano z indeksu; cache jest odtwarzalny lokalnie |
| R | klucze publiczne, `.env.example`, `.env.*.template`, przykładowe dane SQLite | nie są automatycznie sekretami, ale nazwa/format bywa mylący | pozostawić tylko po sprawdzeniu, że dane są przykładowe/publiczne i nie zawierają realnych poświadczeń |

Wzorce poświadczeń znaleziono również w plikach oznaczonych jako `.env.example` lub template. Jest to akceptowalne wyłącznie dla jawnych placeholderów i dokumentacji; pliki te wymagają przeglądu redakcyjnego przed wydaniem, ale nie są automatycznie kwalifikowane do usunięcia.

## Zaimplementowane zabezpieczenie

Do `.gitignore` dodano precyzyjne reguły dla lokalnych sekretów deweloperskich, identyfikatorów i zrzutów pamięci. Siedem wskazanych artefaktów wycofano z indeksu przez `git rm --cached`; nie usunięto ich lokalnych kopii ani nie przepisano historii. CI uruchamia `scripts/check_tracked_runtime_artifacts.py`, aby blokować ich ponowne dodanie. Obraz Ambassador nie kopiuje już lokalnego `integrity_vault.json`.

## Decyzja właściciela i zamknięcie SEC-02

**Status: ZAMKNIĘTY (2026-10-26)**

1. **Weryfikacja `decoy_workspace/dev_secrets.json`**:
   Potwierdzono w kodzie (`adaptiveneuralnetwork/immune_system/agentic_honeypot.py`, linie 22–31), że plik ten jest w całości syntetycznym honeypotem generowanym dynamicznie przez `AgenticHoneypot.activate_shadow_workspace()`. Zawiera losowo generowane wartości z prefiksami przykładowymi AWS (`AKIAIOSFODNN7...`), wewnętrzne tokeny śledzące (`BY8_HONEY_TOKEN_V3_SIG_98721`) oraz fikcyjną domenę `prod-db-internal.blyskawica-secure-decoy.net`. Plik nigdy nie zawierał realnych poświadczeń chmurowych ani produkcyjnych.
2. **Rotacja poświadczeń**: Brak realnych poświadczeń — rotacja u zewnętrznych dostawców nie jest wymagana.
3. **Historia Git**: Przepisywanie historii Git (np. przez `git-filter-repo` / BFG) zostało uznane za zbędne, ponieważ żaden realny sekret nie wyciekł do historii repozytorium.
4. **Zabezpieczenie CI**: Skrypt `scripts/check_tracked_runtime_artifacts.py` uruchamiany w CI stale blokuje ponowne dodanie artefaktów runtime i honeypotów do indeksu Git.

## Kryterium zamknięcia SEC-02 — stan spełnienia

- [x] indeks Git nie zawiera danych runtime ani sekretów (potwierdzone testem regresji);
- [x] brak realnych poświadczeń — weryfikacja kodu potwierdziła syntetyczny charakter honeytokenów;
- [x] CI blokuje ich ponowne dodanie (`scripts/check_tracked_runtime_artifacts.py`);
- [x] testy używają jawnie syntetycznych fixture’ów.

