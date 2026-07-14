# UX Information Architecture — SPARKLE VIBE IDE

## Cel projektu
Uporządkowanie struktury informacji i elementów interfejsu graficznego SPARKLE, aby unikalne, zaawansowane cechy (takie jak monitor neurochemiczny czy regime bezpieczeństwa) miały jasne znaczenie i nie przytłaczały użytkownika przy pierwszym kontakcie.

---

## 1. Obietnica Produktu (Product Promise)
> *"Zogniskowana przestrzeń robocza AI do myślenia, kodowania i kolaboracji — zasilana żywym rdzeniem kognitywnym."*

Obietnica ta musi być widoczna na ekranie powitalnym aplikacji oraz w głównym pliku `README.md`.

---

## 2. Mapa Poziomów Funkcji (Feature Tier Map)

Aby zapewnić czystość i czytelność interfejsu, funkcje zostały podzielone na trzy poziomy widoczności:

### Poziom 1: Główne (Primary) — Zawsze Widoczne
Te funkcje stanowią o wartości użytkowej systemu jako asystenta AI i środowiska programistycznego:
1.  **Czat kognitywny Błyskawicy** (Centralny Hub konwersacyjny).
2.  **Eksplorator plików workspace** (Pasek boczny z listą plików w katalogu roboczym).
3.  **Edytor kodu** (Główny edytor tekstowy z przyciskiem zapisu Vibe Code).
4.  **Wskaźnik statusu rdzenia** (Nagłówek aplikacji z informacją o aktywności silnika i przyciskiem uruchomienia).

### Poziom 2: Drugorzędne (Secondary) — Łatwo Dostępne (1 kliknięcie)
Te funkcje są unikalne dla Błyskawicy, ale nie są wymagane do każdej podstawowej akcji:
1.  **Monitor neurochemiczny** (Wizualne wskaźniki Dopaminy, Serotoniny, GABA, Oksytocyny i Melatoniny). Umieszczony pod czatem w lewym panelu.
2.  **Współpraca z modelami gości (Guest Collaboration)** (Zakładka pozwalająca zapraszać i rozmawiać z zewnętrznymi modelami LLM w trybie dualnym).

### Poziom 3: Zaawansowane (Advanced) — Schowane / Mniej Eksponowane
Funkcje systemowe i monitorujące, które interesują zaawansowanych użytkowników lub deweloperów:
1.  **Reżim bezpieczeństwa (Security Regime)** (Slider wyboru poziomu uprawnień: Sandbox / Workspace / Full OS). Umieszczony dyskretnie w stopce aplikacji.
2.  **Lokalny Emisariusz Edge (ONNX Spore)** (Zakładka z symulacją działania sieci neuronowej na WebGPU).
3.  **Strumień aktywności rdzenia (Activity Stream/Logs)** (Konsola z logami zrzucana na sam dół lewego panelu, z opcją czyszczenia i eksportu).

---

## 3. Przebieg Interakcji & Hierarchia Wizualna
1.  **Lewy Panel (Wąski/Główny)**: Skupia się na relacji z Błyskawicą (Czat, stan neurochemiczny) oraz diagnostyce technicznej (Activity Stream).
2.  **Prawy Panel (Szeroki/Zakładki)**: Przestrzeń robocza i zaawansowana. Domyślnie otwiera Workspace (edytor). Pozostałe dwie zakładki (Guest Collaboration i ONNX Spore) są dostępne jako karty.
3.  **Stopka (Status Bar)**: Dedykowana kontroli bezpieczeństwa systemu.
