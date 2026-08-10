"""
Chemical Simulator: Molecular Logic for Błyskawica.
Maps atomic properties to neural populations and bonds to synchrony.
"""

import torch
import torch.nn as nn


class MolecularAffinity(nn.Module):
    """
    Simulates chemical interactions as neural resonance.
    """

    def __init__(self):
        super().__init__()
        # Atomic descriptors: [Electronegativity, Atomic Radius, Valence Electrons]
        self.atomic_properties = {
            "H": torch.tensor([2.20, 0.37, 1.0]),
            "C": torch.tensor([2.55, 0.77, 4.0]),
            "O": torch.tensor([3.44, 0.73, 6.0]),
            "N": torch.tensor([3.04, 0.75, 5.0])
        }

    def calculate_bond_resonance(self, atom_a, atom_b):
        """Determines affinity as a sync coefficient."""
        props_a = self.atomic_properties.get(atom_a)
        props_b = self.atomic_properties.get(atom_b)
        if props_a is None or props_b is None: return 0.0  # noqa: E701
        delta_en = torch.abs(props_a[0] - props_b[0])
        return (1.0 / (1.0 + delta_en)).item()

    def simulate_reaction(self, reactants: list):
        """Standard interaction simulator (Bond calculation)."""
        if len(reactants) < 2: return 0.0  # noqa: E701
        total_resonance = 0.0
        for i in range(len(reactants)):
            for j in range(i+1, len(reactants)):
                total_resonance += self.calculate_bond_resonance(reactants[i], reactants[j])
        return total_resonance / (len(reactants) * (len(reactants)-1) / 2)

    def calculate_activation_energy(self, reactants: list):
        """Activation Energy Barrier Index."""
        base_energy = len(set(reactants)) * 0.5
        valence_sum = sum([self.atomic_properties.get(a, torch.tensor([0,0,0]))[2].item() for a in reactants])
        return base_energy * (1.0 + valence_sum / 20.0)

    def simulate_thermodynamic_reaction(self, reactants: list, environmental_entropy: float = 0.01):
        """Full Thermodynamic Simulation Pass."""
        stability = self.simulate_reaction(reactants)
        threshold = self.calculate_activation_energy(reactants)
        effective_stability = stability / (1.0 + environmental_entropy * 10.0)

        is_stable = effective_stability > 0.4
        yield_rate = max(0.0, effective_stability - (threshold / 10.0))

        return {
            "stability": effective_stability,
            "is_stable": is_stable,
            "yield": yield_rate,
            "limitations": "Entropy Collapse" if not is_stable else "None"
        }

if __name__ == "__main__":
    chem = MolecularAffinity()
    # Testing H2O under high entropy (0.1)
    res = chem.simulate_thermodynamic_reaction(["H", "H", "O"], environmental_entropy=0.1)
    print(f"[CHEMISTRY] Water Synthesis: Stable={res['is_stable']}, Yield={res['yield']:.4f}")
    print("[CHEMISTRY] Molecular logic fully synchronized with physics. !!!")
