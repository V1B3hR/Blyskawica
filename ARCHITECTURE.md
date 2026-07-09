# Architektura Systemu Błyskawica V9

> **Data aktualizacji**: 2026-05-28  
> **Audyt spójności**: Przeprowadzony — patrz `roadmap_V9.md` sekcja "Status aktualizacji"

---

## 1. Przegląd Architektoniczny

Błyskawica V9 to hybrydowy system kognitywno-symulacyjny zbudowany na **trzech warstwach**:

```mermaid
graph TB
    subgraph "Warstwa 1: Interfejs Użytkownika"
        A["Sparkle UI (HTML/CSS/JS)"]
        B["Tauri Shell (Rust)"]
    end
    
    subgraph "Warstwa 2: Backend & Orkiestracja"
        C["FastAPI Backend (Python)\nmain.py — 970 LOC"]
        D["Ollama LLM\nlocalhost:11434"]
        E["blyskawica_core (Rust)\nstate_manager.rs"]
    end
    
    subgraph "Warstwa 3: Rdzeń Kognitywny"
        F["CNS\nnetwork.py, neurochemistry.py,\nsoul.py, cognitive_hygiene.py"]
        G["Układ Immunologiczny\nwolf_teeth.py, epistemic_defense.py"]
        H["Konsolidacja\nconsolidation.py (intelligence/)"]
        I["ONNX Bridge\nonnx_bridge.py"]
    end
    
    A --> C
    B --> E
    C --> D
    C --> F
    C --> G
    C --> H
    C --> I
    E --> B
```

---

## 2. Dwie Ścieżki Aplikacyjne

### Ścieżka A: Python FastAPI (`blyskawica_app/`)
- **Backend**: `blyskawica_app/backend/main.py` — serwer FastAPI
- **Frontend**: `blyskawica_app/frontend/` — HTML/CSS/JS (3 pliki)
- **Integracje**: Ollama LLM, CRA Engine, Wolf Teeth, Konsolidacja, DuckDuckGo search
- **Uruchomienie**: `python -m uvicorn main:app` na porcie 8000

### Ścieżka B: Rust/Tauri (`sparkle_app/`)
- **Shell**: `sparkle_app/src-tauri/` — Tauri v2 z `lib.rs` (338 LOC)
- **Core**: `blyskawica_core/` — oddzielna biblioteka Rust
- **Frontend**: `sparkle_app/src/` — HTML/CSS/JS (3 pliki)
- **Uruchomienie**: `cargo tauri dev`

> **⚠️ Uwaga**: Te dwie ścieżki posiadają **oddzielne implementacje** neurochemii i zarządzania stanem. Docelowa architektura powinna wykorzystywać Tauri jako natywny shell z Python FastAPI jako serwisem backendowym.

---

## 3. Moduły Rdzeniowe (Python)

### Centralny Układ Nerwowy (`central_nervous_system/`)
| Moduł | Rozmiar | Funkcja |
|-------|---------|---------|
| `alive_node.py` | 149 KB | Logika uczenia węzłów sieci |
| `network.py` | 40 KB | Sieć ewolucyjna z genomami i selekcją Pareto |
| `neurochemistry.py` | 12 KB | Stan neurochemiczny (adenozyna, dopamina, serotonina, GABA, oksytocyna, testosteron) |
| `cognitive_hygiene.py` | 11 KB | CRA Engine — RealityAnchor, EthicalLongTermVector, ExistentialPause |
| `soul.py` | 7 KB | Tożsamość, integralność kwantowa, więź z Architektem |
| `consolidation.py` | 23 KB | Konsolidacja pamięci (fazowa, synaptyczna, narracyjna) |
| `onnx_bridge.py` | 7 KB | Eksport/podpis kryptograficzny modeli ONNX |

### Układ Immunologiczny (`immune_system/`)
| Moduł | Funkcja |
|-------|---------|
| `wolf_teeth.py` | Honey-pot, Sticky Ooze, Dissolve (glitch tokens) |
| `epistemic_defense.py` | Kwarantanna sprzeczności ontologicznych |
| `trust_network.py` | Sieć zaufania między węzłami |
| `robustness_validator.py` | Walidacja odporności (44 KB) |

### Narzędzia Kognitywne (`cognitive_tools/`)
| Moduł | Funkcja |
|-------|---------|
| `pinn_thermal_engine.py` | Physics-Informed Neural Network (Fourier) |
| `diamond_yant_cymatics.py` | Symulacja cymatyczna (Chladni) |
| `neuro_regulator.py` | Automatyczne profilowanie transmiterów |
| `polymathic_hub.py` | Hub interdyscyplinarny |

---

## 4. Rozszerzenie Nethical (`extensions/nethical/`)
Samodzielny framework etyczny z:
- 25 Fundamentalnymi Prawami (`FUNDAMENTAL_LAWS.md`)
- Formalną weryfikacją (`formal/`)
- API v1 (`openapi-v1.yaml`)
- SDK i taksonomie
- Docker Compose + monitoring Prometheus/Grafana

---

## 5. Stos Technologiczny

| Warstwa | Technologie |
|---------|------------|
| Frontend | HTML5, CSS3, JavaScript (vanilla) |
| Backend Python | FastAPI, PyTorch ≥2.0, ONNX, NumPy, SciPy |
| Backend Rust | Tauri v2, tokio, serde |
| LLM | Ollama (qwen2.5:7b / qwen2.5:14b) |
| Baza danych | SQLite (cache wyszukiwania, time series) |
| Deployment | Docker, docker-compose, Kubernetes (k8s/) |
| Testy | pytest (1006 zebranych testów), cargo test |

---

## 6. Bezpieczeństwo

- **3-poziomowy model uprawnień**: Sandbox (1) → Workspace (2) → Full OS (3)
- **CORS**: Ograniczone do `localhost` i Tauri origins
- **Wolf Teeth**: 3-etapowa obrona (bait → ooze → dissolve)
- **Epistemic Defense**: Kwarantanna sprzeczności logicznych
- **Synaptyczne Veto**: Ochrona plików rdzeniowych przed modyfikacją
- **ONNX signing**: Podpis RSA-2048 eksportowanych modeli
