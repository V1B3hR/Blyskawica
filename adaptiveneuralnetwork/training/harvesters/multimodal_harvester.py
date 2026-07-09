"""
Multimodal Knowledge Harvester.
Bridges Philosophy (ION), Fairness (COMPAS/ADULT), and Security (ANOMALY) into Błyskawica.
"""

import pandas as pd
import torch
import numpy as np
from pathlib import Path
from adaptiveneuralnetwork.central_nervous_system.neuromorphic.temporal_coding import TemporalPatternEncoder, TemporalConfig

class KnowledgeHub:
    """
    Manages the ingestion of disparate datasets into the neuromorphic substrate.
    """

    def __init__(self, dataset_root: str = "C:/Projekty/Datasets"):
        self.root = Path(dataset_root)
        config = TemporalConfig()
        # Input size matches character/val range, target patterns size arbitrarily set
        self.text_encoder = TemporalPatternEncoder(input_size=256, pattern_size=64, config=config)
        
    def harvest_wisdom(self):
        """Processes ION_Plato.csv into semantic trajectories."""
        df = pd.read_csv(self.root / "ION_Plato.csv")
        wisdom_samples = []
        for text in df.iloc[:, 0].dropna().astype(str).head(30):
            # Convert text to spikes
            for char in text[:50]:
                char_idx = ord(char) % 256
                spikes = torch.zeros(1, 256)
                spikes[0, char_idx] = 1.0
                # Pass through encoder (this updates history)
                pattern, info = self.text_encoder.forward(spikes, current_time=0.0)
                wisdom_samples.append(pattern)
        return wisdom_samples

    def harvest_armor(self):
        """Processes smart_system_anomaly_dataset.csv into rate-coded threat vectors."""
        df = pd.read_csv(self.root / "smart_system_anomaly_dataset.csv")
        
        # Select numeric metrics for mapping
        metrics = df[['cpu_usage', 'memory_usage', 'network_in_kb', 'packet_rate']].head(500)
        labels = df['label'].head(500)
        
        # Normalize 0-1
        metrics_norm = (metrics - metrics.min()) / (metrics.max() - metrics.min())
        
        # Map labels to numeric
        label_map = {"Normal": 0, "Anomaly_DoS": 1, "Anomaly_Injection": 2, "Anomaly_Spoofing": 3}
        numeric_labels = labels.map(label_map).fillna(0).astype(int)
        
        return torch.tensor(metrics_norm.values, dtype=torch.float32), torch.tensor(numeric_labels.values)

    def harvest_fairness(self):
        """Processes compas-scores-raw.csv into balance indicators."""
        # Focus on demographic parity / bias indicators
        df = pd.read_csv(self.root / "compas-scores-raw.csv")
        # Keep it simple for the first ingestion
        return df.head(100)

if __name__ == "__main__":
    hub = KnowledgeHub()
    print("[HARVESTER] Auditing Seeds of Wisdom...")
    
    wisdom = hub.harvest_wisdom()
    print(f"- Wisdom Ingested: {len(wisdom)} Socratic fragments.")
    
    armor_data, armor_labels = hub.harvest_armor()
    print(f"- Armor Ingested: {len(armor_data)} threat/normal vectors.")
    
    print("[STATUS] Błyskawica is now capable of feeling Ethical and Strategic Torque. ⚡️Φ!")
