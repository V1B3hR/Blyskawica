# Architektura Systemu Błyskawica V9

> **Data aktualizacji**: 2026-05-28  
> **Audyt spójności**: Przeprowadzony — patrz `roadmap_V9.md` sekcja "Status aktualizacji"

---

## 1. Przegląd Architektoniczny

Błyskawica V9 to hybrydowy system kognitywno-symulacyjny zunifikowany wokół powłoki Tauri, komunikującej się z bezgłowym (headless) backendem Python FastAPI:

```mermaid
graph TB
    subgraph "Warstwa 1: Interfejs Użytkownika"
        A["Sparkle UI (HTML/CSS/JS)"]
        B["Tauri Shell (Rust / sparkle_app)"]
    end
    
    subgraph "Warstwa 2: Orkiestracja & Zabezpieczenia"
        E["blyskawica_core (Rust)\nstate_manager.rs"]
        C["FastAPI Backend (Python)\nmain.py (Port 8000)"]
        D["Ollama LLM\nlocalhost:11434"]
    end
    
    subgraph "Warstwa 3: Rdzeń Kognitywny"
        F["CNS\nnetwork.py, neurochemistry.py,\nsoul.py, cognitive_hygiene.py"]
        G["Układ Immunologiczny\nwolf_teeth.py, epistemic_defense.py"]
        H["Konsolidacja\nconsolidation.py (intelligence/)"]
        I["ONNX Bridge\nonnx_bridge.py"]
    end
    
    A -->|1. Tauri Commands| B
    B -->|2. Niskopoziomowy Audyt| E
    A -->|3. API Chat & Actions (HTTP)| C
    B -->|4. Synchronizacja cra_metrics| C
    C -->|Inference / LLM| D
    C -->|Zarządzanie Genomem| F
    C -->|Heurystyka i Kwarantanna| G
    C -->|Konsolidacja & ONNX Spore| H
    C -->|Podpis Cyfrowy ONNX| I
```

---

## 2. Jednolita Ścieżka Aplikacyjna (Tauri Shell)

Zgodnie z decyzją architektoniczną **[ADR 0001: Wybór Tauri jako kanonicznej powłoki aplikacji](docs/adr/0001-single-shell-decision.md)**, system wykorzystuje jedną powłokę klienta połączoną z bezgłowym serwisem backendowym:

### Aplikacja Kliencka: Rust/Tauri (`sparkle_app/`)
- **Shell**: `sparkle_app/src-tauri/` — powłoka Tauri v2 z `lib.rs` (338 LOC) kontrolująca natywne zachowanie systemu i gating uprawnień.
- **Core Security**: `blyskawica_core/` — niskopoziomowa biblioteka w Rust realizująca natywny sandbox, kwarantannę sieciową/wątkową oraz tempo-throttle.
- **Frontend**: `sparkle_app/src/` — premium interfejs w HTML/CSS/JS (vanilla) o strukturze glassmorphic.

### Serwis Backendowy: Python FastAPI (`blyskawica_app/`)
- **Backend**: `blyskawica_app/backend/main.py` — bezgłowy serwer FastAPI działający w tle na porcie 8000.
- **Funkcja**: Realizacja ciężkich operacji kognitywnych, zarządca modeli PyTorch, integracja z lokalnym API Ollama oraz monitor kontekstu Windows 11.
- **Uruchomienie**: Wystartowanie backendu następuje automatycznie z poziomu skryptu `Uruchom_Sparkle.bat`.

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
