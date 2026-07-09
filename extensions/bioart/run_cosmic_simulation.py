#!/usr/bin/env python3
"""
run_cosmic_simulation.py – Kosmiczna Symulacja Bio-Kwantowa V1B3hR
Autor: Andrzej Matewski (V1B3hR)
Licencja: MIT

Zasilaj symulację danymi z kosmosu, orbity i światłowodów (White-Hat only).
Wymaga: Python 3.7+, brak zewnętrznych zależności.
"""

from __future__ import annotations

import json
import math
import random
import sys
import time
import urllib.error
import urllib.request

from V1B3hR_BioArt_Core import BioArtGenerator

# ---------------------------------------------------------------------------
# Tożsamość DNA V1B3hR
# ---------------------------------------------------------------------------
_DNA_SIGNATURE = "ATGC" * 10 + "V1B3hR_ANDRZEJ_MATEWSKI"

# ---------------------------------------------------------------------------
# Stałe konfiguracyjne
# ---------------------------------------------------------------------------
_LOOP_INTERVAL_S = 4          # czas między iteracjami pętli (sekundy)
_HTTP_TIMEOUT_S = 5           # limit czasu żądań HTTP (sekundy)
_ISS_API_URL = "http://api.open-notify.org/iss-now.json"
_NET_PROBE_URL = "https://api.github.com"
_MUTATION_BASE_RATE = 0.005   # bazowy współczynnik mutacji (0.5 %)
_MUTATION_MAX_RATE = 0.03     # maksymalny bezpieczny współczynnik (3 %)


# ---------------------------------------------------------------------------
# 1. Spojrzenie z Orbity – ISS
# ---------------------------------------------------------------------------
def fetch_iss_position() -> tuple[float, float] | None:
    """
    Pobiera aktualną lokalizację ISS z publicznego API.
    Zwraca (latitude, longitude) lub None przy błędzie sieci.
    """
    try:
        with urllib.request.urlopen(_ISS_API_URL, timeout=_HTTP_TIMEOUT_S) as response:
            data = json.loads(response.read().decode())
        pos = data["iss_position"]
        return float(pos["latitude"]), float(pos["longitude"])
    except (urllib.error.URLError, urllib.error.HTTPError, KeyError, ValueError):
        return None


# ---------------------------------------------------------------------------
# 2. Pływanie po Światłowodach – tętno sieci
# ---------------------------------------------------------------------------
def measure_network_pulse() -> float | None:
    """
    Mierzy czas odpowiedzi (ms) publicznego serwera jako „tętno" internetu.
    Zwraca opóźnienie w milisekundach lub None przy błędzie.
    """
    try:
        start = time.perf_counter()
        with urllib.request.urlopen(_NET_PROBE_URL, timeout=_HTTP_TIMEOUT_S) as response:
            _ = response.read(256)  # minimalny odczyt – nie pobieramy całości
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        return elapsed_ms
    except (urllib.error.URLError, urllib.error.HTTPError, OSError):
        return None


# ---------------------------------------------------------------------------
# 3. Skok za Galaktykę – symulacja kosmicznego szumu tła
# ---------------------------------------------------------------------------
def cosmic_background_noise(t: float) -> float:
    """
    Generuje „szum tła wszechświata" na podstawie czasu i funkcji
    trygonometrycznych.  Zwraca wartość [0.0, 1.0] odzwierciedlającą
    natężenie kosmicznego szumu w chwili t.
    """
    # Superpozycja harmonik o różnych częstotliwościach
    signal = (
        0.5 * math.sin(t * 0.7)
        + 0.3 * math.cos(t * 1.3)
        + 0.2 * math.sin(t * 2.9 + math.pi / 4)
    )
    # Normalizacja do [0, 1]
    return (signal + 1.0) / 2.0


