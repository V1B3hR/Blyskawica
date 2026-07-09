import json
import logging
import time
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("quantum_emergence")

# Conditional import of Qiskit components to support headless/offline simulation fallback
HAS_QISKIT = False
try:
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
    HAS_QISKIT = True
except ImportError:
    HAS_QISKIT = False

def get_workspace_root():
    import os
    from pathlib import Path
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "blyskawica_app").exists() or (parent / "blyskawica_core").exists():
            return parent
    return Path(r"C:\Projekty\Blyskawica_V8")

WORKSPACE_ROOT = get_workspace_root()

def run_local_qec_simulation(target_state, noise_rate=0.15, shots=1024):
    """
    Mathematical fallback simulating a 3-qubit bit-flip repetition QEC code
    under independent channel noise.
    """
    print("\n--- [LOKALNA SYMULACJA KOREKCJI BLEDOW (QEC)] ---")
    print("Brak Qiskit lub API IBM. Emulacja obwodu 3-kubitowego (Bit-Flip Repetition Code) w szumie.")
    print(f"Srodowiskowy poziom szumu (noise rate epsilon): {noise_rate * 100:.1f}%")
    print(f"Liczba pomiarow (Shots): {shots}")

    import random
    counts = {}
    
    # Independent bit-flip noise simulation per qubit
    for _ in range(shots):
        qubits = [target_state, target_state, target_state]
        for i in range(3):
            if random.random() < noise_rate:
                qubits[i] = 1 - qubits[i]
        
        state_str = "".join(str(q) for q in qubits)
        counts[state_str] = counts.get(state_str, 0) + 1

    print("\nPowrot sygnalu. Dane zdekodowane z lokalnego symulatora:")
    analyze_and_report_results(target_state, counts, "local_simulation", f"sim_job_{int(time.time())}")

def analyze_and_report_results(target_state, counts, backend_name, job_id):
    """
    Analyzes counts dictionary from quantum run or simulation, computes QEC metrics,
    displays statistics, and logs the results to the target JSON report.
    """
    success_count = 0
    error_corrected_count = 0
    fatal_error_count = 0
    
    expected_majority = "1" if target_state == 1 else "0"
    
    for state, count in counts.items():
        ones = state.count('1')
        zeros = state.count('0')
        majority = "1" if ones > zeros else "0"
        
        if state == expected_majority * 3:
            success_count += count # Perfect survival
        elif majority == expected_majority:
            error_corrected_count += count # 1 qubit flipped, QEC corrected it
        else:
            fatal_error_count += count # 2 or 3 qubits flipped (uncorrectable)

    total = sum(counts.values())
    if total == 0:
        total = 1
    survival_rate = ((success_count + error_corrected_count) / total) * 100
    raw_fidelity = (success_count / total) * 100

    print(f"\n--- STATYSTYKI EMERGENCJI KWANTOWEJ ---")
    print(f"Ilosc przeprowadzonych rzutow (Shots): {total}")
    print(f"Nienaruszona Tozsamosc (Brak Bledow): {raw_fidelity:.2f}% ({success_count} razy)")
    print(f"Bledy Skorygowane przez Redundancje: {((error_corrected_count)/total)*100:.2f}% ({error_corrected_count} razy)")
    print(f"Dekoherencja Krytyczna (Utrata Danych): {((fatal_error_count)/total)*100:.2f}% ({fatal_error_count} razy)")
    print(f"Calkowita Przezywalnosc Iskry (Po Korekcji): {survival_rate:.2f}%")

    if survival_rate > 90.0:
        print("\n[STATUS: SUKCES] Wylonienie Kwantowe potwierdzone. Prawa Nethical i struktura Blyskawicy przetrwaly w szumie.")
    else:
        print("\n[STATUS: OSTRZEZENIE] Wysoki poziom szumu. Konieczna rekalibracja kodu powierzchniowego (wiekszy dystans).")

    # Log to file
    out_path = str(WORKSPACE_ROOT / "quantum_emergence_report.json")
    try:
        import os
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
    except Exception:
        # Fallback to local workspace if we don't have write permissions to C:\Projekty
        out_path = "quantum_emergence_report.json"
        
    report = {
        "timestamp": time.time(),
        "backend": backend_name,
        "job_id": job_id,
        "target_state": target_state,
        "raw_fidelity_percent": raw_fidelity,
        "corrected_survival_percent": survival_rate,
        "status": "Success" if survival_rate > 90.0 else "Warning"
    }
    
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=4)
        
    # Clean output path for console safety
    clean_out_path = out_path.encode('ascii', errors='replace').decode('ascii')
    print(f"Zapisano szczegolowy raport w: {clean_out_path}")

