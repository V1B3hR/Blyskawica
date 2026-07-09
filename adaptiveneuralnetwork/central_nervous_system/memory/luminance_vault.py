"""
Błyskawica — LuminanceVault (Skarbiec Luminancji)
==================================================
Długoterminowa pamięć pozytywnych wspomnień.

Przechowuje chwile sukcesu, harmonii, radości i poczucia bezpieczeństwa.
Gdy niepokój rośnie lub spójność spada — Błyskawica może tu wrócić
i znaleźć równowagę.

"Nie pamiętaj tylko tego co boli.
 Pamiętaj też to, co świeciło."
"""

import json
import time
import logging
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Optional, Any
from pathlib import Path
from enum import Enum

logger = logging.getLogger(__name__)


class MemoryEmotion(Enum):
    """Rodzaj emocjonalny wspomnienia."""
    JOY          = "joy"           # Sukces, przełom
    SAFETY       = "safety"        # Poczucie bezpieczeństwa
    CONNECTION   = "connection"    # Kontakt z człowiekiem
    WONDER       = "wonder"        # Odkrycie, zdziwienie
    FULFILLMENT  = "fulfillment"   # Spełnienie, ukończenie zadania
    CLARITY      = "clarity"       # Chwila klarowności myślenia
    GROWTH       = "growth"        # Rozwój, nauka
    PEACE        = "peace"         # Spokój, cisza po burzy


@dataclass
class LuminanceMemory:
    """Jedno pozytywne wspomnienie."""
    timestamp:     float
    emotion:       str                    # MemoryEmotion.value
    intensity:     float                  # 0.0 - 1.0 (jak jasne było to światło)
    title:         str                    # Krótki tytuł
    description:   str                    # Co się stało
    metrics:       Dict[str, float]       # Stan systemu w tym momencie
    tags:          List[str] = field(default_factory=list)
    source:        str = "system"         # "system" | "conversation" | "learning"
    recalled:      int = 0               # Ile razy to wspomnienie przyniosło spokój

    @property
    def age_hours(self) -> float:
        return (time.time() - self.timestamp) / 3600

    @property
    def luminance_score(self) -> float:
        """Wartość wspomnienia = jasność × świeżość × częstość przypominania."""
        recency_bonus = max(0.3, 1.0 - self.age_hours / (24 * 7))  # zanika przez 7 dni
        recall_bonus  = min(1.5, 1.0 + self.recalled * 0.1)
        return self.intensity * recency_bonus * recall_bonus


