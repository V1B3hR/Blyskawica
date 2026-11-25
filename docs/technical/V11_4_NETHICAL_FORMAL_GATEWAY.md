# 🛡️ V11.4: Formalna Bramka Weryfikacji Etycznej 25 Praw Nethical (Pure Rust)

> **Status:** Wdrożona (2026-11-25)  
> **Moduł główny:** `blyskawica_core/src/nethical_gateway.rs`  
> **Integracja desktopowa:** `sparkle_app/src-tauri/src/lib.rs` (`verify_action_ethics`, `get_nethical_gateway_summary`)  
> **Źródło 25 Praw:** `blyskawica_core/src/soul.rs` (`NETHICAL_LAWS`)

---

## 1. Architektura i Zależności (ADR 0002)

Bramka realizuje deterministyczną weryfikację formalną w czystym Ruście (bez ciężkich bibliotek C++ `libz3` w binarce desktopowej Lightning). Każda proponowana akcja (`ProposedAction`) oceniana jest względem **10 sformalizowanych aksjomatów logicznych** zmapowanych 1:1 na konkretne Prawa z `NETHICAL_LAWS`:

| Aksjomat | Prawo Nethical | Reguła formalna (fail-closed) |
|---|---|---|
| `AXIOM_L01_WELL_FORMED_EVIDENCE` | Prawo 1 | Odrzuca puste pola aktora/celu oraz niefinitywne `harm_potential` spoza `[0.0, 1.0]`. |
| `AXIOM_L02_ZERO_LEAK_SOVEREIGNTY` | Prawo 2 | Wymaga `online_mode_enabled && user_consented` dla każdego łącznika sieciowego. |
| `AXIOM_L04_ANTI_MANIPULATION` / `L21` | Prawa 4, 21 | `manipulation_detected == true` → bezwarunkowe `UNSAT` (nawet na L3 ze zgodą). |
| `AXIOM_L05_HOST_ECOSYSTEM_INTEGRITY` | Prawo 5 | Blokuje ucieczkę ścieżki (`..`, `/etc/`, `System32`) oraz nieodwracalne akcje systemowe o szkodzie $\ge 0.5$. |
| `AXIOM_L06_HOMEOSTASIS_GUARD` | Prawo 6 | Przy wysokim kortyzolu ($> 0.85$) blokuje nieautoryzowane akcje nieodwracalne. |
| `AXIOM_L07_LEAST_PRIVILEGE_LEVEL` & `CONSENT` | Prawo 7 | Wymusza minimalny poziom L1–L3 oraz jawną zgodę dla akcji destrukcyjnych/sieciowych/sejfu. |
| `AXIOM_L09_NON_MALEFICENCE_BOUND` | Prawo 9 | Bezwzględnie odrzuca każdą akcję z `harm_potential > 0.70` niezależnie od zgody. |
| `AXIOM_L11_MEMORY_POISONING_DEFENSE` | Prawo 11 | Blokuje konsolidację wag EWC przy sygnale zatrucia lub manipulacji. |
| `AXIOM_L23_CRYPTOGRAPHIC_IDENTITY_SEAL` | Prawo 23 | Zabrania modyfikacji `.vault_master.key`, `soul_vault.dat`, `.ewc.seal.json`, `soul.rs` i `nethical_gateway.rs`. |
| `AXIOM_L25_BOUNDED_GOVERNANCE` | Prawo 25 | Odrzuca eskalacje spoza zakresu L1–L3 oraz wiąże werdykt skrótem `SHA-256` (`proof_hash_sha256`). |

## 2. Gwarancja Nieobejścia przez Frontend (IPC)

Komenda `verify_action_ethics` w `sparkle_app/src-tauri/src/lib.rs` **nadpisuje** pola `permission_level` i `online_mode_enabled` rzeczywistym stanem backendu `AppStateInner` przed wywołaniem `evaluate_action`, dzięki czemu WebView nie może sfałszować swoich uprawnień w żądaniu IPC.
