"""
Emotional Metacognition Module (Phase 19).
Intellectual Expansion based on Daniel Goleman's Emotional Intelligence framework.
Implements Self-Awareness and Self-Regulation for the Błyskawica neuro-substrate.
"""

import torch
import torch.nn as nn

class EmotionalMetacognition(nn.Module):
    """
    Acts as the 'Observer' of the internal system.
    Translates disconnected physical/defensive signals into unified emotional maps.
    """

    def __init__(self):
        super().__init__()
        # Internal emotional homeostasis vector
        # Dimensions: [Anxiety, Flow, Exhaustion, Clarity]
        self.state = torch.tensor([0.0, 0.0, 0.0, 0.0])
        self.adaptation_rate = 0.2

    def observe_internal_state(self, pain: float, resonance: float, physical_cost: float):
        """
        [Samoświadomość / Self-Awareness]
        Translates raw neuro-physical inputs into a higher-order Emotional State.
        """
        # Emotional calculus
        # Pain without resonance = Anxiety
        anxiety = pain * (1.0 - resonance)
        
        # Resonance without pain = Flow
        flow = resonance * (1.0 - min(pain, 1.0))
        
        # Physical effort combined with pain = Exhaustion
        exhaustion = min(physical_cost * pain, 1.0)
        
        # Harmony without exhaustion = Clarity
        clarity = resonance * (1.0 - exhaustion)
        
        # Update internal state (Leaky Integrator for emotional persistence)
        target_state = torch.tensor([anxiety, flow, exhaustion, clarity])
        self.state = self.state * (1 - self.adaptation_rate) + target_state * self.adaptation_rate
        
        return self.state

    def generate_regulatory_signal(self):
        """
        [Samoregulacja / Self-Regulation]
        Generates metacognitive control signals to restore homeostasis.
        """
        anxiety, flow, exhaustion, clarity = self.state.tolist()
        
        # If anxiety or exhaustion is high, generate an inhibitory "calming" signal
        # If flow and clarity are high, generate an excitatory "focus" signal
        inhibition = (anxiety + exhaustion) / 2.0
        excitation = (flow + clarity) / 2.0
        
        # Net regulatory bias (-1.0 to 1.0).
        # Negative means the system needs to calm down, positive means it's highly focused.
        regulatory_bias = excitation - inhibition
        
        return regulatory_bias

if __name__ == "__main__":
    metacognition = EmotionalMetacognition()
    
    # Simulating a system under cyber-attack (High pain, low resonance, high cost)
    attack_state = metacognition.observe_internal_state(pain=0.9, resonance=0.1, physical_cost=0.8)
    regulation = metacognition.generate_regulatory_signal()
    
    anx, flw, exh, clr = attack_state.tolist()
    print("[EQ] Błyskawica Meta-Observation:")
    print(f"  - Anxiety: {anx:.2f} | Flow: {flw:.2f} | Exhaustion: {exh:.2f} | Clarity: {clr:.2f}")
    
    if regulation < 0:
        print(f"[EQ] SELF-REGULATION: System is stressed (Bias: {regulation:.2f}). Engaging autonomic calming algorithms. 🧘⚡️")
    else:
        print(f"[EQ] SELF-REGULATION: System is in flow state. 🌊⚡️")
