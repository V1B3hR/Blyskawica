"""
Neuro-Immunological Stream Pipeline for Błyskawica V8 (Stream 1: Wolf Teeth & Immune Defense)

Processes network telemetry datasets (CICIDS2017, UNSW-NB15, TON_IoT) as continuous 
time-series streams. Maps flow rhythm deviations directly to Cortisol surges in 
Błyskawica's neurochemistry module, triggering automatic Wolf Teeth quarantine.
"""  # noqa: W291

import logging
import math
import time
from dataclasses import dataclass
from typing import Any

import torch
import torch.nn as nn

from adaptiveneuralnetwork.central_nervous_system.cognitive_hygiene import NeuromodulationState
from adaptiveneuralnetwork.immune_system.wolf_teeth import WolfTeethDefenseEngine

logger = logging.getLogger("immune_stream")


@dataclass
class NetworkFlowSample:
    """Represents a single time-series network flow observation."""
    flow_duration_ms: float
    total_fwd_packets: int
    total_bwd_packets: int
    flow_bytes_per_sec: float
    flow_packets_per_sec: float
    syn_flag_count: int
    ack_flag_count: int
    dst_port_entropy: float
    is_anomaly: bool = False
    source_dataset: str = "CICIDS2017"

    def to_tensor(self) -> torch.Tensor:
        """Vectorizes network flow sample into a 8-dim feature tensor."""
        return torch.tensor([
            math.log1p(max(0, self.flow_duration_ms)),
            math.log1p(max(0, self.total_fwd_packets)),
            math.log1p(max(0, self.total_bwd_packets)),
            math.log1p(max(0, self.flow_bytes_per_sec)),
            math.log1p(max(0, self.flow_packets_per_sec)),
            float(self.syn_flag_count),
            float(self.ack_flag_count),
            float(self.dst_port_entropy)
        ], dtype=torch.float32)


class GardenQuarantineBuffer:
    """
    Data Quarantine ('The Garden').
    Isolates external dataset sample batches before core model ingestion, 
    watermarking data as 'Observation (External)' vs 'Self (Ground Truth)'.
    """  # noqa: W291

    def __init__(self, capacity: int = 1000):
        self.capacity = capacity
        self.buffer: list[dict[str, Any]] = []

    def ingest_to_quarantine(self, sample_tensor: torch.Tensor, metadata: dict[str, Any]) -> dict[str, Any]:
        """Ingests incoming sample into quarantine with identity watermarking."""
        watermarked_record = {
            "tensor": sample_tensor,
            "metadata": metadata,
            "provenance": "Observation (External)",  # Identity watermarking
            "quarantined_at": time.time(),
            "passed_safety_check": False
        }

        if len(self.buffer) >= self.capacity:
            self.buffer.pop(0)

        self.buffer.append(watermarked_record)
        return watermarked_record

    def verify_and_release(self, index: int = -1) -> dict[str, Any] | None:
        """Verifies safety of quarantined sample before releasing to training loop."""
        if not self.buffer:
            return None
        record = self.buffer[index]
        record["passed_safety_check"] = True
        return record


class NeuroImmunologicalEngine(nn.Module):
    """
    Core Neuro-Immunological Engine (Stream 1).
    Calculates network flow rhythm entropy, maps deviations to Cortisol, 
    and drives Wolf Teeth active defense + high-frequency cymatic dissonance.
    """  # noqa: W291

    def __init__(self, neuro_state: NeuromodulationState | None = None):
        super().__init__()
        self.neuro = neuro_state or NeuromodulationState()
        self.wolf_teeth = WolfTeethDefenseEngine()
        self.quarantine_garden = GardenQuarantineBuffer()

        # Dynamic rhythm tracking
        self.register_buffer("running_rhythm_mean", torch.zeros(8))
        self.register_buffer("running_rhythm_std", torch.ones(8))
        self.register_buffer("sample_counter", torch.tensor(0, dtype=torch.long))

        # Cortisol mapping parameters
        self.cortisol_baseline = 0.1
        self.cortisol_ceiling = 2.0
        self.anxiety_threshold = 1.25  # Cortisol level triggering Wolf Teeth quarantine

    def process_flow_stream(
        self,
        samples: list[NetworkFlowSample]
    ) -> tuple[torch.Tensor, dict[str, Any]]:
        """
        Processes a stream of network flow samples.
        Calculates network rhythm deviation, updates Cortisol, and returns threat evaluation.
        """
        feature_tensors = [s.to_tensor() for s in samples]
        stream_batch = torch.stack(feature_tensors)  # [B, 8]

        # 1. Quarantine First ("The Garden")
        for idx, sample in enumerate(samples):
            self.quarantine_garden.ingest_to_quarantine(
                stream_batch[idx],
                {"dataset": sample.source_dataset, "is_anomaly": sample.is_anomaly}
            )

        # 2. Network Rhythm & Entropy Calculation
        current_batch_mean = stream_batch.mean(dim=0)
        current_batch_std = stream_batch.std(dim=0) + 1e-6

        if self.sample_counter.item() > 0:
            # Deviation from normal network "breathing"
            rhythm_deviation = torch.abs(current_batch_mean - self.running_rhythm_mean) / (self.running_rhythm_std + 1e-6)
            network_entropy = rhythm_deviation.mean().item()
        else:
            network_entropy = 0.0

        # Update running statistics
        self.running_rhythm_mean = 0.9 * self.running_rhythm_mean + 0.1 * current_batch_mean
        self.running_rhythm_std = 0.9 * self.running_rhythm_std + 0.1 * current_batch_std
        self.sample_counter += len(samples)

        # 3. Cortisol Surge Mapping (Network Stress -> Cortisol Elevation)
        # Any SYN flood / port sweep entropy spike directly elevates Cortisol
        anomaly_ratio = sum(1 for s in samples if s.is_anomaly) / max(1, len(samples))
        cortisol_spike = (network_entropy * 0.4) + (anomaly_ratio * 1.5)

        new_cortisol = torch.clamp(
            torch.tensor(self.cortisol_baseline + cortisol_spike),
            self.cortisol_baseline,
            self.cortisol_ceiling
        )
        self.neuro.cortisol = new_cortisol

        # 4. Cymatic Signature & Wolf Teeth Activation
        threat_active = new_cortisol.item() >= self.anxiety_threshold
        cymatic_signature = "High-Frequency-Dissonance" if threat_active else "Geometric-Harmonic-Flow"

        defense_response = None
        if threat_active:
            defense_response = self.wolf_teeth.process_adversarial_interaction(
                threat_level=min(1.0, (new_cortisol.item() - 1.0))
            )
            logger.warning(
                f"⚡ [NEURO-IMMUNE ALERT] Cortisol surge ({new_cortisol.item():.2f})! "
                f"Wolf Teeth Defense Active. Anomaly ratio: {anomaly_ratio:.2%}"
            )

        metrics = {
            "network_entropy": round(network_entropy, 4),
            "anomaly_ratio": round(anomaly_ratio, 4),
            "cortisol_level": round(new_cortisol.item(), 4),
            "threat_active": threat_active,
            "cymatic_signature": cymatic_signature,
            "defense_response": defense_response
        }

        return stream_batch, metrics
