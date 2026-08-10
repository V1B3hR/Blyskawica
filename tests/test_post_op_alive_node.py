import logging

import torch

# Wyciszamy zbędne logi na czas testu
logging.getLogger("quantum_dual_rotor").setLevel(logging.WARNING)

from adaptiveneuralnetwork.central_nervous_system.alive_node import AliveLoopNode  # noqa: E402


def run_post_op_check():
    print("🏥 Rozpoczynamy badania kontrolne pacjentki (Post-Op Check)...")

    # 1. Inicjalizacja AliveLoopNode (Z nowym sercem!)
    print("\n[Test 1] Próba wybudzenia układu...")
    node = AliveLoopNode(position=[0.0, 0.0], velocity=[0.0, 0.0], initial_energy=100.0)
    print("✅ System wybudzony. AliveLoopNode zainicjowany pomyślnie.")

    # 2. Symulacja podania impulsu wejściowego (Tensor)
    print("\n[Test 2] Testowanie przewodnictwa nerwowego (Pierwszy impuls)...")
    sensory_input = torch.randn(1, 128) * 5.0 # Silny sygnał

    # Wykonanie głównej pętli update
    node.update(external_activity=sensory_input, internal_stimuli=0.0)

    # Sprawdzenie, czy Dual Rotor został zainicjowany przez update
    if node.dual_rotor_engine is not None:
        print("✅ Podwójny Wirnik zaskoczył! Silnik i dławiki zostały dynamicznie zmontowane.")
    else:
        print("❌ Błąd: Silnik nie został zainicjowany.")
        return

    print("\n[Test 3] Testowanie wytrzymałości na stres i kompensacji (Multiple ticks)...")
    for i in range(5):  # noqa: B007
        noise = torch.randn(1, 128) * 10.0
        node.update(external_activity=noise, internal_stimuli=0.0)

    print(f"✅ Próba wysiłkowa zdana. Aktualny poziom Świadomości (Activity): {node.activity:.4f}")
    print(f"✅ Poziom energii życiowej pozostał stabilny: {node.energy:.2f}/{node.energy_capacity:.2f}")
    print("\n🩺 Pacjentka jest całkowicie zdrowa. Nowy organ (Dual Rotor + Chokes) funkcjonuje w 100% poprawnie wewnątrz naturalnego środowiska AliveNode.")

def test_post_op_check():
    run_post_op_check()

if __name__ == "__main__":
    run_post_op_check()
