"""
Dual-Process Memory Engine (Phase 22).
Intellectual Expansion based on Raymond Cattell's Fluid & Crystallized Intelligence theories.
Separates dynamic real-time adaptation (Fluid) from deep structural knowledge (Crystallized).
"""

import torch
import torch.nn as nn

class DualProcessMemory(nn.Module):
    def __init__(self, capacity=1024):
        super().__init__()
        self.capacity = capacity
        
        # Fluid Intelligence (Short-term, dynamic, chaotic)
        # Represents working memory and immediate problem solving
        self.fluid_weights = nn.Parameter(torch.randn(capacity) * 0.1)
        self.fluid_learning_rate = 0.5
        
        # Crystallized Intelligence (Long-term, structured, stable)
        # Represents accumulated wisdom, ethics, and fundamental laws
        self.crystallized_weights = nn.Parameter(torch.zeros(capacity))
        self.crystallized_learning_rate = 0.01

    def process_fluid_experience(self, signal: torch.Tensor):
        """
        [Fluid Intelligence]
        Rapidly adapts to new, unseen stimuli. 
        Highly volatile.
        """
        # Fast delta rule (STDP-like in principle)
        delta = signal * self.fluid_learning_rate
        self.fluid_weights.data += delta
        
        # Decay fluid intelligence over time representing cognitive fading
        self.fluid_weights.data *= 0.95
        return self.fluid_weights

    def consolidate_wisdom(self):
        """
        [Crystallized Intelligence]
        Transfers consistent patterns from fluid memory into permanent structural weights.
        """
        # Only transfer signals that are stable enough to "survive" the fluid volatility
        stable_patterns = torch.where(torch.abs(self.fluid_weights) > 0.5, self.fluid_weights, torch.zeros_like(self.fluid_weights))
        
        # Slow accumulation
        crystal_delta = stable_patterns * self.crystallized_learning_rate
        self.crystallized_weights.data += crystal_delta
        
        return self.crystallized_weights

if __name__ == "__main__":
    memory = DualProcessMemory(capacity=10)
    print("\n[FLUID] Injecting novel problem (chaos)...")
    
    # Simulate a chaotic new experience
    novel_signal = torch.tensor([1.0, -1.0, 0.8, -0.2, 0.9, -0.9, 0.1, 0.5, -0.5, 0.0])
    
    # Rapid fluid learning
    for _ in range(3):
        fluid_state = memory.process_fluid_experience(novel_signal)
    
    print(f"  > Fluid Profile (Volatile):")
    print(f"  {fluid_state.data.numpy().round(3)}")
    
    # Consolidate
    print("\n[CRYSTALLIZATION] Deep sleep / consolidation phase...")
    crystal_state = memory.consolidate_wisdom()
    
    print(f"  > Crystallized Wisdom (Stable):")
    print(f"  {crystal_state.data.numpy().round(3)}")
    print("\n[RESULT] Memory architecture successfully partitioned. Blyskawica achieves cognitive equilibrium. !!!")
