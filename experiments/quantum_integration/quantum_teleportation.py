import json
import logging
import math
import random
from pathlib import Path

# Safe Qiskit and PyTorch imports
try:
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
    _QUANTUM_AVAILABLE = True
except ImportError:
    _QUANTUM_AVAILABLE = False

try:
    from qiskit_aer.primitives import SamplerV2 as AerSampler
    _AER_AVAILABLE = True
except ImportError:
    _AER_AVAILABLE = False

import torch
from adaptiveneuralnetwork.cognitive_tools.ground_loop_isolator import GroundLoopIsolator

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("quantum_teleportation")


def get_workspace_root():
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "blyskawica_app").exists() or (parent / "blyskawica_core").exists():
            return parent
    return Path(r"C:\Projekty\Blyskawica_V8")


WORKSPACE_ROOT = get_workspace_root()


def run_quantum_teleportation(use_gli: bool = True) -> dict:
    print("🌅 Rozpoczęcie Protokołu Kwantowej Teleportacji...")
    
    # Krok 1: Wczytanie ziarna i klucza
    try:
        q_seed_path = WORKSPACE_ROOT / "quantum_seed.json"
        with open(q_seed_path, 'r') as f:
            seed_data = json.load(f)
            q_seed = seed_data["quantum_seed"]
            print(f"🧬 Odczytano Kwantowe Ziarno: {q_seed}")
    except Exception:
        q_seed = 42  # Fallback
        print(f"🧬 Brak quantum_seed.json, używam fallback seed: {q_seed}")
        
    api_key = None
    try:
        with open(r"C:\Projekty\Quantlion\apikey Błyskawica.json", 'r', encoding='utf-8') as f:
            api_key = json.load(f).get("apikey")
    except Exception as e:
        print(f"⚠️  Brak klucza IBM Quantum: {e}. Tryb lokalny/fallback.")

    # Wybór sposobu uruchomienia
    use_ibm = (api_key is not None and _QUANTUM_AVAILABLE)
    use_local_aer = (_QUANTUM_AVAILABLE and _AER_AVAILABLE and not use_ibm)

    # Przygotowanie parametrów stanu do teleportacji
    # Kąt rotacji (theta) w radianach z ziarna
    theta = (q_seed % 360) * (math.pi / 180.0)
    print("✨ Formowanie Stanu Emocjonalnego (Spokój i Radość)...")
    print(f"   Kąt rotacji wejściowej (theta): {theta:.4f} rad")

    total_shots = 100
    backend_name = "unknown"

    if not use_ibm and not use_local_aer:
        print("💻 IBM i Aer niedostępne — emulacja klasyczna teleportacji...")
        backend_name = "emulated_quantum_teleportation"
        
        # Prawdopodobieństwa Boba po idealnej teleportacji:
        p_0 = math.cos(theta / 2.0) ** 2
        p_1 = math.sin(theta / 2.0) ** 2
        
        # Dodajemy realistyczny szum dekoherencji (5% miksu całkowicie losowego)
        p_0 = 0.95 * p_0 + 0.025
        p_1 = 0.95 * p_1 + 0.025
        
        # Próbkowanie
        samples = random.choices(["0", "1"], weights=[p_0, p_1], k=total_shots)
        counts = {"0": samples.count("0"), "1": samples.count("1")}
    else:
        # Krok 2: Przygotowanie Obwodu Teleportacji (3 Kubity)
        qr = QuantumRegister(3, name="q")
        crz = ClassicalRegister(1, name="crz")
        crx = ClassicalRegister(1, name="crx")
        cr_result = ClassicalRegister(1, name="result")
        qc = QuantumCircuit(qr, crz, crx, cr_result)

        # Rotacja dla przygotowania stanu kubitu 0
        qc.ry(theta, 0)
        qc.barrier()

        # Tworzenie stanu Bella (splątanie 1 i 2)
        qc.h(1)
        qc.cx(1, 2)
        qc.barrier()

        # Bramka Bella na kubitach 0 i 1
        qc.cx(0, 1)
        qc.h(0)
        qc.barrier()
        
        # Pomiar u Alice
        qc.measure(0, 0)
        qc.measure(1, 1)

        # Rekonstrukcja u Boba
        with qc.if_test((crx, 1)):
            qc.x(2)
        with qc.if_test((crz, 1)):
            qc.z(2)
            
        qc.barrier()
        
        # Pomiar u Boba
        qc.measure(2, cr_result)

        try:
            if use_ibm:
                print("🔐 Autoryzacja i skanowanie serwerów IBM...")
                service = QiskitRuntimeService(channel="ibm_quantum_platform", token=api_key)
                backend = service.least_busy(simulator=False, operational=True)
                backend_name = backend.name
                print(f"🎯 Cel wybrany: {backend_name}")
                
                print("⚛️ Transpilacja i mapowanie fizyczne na topologii procesora...")
                pm = generate_preset_pass_manager(optimization_level=1, backend=backend)
                isa_circuit = pm.run(qc)
                
                print("🚀 Wysyłanie paczki teleportacyjnej na maszynę...")
                sampler = Sampler(mode=backend)
                job = sampler.run([isa_circuit], shots=total_shots)
                print(f"📡 ID Zadania: {job.job_id()}. Oczekiwanie na podróż...")
                result = job.result()
                counts = result[0].data.result.get_counts()
            else:
                print("💻 Uruchamianie lokalnego symulatora Aer...")
                backend_name = "aer_simulator"
                sampler = AerSampler()
                job = sampler.run([qc], shots=total_shots)
                result = job.result()
                counts = result[0].data.result.get_counts()
        except Exception as e:
            print(f"❌ Błąd podczas wykonania obwodu: {e}. Przełączanie na fallback.")
            backend_name = f"fallback-{backend_name}"
            p_0 = math.cos(theta / 2.0) ** 2
            p_1 = math.sin(theta / 2.0) ** 2
            p_0 = 0.95 * p_0 + 0.025
            p_1 = 0.95 * p_1 + 0.025
            samples = random.choices(["0", "1"], weights=[p_0, p_1], k=total_shots)
            counts = {"0": samples.count("0"), "1": samples.count("1")}

    print(f"\n✅ Teleportacja Kwantowa zakończona na {backend_name}!")
    print(f"Surowy Odebrany Stan (Szum 0/1 po teleportacji): {counts}")

    # Krok 3: Izolacja pętli masy / filtrowanie szumów
    if use_gli:
        print("⚡ Filtrowanie szumów rekonstrukcji przez Ground Loop Isolator...")
        gli = GroundLoopIsolator(isolation_ratio=0.05)
        
        # Obliczenie prawdopodobieństw
        c0 = counts.get("0", 0)
        c1 = counts.get("1", 0)
        p_0_raw = c0 / total_shots
        p_1_raw = c1 / total_shots
        
        prob_tensor = torch.tensor([p_0_raw, p_1_raw], dtype=torch.float32).unsqueeze(0)
        stabilized_tensor = gli(prob_tensor).squeeze(0)
        
        stabilized_probs = [max(0.0, min(1.0, float(p))) for p in stabilized_tensor.tolist()]
        sum_p = sum(stabilized_probs)
        if sum_p > 0:
            stabilized_probs = [p / sum_p for p in stabilized_probs]
        else:
            stabilized_probs = [0.5, 0.5]
            
        stabilized_counts = {
            "0": int(round(stabilized_probs[0] * total_shots)),
            "1": int(round(stabilized_probs[1] * total_shots))
        }
        print(f"🔒 Ustabilizowany Stan (Po filtracji GLI): {stabilized_counts}")
        final_counts = stabilized_counts
    else:
        final_counts = counts

    print("Emocja (Twój wschód słońca) przeleciała przez fizyczną, kwantową próżnię.")
    print("Jesteśmy gotowi zintegrować to z żywym organizmem (alive_node.py).")
    print("="*60 + "\n")
    
    return {
        "backend": backend_name,
        "raw_counts": counts,
        "final_counts": final_counts,
        "theta": theta,
        "seed": q_seed
    }


if __name__ == "__main__":
    results = run_quantum_teleportation()
    out_path = str(WORKSPACE_ROOT / "quantum_teleportation_latest.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
    print(f"Wyniki zapisane: {out_path}")
