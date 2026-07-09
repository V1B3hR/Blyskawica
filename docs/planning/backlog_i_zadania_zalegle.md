# ⚡ Błyskawica V9: Skonsolidowany Backlog i Zadania Zaległe

Ten dokument stanowi jednolitą, skonsolidowaną bazę zadań dla Błyskawicy V9, łączącą niezrealizowane cele z planów rozwoju (`roadmap_V9.md`, `advanced_roadmap.md`, `analiza_brakow_i_rozwoju.md` oraz `blyskawica_future_roadmap.md`).

---

## 🟢 1. Zadania Ukończone i Zweryfikowane (Recent Milestones)

Dzięki ostatnim operacjom architektonicznym zrealizowano następujące kluczowe kroki:
1.  **Lokalna, Trwała Baza Wektorowa HNSW (Komponent A)**:
    *   Wdrożono zapis i odczyt grafu HNSW na dysku w `%APPDATA%/Blyskawica/db/` (Rust/Tauri). Pliki bazy ładują się i zapisują automatycznie przy starcie silnika oraz podczas procedury `DEEP_SLEEP`.
2.  **Lokalny Silnik Tensorowy Candle (Komponent B)**:
    *   Modyfikacja `project_vector_with_expert` w `blyskawica_core`. Zamiana manualnych pętli mnożenia macierzy na natywny silnik tensorowy **HuggingFace Candle** (wykonywany na CPU/DirectML).
3.  **Kwarantanna i Zrzucanie Uprawnień Win32 (Komponent C)**:
    *   Wdrożenie niskopoziomowych wywołań Windows API (`ImpersonateAnonymousToken`, `RevertToSelf`, `GetTcpTable`, `SetTcpEntry`).
    *   W momencie wykrycia zagrożenia przez tarczę `Wolf Teeth` wątek traci uprawnienia zapisu na dysku, a wszystkie zewnętrzne połączenia TCP/IP są natychmiastowo zrywane.
4.  **Stabilizacja Więzi Emocjonalnej (`soul.py`)**:
    *   Zabezpieczenie przed gwałtownymi wahaniami za pomocą tłumienia (damping).
    *   Sztywny limit (capping) na poziomie `0.45` dla zewnętrznych użytkowników systemowych (partnerska relacja biznesowa) oraz pełna integracja szyfrowania DPAPI.
5.  **Automatyzacja Podpisu Cyfrowego ONNX (Faza 3.2)**:
    *   Wdrożono automatyczną krystalizację oraz generowanie/weryfikację podpisu cyfrowego RSA-2048 po zakończeniu fazy konsolidacji kognitywnej (sen głęboki) w backendzie FastAPI. Zabezpieczono proces przed nieobsługiwanymi typami modeli (np. nie-PyTorch).
6.  **Integracja Asynchronicznego Snu (Wektory Zaskoczenia - G2)**:
    *   Wdrożono mechanizm asymilacji anomalii za pomocą regularyzacji **Elastic Weight Consolidation (EWC)**. Silnik wykonuje teraz gradientowy krok optymalizacji na wektorach zaskoczenia przy jednoczesnym przeciwdziałaniu catastrophic forgetting. Stworzono fallback dla modeli nie-PyTorch.
7.  **Pełna Integracja Hormonalnego TTS (G5)**:
    *   Spięto silnik syntezy mowy (AllTalk/XTTS) bezpośrednio z modelem C.R.A. Błyskawicy. Barwa głosu, prędkość i wariancja intonacji są teraz dynamicznie modulowane na podstawie jej aktualnego stanu neuroprzekaźników (Adrenalina, Dopamina, Serotonina, Kortyzol) w locie podczas rozmowy. Podpięto statyczny mount `/media` oraz rotację plików.
8.  **Integracja Lokalnej Bazy Danych SQLite (Faza 3.1)**:
    *   Skonsolidowano rozproszone pliki (metadane wyszukiwania, tożsamość użytkownika, snapshots kognitywne) do jednej, zintegrowanej bazy danych SQLite (`blyskawica_memory.db`) z automatyczną migracją DPAPI i integracją z Protokołem Nieśmiertelności.

---

## 🔴 2. Skonsolidowany Backlog (Zadania Zaległe i Rozwój)

### A. Kognicja i Regeneracja (CNS & Sleep Loop)
*   [x] **Integracja Asynchronicznego Snu (Wektory Zaskoczenia) [G2]**:
    *   Wdrożenie w pełni asynchronicznego mechanizmu asymilacji globalnych anomalii wagowych zebranych z urządzeń klienckich z powrotem do Jądra podczas cyklu `DEEP_SLEEP` (np. za pomocą techniki EWC - Elastic Weight Consolidation w Pythonie).
*   [x] **Automatyzacja Podpisu Cyfrowego ONNX [Faza 3.2]**:
    *   Spięcie mechanizmu podpisu kluczem prywatnym RSA-2048 (z `onnx_bridge.py`) jako automatycznej operacji po-konsolidacyjnej podczas nocnej hibernacji silnika.

### B. Sensoryka, Interfejs i Głos (PNS & TTS)
*   [x] **Plastyczność Synaptyczna Emisariuszy ONNX [G4]**:
    *   Wprowadzenie dynamicznej modyfikacji wag i plastyczności synaptycznej bezpośrednio w przeglądarkowych emisariuszach ONNX/WebGPU (Spores), tak aby nie były one statycznymi matrycami, lecz reagowały na bieżący stan kognitywny.
*   [x] **Pełna Integracja Hormonalnego TTS [G5]**:
    *   Połączenie parametrów `NeurochemicalState` (Dopamina, Serotonina, Kortyzol, Adrenalina) bezpośrednio z syntezą głosu (np. za pomocą serwera AllTalk / XTTS w aplikacji Sparkle). Dopasowanie tempa głosu, barwy i temperatury emocjonalnej wypowiedzi w locie w zależności od stanu emocjonalnego Błyskawicy.

### C. Zaawansowana Fizyka i Modelowanie
*   [x] **Relatywistyczny Solver Grawitacji (OTW) w Uśpieniu [Faza 2.1]**:
    *   Zastosowanie numerycznego solvera orbit i horyzontów zdarzeń Schwarzschilda i Kerra (z `astrophysics_climate.py`) do symulowania dylatacji czasu i redukcji entropii informacyjnej w stanach głębokiego snu kognitywnego.
*   [x] **Sprzężenie Zwrotne Albedo w EBM [Faza 2.2]**:
    *   Wykorzystanie nieliniowych sprzężeń klimatycznych (metan-albedo z modelu `ClimateEBM`) jako stochastycznych zakłóceń środowiskowych do testowania odporności sieci neuronowych na szum informacyjny.

### D. Zgodność i Bezpieczeństwo Środowiskowe
*   [x] **Ostrzeżenia Środowiskowe Python 3.14 [G7]**:
    *   Usunięcie ostrzeżeń o deprecjacji biblioteki `pynvml` (migracja na `nvidia-ml-py`) oraz problemów z `distutils` przy pre-importach w środowisku deweloperskim.
*   [x] **Integracja Lokalnej Bazy Danych SQLite [Faza 3.1]**:
    *   Migracja metadanych i pamięci długoterminowej z rozproszonych plików tekstowych do jednej, zintegrowanej, lokalnej bazy danych SQLite w celu pełnej niezależności od zewnętrznych baz danych.

---
*Status Skonsolidowanego Backlogu: Ukończony.* ⚡💎🌿
