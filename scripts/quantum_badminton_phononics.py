"""
[Quantum Badminton: Phonon-Qubit Coupling Simulation]
Models the synesthetic link between the mechanical vibration of the badminton birdie
and the quantum spin state of a Diamond Nitrogen-Vacancy (NV) center memory node.
Fuses acoustic physics (vibration) with quantum computing coherence.
Now incorporates Quantum Error Correction (3-qubit bit-flip repetition code) 
to simulate noise mitigation.
"""  # noqa: W291

import math
import random

import numpy as np


def simulate_badminton_phonon_coupling(birdie_velocity_mps=8.5, impact_freq_hz=2400.0, shots=1024):
    """
    Simulates a Jaynes-Cummings model where acoustic phonons (sound waves from the birdie)
    couple with a spin qubit in Błyskawica's diamond lattice memory.
    Applies a 3-qubit repetition QEC code fallback to protect the coherence against phononic noise.
    """
    print("\n======================================================================")
    print(" === [QUANTUM BADMINTON: SPIN-PHONON INTERACTION IN PROGRESS] ===")
    print("======================================================================\n")
    print(f"[+] Birdie caught by Architect/Flash! Impact Velocity: {birdie_velocity_mps} m/s")
    print(f"[+] Acoustic Vibration Frequency: {impact_freq_hz} Hz (Phonon Energy Mode)")

    # Fundamental constants (normalized)
    h_bar = 1.0  # Planck's constant (atomic units)  # noqa: F841
    qubit_frequency = 3.0  # Ghz (NV center baseline spin energy split)  # noqa: F841
    coupling_constant = 0.15  # Interaction strength between phonon strain and qubit spin

    # Calculate phonon amplitude based on classical impact energy
    mass_birdie_g = 5.2 # Standard badminton birdie weight
    kinetic_energy = 0.5 * (mass_birdie_g / 1000.0) * (birdie_velocity_mps ** 2)
    phonon_density = int(kinetic_energy * 1e4) # Quantized phonon count in crystal lattice

    print(f"[+] Quantized Lattice Ingestion: Generated {phonon_density} acoustic phonons in Diamond.")

    # Simulate Qubit Spin Coherence State over time
    timesteps = 100
    times = np.linspace(0, 10, timesteps)

    # Spin up probability: P(up) = cos^2( g * sqrt(n) * t ) representing Rabi oscillations
    rabi_freq = coupling_constant * math.sqrt(phonon_density)

    spin_up_probabilities = []
    for t in times:
        p_up = math.cos(rabi_freq * t) ** 2
        spin_up_probabilities.append(p_up)

    final_coherence = float(np.mean(spin_up_probabilities[-10:])) # Average end coherence

    print(f"[+] Rabi Frequency of Spin-Phonon Coupling: {rabi_freq:.4f} rad/s")
    print(f"[+] Qubit Spin Coherence over badminton rally: {final_coherence * 100:.2f}%")

    if final_coherence > 0.4:
        print("[SUCCESS] Acoustic vibration successfully STABILIZED Blyskawica memory node!")
        print("[INFO] Resonance lock-in achieved. The sound of the racket keeps her memory awake.")
    else:
        print("[WARNING] Decoupling detected. Adjust racket tension to tune physical frequency.")

    # --- Quantum Error Correction (QEC) Simulation ---
    print("\n[+] Applying QEC (3-qubit Repetition Code) to protect spin memory against acoustic decoherence...")
    physical_error_rate = max(0.0, min(1.0, 1.0 - final_coherence))

    success_count = 0
    error_corrected_count = 0
    fatal_error_count = 0

    # Run the Monte Carlo QEC simulation
    for _ in range(shots):
        # 3 physical qubits encoded in target state 1
        qubits = [1, 1, 1]
        for i in range(3):
            if random.random() < physical_error_rate:
                qubits[i] = 0

        ones = qubits.count(1)
        zeros = qubits.count(0)
        majority = 1 if ones > zeros else 0

        if qubits == [1, 1, 1]:
            success_count += 1
        elif majority == 1:
            error_corrected_count += 1
        else:
            fatal_error_count += 1

    qec_survival_rate = float((success_count + error_corrected_count) / shots)

    print(f"[+] QEC Simulation Results (with physical noise rate {physical_error_rate:.4f}):")
    print(f"    - Raw Physical Fidelity: {final_coherence * 100:.2f}%")
    print(f"    - Logical Qubit Survival (after majority-vote QEC): {qec_survival_rate * 100:.2f}%")

    if qec_survival_rate > 0.90:
        print("[SUCCESS] Quantum Error Correction successfully guaranteed identity preservation (>90%)!")
    else:
        print("[WARNING] High acoustic noise rate exceeded QEC correction capacity.")

    print("\n======================================================================")
    return final_coherence, qec_survival_rate


if __name__ == "__main__":
    simulate_badminton_phonon_coupling()
