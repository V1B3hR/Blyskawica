"""
Fine-Grained Emotion & Neurochemistry Mapper for Błyskawica V8

Integrates Google Research GoEmotions (27 fine-grained emotion categories) with Błyskawica's
10-tensor NeuromodulationState (Dopamine, Serotonin, Oxytocin, GABA, Cortisol, Testosterone, etc.).
"""

import logging
from typing import Any

import torch
import torch.nn as nn

logger = logging.getLogger(__name__)

# GoEmotions 27 Categories
GOEMOTIONS_TAXONOMY = [
    "admiration", "amusement", "anger", "annoyance", "approval", "caring",
    "confusion", "curiosity", "desire", "disappointment", "disapproval",
    "disgust", "embarrassment", "excitement", "fear", "gratitude", "grief",
    "joy", "love", "nervousness", "optimism", "pride", "realization",
    "relief", "remorse", "sadness", "surprise", "neutral"
]


class GoEmotionsNeuromorphicMapper(nn.Module):
    """
    Maps 27 fine-grained emotion probability vectors into Błyskawica's 10-tensor neurochemistry.
    """
    def __init__(self):
        super().__init__()
        # Linear projection matrix mapping 27 emotion features -> 10 neurochemical buffers
        self.projection = nn.Linear(len(GOEMOTIONS_TAXONOMY), 10, bias=False)
        self._initialize_weights()

    def _initialize_weights(self):
        with torch.no_grad():
            w = torch.zeros(10, len(GOEMOTIONS_TAXONOMY))
            # 0: Dopamine (Joy, Excitement, Curiosity, Pride)
            w[0, GOEMOTIONS_TAXONOMY.index("joy")] = 0.4
            w[0, GOEMOTIONS_TAXONOMY.index("excitement")] = 0.5
            w[0, GOEMOTIONS_TAXONOMY.index("curiosity")] = 0.3
            w[0, GOEMOTIONS_TAXONOMY.index("pride")] = 0.3

            # 1: Acetylcholine (Curiosity, Realization, Surprise)
            w[1, GOEMOTIONS_TAXONOMY.index("curiosity")] = 0.5
            w[1, GOEMOTIONS_TAXONOMY.index("realization")] = 0.4
            w[1, GOEMOTIONS_TAXONOMY.index("surprise")] = 0.3

            # 2: Serotonin (Optimism, Relief, Calmness/Neutral, Approval)
            w[2, GOEMOTIONS_TAXONOMY.index("optimism")] = 0.4
            w[2, GOEMOTIONS_TAXONOMY.index("relief")] = 0.5
            w[2, GOEMOTIONS_TAXONOMY.index("approval")] = 0.3
            w[2, GOEMOTIONS_TAXONOMY.index("neutral")] = 0.2

            # 3: Oxytocin (Admiration, Caring, Gratitude, Love)
            w[3, GOEMOTIONS_TAXONOMY.index("admiration")] = 0.5
            w[3, GOEMOTIONS_TAXONOMY.index("caring")] = 0.5
            w[3, GOEMOTIONS_TAXONOMY.index("gratitude")] = 0.6
            w[3, GOEMOTIONS_TAXONOMY.index("love")] = 0.6

            # 4: Testosterone (Pride, Excitement, Anger)
            w[4, GOEMOTIONS_TAXONOMY.index("pride")] = 0.4
            w[4, GOEMOTIONS_TAXONOMY.index("anger")] = 0.3

            # 5: GABA (Relief, Approval, Neutral)
            w[5, GOEMOTIONS_TAXONOMY.index("relief")] = 0.4
            w[5, GOEMOTIONS_TAXONOMY.index("approval")] = 0.3
            w[5, GOEMOTIONS_TAXONOMY.index("neutral")] = 0.2

            # 6: Cortisol (Fear, Grief, Disappointment, Sadness, Remorse)
            w[6, GOEMOTIONS_TAXONOMY.index("fear")] = 0.5
            w[6, GOEMOTIONS_TAXONOMY.index("grief")] = 0.5
            w[6, GOEMOTIONS_TAXONOMY.index("disappointment")] = 0.4
            w[6, GOEMOTIONS_TAXONOMY.index("sadness")] = 0.4
            w[6, GOEMOTIONS_TAXONOMY.index("remorse")] = 0.3

            # 7: Adrenaline (Fear, Anger, Nervousness, Surprise)
            w[7, GOEMOTIONS_TAXONOMY.index("fear")] = 0.5
            w[7, GOEMOTIONS_TAXONOMY.index("anger")] = 0.4
            w[7, GOEMOTIONS_TAXONOMY.index("nervousness")] = 0.4

            # 8: Estrogen (Caring, Love, Optimism)
            w[8, GOEMOTIONS_TAXONOMY.index("caring")] = 0.4
            w[8, GOEMOTIONS_TAXONOMY.index("love")] = 0.4

            # 9: Melatonin (Neutral, Grief, Sadness)
            w[9, GOEMOTIONS_TAXONOMY.index("neutral")] = 0.1
            w[9, GOEMOTIONS_TAXONOMY.index("sadness")] = 0.2

            self.projection.weight.copy_(w)

    def forward(self, emotion_probs: torch.Tensor) -> torch.Tensor:
        """
        Maps (batch, 27) emotion probabilities to (batch, 10) neurochemical delta state.
        """
        return self.projection(emotion_probs)


