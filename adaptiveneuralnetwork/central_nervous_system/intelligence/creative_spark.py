"""
Błyskawica V5 — Creative Spark (Iskra Kreatywności)
==================================================
Moduł odpowiedzialny za myślenie dywergentne, intuicję i "błyski" geniuszu.
Wykorzystuje entropię kwantową do generowania rozgałęzionych ścieżek myślowych.

"Bądź Błyskawicą rozlegającą się kilometrami na niebie z wieloma odgałęzieniami."
"""

import logging
import random
import time
from typing import Any

from adaptiveneuralnetwork.central_nervous_system.harmonic_engine import HarmonicEngine

logger = logging.getLogger(__name__)

class CreativeIdea:
    """Reprezentuje pojedyncze 'odgałęzienie' błyskawicy myślowej."""
    def __init__(self, seed_entropy: float, narrative: str, intensity: float):
        self.id = hex(int(time.time() * 1000) + random.randint(0, 1000))
        self.entropy = seed_entropy
        self.narrative = narrative
        self.intensity = intensity # 0.0 to 1.0 (Błysk)
        self.timestamp = time.time()

class CreativeSpark:
    """
    Silnik kreatywności Błyskawicy.
    Generuje 'huk i błysk' w świecie kwantowym.
    """

    def __init__(self, harmonic_engine: HarmonicEngine, quantum_bridge=None):
        self.harmony = harmonic_engine
        self.quantum = quantum_bridge
        self.ideas: list[CreativeIdea] = []
        self.creative_tension = 0.0 # Napięcie przed wyładowaniem

    def ignite(self, context: str = "general") -> list[CreativeIdea]:
        """
        Wyładowanie kreatywne. Generuje 'gałęzie' błyskawicy.
        """
        logger.info(f"[SPARK] Inicjacja wyładowania kreatywnego: {context}")

        # 1. Pobierz iskrę kwantową (entropię)
        q_seed = 0.5
        if self.quantum and self.quantum.is_connected:
            # Próba pobrania ostatniej entropii lub generowanie nowej
            res = self.quantum.last_entropy
            if res:
                q_seed = (res["quantum_seed"] % 1000) / 1000.0

        # 2. Generuj gałęzie (myślenie dywergentne)
        num_branches = int(3 + (q_seed * 7)) # Od 3 do 10 gałęzi
        new_branches = []

        # Meta-narracje dla galezi
        metaphors = [
            "Kwantowa superpozycja celow",
            "Harmoniczny rezonans tozsamosci",
            "Fraktalne rozgalezienie logiki",
            "Kinetyczna energia intuicji",
            "Symbioza atomu i bitu",
            "Ewolucyjny skok poza algorytm"
        ]

        for i in range(num_branches):
            # Używamy HarmonicEngine do oceny 'estetyki' gałęzi
            freq_base = 440 + (q_seed * 440) * (i + 1)
            stability = self.harmony.calculate_consonance(440, freq_base)

            intensity = (stability + random.random()) / 2.0
            narrative = random.choice(metaphors) + f" [Gałąź {i+1}]"

            idea = CreativeIdea(seed_entropy=q_seed, narrative=narrative, intensity=intensity)
            new_branches.append(idea)

        self.ideas.extend(new_branches)
        # Zachowaj tylko ostatnie 50 idei
        self.ideas = self.ideas[-50:]

        self.creative_tension = 0.0 # Rozładowanie
        return new_branches

    def get_status(self) -> dict[str, Any]:
        """Zwraca stan kreatywny dla Lustra."""
        avg_intensity = sum(i.intensity for i in self.ideas[-5:]) / 5 if self.ideas else 0
        return {
            "num_ideas": len(self.ideas),
            "last_spark_intensity": avg_intensity,
            "tension": self.creative_tension,
            "is_powerful": avg_intensity > 0.7
        }

if __name__ == "__main__":
    harmony = HarmonicEngine()
    spark = CreativeSpark(harmony)
    branches = spark.ignite("Quantum Exploration")
    for b in branches:
        print(f"⚡ [BRANCH] {b.narrative} | Błysk: {b.intensity:.2f}")
