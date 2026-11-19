# ⚡ Audyt Statusu: Co z P2, P3, P4, P5? (Stan Realizacji i Zadania Otwarte)

> **Data audytu:** 2026-11-09  
> **Kontekst:** Odpowiedź na weryfikację stanu realizacji po wdrożeniu P0/P1 i wydaniu standalone bundle.  
> **Źródła dokumentacji:**  
> - `docs/planning/2026-11-01-finish-and-rust-audit-plan.md` (Plan Kroków 1–5)  
> - `docs/planning/2026-10-development-plan.md` (Priorytety P0, P1, P2)  
> - `docs/technical/SPARKLE_RUNTIME_CONTRACT.md` (Kamienie milowe runtime 1–6)  
> - `docs/roadmaps/ROADMAP_V11_NEXTGEN.md` (Architektura Next-Gen V11)  
> - `docs/planning/backlog_i_zadania_zalegle.md` (Skonsolidowany backlog V9/V10)

---

## 🎯 Podsumowanie Wykonawcze: Twoje przeczucie było w 100% słuszne

Twoje wewnętrzne przeczucie, że **"coś jest jeszcze w toku lub zostało do zrobienia"**, jest w pełni uzasadnione. W projekcie występują **trzy nakładające się na siebie konteksty** używające oznaczeń "P2–P5" lub "Kroki 2–5":

1. **Kroki Realizacyjne 2, 3, 4, 5** z aktualnego planu audytu (`2026-11-01-finish-and-rust-audit-plan.md`) – z czego kroki 2 i 3 są zaimplementowane i przetestowane lokalnie, krok 4 jest intencjonalnie rozdzielony (CRA w Rust, PINN w PyTorch), a krok 5 ma **3 otwarte bramki wydaniowe**.
2. **Priorytet P2 (QLT-01 oraz V11)** z planu strategicznego (`2026-10-development-plan.md`) – zadania wydajnościowo-obserwacyjne (QLT-01) są częściowo sprofilowane, a moduły nowej generacji V11 (WebGPU Spores, BCI, EWC Async Sleep, Z3 SMT solver) są **intencjonalnie zamrożone (gated)** do czasu stabilizacji V10.
3. **Kamienie Milowe Migracji 3–6** z kontraktu runtime (`SPARKLE_RUNTIME_CONTRACT.md`) – wymagające walidacji na fizycznych maszynach Linux/macOS oraz budowy instalatorów wieloplatformowych.

Poniżej znajduje się szczegółowe, precyzyjne zestawienie: co jest zrobione, co jest w toku, a co czeka w kolejce.

---

## 1. Plan Realizacyjny: Kroki 2, 3, 4, 5 (`2026-11-01-finish-and-rust-audit-plan.md`)

