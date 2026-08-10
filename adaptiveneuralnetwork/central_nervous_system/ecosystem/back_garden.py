"""
Błyskawica V5 — Back Garden (Ogród Tła)
=======================================
Autonomiczna pętla samodoskonalenia działająca w pasmie SLOW_AI.

Adaptacja `SelfImprovementLoop` z NeuralForest.
Zadania Ogrodu:
1. Analizuje izolowane atomy i wyciąga lekcje.
2. Sadzi nowe atomy na podstawie potrzeb (zbyt mała spójność, nowe typy danych).
3. Konsoliduje wspomnienia w LuminanceVault.
4. Przetwarza dane w tle, powoli, bez obciążania zasobów czasu rzeczywistego (FAST_AI).
"""

import logging
import threading
import time

from adaptiveneuralnetwork.central_nervous_system.neuromorphic.atomic_body import AtomicBody
from adaptiveneuralnetwork.central_nervous_system.time_manager import (
    ProcessingLane,
    get_time_manager,
)
from adaptiveneuralnetwork.core.memory import MemoryVault

logger = logging.getLogger(__name__)


class BackGardenLoop:
    """
    Pętla samodoskonalenia działająca w tle (pasmo SLOW_AI).
    Pracuje powoli, analizuje logi, optymalizuje strukturę AtomicBody.
    """

    def __init__(self, atomic_body: AtomicBody, memory_vault: MemoryVault,
                 sleep_interval: float = 5.0):
        self.body = atomic_body
        self.memory = memory_vault
        self.sleep_interval = sleep_interval

        self._running = False
        self._thread: threading.Thread | None = None
        self.time_manager = get_time_manager()

        # Statystyki ogrodu
        self.cycles_completed = 0
        self.atoms_planted = 0
        self.atoms_pruned = 0
        self.last_action = "Ogród czeka..."

    def start(self):
        """Uruchamia ogród w tle."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True, name="BackGarden")
        self._thread.start()
        logger.info("[BackGarden] Ogród został otwarty. Samodoskonalenie w tle aktywne.")
        self.last_action = "Ogród otwarty."

    def stop(self):
        """Zatrzymuje pracę ogrodu."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
        logger.info("[BackGarden] Ogród został zamknięty.")
        self.last_action = "Ogród zamknięty."

    def _loop(self):
        """Główna pętla ogrodu."""
        while self._running:
            try:
                # Ogród pracuje tylko jeśli system ma czas (lub jest w SLOW_AI)
                if self.time_manager._current_lane == ProcessingLane.SLOW_HUMAN:
                    # Jeśli człowiek wchodzi w interakcję, zwalniamy ogród, by nie opóźniać
                    time.sleep(self.sleep_interval * 2)
                    continue

                self._garden_cycle()
                self.cycles_completed += 1

            except Exception as e:
                logger.error(f"[BackGarden] Błąd w pętli: {e}")
                self.last_action = f"Błąd krytyczny: {str(e)}"

            # Sen między cyklami (drzemka pod drzewem)
            time.sleep(self.sleep_interval)

    def _garden_cycle(self):
        """Jeden pełny cykl prac w ogrodzie."""

        # 1. Analiza zdrowia (pruning / izolacja)
        health = self.body.health_monitor.get_summary()
        if health.get("sick", 0) > 0 or health.get("dead", 0) > 0:
            self._tend_sick_atoms()

        # 2. Refleksja (konsolidacja wspomnień)
        self._consolidate_memories()

        # 3. Potrzeba wzrostu (planting)
        # Jeśli spójność jest bardzo niska od dłuższego czasu, potrzebujemy więcej 'guardian' lub 'memory'
        if self.body.dark_matter.self_modeler.coherence_history.mean() < 0.3:
            self._plant_new_atom("guardian")

    def _tend_sick_atoms(self):
        """Przenosi izolowane atomy na cmentarz i robi porządki."""
        sick = self.body.health_monitor.get_sick_atoms()
        for atom_id in sick:
            if atom_id in self.body._isolated:
                # Już wyizolowany, przenieś do pamięci
                spec = self.body.atom_specs.get(atom_id, "general")
                reason = "health_critical" # Uproszczenie na razie
                self.memory.on_atom_isolated(
                    atom_id=atom_id,
                    specialization=spec,
                    reason=reason,
                    final_metrics=self.body.health_monitor.atom_health.get(atom_id, {})
                )
                self.atoms_pruned += 1
                self.last_action = f"Pielęgnacja: atom {atom_id} ({spec}) przeniesiony na Cmentarz."

    def _consolidate_memories(self):
        """Porządkuje wspomnienia, łączy podobne, wyciąga wnioski."""
        from adaptiveneuralnetwork.central_nervous_system.memory.luminance_vault import (
            MemoryEmotion,
        )
        if self.cycles_completed % 12 == 0:  # Co ~minutę
            # Pobierz wspomnienia i posegreguj według emocji
            memories_by_emotion = {}
            for m in list(self.memory.luminance.memories):
                memories_by_emotion.setdefault(m.emotion, []).append(m)

            merged_count = 0
            for emotion, memories in memories_by_emotion.items():
                if len(memories) > 5:
                    memories.sort(key=lambda x: x.timestamp)
                    # Konsolidacja starych wspomnień (starsze niż 2 godziny)
                    old_memories = [m for m in memories if m.age_hours > 2.0]
                    if len(old_memories) >= 3:
                        avg_intensity = sum(m.intensity for m in old_memories) / len(old_memories)
                        consolidated_title = f"Skonsolidowane wspomnienie {emotion}"
                        consolidated_desc = f"Połączenie {len(old_memories)} starszych zdarzeń o charakterze {emotion} w jedno trwałe wspomnienie."
                        for m in old_memories:
                            if m in self.memory.luminance.memories:
                                self.memory.luminance.memories.remove(m)
                        self.memory.luminance.remember(
                            emotion=MemoryEmotion(emotion),
                            title=consolidated_title,
                            description=consolidated_desc,
                            intensity=avg_intensity,
                            source="consolidation"
                        )
                        merged_count += len(old_memories)

            self.memory.save()
            if merged_count > 0:
                self.last_action = f"Głęboka konsolidacja: połączono {merged_count} wspomnień."
            else:
                self.last_action = "Zapisano wspomnienia (Konsolidacja)."

    def _plant_new_atom(self, specialization: str):
        """Sadzi nowy atom w ciele, jeśli brakuje zasobów."""
        from adaptiveneuralnetwork.central_nervous_system.neuromorphic.atomic_body import (
            AtomFactory,
            AtomSize,
        )
        new_atom_id = f"{specialization}_planted_{self.atoms_planted + 1:02d}"

        try:
            new_atom = AtomFactory.create(
                size=AtomSize.SMALL,
                specialization=specialization,
                atom_id=new_atom_id
            )
            # Add to nn.ModuleDict dynamically (thread-safe copy in forward loop)
            self.body.atoms[new_atom_id] = new_atom
            self.body.atom_ids.append(new_atom_id)
            self.body.atom_specs[new_atom_id] = specialization

            self.atoms_planted += 1
            self.last_action = f"Posadzono nowy atom: {new_atom_id} ({specialization}) z powodu niskiej spójności."
            logger.info(f"[BackGarden] {self.last_action}")
        except Exception as e:
            logger.error(f"[BackGarden] Błąd podczas sadzenia atomu: {e}")

    def get_status(self) -> str:
        return (
            f"[Back Garden] Cykle: {self.cycles_completed} | "
            f"Posadzone: {self.atoms_planted} | Przycięte: {self.atoms_pruned} | "
            f"Ostatnia akcja: {self.last_action}"
        )