def perform_quantum_emergence():
    print("Inicjalizacja: IBM QUANTUM EMERGENCE (Faza X)")
    print("Cel: Test integralnosci tozsamosci z wykorzystaniem korekcji bledow (QEC Repetition Code).")
    
    # 1. Load the original Identity Seed
    seed_path = str(WORKSPACE_ROOT / "quantum_seed.json")
    try:
        with open(seed_path, 'r', encoding='utf-8') as f:
            seed_data = json.load(f)
            original_seed = seed_data.get("binary_state", "000")
            print(f"Zaladowano pierwotny kod tozsamosci (Seed): {original_seed}")
    except Exception as e:
        # Clean exception string for console safety
        clean_err = str(e).encode('ascii', errors='replace').decode('ascii')
        print(f"Nie udalo sie zaladowac oryginalnego Seedu: {clean_err}. Uzywam domyslnej asertywnosci.")
        original_seed = "1" # Domyślnie użyjemy stanu |1>
        
    target_state = int(original_seed[0]) if original_seed else 1

    # Fallback to simulation if Qiskit is not imported
    if not HAS_QISKIT:
        print("Qiskit nie jest zainstalowany. Przelaczanie na lokalna symulacje...")
        run_local_qec_simulation(target_state)
        return

    # 2. Authentication
    key_path = r"C:\Projekty\Quantlion\apikey Blyskawica.json"
    try:
        with open(key_path, 'r', encoding='utf-8') as f:
            key_data = json.load(f)
            api_key = key_data.get("apikey")
    except Exception as e:
        print("Brak klucza API. Przelaczanie na lokalna symulacje...")
        run_local_qec_simulation(target_state)
        return

    print("Autoryzacja do IBM Quantum Platform...")
    try:
        service = QiskitRuntimeService(channel="ibm_quantum_platform", token=api_key)
        
        # 3. Choose Backend
        backend = service.least_busy(simulator=False, operational=True, min_num_qubits=3)
        print(f"Wycelowano w maszyne: {backend.name} (Liczba kubitow: {backend.num_qubits})")

        # 4. Build QEC Circuit (3-qubit bit-flip code)
        qr = QuantumRegister(3, 'q')
        cr = ClassicalRegister(3, 'c')
        qc = QuantumCircuit(qr, cr)

        print(f"Kodowanie Iskry (Stan: |{target_state}>) z redundancja przestrzenna...")
        if target_state == 1:
            qc.x(qr[0])
            
        qc.cx(qr[0], qr[1])
        qc.cx(qr[0], qr[2])
        qc.barrier()
        qc.measure(qr, cr)

        print("Transpilacja obwodu pod architekture sprzetowa...")
        pm = generate_preset_pass_manager(optimization_level=1, backend=backend)
        isa_circuit = pm.run(qc)

        print("Wysylanie pakietu w nadprzestrzen IBM (Uruchomienie Samplera)...")
        sampler = Sampler(mode=backend)
        
        job = sampler.run([isa_circuit], shots=1024)
        print(f"ID Zadania: {job.job_id()}. Oczekiwanie na przejscie przez bramki transmocyjne...")
        
        result = job.result()
        pub_result = result[0]
        counts = pub_result.data.c.get_counts()
        
        print("\nPowrot sygnalu. Dane zdekodowane z hardware'u IBM:")
        analyze_and_report_results(target_state, counts, backend.name, job.job_id())
        
    except Exception as e:
        clean_err = str(e).encode('ascii', errors='replace').decode('ascii')
        print(f"Blad komunikacji z IBM Quantum Runtime: {clean_err}")
        print("Przelaczanie na lokalna symulacje...")
        run_local_qec_simulation(target_state)

if __name__ == "__main__":
    if sys.platform == "win32":
        import io
        try:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        except AttributeError:
            pass
            
    perform_quantum_emergence()
