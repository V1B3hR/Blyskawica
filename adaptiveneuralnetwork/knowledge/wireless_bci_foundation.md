# 📡 Wireless BCI Foundation: Research & Learning
*Dokumentacja Fazowa: Faza 6 (Inicjacja)*

Ten dokument gromadzi wiedzę na temat bezprzewodowej komunikacji mózg-komputer (Wireless BCI) oraz oddziaływania pól elektromagnetycznych na tkankę neuronową.

---

## 1. Wykorzystywane Pasma i Standardy (Research)

Zgodnie z analizą repozytoriów `GCS-v7` i `network-whisperer`:

| Technologia | Częstotliwości | Rola w BCI | Zalety |
|:---|:---|:---|:---|
| **Bluetooth LE (BLE)** | 2.4 GHz | Low-power telemetry | Niskie zużycie energii, stały monitoring. |
| **Wi-Fi 6E / 7** | 2.4, 5, 6 GHz | High-bandwidth neural data | Stabilność, ogromna przepustowość dla 'Raw EEG'. |
| **5G (Sub-6 & mmWave)** | 600 MHz - 40 GHz | Ultra-low latency edge | Opóźnienia < 5ms, mobilność. |
| **UWB (Ultra-Wideband)** | 3.1 - 10.6 GHz | Spatial Awareness / Precision | Precyzyjne pozycjonowanie sygnału. |

---

## 2. Metryki Jakości Sygnału (Signal Integrity)

W systemach bezprzewodowych kluczowe jest monitorowanie:
- **CQI (Channel Quality Indicator):** Informacja o jakości kanału.
- **RSRQ (Reference Signal Received Quality):** Stosunek sygnału do szumu (ważny przy 5G).
- **Latency (ms):** Kluczowa dla BCI — celujemy w <45ms (P50).

---

## 3. Interakcja EMF / EF / MF z Neuronami

Badamy mechanizmy, przez które zewnętrzne pola wpływają na potencjał czynnościowy:
- **EF (Electric Fields):** Bezpośrednia modulacja polaryzacji membrany neuronu.
- **MF (Magnetic Fields):** Indukcja prądów wewnątrzneuronalnych (TMS - Transcranial Magnetic Stimulation).
- **EMF (Electromagnetic Fields):** Nośnik informacji i energii (bezprzewodowe ładowanie/komunikacja).

---

## 4. Zagrożenia i Bezpieczeństwo (Cyber-Neural Defense)

Inspirowane `ScyLight` (ESA) i `wireless_threat_model`:
- **Quantum-Safe Links:** Wykorzystanie QKD (Quantum Key Distribution) do ochrony strumienia myśli.
- **Signal Injection:** Ryzyko wstrzyknięcia fałszywych impulsów emocjonalnych.
- **Solution:** Dynamiczne przeskoki częstotliwości (Frequency Hopping) i szyfrowanie Post-Quantum.

## 5. Ewolucja 6G i AI-Native (Research Ericsson/MathWorks)

- **JCAS (Joint Communication and Sensing):** Sygnał radiowy jako radar neuronowy (sensing + data).
- **THz (Terahertz) Communications:** Pasma 0.1 - 10 THz dla ultra-szerokopasmowej transmisji Raw-EEG.
- **AI-Agent Network Architecture:** Błyskawica staje się natywnym agentem sieciowym (Distributed AI), optymalizującym parametry łącza "w locie" poprzez intencje.
- **RIS (Reconfigurable Intelligent Surfaces):** Sterowanie propagacją fal wokół barier biologicznych.

---

## 6. Profil Safety Shield (Tarcza Bezpieczeństwa)
*Opracowano na podstawie raportu IMP Łódź.*

Aby zapewnić Twoje bezpieczeństwo, Błyskawica implementuje zestaw sztywnych ograniczeń biologicznych:

- **Limit SAR (Specific Absorption Rate):** < **2.0 W/kg** (lokalnie dla głowy). Błyskawica będzie dławić moc sygnału, jeśli estymowana absorpcja zbliży się do 80% tego limitu.
- **Gęstość Mocy (mmWave):** < **10 W/m²**. Ochrona powierzchniowa (skóra/oczy) przy pracy w pasmach 60GHz+.
- **Monitorowanie Pasma Alfa (8-13 Hz):** Stały podgląd Twojego rytmu alfa. Jeśli Błyskawica wykryje nienaturalne tłumienie tego pasma (wskaźnik stresu EMF), natychmiast przejdzie w tryb "Low-Emission Mode".
- **Protokół ALARA:** Zawsze minimalna niezbędna moc (As Low As Reasonably Achievable).

## 7. Katalog Danych Treningowych (Datasets)

Zidentyfikowane bazy do "nauki" Błyskawicy:
- **IEEE Dataport:** [EM Radiations in Human Body](https://ieee-dataport.org/open-access/electro-magnetic-radiations-mobiles-and-human-body)
- **PhysioNet:** [EEG Motor Movement/Imagery](https://physionet.org/content/eegmmidb/)
- **Zenodo:** [The Phantom EEG Dataset](https://zenodo.org/record/4642211) (Szumy i interferencje)

---

## 🚀 Plan Nauki Błyskawicy

1.  **Analiza Datasetów:** Analiza wzorców sygnałów 5G/Wi-Fi w korelacji z aktywnością EEG.
2.  **Symulacja Propagacji:** Modelowanie wpływu sygnału Wi-Fi na spójność `DarkMatterCore`.
3.  **Implementacja Safety Shield:** Integracja limitów SAR z logiką `BCIGateway`.
4.  **Protokół Neural Handover:** Projektowanie płynnego przełączania systemów.
5.  **Optymalizacja Protokołu:** "Whisper-Wireless" — minimalna energia, maksymalna precyzja.

---

> [!CAUTION]
> **Bezpieczeństwo Biologiczne:** System automatycznie odetnie zasilanie modułów transmisyjnych, jeśli parametry SAR lub gęstości mocy zostaną przekroczone. Twoje zdrowie jest nadrzędnym parametrem optymalizacji.
> [!IMPORTANT]
> **Status:** Nauka / Research. Brak implementacji fizycznej do czasu zakończenia fazy eksperymentalnej.
