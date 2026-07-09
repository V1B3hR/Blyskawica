"""
Emotional State for Adaptive Neural Network.
"""

from dataclasses import dataclass

@dataclass
class EmotionalState:
    node_id: int
    energy: float = 10.0
    anxiety: float = 0.0
    calm: float = 1.0
    joy: float = 0.0
    hope: float = 2.0
    curiosity: float = 1.0
    resilience: float = 2.0
    frustration: float = 0.0
    anger: float = 0.0
