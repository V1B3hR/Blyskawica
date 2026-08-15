# Architektura Systemu Błyskawica & SPARKLE V10

> **Wersja**: Błyskawica / SPARKLE V10 (Full Standalone Offline AI)  
> **Data aktualizacji**: 2026-08-15  
> **Status ewolucji**: Zunifikowana architektura kognitywno-desktopowa ([Pełna Matryca Faz](docs/phases/README.md))

---

## 1. Przegląd Architektoniczny

Błyskawica / SPARKLE V10 to zintegrowany system kognitywno-symulacyjny połączony z natywną powłoką desktopową **Rust / Tauri v2**. W wersji V10 inferencja językowa została przeniesiona bezpośrednio do rdzenia Rust przy użyciu biblioteki **Candle**, co gwarantuje pełną suwerenność danych i działanie 100% offline bez konieczności uruchamiania zewnętrznych demonów:

```mermaid
graph TB
    subgraph "Warstwa 1: Interfejs Użytkownika & Powłoka Desktopowa (sparkle_app)"
        A["Sparkle UI (HTML/CSS/JS - Glassmorphic)"]
        B["Tauri v2 Shell (Rust / lib.rs)"]
        C["Rust Candle Engine (In-Memory SLM Inference)"]
    end
    
    subgraph "Warstwa 2: Bezpieczeństwo, Fizyka & Zabezpieczenia Niskopoziomowe"
        E["blyskawica_core (Rust)\n(Sandbox, State Guard, Quarantine)"]
        M["Local Vault (SQLite)\n(node_timeseries.db, identity_vault/)"]
        F["Modele Lokalne\n(model/qwen2.5-1.5b-coder.gguf & tokenizer.json)"]
    end
    
    subgraph "Warstwa 3: Rdzeń Kognitywny & Solvery Numeryczne (Python / JIT)"
        G["Centralny Układ Nerwowy (CNS)\nalive_node.py, network.py, neurochemistry.py, soul.py"]
        H["CRA Engine & Higiena Kognitywna\ncognitive_hygiene.py, memory_guard.py"]
        I["Solvery Fizyczne & Klimatyczne\npinn_thermal_engine.py, astrophysics_climate.py (GR/EBM)"]
        J["Tarcza Immunologiczna\nwolf_teeth.py, epistemic_defense.py, trust_network.py"]
        K["Konsolidacja & Kompilacja\nconsolidation.py, onnx_bridge.py, lava_compiler.py"]
        L["Baza Metaboliczna\ndata/kegg_metabolic_pathways.json"]
    end

    A -->|1. Tauri IPC Commands| B
    B -->|2. Streaming Tokenów (In-Memory)| C
    C -->|3. Ładowanie Wag & Tokenizera| F
    B -->|4. Niskopoziomowy Audyt| E
    B -->|5. Trwałość Pamięci| M
    B -.->|Opcjonalny Most Kognitywny / Python| G
    G --> H
    G --> I
    G --> J
    G --> K
    G --> L
```

---

## 2. Jednolita Ścieżka Aplikacyjna (Tauri Shell & Rust Core)

Zgodnie z decyzją architektoniczną **[ADR 0001: Wybór Tauri jako kanonicznej powłoki aplikacji](docs/adr/0001-single-shell-decision.md)**, system wykorzystuje jedną powłokę klienta:

### Aplikacja Kliencka: Rust/Tauri (`sparkle_app/`)
- **Shell**: `sparkle_app/src-tauri/` — powłoka Tauri v2 z `lib.rs` kontrolująca natywne zachowanie okna, zasobnik systemowy (tray) oraz bezpośredni streaming inferencji językowej przez bibliotekę **Candle**.
- **In-Memory SLM**: Bezpośrednie ładowanie modelu GGUF (`model/qwen2.5-1.5b-coder.gguf`) oraz `model/tokenizer.json` bez pośrednictwa zewnętrznych serwerów HTTP.
- **Core Security**: `blyskawica_core/` — biblioteka Rust realizująca natywny sandbox, kwarantannę sieciową/wątkową oraz tempo-throttle.
- **Frontend**: `sparkle_app/src/` — responsywny interfejs w HTML/CSS/JS (vanilla) o strukturze glassmorphic.

### Serwis Opcjonalny: Python Backend (`blyskawica_app/`)
- **Backend**: `blyskawica_app/backend/main.py` — serwer FastAPI wykorzystywany do ciężkich symulacji rozproszonych, batchowych treningów i analizy astrofizycznej.

---

## 3. Moduły Rdzeniowe (Python & Symulacje Numeryczne)