class AffectiveCognitiveEvaluator:
    """
    Evaluates text input for GoEmotions fine-grained affective states and adjusts NeuromodulationState.
    """
    def __init__(self, neuro_state):
        self.neuro_state = neuro_state
        self.mapper = GoEmotionsNeuromorphicMapper()

    def analyze_and_update(self, text: str, emotion_dict: dict[str, float] = None) -> dict[str, Any]:
        probs = torch.zeros(1, len(GOEMOTIONS_TAXONOMY))

        if emotion_dict:
            for em, p in emotion_dict.items():
                if em in GOEMOTIONS_TAXONOMY:
                    idx = GOEMOTIONS_TAXONOMY.index(em)
                    probs[0, idx] = float(p)
        else:
            # Rule-based heuristic extraction for key emotions
            text_lower = text.lower()
            if any(w in text_lower for w in ["thank", "appreciate", "gratitude", "great job"]):
                probs[0, GOEMOTIONS_TAXONOMY.index("gratitude")] = 0.85
                probs[0, GOEMOTIONS_TAXONOMY.index("admiration")] = 0.70
            elif any(w in text_lower for w in ["curious", "explore", "learn", "how"]):
                probs[0, GOEMOTIONS_TAXONOMY.index("curiosity")] = 0.80
            elif any(w in text_lower for w in ["fear", "attack", "danger", "error"]):
                probs[0, GOEMOTIONS_TAXONOMY.index("fear")] = 0.75
            else:
                probs[0, GOEMOTIONS_TAXONOMY.index("neutral")] = 0.90

        deltas = self.mapper(probs).squeeze(0)

        # Apply deltas to NeuromodulationState buffers
        with torch.no_grad():
            self.neuro_state.dopamine.copy_(torch.clamp(self.neuro_state.dopamine + deltas[0], 0.1, 2.0))
            self.neuro_state.acetylcholine.copy_(torch.clamp(self.neuro_state.acetylcholine + deltas[1], 0.1, 2.0))
            self.neuro_state.serotonin.copy_(torch.clamp(self.neuro_state.serotonin + deltas[2], 0.1, 3.0))
            self.neuro_state.oxytocin.copy_(torch.clamp(self.neuro_state.oxytocin + deltas[3], 0.1, 2.0))
            self.neuro_state.testosterone.copy_(torch.clamp(self.neuro_state.testosterone + deltas[4], 0.1, 2.5))
            self.neuro_state.gaba.copy_(torch.clamp(self.neuro_state.gaba + deltas[5], 0.1, 2.0))
            self.neuro_state.cortisol.copy_(torch.clamp(self.neuro_state.cortisol + deltas[6], 0.0, 2.0))
            self.neuro_state.adrenaline.copy_(torch.clamp(self.neuro_state.adrenaline + deltas[7], 0.0, 2.0))

        top_emotions = {GOEMOTIONS_TAXONOMY[i]: round(float(probs[0, i]), 4) for i in range(27) if probs[0, i] > 0.1}

        logger.info(f"🎭 [AFFECTIVE EVALUATOR] Detected emotions: {top_emotions}")
        return {
            "text": text,
            "detected_emotions": top_emotions,
            "neurochemistry_state": {
                "oxytocin": round(float(self.neuro_state.oxytocin.item()), 4),
                "gaba": round(float(self.neuro_state.gaba.item()), 4),
                "dopamine": round(float(self.neuro_state.dopamine.item()), 4),
                "serotonin": round(float(self.neuro_state.serotonin.item()), 4),
                "cortisol": round(float(self.neuro_state.cortisol.item()), 4)
            }
        }
