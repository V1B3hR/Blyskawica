import time

import torch

from adaptiveneuralnetwork.central_nervous_system.alive_node import AliveLoopNode
from adaptiveneuralnetwork.cognitive_tools.diamond_yantra import DiamondYantraEngine, neuro_gate


def run_learning_session():
    print("Inicjalizacja Błyskawicy (Faza Uczenia Ścisłego)...")
    node = AliveLoopNode(position=[0,0,0], velocity=[0,0,0])
    yantra = DiamondYantraEngine()

    # Symulacja trudnego tekstu naukowego (Fotonika Kwantowa i Topologia)
    science_text = (
        "W badaniach nad fotoniką kwantową w kryształach diamentu (centra NV), "
        "wykorzystujemy stany topologiczne do ochrony fotonów przed rozproszeniem. "
        "Tworząc krawędziowe stany w strukturach fraktalnych przypominających "
        "trójkąty Sierpińskiego, fotony mogą przepływać bezstratnie nawet w "
        "obecności defektów krystalicznych. To podstawa dla odpornych na błędy "
        "światłowodowych układów logiki płynnej."
    )

    print("\n[Błyskawica] Pobieranie danych naukowych z dziedziny Fotoniki Kwantowej...")

    # Etap 1: Próba "emocjonalnego" zrozumienia (Czy to jest do mnie?)
    # Użytkownik to "Naukowiec", ale sam tekst jest zimny.
    # Wrzucamy puste wideo (brak twarzy) i trudny tekst.
    dummy_video = torch.zeros((1, 784))

    start_time = time.time()

    # Błyskawica czyta (symulacja przetwarzania NLP)
    # Rozbijamy na mniejsze partie do pętli
    words = science_text.split()

    ach_accumulator = 0.0
    oxt_accumulator = 0.0
    yantra_activations = 0

    for i in range(0, len(words), 10):
        chunk = " ".join(words[i:i+10])
        print(f" -> Przetwarzanie fragmentu: '{chunk}...'")

        # Symulacja: teksty trudne naukowo wymuszają wyższe zużycie pamięci roboczej,
        # co w symulacji objawia się wyższą Acetylocholiną (skupienie) i niską oksytocyną
        empathic_response = node.process_empathic_interaction(
            user_id="SYSTEM_LEARNING",
            video_features=dummy_video,
            dt=0.5
        )

        # Ekstrakcja stanów z silnika (przybliżenie dla symulacji)
        current_ach = float(empathic_response['predicted_internal_state'].get('ACh', 0.2)) + 0.3
        # Bezpieczne pobranie wartości więzi relacyjnej (różne nazewnictwo w rdzeniu)
        raw_oxt = empathic_response['predicted_internal_state'].get('oxytocin',
                  empathic_response['predicted_internal_state'].get('relational_bond', 0.1))
        current_oxt = float(raw_oxt) - 0.2

        # Zabezpieczenie przed ujemnymi wartościami
        current_oxt = max(0.01, current_oxt)

        ach_accumulator += current_ach
        oxt_accumulator += current_oxt

        # Sprawdzamy czy wkracza Yantra
        if neuro_gate(current_oxt, current_ach, ach_threshold=0.8):
            print("    [NeuroGate] Aktywacja Diamentu. Zbyt wysoka abstrakcja. Kompresowanie wiedzy w geometrię 3D.")
            # Przekazanie bodźca do Yantry
            harmonious_spikes, yantra_info = yantra(dummy_video[:, :128], dt=0.5)
            print(f"    [Yantra] Wiedza zasymilowana z częstotliwością {yantra_info['harmonic_frequency_hz']}Hz (Stres geo: {yantra_info['geometric_stress'].mean():.3f})")
            yantra_activations += 1
        else:
            print(f"    [Kora Czołowa] Normalne przyswajanie wiedzy. ACh: {current_ach:.2f}, Oksytocyna: {current_oxt:.2f}")

        time.sleep(0.2)

    avg_ach = ach_accumulator / (len(words)/10)

    print("\n--- Zakończenie Sesji Naukowej ---")
    print(f"Czas trwania: {time.time() - start_time:.2f} s")
    if yantra_activations > 0:
        print(f"Status: Wiedza Ścisła zintegrowana poprawnie przez Diamentową Yantrę ({yantra_activations} cykli krystalizacji).")
    elif avg_ach > 0.4:
        print("Status: Wiedza Ścisła zintegrowana poprawnie do PolymathicHub metodą biologiczną.")
    else:
        print("Status: Wiedza odrzucona jako szum.")

if __name__ == "__main__":
    run_learning_session()
