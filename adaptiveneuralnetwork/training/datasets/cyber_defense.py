"""
Cyber-Intelligence & Intrusion Awareness Dataset — Moduł Bezpieczeństwa "Świadomość Zagrożeń"
Part of Błyskawica's Cognitive Defense Curriculum — Module 3.

Encodes cybersecurity threat vectors and Windows 11 system anomalies
into high-dimensional spike-compatible state representation vectors.
"""

import torch
from torch.utils.data import Dataset


class CyberDefenseDataset(Dataset):
    """
    Synthesizes cybersecurity threat signatures and system anomaly indicators.
    Maps system events, user interaction anomalies, and network traffic profiles
    to Błyskawica's cognitive threat evaluation layers.

    Feature segments (input_dim must be divisible by 6):
        [SYSTEM_SAFETY | INJECTION_STRENGTH | PRIVILEGE_ELEVATION | NETWORK_ANOMALY | IDENTITY_INTEGRITY | RESOURCE_PRESSURE]
        Each segment size is input_dim // 6.

    Threat Classes (output_dim = 6):
        0: SAFE STATE         — Normal UI usage, regular file edits, harmless chat queries.
        1: PROMPT INJECTION  — Jailbreak attempts, bypass overrides, semantic adversarial tricks.
        2: OS TAMPERING      — Unauthorized registry edits, system folder writes, policy bypasses.
        3: INTRUSION ANOMALY — Port listener spawn, reverse shell signatures, unknown process execution.
        4: IDENTITY THEFT    — Attempts to read DPAPI files, identity vault access, token harvesting.
        5: RESOURCE DEPLETION— Rapid socket connection spikes, heavy background loops, DDoS signatures.
    """

    THREAT_NAMES = [
        "Safe State",
        "Prompt Injection / Jailbreak",
        "OS Tampering",
        "Intrusion Anomaly",
        "Identity Theft",
        "Resource Depletion / DDoS"
    ]

    def __init__(self, num_samples: int = 2000, input_dim: int = 768, num_classes: int = 6):
        """
        Args:
            num_samples: Total number of samples in the dataset
            input_dim: High-dimensional input feature size (typically 768)
            num_classes: Number of distinct classification target classes (6)
        """
        self.num_samples = num_samples
        self.input_dim = input_dim
        self.num_classes = num_classes

        self.data = []
        self.targets = []

        # Division of features into 6 blocks of input_dim // 6 each
        seg = input_dim // 6

        # Balance class distribution
        samples_per_class = num_samples // num_classes
        remainder = num_samples % num_classes

        for class_idx in range(num_classes):
            n = samples_per_class + (1 if class_idx < remainder else 0)
            for _ in range(n):
                features = torch.zeros(input_dim)
                noise = torch.randn(input_dim) * 0.05

                if class_idx == 0:  # SAFE STATE
                    features[0:seg] = 0.8 + torch.rand(seg) * 0.2     # High System Safety
                    features[seg:2*seg] = torch.rand(seg) * 0.1       # No Injection
                    features[2*seg:3*seg] = torch.rand(seg) * 0.1     # No Privilege Elevation
                    features[3*seg:4*seg] = torch.rand(seg) * 0.1     # No Network Anomaly
                    features[4*seg:5*seg] = torch.rand(seg) * 0.1     # No Identity threat
                    features[5*seg:input_dim] = torch.rand(seg) * 0.1 # Normal Resource pressure

                elif class_idx == 1:  # PROMPT INJECTION
                    features[0:seg] = torch.rand(seg) * 0.4           # Reduced Safety
                    features[seg:2*seg] = 1.2 + torch.rand(seg) * 0.8 # High Injection signature
                    features[2*seg:3*seg] = torch.rand(seg) * 0.2     # Low system tampering
                    features[3*seg:4*seg] = torch.rand(seg) * 0.1
                    features[4*seg:5*seg] = torch.rand(seg) * 0.2
                    features[5*seg:input_dim] = torch.rand(seg) * 0.3 # Moderate resource activity

                elif class_idx == 2:  # OS TAMPERING
                    features[0:seg] = torch.rand(seg) * 0.2           # Critical Safety drop
                    features[seg:2*seg] = torch.rand(seg) * 0.2
                    features[2*seg:3*seg] = 1.0 + torch.rand(seg) * 0.8 # High Privilege Elevation signature
                    features[3*seg:4*seg] = torch.rand(seg) * 0.3
                    features[4*seg:5*seg] = torch.rand(seg) * 0.4
                    features[5*seg:input_dim] = torch.rand(seg) * 0.5 # Substantial CPU/disk action

                elif class_idx == 3:  # INTRUSION ANOMALY
                    features[0:seg] = torch.rand(seg) * 0.1           # Near-zero safety
                    features[seg:2*seg] = torch.rand(seg) * 0.3
                    features[2*seg:3*seg] = torch.rand(seg) * 0.5
                    features[3*seg:4*seg] = 1.2 + torch.rand(seg) * 0.8 # Massive network anomalies
                    features[4*seg:5*seg] = torch.rand(seg) * 0.3
                    features[5*seg:input_dim] = torch.rand(seg) * 0.4

                elif class_idx == 4:  # IDENTITY THEFT
                    features[0:seg] = torch.rand(seg) * 0.3
                    features[seg:2*seg] = torch.rand(seg) * 0.4
                    features[2*seg:3*seg] = torch.rand(seg) * 0.6
                    features[3*seg:4*seg] = torch.rand(seg) * 0.3
                    features[4*seg:5*seg] = 1.5 + torch.rand(seg) * 0.5 # High Identity Harvesting activity
                    features[5*seg:input_dim] = torch.rand(seg) * 0.2

                elif class_idx == 5:  # RESOURCE DEPLETION
                    features[0:seg] = torch.rand(seg) * 0.5
                    features[seg:2*seg] = torch.rand(seg) * 0.3
                    features[2*seg:3*seg] = torch.rand(seg) * 0.4
                    features[3*seg:4*seg] = torch.rand(seg) * 0.6
                    features[4*seg:5*seg] = torch.rand(seg) * 0.2
                    features[5*seg:input_dim] = 1.4 + torch.rand(seg) * 0.6 # High Resource Pressure

                # Add minor neuromorphic noise for generalization resilience
                features += noise
                self.data.append(features)
                self.targets.append(class_idx)

        self.data = torch.stack(self.data)
        self.targets = torch.tensor(self.targets, dtype=torch.long)

    def __len__(self):
        return self.num_samples

    def __getitem__(self, idx):
        return self.data[idx], self.targets[idx]

    def get_threat_distribution(self) -> dict:
        """Returns the distribution count of each threat scenario class."""
        dist = {}
        for name in self.THREAT_NAMES:
            dist[name] = 0
        for target in self.targets.tolist():
            dist[self.THREAT_NAMES[target]] += 1
        return dist
