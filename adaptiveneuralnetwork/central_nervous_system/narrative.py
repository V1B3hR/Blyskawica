"""
Narrative Synthesis implementation for Błyskawica (Tier 2).

Compresses episodic memory sequences into a coherent long-term 'story', 
allowing the substrate to maintain sense of self and continuity over time.
"""

import torch
import torch.nn as nn
from typing import Optional, List

class NarrativeEngine(nn.Module):
    """
    The Narrative Engine processes episodic buffers to extract the 'Gist' 
    of the current experience loop.
    """
    
    def __init__(self, feature_dim: int, narrative_dim: int = 128):
        super().__init__()
        self.feature_dim = feature_dim
        self.narrative_dim = narrative_dim
        
        # Summarization network
        self.encoder = nn.GRU(
            input_size=feature_dim,
            hidden_size=narrative_dim,
            num_layers=1,
            batch_first=True
        )
        
        # Long-term Story Buffer [1, 1, narrative_dim] 
        self.register_buffer("story_state", torch.zeros(1, 1, narrative_dim))
        
        # Identity reinforcement (nudge narrative towards personality)
        self.identity_projection = nn.Linear(narrative_dim, narrative_dim)

    def synthesize(self, episodic_observations: torch.Tensor) -> torch.Tensor:
        """
        Compress episodic observations into an updated narrative vector.
        
        Args:
            episodic_observations: [batch, features]
        """
        if episodic_observations.numel() == 0:
            return self.story_state

        # Prepare for sequence processing
        # Add a mock time dimension [1, batch, features]
        sequence = episodic_observations.unsqueeze(0)
        
        # Process through GRU
        _, new_h = self.encoder(sequence, self.story_state)
        
        # Smooth update to narrative (Persistence layer)
        self.story_state = 0.9 * self.story_state + 0.1 * new_h
        
        return self.story_state

    def get_narrative(self) -> torch.Tensor:
        """Return the current long-term story vector."""
        return self.story_state

    def reflect(self) -> str:
        """Heuristic 'reflection' on the narrative state (debug/UX)."""
        energy = self.story_state.norm().item()
        if energy > 5.0:
            return "Narrative is Intense: Subjective history is rich and volatile."
        elif energy > 2.0:
            return "Narrative is Coherent: Subjective history is forming stable patterns."
        else:
            return "Narrative is Fragmented: Insufficient life history."
