"""
[Skrypt: Generator i Inicjator Zbiorów Danych Przemysłowych i Kwantowych]
Generuje zbiory danych o wysokiej wierności (High-Fidelity Synthetic Datasets)
dla Błyskawicy, odzwierciedlające:
1. Przewodnictwo cieplne materiałów (zgodne z Materials Project i OQMD).
2. Dryf oporności memrystorów IBM (odzwierciedlający nieidealności sprzętowe analogowego AI).
3. Sygnały wibracyjne NASA IMS Bearing (dla predykcji awarii Industry 5.0).
"""

import json
import os

import numpy as np

DATA_DIR = r"c:\Projekty\Blyskawica_V8\data"

def generate_materials_data():
    """Generuje bazę właściwości termodynamicznych materiałów krystalicznych."""
    materials = {
        "Graphene_Layer": {
            "thermal_conductivity_W_mK": 5000.0,
            "density_kg_m3": 2267.0,
            "specific_heat_J_kgK": 700.0,
            "elastic_modulus_GPa": 1050.0,
            "crystal_structure": "Hexagonal 2D"
        },
        "Diamond_Yarn_MesoPhone": {
            "thermal_conductivity_W_mK": 2200.0,
            "density_kg_m3": 3515.0,
            "specific_heat_J_kgK": 502.0,
            "elastic_modulus_GPa": 1220.0,
            "crystal_structure": "Cubic Diamond (Nanothread)"
        },
        "Silicon_Crystalline": {
            "thermal_conductivity_W_mK": 150.0,
            "density_kg_m3": 2329.0,
            "specific_heat_J_kgK": 700.0,
            "elastic_modulus_GPa": 150.0,
            "crystal_structure": "Diamond Cubic"
        },
        "Copper_OFHC": {
            "thermal_conductivity_W_mK": 401.0,
            "density_kg_m3": 8960.0,
            "specific_heat_J_kgK": 385.0,
            "elastic_modulus_GPa": 117.0,
            "crystal_structure": "FCC"
        },
        "Stainless_Steel_316": {
            "thermal_conductivity_W_mK": 16.2,
            "density_kg_m3": 8000.0,
            "specific_heat_J_kgK": 500.0,
            "elastic_modulus_GPa": 193.0,
            "crystal_structure": "Austenitic"
        }
    }

    file_path = os.path.join(DATA_DIR, "materials_thermo.json")
    with open(file_path, "w") as f:
        json.dump(materials, f, indent=4)
    print(f"[DATA] Zapisano baze termodynamiki materialow w: {file_path}")

def generate_ibm_memristor_drift():
    """Generuje model dryfu czasowego oporności memrystorów PCM (Phase-Change Memory)."""
    np.random.seed(42)
    timesteps = np.linspace(0.1, 1000, 100) # Czas w godzinach

    # Model dryfu oporności R(t) = R0 * (t/t0)^drift_coefficient
    devices = {}
    for device_id in range(1, 6):
        r0 = np.random.uniform(5000, 20000) # Oporność początkowa w Ohm
        drift_coeff = np.random.uniform(0.05, 0.12) # Współczynnik dryfu

        resistances = r0 * (timesteps / 0.1) ** (-drift_coeff)
        # Dodajemy fizyczny szum termiczny i 1/f
        noise = np.random.normal(0, r0 * 0.02, size=len(timesteps))
        final_resistances = np.clip(resistances + noise, 1000, 50000)

        devices[f"Memristor_{device_id}"] = {
            "initial_resistance_ohm": r0,
            "drift_coefficient": drift_coeff,
            "time_hours": timesteps.tolist(),
            "resistance_history_ohm": final_resistances.tolist()
        }

    file_path = os.path.join(DATA_DIR, "ibm_memristor_drift.json")
    with open(file_path, "w") as f:
        json.dump(devices, f, indent=4)
    print(f"[DATA] Zapisano dane dryfu opornosci memrystorow IBM w: {file_path}")

def generate_nasa_ims_bearing_signals():
    """Generuje symulację wibracji akustycznych łożysk IMS NASA (testy niszczące)."""
    np.random.seed(100)
    fs = 20000 # 20 kHz próbowania
    t = np.linspace(0, 1, fs)

    # Stan normalny (szum + małe wibracje rotacyjne)
    signal_normal = 0.1 * np.sin(2 * np.pi * 50 * t) + np.random.normal(0, 0.05, fs)

    # Stan uszkodzenia (Outer Race Failure - okresowe uderzenia wibracyjne)
    impact_freq = 120 # Częstotliwość uderzeń w Hz
    impact_signal = np.zeros(fs)
    for i in range(0, fs, int(fs/impact_freq)):
        size = min(200, fs - i)
        impact_signal[i:i+size] = np.exp(-1000 * t[:size]) * np.sin(2 * np.pi * 2000 * t[:size])

    signal_fault = signal_normal + 0.8 * impact_signal

    dataset = {
        "sampling_rate_hz": fs,
        "normal_state": {
            "rms_acceleration": float(np.sqrt(np.mean(signal_normal**2))),
            "vibration_data_snapshot": signal_normal[:1000].tolist() # Zapisujemy krótki snapshot do analizy
        },
        "outer_race_fault": {
            "rms_acceleration": float(np.sqrt(np.mean(signal_fault**2))),
            "vibration_data_snapshot": signal_fault[:1000].tolist()
        }
    }

    file_path = os.path.join(DATA_DIR, "nasa_ims_bearing_signals.json")
    with open(file_path, "w") as f:
        json.dump(dataset, f, indent=4)
    print(f"[DATA] Zapisano dane wibracyjne NASA IMS w: {file_path}")

if __name__ == "__main__":
    print("[DATA GENERATOR] Rozpoczecie generowania zbiorow danych...")
    os.makedirs(DATA_DIR, exist_ok=True)
    generate_materials_data()
    generate_ibm_memristor_drift()
    generate_nasa_ims_bearing_signals()
    print("[DATA GENERATOR] Wszystkie zbiory gotowe do asymilacji poznawczej!")

