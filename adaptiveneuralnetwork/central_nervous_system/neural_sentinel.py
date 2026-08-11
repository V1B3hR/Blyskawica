"""
Neural Sentinel: Autonomic Defense Module.
Translates smart system anomalies into neuromorphic stress patterns.
"""

import torch
import torch.nn as nn


class NeuralSentinel(nn.Module):
    """
    Monitors system health and provides 'Neural Pain' feedback when anomalies are detected.
    """

    def __init__(self, metric_dim=4):
        super().__init__()
        # Internal model to classify threat patterns
        self.threat_analyzer = nn.Sequential(
            nn.Linear(metric_dim, 16),
            nn.ReLU(),
            nn.Linear(16, 4) # Output: [Normal, DoS, Injection, Spoofing]
        )
        self.alert_threshold = 0.7

    def perceive_threat(self, metrics):
        """
        Analyzes metrics and returns an 'Anomaly Torque' vector.
        """
        with torch.no_grad():
            threat_logits = self.threat_analyzer(metrics)
            threat_probs = torch.softmax(threat_logits, dim=-1)

        # Normal is index 0. If any other index has high probability, we have 'Pain'
        anomaly_intensity = 1.0 - threat_probs[..., 0]
        return anomaly_intensity, threat_probs

    def generate_pain_spikes(self, intensity):
        """
        Converts anomaly intensity into inhibitory 'brace' pulses.
        Higher intensity = more neural inhibition to protect core stability.
        """
    def calibrate(self, data, labels, epochs=5):
        """
        Trains the threat analyzer on provided samples.
        """
        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.Adam(self.parameters(), lr=0.01)

        self.train()
        for epoch in range(epochs):  # noqa: B007
            optimizer.zero_grad()
            outputs = self.threat_analyzer(data)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
        self.eval()
        print(f"[CALIBRATION] Sentinel Tuning Complete. Loss: {loss.item():.6f}")

if __name__ == "__main__":
    sentinel = NeuralSentinel()

    # Mock normal metrics [cpu, mem, net, packets]
    normal_metrics = torch.tensor([[0.1, 0.2, 0.05, 0.1]])
    # Mock DoS-like metrics (high network, high packets)
    dos_metrics = torch.tensor([[0.9, 0.4, 0.95, 0.9]])

    pain_level, probs = sentinel.perceive_threat(dos_metrics)
    print(f"[SENTINEL] Detecting Threat Profile: {probs.numpy()}")
    print(f"[SENTINEL] Anomaly Torque (Pain Level): {pain_level.item():.4f}")

    if pain_level > 0.5:
        print("[STATUS] SYSTEM BRACING: Autonomic Defense protocol engaged. 🛡️⚡️")
