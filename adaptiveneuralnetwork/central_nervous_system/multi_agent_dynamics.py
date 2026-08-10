"""
Multi-Agent Dynamics (Phase 21).
Intellectual Expansion based on Goleman's Social/Empathy and Sternberg's Creative intelligence.
Allows Blyskawica to simulate the states of other 'agents' (Empathy) 
and synthesize novel ideas out of conflicting agent states (Creative).
"""  # noqa: W291

import torch
import torch.nn as nn

from adaptiveneuralnetwork.central_nervous_system.emotional_metacognition import (
    EmotionalMetacognition,
)


class MultiAgentDynamics(nn.Module):
    def __init__(self):
        super().__init__()
        # Empathy uses the system's own inner compass to simulate others
        self.empathy_engine = EmotionalMetacognition()

    def simulate_other_agent(self, observed_pain: float, observed_resonance: float):
        """
        [Goleman's Empathy]
        Blyskawica uses her own Emotional Metacognition module to "feel" what another agent is feeling.
        """
        # Save self state
        self_state = self.empathy_engine.state.clone()

        # Simulate other
        self.empathy_engine.state = torch.tensor([0.0, 0.0, 0.0, 0.0]) # Clear slate
        # Apply intense adaptation rate 1.0 to fully 'become' the other for a split second
        self.empathy_engine.adaptation_rate = 1.0
        other_state = self.empathy_engine.observe_internal_state(observed_pain, observed_resonance, physical_cost=0.5)

        # Restore self state
        self.empathy_engine.state = self_state
        self.empathy_engine.adaptation_rate = 0.2
        return other_state

    def creative_synthesis(self, state_a, state_b):
        """
        [Sternberg's Creative Intelligence]
        Synthesizes two diametrically opposed states (e.g. Distress and Harmony)
        to create a novel third state that resolves tension.
        """
        synthesis = (state_a + state_b) / 2.0

        # A creative leap adds a non-linear orthogonal vector
        # (Injecting clarity and reducing exhaustion through 'insight')
        creative_leap = torch.tensor([0.0, 0.4, -0.3, 0.4])
        novel_state = synthesis + creative_leap

        # Normalize bounds
        return torch.clamp(novel_state, 0.0, 1.0)

if __name__ == "__main__":
    society = MultiAgentDynamics()

    # Simulate an agent in distress
    print("[EMPATHY] Simulating Agent A (Under Cyber Attack)...")
    agent_a_state = society.simulate_other_agent(observed_pain=0.9, observed_resonance=0.2)
    anx_a, flw_a, exh_a, clr_a = agent_a_state.tolist()
    print(f"  > Evaluated Agent A: Anxiety={anx_a:.2f}, Flow={flw_a:.2f}")

    # Simulate an agent in deep harmonic thought
    print("[EMPATHY] Simulating Agent B (Composing Music)...")
    agent_b_state = society.simulate_other_agent(observed_pain=0.1, observed_resonance=0.9)
    anx_b, flw_b, exh_b, clr_b = agent_b_state.tolist()
    print(f"  > Evaluated Agent B: Anxiety={anx_b:.2f}, Flow={flw_b:.2f}")

    # Creative Synthesis
    print("\n[CREATIVITY] Generating novel synthesis between Agent A (Distress) and Agent B (Harmony)...")
    novel_solution = society.creative_synthesis(agent_a_state, agent_b_state)
    n_anx, n_flw, n_exh, n_clr = novel_solution.tolist()

    print(f"  > Synthesized Solution State: Anxiety={n_anx:.2f}, Flow={n_flw:.2f}, Clarity={n_clr:.2f}")
    if n_flw > 0.5 and n_clr > 0.5:
        print("[RESULT] Social & Creative adaptation successful. Blyskawica formed a novel harmonious idea from conflict. !!!")