| Krok Planu | Tytuł Zadania | Co Zostało UKOŃCZONE ✅ | Co Jest W TOKU / POZOSTAŁO OTWARTE 🟡 |
|---|---|---|---|
| **Krok 2** | **MVP Vertical Flow (P0)** | • Wektorowy indeks pamięci w RAM z leasingiem `IndexLease`<br/>• Trwałość czatu (`chat_autosave.rs` z SHA-256)<br/>• Anulowanie generacji w locie (`GenerationGate`)<br/>• Ograniczenie ścieżek workspace (`sanitized_vault_key`, Path Traversal checks)<br/>• Zweryfikowany offline testami (26 Tauri + 19 frontend) | 🟡 **Fizyczny test odcięcia zasilania (Power-Cut Test)**: Zapis SQLite WAL jest odporny na poziomie synchronicznym `PRAGMA synchronous = NORMAL/FULL`, jednak fizyczny test „pulling the plug” został odroczony z braku dedykowanego stanowiska sprzętowego. |
| **Krok 3** | **P1 Privacy, IPC, Online & Portability** | • Granice uprawnień IPC L2 (Workspace) i L3 (Full OS/Vault)<br/>• Inwentaryzacja R0–R4 z bezpiecznym usuwaniem/eksportem<br/>• Sanityzacja floatów `is_finite()` w wagach i feedbacku<br/>• Limity DoS buforów wejściowych<br/>• Domyślny tryb offline (`set_online_mode(false)` resetuje zgody sesyjne)<br/>• **SEC-04 domknięty (2026-11-19)**: wyłączono `withGlobalTauri: false`, przejście na modułowe `@tauri-apps/api` (`tauri-bridge.js`, 20/20 testów)<br/>• **Walidacja uniksowa w CI (2026-11-19)**: `Rust core` i `SPARKLE Tauri` przeszły 100% na `ubuntu-latest` i `macos-latest` (run `44487145933`) | ✅ Zakończony i zweryfikowany na 3 systemach w CI (Windows, Ubuntu, macOS). |
| **Krok 4** | **Migracja wg Kontraktów (C.R.A., Neurochemia, PINN)** | • Kontrakt C.R.A. v1 zaimplementowany w Rust (`cra_contract.rs`)<br/>• 100% zgodności numerycznej CRA (20/20 testów pytest, 8/8 Rust)<br/>• Silnik `BlyskawicaEngine` zintegrowany z CRA (`with_cra_engine`, pętla homeostazy, sygnały zaufania `[R_HUMAN_FEEDBACK]`)<br/>• Zero-Trust MCP sandbox spięty z neurochemią | 🟡 **Trening i Autograd PINN w Pythonie**: Zgodnie z ADR 0002 silnik termiczny PINN i autograd pozostają w Python/PyTorch (jako dedykowany toolchain badawczy).<br/>🟡 **Wygaszenie legacy FastAPI**: Stare endpointy HTTP w `blyskawica_app/backend` działają równolegle jako fallback do czasu całkowitego usunięcia frontendu webowego. |
| **Krok 5** | **Zbierz Dowody Wydania i Zaktualizuj Portal** | • Czyste drzewo robocze Git na `main`<br/>• **Zdalny przebieg CI 3-OS (2026-11-19)**: `CI & Security Audit` (run `44487145933`) **7/7 zielone** (Windows, Ubuntu, macOS + Ruff + `pip-audit` + `pytest`)<br/>• **Podatności i `cargo-audit` (2026-11-19)**: załatane wszystkie alerty Dependabot w `extensions/` (`aiohttp`, `certifi`, `mako`, `multidict`, `pyjwt`, `mlflow`) oraz podatne skrzynki Rust (`anyhow`, `crossbeam-epoch`, `memmap2`, `tokio`, `event-listener`, `rustix`); dodano `cargo-audit` do CI<br/>• **Workflow instalatora (2026-11-19)**: `.github/workflows/release-windows.yml` zaktualizowany do czystego builda Rust/Tauri (`NSIS` + `MSI`, bez sidecara Pythona)<br/>• Przygotowany przenośny pakiet `C:\Projekty\Błyskawica standalone` | 🟡 **Pozostałe Otwarte Bramki (sprzętowe / zewnętrzne)**:<br/>1. **Test czystej instalacji (Clean-Install)**: Manualne uruchomienie wygenerowanego instalatora MSI/NSIS (lub paczki standalone) na komputerze bez VS Build Tools/Rust.<br/>2. **Fizyczny test odcięcia zasilania (Power-Cut)** na docelowym sprzęcie.<br/>3. **Niezależny audyt bezpieczeństwa**: Zewnętrzny przegląd red-team/security. |

---

## 2. Priorytety Strategiczne P2 (`2026-10-development-plan.md`)

W planie z października 2026 zdefiniowano następujące priorytety P2:

### A. QLT-01: Wydajność i Obserwowalność (Performance & Observability)
*   **Stan:** 🟡 **Częściowo ukończone / W toku profilowania**.
*   **Co zrobiono:**
    *   Wstępny profil wydajnościowy w `tests/test_standalone_readiness.py`: Przepustowość tensorowa na CPU $>1000$ TPS, zużycie pamięci przy 200 cyklach inferencji $<5$ MB narzutu.
    *   Binarka release skompilowana z LTO (Link Time Optimization) i stripowaniem symboli.
*   **Co pozostało:**
    *   Zdefiniowanie i egzekwowanie sztywnych budżetów startu aplikacji ($<1.5$ s dla zimnego startu UI) i budżetów RAM ($<250$ MB RAM bez załadowanego modelu, $<5.5$ GB z modelem 7B GGUF).
    *   Lokalna telemetria odporna na wycieki danych (zero-telemetry w trybie offline, lokalne ring-buffery błędów).

