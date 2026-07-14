# Podręcznik Budowania Produkcyjnego (Production Build Guide)
**Projekt: Błyskawica V9 / SPARKLE VIBE IDE**

Podręcznik ten opisuje kroki niezbędne do skompilowania, zoptymalizowania i wdrożenia aplikacji Sparkle w wersji instalacyjnej (Standalone Release) na platformę Windows 11.

---

## 1. Optymalizacje Kompilatora Rust (`Cargo.toml`)

W plikach `blyskawica_core/Cargo.toml` oraz `sparkle_app/src-tauri/Cargo.toml` zdefiniowano produkcyjny profil kompilacji `[profile.release]`, mający na celu minimalizację rozmiaru pliku wykonywalnego i maksymalizację szybkości przetwarzania:

```toml
[profile.release]
opt-level = 3           # Pełna optymalizacja kodu wynikowego pod kątem szybkości
lto = true              # Link-Time Optimization (optymalizacja kodu w poprzek pakietów)
codegen-units = 1       # Redukcja jednostek generowania kodu (lepsze LTO, mniejszy rozmiar)
panic = "abort"         # Zastąpienie mechanizmu rozwijania stosu (unwinding) natychmiastowym przerwaniem
strip = true            # Całkowite usuwanie symboli debugowania oraz tabeli symboli z pliku .exe
```

---

## 2. Przygotowanie Środowiska (Prerequisites)

Do zbudowania aplikacji wymagane są zainstalowane na systemie Windows 11:
1.  **Rust i Cargo**: Najnowsza stabilna wersja (np. poprzez `rustup`).
2.  **Node.js & npm**: Do spakowania i przygotowania frontendowych zasobów SPA.
3.  **Wix Toolset (v3)**: Wymagany przez Tauri v2 do generowania plików instalacyjnych `.msi`.

---

## 3. Procedura Budowania Krokowego (Build Procedure)

### Krok 3.1: Budowa i Instalacja Zależności Frontendu
W folderze aplikacji klienckiej zainstaluj pakiety i przygotuj zasoby webowe:

```bash
cd sparkle_app
npm install
```

### Krok 3.2: Kompilacja Produkcyjna Powłoki Tauri
Uruchom oficjalną procedurę Tauri, która automatycznie skompiluje frontend, połączy go ze skompilowaną biblioteką Rust (`blyskawica_core`) i utworzy zoptymalizowany plik instalacyjny:

```bash
npm run tauri build
```

*Alternatywnie (używając bezpośrednio CLI Cargo):*
```bash
cargo tauri build
```

---

## 4. Specyfikacja Artefaktów Wynikowych (Build Artifacts)

Po udanym zakończeniu procesu budowania, instalator oraz binaria będą zlokalizowane w poniższych ścieżkach:

| Typ Artefaktu | Ścieżka Wynikowa |
| --- | --- |
| **Samodzielny Plik Wykonywalny (.exe)** | `sparkle_app\src-tauri\target\release\sparkle_app.exe` |
| **Instalator Systemowy Windows (.msi)** | `sparkle_app\src-tauri\gen\binder\sparkle_app_0.1.0_x64_en-US.msi` |

---

## 5. Zapewnienie Trybu "Offline Standalone" (Static Linking)

Wszystkie kluczowe biblioteki Rust (np. `hnsw_rs`, `candle-core`, `candle-nn`) są statycznie linkowane wewnątrz pliku wykonywalnego `sparkle_app.exe`. Gwarantuje to, że:
*   Aplikacja Tauri uruchamia się i działa bez potrzeby pobierania bibliotek DLL z internetu.
*   Logika kwarantanny sieciowej `wolf_teeth` oraz lokalne dopasowywanie wektorów HNSW działają całkowicie w trybie offline.
*   Zasoby frontendu (HTML/CSS/JS) są osadzone bezpośrednio wewnątrz kodu binarnego aplikacji Tauri przy użyciu wbudowanego kompilatora zasobów webview.
