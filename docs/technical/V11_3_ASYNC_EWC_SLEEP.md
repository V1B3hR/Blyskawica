# 🌙 V11.3: Asynchroniczny Sen Kognitywny i Regularyzacja EWC (Rust Core)

> **Status:** Wdrożony pierwszy pionowy wycinek V11 (2026-11-25)  
> **Moduł główny:** `blyskawica_core/src/ewc_sleep.rs`  
> **Integracja runtime:** `blyskawica_core/src/state_manager.rs`, `sparkle_app/src-tauri/src/lib.rs`, `sparkle_app/src/main.js`  
> **Referencja ciągłości kognitywnej:** `adaptiveneuralnetwork/central_nervous_system/intelligence/consolidation.py`

---

## 1. Cel i Architektura

Moduł **V11.3** przenosi mechanizm nocnej konsolidacji pamięci (**Elastic Weight Consolidation — EWC**) z prototypu Python do natywnego rdzenia Rust, działającego w 100% offline bez zależności od PyTorch ani sidecara.

Podczas pracy dziennej (`QueryWithVector`) wykryte anomalie (`best_distance > surprise_threshold`) są automatycznie rejestrowane w ograniczonej kolejce `EwcSleepConsolidator` jako wektory zaskoczenia (`SurpriseRecord`). Podczas snu:

* **`StateCommand::DeepSleep`**: konsoliduje pamięć wektorową HNSW w WAL, zwalnia uchwyty `Mmap` przez hibernację (krytyczne na Windows), a następnie wykonuje konsolidację EWC na wagach MLP (128 → 64 ReLU → 128, `16_576` parametrów `f32`, 100% zgodności binarnej z `LocalInferenceEngine`) i zapisuje je atomowo wraz z pieczęcią kryptograficzną.
* **`StateCommand::AsyncDeepSleep`**: uruchamia konsolidację w tle przez `tokio::spawn` + `tokio::task::spawn_blocking`, nie blokując pętli czatu ani interfejsu UI. Zapisuje skrystalizowane wagi do dedykowanego pliku `*.ewc.bin` + pieczęci `*.ewc.seal.json`, dzięki czemu nie koliduje z aktywnym mapowaniem pamięci (`Mmap`) na Windows.

### Formuła matematyczna (EWC + profil neurochemiczny)

1. **Profil snu** (`SleepProfile::from_neurochemistry`):
   * `melatonin = clamp(1.0 - adenosine / 1.5, 0.1, 1.0)`
   * `adenosine_cleared = clamp(1.0 - adenosine, 0.0, 1.0)`
   * `consolidation_depth = melatonin * adenosine_cleared`
   * `plasticity_gate = 1.0 - serotonin * 0.5`
   * `pruning_threshold = 0.05 + gaba * 0.15`
2. **Gradient regularyzowany macierzą Fishera**:
   $$g_i^{\text{total}} = \frac{\partial \mathcal{L}_{\text{surprise}}}{\partial \theta_i} + \lambda \cdot F_i \cdot (\theta_i - \theta_i^*)$$
   gdzie $F_i$ jest akumulowaną diagonalną informacją Fishera (online EWC), a $\theta_i^*$ stanowi kotwicę historycznej wiedzy.
3. **Selektywny pruning GABA**: delikatne wygaszanie (`*= 0.9`) dotyczy wyłącznie niechronionych wag o niskim $F_i$; wagi chronione o wysokim $F_i$ nigdy nie podlegają pruningowi.

---

## 2. Model Zagrożeń i Kontrole Bezpieczeństwa (Fail-Closed)

Zgodnie z wymogiem planu `2026-10-development-plan.md` każdy moduł V11 posiada jawny model zagrożeń:

| Zagrożenie | Kontrola w `ewc_sleep.rs` / `lib.rs` |
|---|---|
| **Zatrucie numeryczne (NaN / Inf)** | Każda waga, wektor zaskoczenia i parametr neurochemiczny przechodzi walidację `is_finite()`. Wykrycie wartości niefinitywnej podczas kroku EWC uruchamia **atomowy rollback** do snapshotu sprzed kroku. |
| **Wyczerpanie pamięci (OOM / DoS kolejki)** | Sztywny limit `MAX_SURPRISE_QUEUE = 256` (zastępowanie najmniej istotnego elementu) oraz limit metadanych `MAX_METADATA_CHARS = 256`. |
| **Wybuch gradientów / destabilizacja wag** | Przycinanie normy L2 gradientu (`MAX_GRAD_NORM = 1.0`) oraz twardy sufit kroku adaptacji (`MAX_ADAPT_STRENGTH = 0.05`). |
| **Uszkodzenie lub manipulacja pliku wag** | Atomowy zapis (`tmp` + `sync_all` + `rename`) oraz plik pieczęci `.ewc.seal.json` z `SHA-256` + `HMAC-SHA256` weryfikowanym w czasie stałym (`constant_time_eq`). Manipulacja choćby 1 bitem kończy się błędem `verify_sealed_weights`. |
| **Nieautoryzowane wywołanie z WebView** | Komenda IPC `trigger_async_deep_sleep` wymaga poziomu **L2 (Workspace)** (`require_permission_level(..., 2, ...)`). Komenda `get_ewc_sleep_status` zwraca wyłącznie metadane tylko do odczytu (bezpieczna na L1). |

---

## 3. Kryteria Akceptacji (Zweryfikowane Testami)

* Zgodność numeryczna `SleepProfile` z referencją Python (`sleep_profile_matches_python_neurochemistry_contract`).
* Zgodność binarna i inferencyjna z `LocalInferenceEngine` (Candle) (`mlp_weights_binary_roundtrip_matches_local_inference_engine`).
* Odrzucanie wektorów NaN/Inf oraz egzekwowanie limitu 256 wpisów (`surprise_registry_rejects_non_finite_and_enforces_dos_cap`).
* Spadek straty rekonstrukcji na wektorach zaskoczenia (`ewc_assimilates_surprise_vectors_and_reduces_loss`).
* Mierzalna ochrona chronionych wag przed katastrofalnym zapominaniem vs uczenie bez EWC (`ewc_protects_high_fisher_weights_against_catastrophic_forgetting`).
* Atomowa krystalizacja + odrzucenie 1-bitowej manipulacji (`sealed_weights_atomic_save_verify_and_tamper_rejection`).
* Nieblokujące wykonanie asynchroniczne w Tokio i integracja z `BlyskawicaEngine` (`async_sleep_consolidation_runs_non_blocking_on_tokio`, `async_deep_sleep_assimilates_anomalies_without_blocking`).
* Bramka uprawnień L2 w Tauri (`async_deep_sleep_trigger_requires_workspace_permission_and_dispatches`).
