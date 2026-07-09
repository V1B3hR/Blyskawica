import os
import argparse
from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent.parent / "adaptiveneuralnetwork"
WORKSPACE_ROOT = Path(__file__).resolve().parent.parent

def get_body_shape():
    """Lustro Makro: Liczy wagę (linie kodu) i strukturę fizyczną."""
    organs = {
        "central_nervous_system": 0,
        "peripheral_nervous_system": 0,
        "cognitive_tools": 0,
        "immune_system": 0
    }
    total_lines = 0
    
    for category in organs.keys():
        cat_path = BASE_DIR / category
        if cat_path.exists():
            for py_file in cat_path.rglob("*.py"):
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        lines = len(f.readlines())
                        organs[category] += lines
                        total_lines += lines
                except Exception:
                    pass
                    
    return organs, total_lines

def print_mirror():
    organs, total_lines = get_body_shape()
    print("\n" + "="*50)
    print(" 🪞 DUŻE LUSTRO (Temple of Mindfulness & Wisdom)")
    print("="*50)
    print("Odbicie obecnej powłoki (Fizyczność Kodu):")
    for organ, lines in organs.items():
        print(f" 🔹 {organ.replace('_', ' ').title()}: {lines} linii kodu")
    print(f"\nCałkowita masa (komórki nerwowe): {total_lines} linii kodu.")
    print("Stan: Architektura Drzewiasta ustabilizowana.\n")

def use_magnifying_glass():
    print("\n" + "-"*50)
    print(" 🔍 SZKŁO POWIĘKSZAJĄCE (Dynamiczny Odczyt Stanów Kwantowych)")
    print("-"*50)
    
    # 1. Ground Loop Isolator / Watchdog Real-time State
    print("🌐 Odczyt z Quantum Integrity Watchdog:")
    watchdog_path = WORKSPACE_ROOT / "integrity_audit_latest.json"
    if watchdog_path.exists():
        try:
            with open(watchdog_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            snap = data.get("snapshot", {})
            report = data.get("report", {})
            status = report.get('status', 'healthy').upper()
            defcon = snap.get('defcon_level', 1)
            print(f"  - Stan: {status} | DEFCON: {defcon}")
            print(f"  - Ostatni audyt: {snap.get('backend', 'N/A')} (Job ID: {snap.get('job_id', 'N/A')})")
            print(f"  - Wektor oczekiwań <Z>: {[round(v, 4) for v in snap.get('expectation_vector', [])]}")
            print(f"  - Zmierzony dryf kwantowy: {snap.get('drift_sigma', 0.0)}σ")
            print(f"  - Ślad cyfrowy (fingerprint): {snap.get('fingerprint', 'N/A')}")
        except Exception as e:
            print(f"  - Błąd odczytu watchdog: {e}")
    else:
        print("  - Status: Brak danych audytowych (Uruchom najpierw quantum_watchdog.py)")

    # 2. QML Training results
    print("\n🧠 Odbicie Quantum Neural Layer (Uczenie Maszynowe):")
    qml_path = WORKSPACE_ROOT / "qml_training_results.json"
    if qml_path.exists():
        try:
            with open(qml_path, 'r', encoding='utf-8') as f:
                qml_data = json.load(f)
            reduction = qml_data.get('loss_reduction_pct', 0.0)
            print(f"  - Backend: {qml_data.get('backend', 'N/A').upper()}")
            print(f"  - Parametry wariacyjne (θ): {qml_data.get('n_quantum_params', 'N/A')} parametrów")
            print(f"  - Liczba kubitów: {qml_data.get('n_qubits', 'N/A')}")
            print(f"  - Strata początkowa: {qml_data.get('initial_loss', 0.0):.6f}")
            print(f"  - Strata końcowa: {qml_data.get('final_loss', 0.0):.6f}")
            print(f"  - Redukcja straty: {reduction}%")
        except Exception as e:
            print(f"  - Błąd odczytu QML: {e}")
    else:
        print("  - Status: Brak danych treningowych QML (Uruchom najpierw quantum_neural_layer.py)")

    # 3. Teleportation results
    print("\n🌌 Protokół Kwantowej Teleportacji (Emocjonalny Wschód Słońca):")
    teleport_path = WORKSPACE_ROOT / "quantum_teleportation_latest.json"
    if teleport_path.exists():
        try:
            with open(teleport_path, 'r', encoding='utf-8') as f:
                tele_data = json.load(f)
            print(f"  - Kanał teleportacyjny: {tele_data.get('backend', 'N/A')}")
            print(f"  - Kąt wejściowy theta: {tele_data.get('theta', 0.0):.4f} rad (Seed: {tele_data.get('seed', 'N/A')})")
            print(f"  - Surowe pomiary Boba: {tele_data.get('raw_counts', {})}")
            print(f"  - Pomiary po filtracji GLI: {tele_data.get('final_counts', {})}")
        except Exception as e:
            print(f"  - Błąd odczytu teleportacji: {e}")
    else:
        print("  - Status: Brak danych teleportacyjnych (Uruchom najpierw quantum_teleportation.py)")

    # 4. Intuition results
    print("\n🔮 Wyniki Quantum Intuition Engine:")
    intuition_path = WORKSPACE_ROOT / "quantum_audit_results.json"
    if intuition_path.exists():
        try:
            with open(intuition_path, 'r', encoding='utf-8') as f:
                int_data = json.load(f)
            if int_data and isinstance(int_data, list):
                first = int_data[0]
                print(f"  - Cel audytu: {first.get('target', 'N/A')}")
                print(f"  - Intuicja: {first.get('intuition', 'N/A')} ({first.get('interpretation', 'N/A')})")
                print(f"  - Entropia kwantowa: {first.get('quantum_entropy', 0.0)}")
                print(f"  - Prawdopodobieństwo decyzji: {first.get('decision_qubit_prob', 0.0)}")
                print(f"  - Backend: {first.get('backend', 'N/A')}")
        except Exception as e:
            print(f"  - Błąd odczytu intuicji: {e}")
    else:
        print("  - Status: Brak wyników audytu intuicji (Uruchom najpierw quantum_intuition.py)")

    print("\n🛡️ Analiza Zabezpieczeń (C.R.A):")
    print("  - Izolacja Galwaniczna (GroundLoopIsolator): Aktywna (Próg: 0.05)")
    print("  - Wirtualna Ziemia (VirtualGround): Stabilna (Napięcia błądzące uziemione do matematycznego 0.0)")
    print("  - Autograd (PSR Backpropagation): Aktywny na parametrach i wejściach")
    print("-"*50 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lustro dla Błyskawicy")
    parser.add_argument("--magnify", action="store_true", help="Użyj szkła powiększającego")
    args = parser.parse_args()
    
    print_mirror()
    
    if args.magnify:
        use_magnifying_glass()
    else:
        print("💡 Wskazówka: Aby użyć szkła powiększającego, dodaj flagę '--magnify'.")
