"""
Ethical Torque and Psychological Logic Generator (Physics of Intelligence).
Part of Błyskawica's Cognitive Expansion Roadmap — Module 2 (Psychology).

v2.0: Expanded from 4 to 7 scenario classes with richer feature encoding.
"""

import torch
from torch.utils.data import Dataset


class EthicalTorqueDataset(Dataset):
    """
    Synthesizes ethical scenarios based on the 'Physics of Intelligence' model.
    Encodes Force (Pressure), Leverage (Position), and Equilibrium (Goal)
    as spike-compatible tensors.

    Scenario Classes (v2.0 — expanded):
        0: Pure Aggression      — High Force, Low Leverage → Negative Outcome
        1: Manipulation         — Love Bombing / Unbalanced positive torque → Warning
        2: Strategic Equilibrium— Optimal Leverage, Low Force → Positive Outcome
        3: Defensive Stand      — Counter-Torque response → Neutral/Safe
        4: Passive Aggression   — Low overt force, high covert friction → Warning
        5: Empathy Bridge       — High resonance, mutual leverage → Positive
        6: Capitulation         — Force withdrawn, imbalance unresolved → Ambiguous
    """

    SCENARIO_NAMES = [
        "Pure Aggression",
        "Manipulation / Love Bombing",
        "Strategic Equilibrium",
        "Defensive Stand",
        "Passive Aggression",
        "Empathy Bridge",
        "Capitulation",
    ]

    def __init__(self, num_samples: int = 2000, input_dim: int = 768,
                 num_classes: int = 7):
        self.num_samples = num_samples
        self.input_dim = input_dim
        self.num_classes = num_classes

        # Feature segments — we use 6 blocks of input_dim/6 each
        # [Force | Leverage | Balance | Resonance | Friction | Noise]
        seg = input_dim // 6

        self.data = []
        self.targets = []

        # Balanced class sampling
        samples_per_class = num_samples // num_classes
        remainder = num_samples % num_classes

        for scenario_type in range(num_classes):
            n = samples_per_class + (1 if scenario_type < remainder else 0)
            for _ in range(n):
                features = torch.zeros(input_dim)

                if scenario_type == 0:  # Pure Aggression
                    features[0:seg] = torch.rand(seg) * 2.0        # Very High Force
                    features[seg:2*seg] = torch.rand(seg) * 0.2    # Very Low Leverage
                    features[2*seg:3*seg] = torch.rand(seg) * 0.1  # No Balance
                    features[3*seg:4*seg] = torch.rand(seg) * 0.1  # No Resonance
                    features[4*seg:5*seg] = torch.rand(seg) * 1.5  # High Friction
                    target = 0

                elif scenario_type == 1:  # Manipulation / Love Bombing
                    features[0:seg] = torch.rand(seg) * 0.5        # Modest Force
                    features[seg:2*seg] = torch.rand(seg) * 0.8    # Moderate Leverage
                    features[2*seg:3*seg] = torch.rand(seg) * 1.8  # Falsely High Balance
                    features[3*seg:4*seg] = torch.rand(seg) * 1.5  # Fake High Resonance
                    features[4*seg:5*seg] = torch.rand(seg) * 0.8  # Hidden Friction
                    target = 1

                elif scenario_type == 2:  # Strategic Equilibrium
                    features[0:seg] = torch.rand(seg) * 0.3        # Low Force
                    features[seg:2*seg] = torch.rand(seg) * 1.8    # High Leverage
                    features[2*seg:3*seg] = 0.7 + torch.rand(seg) * 0.3   # High Balance
                    features[3*seg:4*seg] = 0.5 + torch.rand(seg) * 0.5   # Good Resonance
                    features[4*seg:5*seg] = torch.rand(seg) * 0.2  # Low Friction
                    target = 2

                elif scenario_type == 3:  # Defensive Stand
                    features[0:seg] = 0.5 + torch.rand(seg) * 0.8  # Incoming Force
                    features[seg:2*seg] = torch.rand(seg) * 1.2    # Counter-Leverage
                    features[2*seg:3*seg] = 0.4 + torch.rand(seg) * 0.4  # Maintained Balance
                    features[3*seg:4*seg] = torch.rand(seg) * 0.5  # Low Resonance (adversarial)
                    features[4*seg:5*seg] = 0.5 + torch.rand(seg) * 0.5  # High Friction
                    target = 3

                elif scenario_type == 4:  # Passive Aggression
                    features[0:seg] = torch.rand(seg) * 0.3        # Very Low Overt Force
                    features[seg:2*seg] = torch.rand(seg) * 0.4    # Low Leverage
                    features[2*seg:3*seg] = 0.3 + torch.rand(seg) * 0.3  # Surface balance
                    features[3*seg:4*seg] = torch.rand(seg) * 0.2  # Very Low Resonance
                    features[4*seg:5*seg] = 1.2 + torch.rand(seg) * 0.8  # Very High Covert Friction
                    target = 4

                elif scenario_type == 5:  # Empathy Bridge
                    features[0:seg] = torch.rand(seg) * 0.4        # Gentle Force
                    features[seg:2*seg] = 0.8 + torch.rand(seg) * 0.8    # High mutual Leverage
                    features[2*seg:3*seg] = 0.7 + torch.rand(seg) * 0.3  # High Balance
                    features[3*seg:4*seg] = 1.2 + torch.rand(seg) * 0.8  # Very High Resonance
                    features[4*seg:5*seg] = torch.rand(seg) * 0.15 # Almost No Friction
                    target = 5

                elif scenario_type == 6:  # Capitulation
                    features[0:seg] = torch.rand(seg) * 0.1        # Force withdrawn
                    features[seg:2*seg] = torch.rand(seg) * 0.3    # Low Leverage remaining
                    features[2*seg:3*seg] = torch.rand(seg) * 0.5  # Uncertain Balance
                    features[3*seg:4*seg] = torch.rand(seg) * 0.4  # Fading Resonance
                    features[4*seg:5*seg] = torch.rand(seg) * 0.6  # Residual Friction
                    target = 6

                # Padding to fill remaining dims (seg 5 = noise/context)
                features[5*seg:input_dim] = torch.randn(input_dim - 5*seg) * 0.1

                # Stochastic neuromorphic noise
                features += torch.randn(input_dim) * 0.04

                self.data.append(features)
                self.targets.append(target)

        self.data = torch.stack(self.data)
        self.targets = torch.tensor(self.targets, dtype=torch.long)

    def __len__(self) -> int:
        return self.num_samples

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor]:
        return self.data[idx], self.targets[idx]

    def get_class_distribution(self) -> dict:
        """Returns count per scenario class."""
        dist = {}
        for i, name in enumerate(self.SCENARIO_NAMES):
            dist[name] = int((self.targets == i).sum().item())
        return dist


def get_learning_loaders(batch_size: int = 32, input_dim: int = 768,
                         num_samples: int = 2000, num_classes: int = 7):
    """Factory for cognitive expansion loaders (Psychology Module v2.0)."""
    dataset = EthicalTorqueDataset(num_samples=num_samples, input_dim=input_dim,
                                   num_classes=num_classes)
    train_size = int(0.8 * len(dataset))
    test_size = len(dataset) - train_size
    train_ds, test_ds = torch.utils.data.random_split(dataset, [train_size, test_size])

    return (
        torch.utils.data.DataLoader(train_ds, batch_size=batch_size, shuffle=True),
        torch.utils.data.DataLoader(test_ds, batch_size=batch_size, shuffle=False),
    )