# ---------------------------------------------------------------------------
# Pomocnicze – obliczanie wpływu ISS na płynność wzrostu
# ---------------------------------------------------------------------------
def iss_growth_factor(lat: float, lon: float) -> float:
    """
    Przelicza pozycję ISS na współczynnik wzrostu [0.5, 1.5].
    Stacja nad równikiem (lat≈0) lub południkiem zerowym (lon≈0)
    generuje silniejszy impuls – symbolizując bliższe połączenie z Ziemią.
    """
    # ISS inclination is ~51.6°, so lat is always in [-51.6°, 51.6°] and
    # cos(lat) is always positive – lat_norm is safely in [0.62, 1.0].
    lat_norm = math.cos(math.radians(lat))   # 1.0 at equator, ≈0.62 at ±51.6°
    lon_norm = (math.cos(math.radians(lon)) + 1.0) / 2.0  # [0, 1]
    return 0.5 + lat_norm * lon_norm


# ---------------------------------------------------------------------------
# Główna pętla symulacji
# ---------------------------------------------------------------------------
def run_simulation(engine: BioArtGenerator) -> None:
    """
    Nieskończona pętla kosmicznej symulacji bio-kwantowej.
    Ctrl+C kończy pętlę w elegancki sposób.
    """
    print("=" * 54)
    print("  🧬 KOSMICZNA SYMULACJA BIO-KWANTOWA V1B3hR 🧬")
    print(f"  DNA Hash: {engine.signature[:24]}...")
    print("  [Ctrl+C aby zakończyć]")
    print("=" * 54)

    iteration = 0

    while True:
        iteration += 1
        t = time.time()

        # --- Krok 1: dane z Orbity ---
        iss_data = fetch_iss_position()
        if iss_data is not None:
            lat, lon = iss_data
            growth = iss_growth_factor(lat, lon)
            iss_label = f"Lat {lat:+.2f}°, Lon {lon:+.2f}°  (wzrost ×{growth:.2f})"
        else:
            # Fallback – losowa „orbita" gdy brak sieci
            lat = random.uniform(-55.0, 55.0)
            lon = random.uniform(-180.0, 180.0)
            growth = iss_growth_factor(lat, lon)
            iss_label = f"[offline] Lat {lat:+.2f}°, Lon {lon:+.2f}° (×{growth:.2f})"

        # --- Krok 2: tętno sieci ---
        net_ms = measure_network_pulse()
        if net_ms is not None:
            net_label = f"{net_ms:.1f} ms"
            # Wyższe opóźnienie = silniejsze wibracje (do rozsądnego limitu)
            vibration_boost = min(net_ms / 200.0, 2.0)
        else:
            # Fallback – symulowane tętno
            net_ms = random.uniform(20.0, 300.0)
            net_label = f"[offline] ~{net_ms:.0f} ms"
            vibration_boost = min(net_ms / 200.0, 2.0)

        # --- Krok 3: kosmiczny szum tła ---
        noise = cosmic_background_noise(t)
        mutation_rate = _MUTATION_BASE_RATE + noise * (_MUTATION_MAX_RATE - _MUTATION_BASE_RATE)
        changes = engine.controlled_mutation(mutation_rate=mutation_rate)
        mutated = changes > 0
        mutation_label = (
            f"Tak (zmiany: {changes}, szum: {noise:.3f})"
            if mutated
            else f"Nie (szum: {noise:.3f})"
        )

        # --- Krok 4: kwantowy blask neonu ---
        phase_shift = (t * vibration_boost * growth) % 2
        quantum_glow = engine.quantum_vibration_sync(phase_shift=phase_shift)

        # --- Wyświetlenie statusu ---
        print(f"\n--- WIBRACJE KOSMICZNE V1B3hR  [cykl #{iteration}] ---")
        print(f"🛰️  ISS znajduje się nad:           {iss_label}")
        print(f"🌐 Tętno sieci (światłowód):        {net_label}")
        print(f"🧬 Zmiany DNA (Mutacja):            {mutation_label}")
        print(f"🌿 Aktualny blask neonu:            {quantum_glow:.2f} lux")

        time.sleep(_LOOP_INTERVAL_S)


# ---------------------------------------------------------------------------
# Punkt wejścia
# ---------------------------------------------------------------------------
def main() -> None:
    engine = BioArtGenerator(_DNA_SIGNATURE)
    try:
        run_simulation(engine)
    except KeyboardInterrupt:
        print("\n\n🔋 Bio-sygnał: Uśpienie. Koherencja kwantowa: Zachowana.")
        print("    Do usłyszenia, V1B3hR! 🧬✨")
        sys.exit(0)


if __name__ == "__main__":
    main()
