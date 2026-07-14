# ADR 0001: Wybór Tauri jako kanonicznej powłoki aplikacji (Single Shell Decision)

## Stan
**ZAAKCEPTOWANE**

## Kontekst
Projekt Błyskawica posiadał wcześniej dwie równoległe ścieżki aplikacyjne (frontendy):
1.  **Ścieżka A**: Python FastAPI serwujący pliki HTML/CSS/JS wyświetlane w przeglądarce (np. Microsoft Edge w trybie app).
2.  **Ścieżka B**: Rust/Tauri v2 renderujący niezależnie ten sam interfejs, komunikujący się z biblioteką `blyskawica_core` w Rust.

To rozwidlenie architektoniczne powodowało szereg problemów:
*   Marnowanie zasobów na utrzymywanie i stylizowanie dwóch osobnych wersji frontendu.
*   Desynchronizacja stanu neurochemicznego (FastAPI używa pełnego silnika CRA w PyTorch, podczas gdy Tauri używał uproszczonego wątku w Rust).
*   Brak spójnego i bezpiecznego zarządzania uprawnieniami systemowymi (3-poziomowy reżim bezpieczeństwa wymaga natywnej integracji z systemem operacyjnym, co jest trudne do osiągnięcia w zwykłej przeglądarce).

## Decyzja
Wybieramy **Tauri (`sparkle_app`)** jako jedyną, oficjalną powłokę użytkownika (canonical shell) dla interfejsu domowego AI Błyskawicy. 

*   Aplikacja Tauri staje się jedynym punktem wejścia dla interakcji graficznej.
*   Frontend FastAPI (`blyskawica_app/frontend`) zostaje wyłączony z dystrybucji produkcyjnej i zachowany wyłącznie do celów testowych/developerskich.
*   Serwer FastAPI w Pythonie będzie działał w tle w trybie bezgłowym (headless), realizując operacje wymagające ciężkich obliczeń uczenia maszynowego (PyTorch, LLM Ollama, dynamiczne monitorowanie procesów Windows 11).
*   Komunikacja między powłoką Tauri a Pythonem będzie odbywać się za pomocą wywołań HTTP API ze strony frontendu Tauri oraz poprzez zapytania statusu w Tauri Core.

## Konsekwencje
*   **Wydajność**: Aplikacja Tauri zapewnia natywne okno o małym narzucie pamięci RAM oraz bezpośredni dostęp do API systemu Windows 11.
*   **Bezpieczeństwo**: 3-poziomowy model bezpieczeństwa (Sandbox → Workspace → Full OS) jest teraz egzekwowany na poziomie natywnego kodu Rust z potwierdzeniami systemowymi (MessageBoxW) i kontrolą uprawnień do plików/katalogów.
*   **Spójność stanu**: Parametry kognitywne i stany neurochemiczne są pobierane w pętli z FastAPI, łącząc natywną kwarantannę sieciową i wątkową (Rust) z plastycznością synaptyczną (Python).
*   **Utrzymanie**: Modyfikacje wyglądu i zachowania UI będą dokonywane wyłącznie w katalogu `sparkle_app/src`.
