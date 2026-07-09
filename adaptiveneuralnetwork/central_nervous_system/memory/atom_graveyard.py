"""
Błyskawica — AtomGraveyard (Cmentarz Atomów)
=============================================
Długoterminowa pamięć porażek i wyciszonych atomów.

Archiwizuje izolowane/martwe atomy z pełnym kontekstem:
- Co doprowadziło do izolacji (anomalie, przeciążenie)
- Jaki był stan systemu w chwili śmierci
- Czy atom może być wskrzeszony (jak TreeGraveyard w NeuralForest)

"Nie trać historii swoich porażek.
 One uczą więcej niż sukcesy."
"""

import json
import time
import logging
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class AtomRecord:
    """Archiwum jednego atomu."""
    atom_id:          str
    specialization:   str
    timestamp:        float                # Kiedy atom został izolowany/zniszczony
    reason:           str                  # Powód: "anomaly_overload" | "health_critical" | "timeout"
    final_metrics:    Dict[str, float]     # Ostatni znany stan atomu
    system_state:     Dict[str, float]     # Stan systemu w chwili śmierci
    lifetime_cycles:  int = 0             # Ile cykli przeżył
    peak_performance: float = 0.0        # Najlepszy wynik jaki osiągnął
    lessons:          List[str] = field(default_factory=list)  # Co można wyciągnąć z tej porażki
    resurrectable:    bool = True          # Czy można go wskrzesić?

    @property
    def age_hours(self) -> float:
        return (time.time() - self.timestamp) / 3600


class AtomGraveyard:
    """
    Cmentarz Atomów — archiwum izolowanych i martwych atomów.

    Port konceptu TreeGraveyard z NeuralForest dostosowany do V5.
    Umożliwia:
    - Archiwizację atomów z pełnym kontekstem
    - Analizę wzorców niepowodzeń
    - Potencjalne wskrzeszenie (resurrection) skutecznych atomów
    """

    def __init__(self, capacity: int = 256,
                 graveyard_path: Optional[str] = None):
        self.capacity = capacity
        self.graveyard_path = Path(graveyard_path) if graveyard_path else None
        self.records: List[AtomRecord] = []
        self.total_archived = 0

        if self.graveyard_path and self.graveyard_path.exists():
            self._load()
            logger.info(f"[AtomGraveyard] Zaladowano {len(self.records)} archiwalnych atomow")

    def archive(self, atom_id: str, specialization: str,
                reason: str,
                final_metrics: Dict[str, float],
                system_state: Optional[Dict[str, float]] = None,
                lifetime_cycles: int = 0,
                peak_performance: float = 0.0) -> AtomRecord:
        """Archiwizuje atom który zakończył swój żywot."""
        lessons = self._extract_lessons(reason, final_metrics)

        record = AtomRecord(
            atom_id          = atom_id,
            specialization   = specialization,
            timestamp        = time.time(),
            reason           = reason,
            final_metrics    = final_metrics,
            system_state     = system_state or {},
            lifetime_cycles  = lifetime_cycles,
            peak_performance = peak_performance,
            lessons          = lessons,
            resurrectable    = peak_performance > 0.3,
        )

        self.records.append(record)
        self.total_archived += 1

        if len(self.records) > self.capacity:
            # Usuń najstarsze które nie są wskrzeszalne
            non_resurrect = [r for r in self.records if not r.resurrectable]
            if non_resurrect:
                oldest = min(non_resurrect, key=lambda r: r.timestamp)
                self.records.remove(oldest)

        logger.info(f"[AtomGraveyard] Zarchiwizowano: {atom_id} [{specialization}] powod='{reason}'")

        if self.total_archived % 5 == 0 and self.graveyard_path:
            self._save()

        return record

    def get_failure_patterns(self) -> Dict[str, int]:
        """Jakie są najczęstsze powody śmierci atomów?"""
        patterns = {}
        for r in self.records:
            patterns[r.reason] = patterns.get(r.reason, 0) + 1
        return dict(sorted(patterns.items(), key=lambda x: -x[1]))

    def get_resurrection_candidates(self, min_performance: float = 0.3) -> List[AtomRecord]:
        """Które atomy mogą zostać wskrzeszone?"""
        candidates = [
            r for r in self.records
            if r.resurrectable and r.peak_performance >= min_performance
        ]
        return sorted(candidates, key=lambda r: r.peak_performance, reverse=True)

    def _extract_lessons(self, reason: str, metrics: Dict[str, float]) -> List[str]:
        """Wyciąga lekcje z porażki atomu."""
        lessons = []
        if reason == "anomaly_overload":
            lessons.append("Siatka grafenowa była zbyt przepuszczalna dla tego strumienia danych")
        if reason == "health_critical":
            lessons.append("Ekosystem mikrobiomu wymagał stabilizacji przed tym atomem")
        if metrics.get("quarantine_rate", 0) > 0.5:
            lessons.append("Wysoki wskaźnik kwarantanny wskazuje na problem z kalibracją progu anomalii")
        if metrics.get("heart_amplitude", 0) < 0.1:
            lessons.append("Serce fuzyjne nie zdążyło osiągnąć rezonansu przed izolacją")
        if not lessons:
            lessons.append("Przyczyna niejasna — wymaga dalszej analizy wzorców")
        return lessons

    def _save(self):
        if not self.graveyard_path:
            return
        try:
            self.graveyard_path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "version":        "1.0",
                "total_archived": self.total_archived,
                "records":        [asdict(r) for r in self.records],
            }
            with open(self.graveyard_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"[AtomGraveyard] Nie mogłam zapisać: {e}")

    def _load(self):
        try:
            with open(self.graveyard_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.total_archived = data.get("total_archived", 0)
            self.records = [AtomRecord(**r) for r in data.get("records", [])]
        except Exception as e:
            logger.warning(f"[AtomGraveyard] Nie mogłam wczytac: {e}")

    def save(self):
        self._save()

    def get_status(self) -> str:
        patterns = self.get_failure_patterns()
        top_reason = list(patterns.keys())[0] if patterns else "brak"
        resurrect  = len(self.get_resurrection_candidates())

        lines = [
            "=" * 54,
            "  [ATOM GRAVEYARD] Archiwum Atomow",
            "-" * 54,
            f"  Zarchiwizowanych: {len(self.records)} / {self.capacity}",
            f"  Wszystkich:       {self.total_archived}",
            f"  Do wskrzeszenia:  {resurrect}",
            f"  Glow. przyczyna:  {top_reason}",
            "=" * 54,
        ]
        return "\n".join(lines)

    def __len__(self) -> int:
        return len(self.records)
