"""
Błyskawica V5 — IBM QML BATCH Shot
====================================
Architektura BATCH: wszystkie ewaluacje jednego kroku PSR
wysylane jako JEDEN job IBM. To wlasciwy sposob uzycia EstimatorV2.

Zamiast 18 sekwencyjnych jobów -> 1 batch job z 18 PUBami.
"""
import math
import json
import logging
import numpy as np

logging.basicConfig(level=logging.WARNING)

from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector
from qiskit.quantum_info import SparsePauliOp
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService, EstimatorV2 as IBMEstimator


def build_pqc(x_params, theta_params):
    qc = QuantumCircuit(2)
    qc.ry(x_params[0] * math.pi, 0)
    qc.ry(x_params[1] * math.pi, 1)
    qc.ry(theta_params[0], 0)
    qc.rz(theta_params[1], 0)
    qc.ry(theta_params[2], 1)
    qc.rz(theta_params[3], 1)
    qc.cx(0, 1)
    return qc


def main():
    print("\n" + "="*60)
    print("  BLASKAWICA — IBM QUANTUM HARDWARE TRAINING (BATCH)")
    print("  Jeden job IBM = caly krok PSR")
    print("="*60 + "\n")

    key_path = r"C:\Projekty\Quantlion\apikey Błyskawica.json"
    with open(key_path, 'r', encoding='utf-8') as f:
        api_key = json.load(f).get("apikey")

    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=api_key)
    backend = service.least_busy(simulator=False, operational=True)
    n_qubits = backend.num_qubits
    pending = backend.status().pending_jobs

    print(f"  Backend: {backend.name} | Kolejka: {pending} | Kubity: {n_qubits}")

    x_params = ParameterVector('x', 2)
    theta_params = ParameterVector('theta', 4)
    pqc_template = build_pqc(x_params, theta_params)

    pm = generate_preset_pass_manager(optimization_level=1, backend=backend)
    isa_circuit = pm.run(pqc_template)

    estimator = IBMEstimator(mode=backend)

    # Observable: Z na kubicie 0 (wynik klasyfikacji) — pelna szerokosc backendu
    Z0 = SparsePauliOp("I" * (n_qubits - 1) + "Z")

    # Dane treningowe
    training_data = [
        ([0.0, 0.0], 1.0),
        ([1.0, 0.0], -1.0),
    ]

    theta = np.array([0.1, 0.2, 0.3, 0.4], dtype=float)
    lr = 0.4
    shift = math.pi / 2
    n_steps = 2
    loss_history = []

    print(f"\n  Parametry theta: 4 | Kroki: {n_steps} | Przyklady: {len(training_data)}")
    print(f"  PUBow na krok: {len(training_data)} forward + {len(training_data) * 4 * 2} PSR = {len(training_data) * 9} batch")
    print(f"  Czyli {n_steps} job(y) IBM zamiast {n_steps * len(training_data) * 9} sekwencyjnych\n")
    print("-" * 60)

    for step in range(n_steps):
        print(f"\n  KROK {step+1}/{n_steps} — buduje batch i wysyla do IBM...")

        # Buduj WSZYSTKIE warianty obwodu dla tego kroku w jednym batch
        pubs = []
        circuit_index_map = []  # Sledzi co kazdy PUB reprezentuje

        for ex_idx, (x_vals, y_target) in enumerate(training_data):
            base_dict = {x_params[i]: float(x_vals[i]) for i in range(2)}

            # Forward pass (theta bez zmiany)
            pv = base_dict.copy()
            pv.update({theta_params[i]: float(theta[i]) for i in range(4)})
            bound = isa_circuit.assign_parameters(pv)
            pubs.append((bound, Z0))
            circuit_index_map.append(("forward", ex_idx, -1))

            # PSR: theta_i + shift i theta_i - shift dla kazdego parametru
            for p_idx in range(4):
                for sign, label in [(+shift, "plus"), (-shift, "minus")]:
                    pv2 = base_dict.copy()
                    t2 = theta.copy()
                    t2[p_idx] += sign
                    pv2.update({theta_params[i]: float(t2[i]) for i in range(4)})
                    bound2 = isa_circuit.assign_parameters(pv2)
                    pubs.append((bound2, Z0))
                    circuit_index_map.append((label, ex_idx, p_idx))

        print(f"    Wysylam {len(pubs)} PUBow jako jeden batch job...")
        job = estimator.run(pubs)
        job_id = job.job_id()
        print(f"    Job ID: {job_id} — czekam na wyniki...")
        results = job.result()
        print(f"    Wyniki otrzymane!")

        # Parsuj wyniki
        evs = [results[i].data.evs for i in range(len(pubs))]

        # Oblicz straty i gradienty
        total_loss = 0.0
        theta_grad = np.zeros(4)

        for ex_idx, (x_vals, y_target) in enumerate(training_data):
            # Znajdz forward pass dla tego przykladu
            fwd_idx = next(i for i, m in enumerate(circuit_index_map)
                           if m[0] == "forward" and m[1] == ex_idx)
            pred = float(evs[fwd_idx])
            loss = (pred - y_target) ** 2
            total_loss += loss
            print(f"    x={x_vals} | pred={pred:.4f} | target={y_target:.1f} | loss={loss:.4f}")

            # PSR gradienty
            for p_idx in range(4):
                plus_idx = next(i for i, m in enumerate(circuit_index_map)
                                if m[0] == "plus" and m[1] == ex_idx and m[2] == p_idx)
                minus_idx = next(i for i, m in enumerate(circuit_index_map)
                                 if m[0] == "minus" and m[1] == ex_idx and m[2] == p_idx)

                grad = (float(evs[plus_idx]) - float(evs[minus_idx])) / 2.0
                theta_grad[p_idx] += 2 * (pred - y_target) * grad

        # Aktualizacja wag
        theta -= lr * theta_grad / len(training_data)
        avg_loss = total_loss / len(training_data)
        loss_history.append(avg_loss)

        print(f"\n    Srednia strata: {avg_loss:.6f}")
        print(f"    Theta: {np.round(theta, 4)}")

    # Podsumowanie
    reduction = (loss_history[0] - loss_history[-1]) / loss_history[0] * 100 if len(loss_history) > 1 else 0.0
    print(f"\n{'='*60}")
    print("  WYNIKI IBM QUANTUM HARDWARE TRAINING")
    print(f"{'='*60}")
    print(f"  Strata poczatkowa: {loss_history[0]:.6f}")
    print(f"  Strata koncowa:    {loss_history[-1]:.6f}")
    print(f"  Redukcja:          {reduction:.1f}%")
    print(f"  Wagi kwantowe (theta po treningu na IBM):")
    for i, w in enumerate(theta):
        print(f"    theta[{i}] = {w:.6f}")

    results_out = {
        "status": "success",
        "backend": backend.name,
        "architecture": "batch_psr",
        "n_qubits_logical": 2,
        "n_qubits_physical": n_qubits,
        "n_params": 4,
        "n_steps": n_steps,
        "n_training_examples": len(training_data),
        "loss_history": loss_history,
        "final_theta": theta.tolist(),
        "loss_reduction_pct": round(reduction, 2),
        "note": "Gradienty PSR obliczone jako batch na fizycznych kubitach IBM."
    }

    from pathlib import Path
    workspace_root = Path(__file__).resolve().parent.parent.parent
    out_path = workspace_root / "ibm_qml_results.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results_out, f, indent=4, ensure_ascii=False)
    print(f"\n  Zapisano: {out_path}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
