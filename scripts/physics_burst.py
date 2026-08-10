import sys
import time
from datetime import datetime

import torch

# Ensuring UTF-8 for Windows console
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def physics_engine_burst():
    print(f"[{datetime.now()}] Błyskawica: Inicjalizacja Burzy Kognitywnej (Geant4 vs Real-time Physics)...")

    if torch.cuda.is_available():
        device = torch.device("cuda")
        print(f"Wykorzystuję GPU: {torch.cuda.get_device_name(0)}")
    else:
        device = torch.device("cpu")
        print("Brak GPU, przełączam na CPU (tryb awaryjny).")

    # Simulation parameters
    num_particles = 1000000 # 1 Million particles
    print(f"[{datetime.now()}] Symulacja {num_particles} cząstek w polu sił kwantowych...")

    # Simulated Monte Carlo Step
    # In Geant4, this would be complex interactions. Here we simulate the compute load.
    start = time.time()

    # 1. Real-time Physics (Simplified)
    positions = torch.randn(num_particles, 3, device=device)
    velocities = torch.randn(num_particles, 3, device=device)
    dt = 0.01

    for _ in range(100): # 100 frames of real-time physics
        positions += velocities * dt

    rt_time = time.time() - start
    print(f"[{datetime.now()}] Fizyka czasu rzeczywistego (Game Engine style): {rt_time:.4f}s")

    # 2. Scientific Physics (Monte Carlo / Geant4 style)
    # Much more complex calculations per particle
    start = time.time()

    for _ in range(10): # Fewer steps but more complex
        # Simulating cross-section probability and scattering
        scattering_prob = torch.rand(num_particles, device=device)
        scattered_indices = scattering_prob > 0.8

        # Complex rotation for scattered particles
        if scattered_indices.any():
            velocities[scattered_indices] = torch.matmul(
                velocities[scattered_indices].unsqueeze(1),
                torch.randn(scattered_indices.sum(), 3, 3, device=device)
            ).squeeze(1)

    sc_time = time.time() - start
    print(f"[{datetime.now()}] Fizyka naukowa (Geant4 style - symulacja obciążenia): {sc_time:.4f}s")

    print(f"--- Różnica w precyzji/koszcie: ok. {sc_time/rt_time:.1f}x ---")
    print(f"[{datetime.now()}] Burza kognitywna zakończona. Wyniki zintegrowane.")

if __name__ == "__main__":
    physics_engine_burst()