### B. V11: Moduły Next-Gen Kognitywne (`ROADMAP_V11_NEXTGEN.md`)
*   **Stan:** ⏸️ **Intencjonalnie wstrzymane (GATED)** do momentu stabilizacji wydania V10.
*   **Szczegółowy podział modułów V11:**
    1.  **V11.1 (WebGPU Spores)**: Dynamiczna plastyczność synaptyczna mikro-modeli brzegowych w przeglądarce/Tauri z adaptacją wag w locie (status: prototyp koncepcyjny).
    2.  **V11.2 (BCI & Diamond Yant)**: Pętla sprzężenia zwrotnego z falami mózgowymi Alpha (8–12 Hz) przez protokół LSL oraz rezonans cymatyczny Chladniego (status: specyfikacja matematyczna).
    3.  **V11.3 (Asynchroniczny Sen i EWC)**: Ciągła regularyzacja Elastic Weight Consolidation asymilująca wektory anomalii z dnia (status: zaimplementowany prototyp w Pythonie `sleep_loop.py`, oczekuje na port do Rust Candle).
    4.  **V11.4 (Z3 SMT Formal Verification Gateway)**: Formalny solwer w logice pierwszego rzędu weryfikujący niesprzeczność akcji z 25 Prawami Netycznymi (status: zarys aksjomatów w `ai_ethics.py`).

---

## 3. Kamienie Milowe Migracji Runtime (`SPARKLE_RUNTIME_CONTRACT.md`)

| Kamień Milowy | Zakres | Status | Uwagi |
|---|---|---|---|
| **Kamień 1** | Kontrakt i inwentaryzacja endpointów | ✅ Zakończony | Ścisły podział: Rust (produkt desktopowy) vs Python (toolchain). |
| **Kamień 2** | Samodzielny MVP na Windows 11 | ✅ Zakończony | `sparkle_app.exe` działa bez Pythona, ładuje model GGUF, obsługuje HNSW i bazę wiedzy. |
| **Kamień 3** | Przenośna warstwa Rust (bez sztywnego WinAPI) | ✅ Zakończony (2026-11-19) | Zwalidowany natywnie na Windows, Ubuntu i macOS w GitHub Actions (`44487145933`); wyeliminowano wyścig inicjalizacji klucza sejfu Unix (`hard_link` + izolacja testów). |
| **Kamień 4** | Wydania natywne (MSI/NSIS, .deb, .dmg) | 🟡 Windows NSIS/MSI zautomatyzowane w CI / Linux & macOS paczki otwarte | Workflow `release-windows.yml` zaktualizowany do czystego builda Tauri (`NSIS` + `MSI`, ADR 0002). Pakiet portable tworzony przez `scripts/bundle_standalone.py`. |
| **Kamień 5** | Online jako opcjonalne rozszerzenie | ✅ Zakończony | Rejestr łączników, domyślna odmowa, brak ukrytego ruchu sieciowego, odizolowana pamięć gościa. |
| **Kamień 6** | Ciągłość zachowania kognitywnego | 🟡 Częściowo zakończony | C.R.A. i neurochemia przeniesione do Rust z zachowaniem 100% parzystości. Silnik PINN pozostaje w PyTorch do zadań badawczych. |

---

## 4. Podsumowanie: Co należy zrobić w następnych krokach?

Jeżeli pytasz: **"Co fizycznie jest jeszcze do zrobienia?"**, oto konkretna lista zadań ułożona według priorytetu:

### Natychmiastowe / Przed oficjalnym ogłoszeniem wydania (Release Gating):
1. **GitHub Actions CI Run**: Upewnić się, że zdalne pipeline'y na GitHubie dla gałęzi `feat/cognitive-core-enhancements` przeszły na zielono na wszystkich 3 systemach operacyjnych (Windows, Ubuntu, macOS).
2. **Smoke Test na czystym Windowsie**: Skopiować folder `C:\Projekty\Błyskawica standalone` na maszynę wirtualną lub komputer bez Visual Studio, Rust i Python, uruchomić `Uruchom_Blyskawice.bat` i potwierdzić bezbłędny start.

### Średnioterminowe (Faza P2 / QLT-01):
3. **Pomiary zużycia zasobów**: Długodystansowy test obciążeniowy (1000 zapytań z rzędu) w celu zweryfikowania, czy pamięć RAM nie ma mikrowycieków w pętli Candle/HNSW.
4. **Wycofanie legacy backendu**: Gdy frontend Tauri zostanie uznany za w 100% stabilny, definitywne usunięcie serwera FastAPI z runtime'u deweloperskiego.

### Długoterminowe (Faza V11 Next-Gen):
5. **Aktywacja kolejnych etapów V11**: Przeniesienie pętli asynchronicznego snu (EWC) i integracja z Z3 SMT Solverem dla reguł etycznych.
