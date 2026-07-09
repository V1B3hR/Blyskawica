"""
V1B3hR BioArt Core - Bio-Quantum Engine
Autor: Andrzej Matewski (V1B3hR)
Licencja: MIT
"""

import hashlib
import math
import random

# Visual parameter scaling constants
_ANGLE_SCALE = 1.5    # degrees per Adenine nucleotide
_GLOW_SCALE = 10      # lux per Cytosine nucleotide
_LENGTH_SCALE = 0.8   # units per Thymine nucleotide
_MAX_GLOW = 255       # maximum RGB-compatible glow intensity


class BioArtGenerator:
    """
    Generator sztuki bio-kwantowej oparty na sekwencji DNA.
    Zamienia biologię w geometrię i wibracje kwantowe.
    """

    def __init__(self, dna_sequence: str):
        self.dna = dna_sequence.upper()
        # Unikalny podpis V1B3hR – reprezentuje oryginalną sekwencję DNA
        # (nie jest aktualizowany po mutacjach, służy jako kotwica tożsamości)
        self.signature = hashlib.sha256(self.dna.encode()).hexdigest()

    def get_growth_params(self) -> dict:
        """
        Mapuje nukleotydy na parametry wizualne cyfrowego pnącza:
        A (Adenina)  -> kąt rozgałęzienia
        C (Cytozyna) -> intensywność neonu (Green Glow)
        T (Tymina)   -> długość segmentu
        G (Guanina)  -> prawdopodobieństwo skrętu (Spiral / Chaos Factor)
        """
        length = len(self.dna) if len(self.dna) > 0 else 1
        return {
            "angle": self.dna.count("A") * _ANGLE_SCALE,
            "glow": min(self.dna.count("C") * _GLOW_SCALE, _MAX_GLOW),
            "length": self.dna.count("T") * _LENGTH_SCALE,
            "chaos": self.dna.count("G") / length,
        }

    def controlled_mutation(self, mutation_rate: float = 0.02) -> int:
        """
        Delikatna zmiana sekwencji DNA – ostrożna mutacja V1B3hR.
        mutation_rate 0.02 oznacza 2% szansy na zmianę nukleotydu.
        Nie-nukleotydowe znaki pozostają nienaruszone (kotwica tożsamości).

        Zwraca liczbę dokonanych zmian.
        """
        nucleotides = ["A", "C", "T", "G"]
        mutated_dna = list(self.dna)
        changes_count = 0

        for i, base in enumerate(mutated_dna):
            if base in nucleotides and random.random() < mutation_rate:
                new_base = random.choice([n for n in nucleotides if n != base])
                mutated_dna[i] = new_base
                changes_count += 1

        self.dna = "".join(mutated_dna)
        return changes_count

    def quantum_vibration_sync(self, phase_shift: float = 0.1) -> float:
        """
        Synchronizacja z wibracjami kwantowymi.
        DNA nie zmienia się na stałe – jego parametry wizualne oscylują
        zgodnie z funkcją falową (inspirowane bramką Hadamarda).

        Zwraca wartość quantum_glow – neonowy puls pnącza.
        """
        vibration = math.sin(phase_shift * math.pi)
        quantum_glow = self.get_growth_params()["glow"] * (1 + 0.1 * vibration)
        return quantum_glow


if __name__ == "__main__":
    my_dna_sample = "ATGC" * 10 + "V1B3hR_ANDRZEJ_MATEWSKI"

    engine = BioArtGenerator(my_dna_sample)
    params = engine.get_growth_params()

    print("--- V1B3hR Bio-Engine Status ---")
    print(f"DNA Hash: {engine.signature[:16]}...")
    print(f"Neon Intensity:  {params['glow']} lux")
    print(f"Growth Angle:    {params['angle']}°")
    print(f"Chaos Factor:    {params['chaos']:.2%}")

    q_glow = engine.quantum_vibration_sync(phase_shift=0.25)
    print(f"Quantum Glow:    {q_glow:.2f} lux")

    mutations = engine.controlled_mutation(mutation_rate=0.01)
    print(f"Mutations:       {mutations} (1% safe mode)")
    print("Bio-sygnał: Stabilny. Koherencja kwantowa: Zachowana.")