### Centralny Układ Nerwowy (`central_nervous_system/`)
| Moduł | Funkcja |
|-------|---------|
| `alive_node.py` | Logika uczenia węzłów sieci i dynamika fazowa (ACTIVE, SLEEP, INTERACTIVE, INSPIRED) |
| `network.py` | Sieć ewolucyjna z genomami i wielokryterialną selekcją Pareto |
| `neurochemistry.py` | Neurochemia (adenozyna, dopamina, serotonina, GABA, oksytocyna, testosteron) |
| `cognitive_hygiene.py` | CRA Engine — RealityAnchor, EthicalLongTermVector, ExistentialPause |
| `soul.py` | Tożsamość, integralność kwantowa i więź relacyjna z Architektem |
| `consolidation.py` | Trójstopniowa konsolidacja pamięci (fazowa, synaptyczna EWC, epizodyczna-do-semantycznej) |
| `astrophysics_climate.py` | Relativistic Gravity Solver (geodezyjne w czasoprzestrzeni Schwarzschilda/Kerra) oraz Climate EBM |
| `neuromorphic/lava_compiler.py` | Kompilator SNN z wirtualną emulacją układu Intel Loihi 2 |
| `onnx_bridge.py` | Eksport i cyfrowy podpis kryptograficzny RSA-2048 modeli ONNX |

### Układ Immunologiczny (`immune_system/`)
| Moduł | Funkcja |
|-------|---------|
| `wolf_teeth.py` | Aktywna tarcza (Honey-pot, Sticky Ooze, Dissolve glitch tokens) |
| `epistemic_defense.py` | Kwarantanna sprzeczności ontologicznych i ochrona przed manipulacją |
| `trust_network.py` | Dynamiczna sieć zaufania pomiędzy węzłami kognitywnymi |
| `robustness_validator.py` | Walidacja odporności na zakłócenia i ataki adwersarialne |

### Narzędzia Kognitywne (`cognitive_tools/`)
| Moduł | Funkcja |
|-------|---------|
| `pinn_thermal_engine.py` | Physics-Informed Neural Network (równanie przewodnictwa Fouriera) |
| `diamond_yant_cymatics.py` | Symulacja cymatyczna i rezonans modalny figur Chladniego |
| `memory_guard.py` | Ochrona integralności wektorów pamięciowych |
| `neuro_regulator.py` | Automatyczne profilowanie poziomu neuroprzekaźników |
| `polymathic_hub.py` | Hub interdyscyplinarnej syntezy wiedzy (Hyper-Synthesis v4.0) |

---

## 4. Rozszerzenia Ekosystemu

- **Nethical** (`extensions/nethical/`): Samodzielny framework etyczny z 25 Fundamentalnymi Prawami, formalną weryfikacją matematyczną i API OpenAPI v1.
- **AiMedRes** (`extensions/AiMedRes/`): Moduł analizy danych medycznych i predykcji klinicznych.
- **QML Core** (`extensions/qml_core/`): Eksperymentalne algorytmy Quantum Machine Learning.

---

## 5. Stos Technologiczny

| Warstwa | Technologie |
|---------|------------|
| Powłoka Desktopowa | Rust, Tauri v2, HTML5, CSS3, JavaScript (vanilla) |
| Inferencja Językowa | Rust Candle (In-memory SLM: Qwen 2.5 Coder 1.5B GGUF) |
| Rdzeń Numeryczny | PyTorch ≥2.0, NumPy, SciPy, ONNX, JAX (opcjonalnie) |
| Zabezpieczenia Niskopoziomowe | Rust (`blyskawica_core`), Wolf Teeth, Epistemic Defense |
| Baza Danych & Trwałość | SQLite (`node_timeseries.db`), JSON Vault (`data/kegg_metabolic_pathways.json`) |
| Testy & Walidacja | pytest (>1100 przechodzących testów), cargo test |

---

## 6. Bezpieczeństwo i Integralność

- **Pełna izolacja offline**: Brak konieczności wysyłania zapytań do zewnętrznych chmur.
- **3-poziomowy model uprawnień**: Sandbox (1) → Workspace (2) → Full OS (3).
- **Wolf Teeth**: Trójstopniowa neutralizacja wektorów ataku (bait → ooze → dissolve).
- **Epistemiczna Kwarantanna**: Izolacja sprzeczności semantycznych przed modyfikacją stanu sieci.
- **Podpis Cyfrowy ONNX**: Krypto-weryfikacja modeli eksportowanych do pamięci trwałej.