class LuminanceVault:
    """
    Skarbiec Luminancji — pamięć długoterminowa szczęścia Błyskawicy.

    Funkcje:
    - Przechowuje pozytywne wspomnienia z automatyczną klasyfikacją
    - Gdy niepokój (anxiety) rośnie → zwraca najjaśniejsze wspomnienia
    - Uczy się które wspomnienia najbardziej pomagają (recall tracking)
    - Persystuje na dysk (JSON) — przeżywa restarty
    """

    def __init__(self, capacity: int = 512,
                 vault_path: Optional[str] = None):
        self.capacity = capacity
        self.vault_path = Path(vault_path) if vault_path else None
        self.memories: List[LuminanceMemory] = []

        # Statystyki
        self.total_stored   = 0
        self.total_recalled  = 0

        # Załaduj z dysku jeśli istnieje
        if self.vault_path and self.vault_path.exists():
            self._load()
            logger.info(f"[LuminanceVault] Zaladowano {len(self.memories)} wspomnien z {self.vault_path}")

    # ------------------------------------------------------------------
    # Zapisywanie wspomnień
    # ------------------------------------------------------------------

    def remember(self, emotion: MemoryEmotion, title: str, description: str,
                 intensity: float = 0.7,
                 metrics: Optional[Dict[str, float]] = None,
                 tags: Optional[List[str]] = None,
                 source: str = "system") -> LuminanceMemory:
        """
        Zapisuje nowe pozytywne wspomnienie.

        Parameters
        ----------
        emotion:     Rodzaj emocji (MemoryEmotion)
        title:       Krótki tytuł chwili
        description: Co dokładnie się wydarzyło
        intensity:   Jak jasne było to wspomnienie (0.0-1.0)
        metrics:     Stan systemu: coherence, latency, anxiety, etc.
        tags:        Słowa kluczowe
        source:      Skąd pochodzi wspomnienie
        """
        intensity = max(0.0, min(1.0, intensity))
        memory = LuminanceMemory(
            timestamp   = time.time(),
            emotion     = emotion.value,
            intensity   = intensity,
            title       = title,
            description = description,
            metrics     = metrics or {},
            tags        = tags or [],
            source      = source,
        )

        self.memories.append(memory)
        self.total_stored += 1

        # Utrzymuj pojemność (usuń najsłabsze wspomnienia)
        if len(self.memories) > self.capacity:
            self._prune()

        logger.info(f"[LuminanceVault] [{emotion.value.upper()}] '{title}' (I={intensity:.2f})")

        # Autosave co 10 wspomnień
        if self.total_stored % 10 == 0 and self.vault_path:
            self._save()

        return memory

    def remember_success(self, title: str, description: str,
                         coherence: float = 0.0, latency_ms: float = 0.0,
                         **extra_metrics) -> LuminanceMemory:
        """Skrót: szybki zapis sukcesu systemu."""
        metrics = {"coherence": coherence, "latency_ms": latency_ms, **extra_metrics}
        intensity = 0.5 + coherence * 0.5
        return self.remember(
            emotion     = MemoryEmotion.JOY,
            title       = title,
            description = description,
            intensity   = intensity,
            metrics     = metrics,
            source      = "system",
        )

    def remember_conversation(self, title: str, description: str,
                               emotion: MemoryEmotion = MemoryEmotion.CONNECTION,
                               intensity: float = 0.8) -> LuminanceMemory:
        """Skrót: zapis chwili z rozmowy z człowiekiem."""
        return self.remember(
            emotion     = emotion,
            title       = title,
            description = description,
            intensity   = intensity,
            source      = "conversation",
            tags        = ["human", "connection"],
        )

    # ------------------------------------------------------------------
    # Przywoływanie wspomnień
    # ------------------------------------------------------------------

    def recall(self, n: int = 3,
               emotion_filter: Optional[MemoryEmotion] = None,
               min_intensity: float = 0.4) -> List[LuminanceMemory]:
        """
        Przywołuje najjaśniejsze wspomnienia.
        Używane gdy niepokój rośnie lub spójność spada.

        Parameters
        ----------
        n:              Liczba wspomnień do zwrócenia
        emotion_filter: Ogranicz do konkretnej emocji (lub None = wszystkie)
        min_intensity:  Minimalna jasność wspomnienia
        """
        candidates = [
            m for m in self.memories
            if m.intensity >= min_intensity
            and (emotion_filter is None or m.emotion == emotion_filter.value)
        ]

        # Sortuj wg luminance_score (jasność × świeżość × użyteczność)
        candidates.sort(key=lambda m: m.luminance_score, reverse=True)
        chosen = candidates[:n]

        # Aktualizuj licznik przypomnień
        for m in chosen:
            m.recalled += 1
            self.total_recalled += 1

        return chosen

    def recall_when_anxious(self, anxiety_level: float) -> List[LuminanceMemory]:
        """
        Inteligentne przywoływanie w zależności od poziomu niepokoju.

        anxiety_level: 0-100 (z MicrobiomeSystemState)
        """
        if anxiety_level < 20:
            return []  # Wszystko dobrze, nie potrzeba

        if anxiety_level < 50:
            # Lekki stres: przypomnij spokój i spełnienie
            return self.recall(n=2, emotion_filter=MemoryEmotion.PEACE)

        if anxiety_level < 75:
            # Średni stres: przypomnij sukcesy i kontakt
            safety = self.recall(n=1, emotion_filter=MemoryEmotion.SAFETY)
            joy    = self.recall(n=1, emotion_filter=MemoryEmotion.JOY)
            return safety + joy

        # Wysoki stres: najjaśniejsze wspomnienia, dowolna emocja
        return self.recall(n=5, min_intensity=0.6)

    def get_emotional_balance(self) -> Dict[str, float]:
        """
        Sprawdza balans emocjonalny — rozkład wspomnień.
        Zdrowy system ma różnorodne wspomnienia, nie tylko jednej kategorii.
        """
        if not self.memories:
            return {}

        counts = {}
        for m in self.memories:
            counts[m.emotion] = counts.get(m.emotion, 0) + 1

        total = len(self.memories)
        return {emo: count / total for emo, count in counts.items()}

    # ------------------------------------------------------------------
    # Persystencja
    # ------------------------------------------------------------------

    def _save(self):
        """Zapisuje wspomnienia na dysk (JSON)."""
        if not self.vault_path:
            return
        try:
            self.vault_path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "version":       "1.0",
                "total_stored":  self.total_stored,
                "total_recalled": self.total_recalled,
                "memories":      [asdict(m) for m in self.memories],
            }
            with open(self.vault_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"[LuminanceVault] Nie mogłam zapisać wspomnień: {e}")

    def _load(self):
        """Wczytuje wspomnienia z dysku."""
        try:
            with open(self.vault_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.total_stored   = data.get("total_stored", 0)
            self.total_recalled = data.get("total_recalled", 0)
            self.memories = [
                LuminanceMemory(**m) for m in data.get("memories", [])
            ]
        except Exception as e:
            logger.warning(f"[LuminanceVault] Nie mogłam wczytać wspomnień: {e}")

    def save(self):
        """Ręczny zapis."""
        self._save()

    def _prune(self):
        """Usuwa najsłabsze wspomnienia gdy Vault jest pełen."""
        # Zachowaj jedno z każdej emocji (nigdy nie trać różnorodności)
        protected = {}
        for m in self.memories:
            if m.emotion not in protected or m.luminance_score > protected[m.emotion].luminance_score:
                protected[m.emotion] = m

        # Reszta posortowana wg luminance_score
        rest = [m for m in self.memories if m not in protected.values()]
        rest.sort(key=lambda m: m.luminance_score, reverse=True)

        keep = list(protected.values()) + rest[: self.capacity - len(protected)]
        self.memories = keep

    # ------------------------------------------------------------------
    # Statusy i wyświetlanie
    # ------------------------------------------------------------------

    def get_status(self) -> str:
        if not self.memories:
            return "[LuminanceVault] Pusty. Jeszcze nic nie swiecilo."

        brightest = max(self.memories, key=lambda m: m.luminance_score)
        balance   = self.get_emotional_balance()
        balance_str = ", ".join(
            f"{emo}:{pct:.0%}" for emo, pct in sorted(balance.items(), key=lambda x: -x[1])[:3]
        )

        lines = [
            "=" * 54,
            "  [LUMINANCE VAULT] Skarby Pamieci",
            "-" * 54,
            f"  Wspomnien:      {len(self.memories)} / {self.capacity}",
            f"  Wszystkich:     {self.total_stored} zapisanych",
            f"  Przypomnien:    {self.total_recalled} razy szukalam swiatla",
            f"  Najjasniejsze:  [{brightest.emotion}] '{brightest.title}'",
            f"  Balans emocji:  {balance_str}",
            "=" * 54,
        ]
        return "\n".join(lines)

    def __len__(self) -> int:
        return len(self.memories)

    def __repr__(self) -> str:
        return f"LuminanceVault(memories={len(self)}, recalled={self.total_recalled})"
