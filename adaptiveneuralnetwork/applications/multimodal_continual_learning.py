"""
Multimodal continual learning implementation for Błyskawica AI.

This module bridges vision-language processing with neuromorphic continual learning,
enabling the association of visual patterns with semantic knowledge.
"""

import logging
from typing import Any

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

from adaptiveneuralnetwork.central_nervous_system.alive_node import AliveLoopNode
from adaptiveneuralnetwork.central_nervous_system.device_manager import device_manager
from adaptiveneuralnetwork.central_nervous_system.neuromorphic_v3.temporal_coding import (
    AudioSpikeEncoder,
    TemporalConfig,
    VisualSpikeEncoder,
)
from adaptiveneuralnetwork.central_nervous_system.phases import PhaseScheduler

from .continual_learning import ContinualLearningConfig, ContinualLearningSystem
from .multimodal_vl import VisionLanguageConfig, VisionLanguageModel, VisionLanguageTask
from .sensory_processing import SensoryConfig, SensoryProcessingPipeline

logger = logging.getLogger(__name__)

class MultimodalContinualLearningSystem(nn.Module):
    """
    Advanced system for learning cross-modal associations (Vision + Text)
    without catastrophic forgetting.
    """

    def __init__(
        self,
        vl_config: VisionLanguageConfig,
        cl_config: ContinualLearningConfig,
        temporal_config: TemporalConfig
    ):
        super().__init__()
        self.vl_config = vl_config
        self.cl_config = cl_config
        self.temporal_config = temporal_config

        # 1. Vision-Language Backbone (for feature extraction)
        # Using CROSS_MODAL_RETRIEVAL as the base task for alignment
        self.vl_model = VisionLanguageModel(vl_config, VisionLanguageTask.CROSS_MODAL_RETRIEVAL)

        # 2. Neuromorphic Bridge
        # Converts visual features and raw audio spectra into spikes
        self.visual_spike_encoder = VisualSpikeEncoder(temporal_config)
        self.audio_spike_encoder = AudioSpikeEncoder(temporal_config, num_frequency_bins=vl_config.audio_feature_dim if hasattr(vl_config, 'audio_feature_dim') else 256)

        # 3. Sensory Processing Pipeline
        # Handles real-time multi-modal input with temporal coding
        sensory_config = SensoryConfig(
            modalities=['vision', 'audio'],
            vision_input_size=vl_config.vision_feature_dim
        )
        self.sensory_pipeline = SensoryProcessingPipeline(sensory_config)

        # 4. Continual Learning Core
        # We reuse the core spiking logic for memory and consolidation
        self.cl_system = ContinualLearningSystem(cl_config)

        # 5. Multimodal Projection
        # Projects fused features to the CL system's input size
        # Increased input dimension to handle V+L+A if necessary
        self.multimodal_projection = nn.Linear(vl_config.fusion_dim, cl_config.input_size)

        # 5. Biological Infrastructure
        self.hidden_dim = vl_config.fusion_dim # Required for Trainer/GlobalWorkspace
        # PhaseScheduler manages circadian rhythms (Active, Sleep, REM)
        # Increased period to 2000 to prevent frequent hygiene-induced slowdowns
        self.phase_scheduler = PhaseScheduler(num_nodes=1, circadian_period=2000)

        # AliveLoopNode tracks energy, anxiety, and neurochemistry (The "Soul" of the node)
        # We start with a single master node for the whole multimodal system
        self.nodes = AliveLoopNode(
            position=[0.0, 0.0],
            velocity=[0.0, 0.0],
            initial_energy=50.0, # High capacity for multimodal processing
            node_id=0
        )

        self.to(device_manager.device)
        logger.info(f"Initialized Triple-Modal Continual Learning System with Phase-Aware Life Loop on {device_manager.device}")

    @property
    def device(self):
        return next(self.parameters()).device

    def forward(
        self,
        grounding_latent: torch.Tensor | dict[str, torch.Tensor],
        text_tokens: torch.Tensor | None = None,
        audio_spectrum: torch.Tensor | None = None,
        task_id: int = 0,
        current_time: float = 0.0
    ) -> dict[str, Any]:
        """
        Processes multi-modal input (via grounding_latent or raw sensors) 
        and returns task prediction + internal states.
        """  # noqa: W291
        # Unpack grounding_latent if it's a dict (from SensoryHub)
        if isinstance(grounding_latent, dict):
            # Extract available modalities
            images = grounding_latent.get('vision', None)
            text_tokens = grounding_latent.get('text', text_tokens)
            audio_spectrum = grounding_latent.get('audio', audio_spectrum)
            # The hub might produce a fused 'latent' directly
            combined_features = grounding_latent.get('latent', None)
        else:
            combined_features = grounding_latent
            images = None # Assume already processed if grounding_latent is a tensor

        # 0. Biological Gating
        # Check if node has enough energy to process high-fidelity multimodal data
        energy_factor = min(1.0, self.nodes.energy / 5.0) # Degradation begins below 5 energy

        # Check if system is in sleep phase (modulate activity)
        is_sleeping = (self.phase_scheduler.node_phases[0] == 1) # SLEEP = 1

        # Ensure a clean slate for the spiking core before processing new input
        if hasattr(self.cl_system, 'network'):
            self.cl_system.network.reset_state()

            # Apply biological modulation to synaptic plasticity if possible
            if hasattr(self.cl_system.network, 'metaplasticity_factor'):
                self.cl_system.network.metaplasticity_factor = energy_factor * (0.2 if is_sleeping else 1.0)

        # Ensure data is on the correct device
        if images is not None:
            images = images.to(self.device)
        if text_tokens is not None:
            text_tokens = text_tokens.to(self.device)
        if audio_spectrum is not None:
            audio_spectrum = audio_spectrum.to(self.device)

        # 1. Vision-Language Feature Extraction (if raw inputs provided)
        if images is not None and text_tokens is not None:
            # Forward through VL model to get fused features
            vl_output = self.vl_model(images, text_tokens)
            fused_features = vl_output['fused_features'] # [batch, fusion_dim]
        elif combined_features is not None:
            # Use already fused features from SensoryHub
            fused_features = combined_features.to(self.device)
        else:
            raise ValueError("MultimodalContinualLearningSystem requires either (images, text) or combined_features")

        # 2. Projection to Spiking Core
        # Ensure dimensions match multimodal_projection expectations (768)
        if fused_features.size(-1) != self.vl_config.fusion_dim:
             # Dimensional Armor: pad or truncate
             if fused_features.size(-1) < self.vl_config.fusion_dim:
                 padding = torch.zeros(*fused_features.shape[:-1], self.vl_config.fusion_dim - fused_features.size(-1), device=fused_features.device)
                 fused_features = torch.cat([fused_features, padding], dim=-1)
             else:
                 fused_features = fused_features[..., :self.vl_config.fusion_dim]

        spiking_input_raw = self.multimodal_projection(fused_features)

        # 3. Spiking Conversion (V+L base)
        spikes_vl, encoding_info_v = self.visual_spike_encoder(spiking_input_raw, current_time)

        # 4. Audio Spiking (if present)
        if audio_spectrum is not None:
            spikes_a, encoding_info_a = self.audio_spike_encoder(audio_spectrum, current_time)
            # Combine spikes: we'll simply sum or concatenate
            # For simplicity in this architecture, we add the audio spikes as a temporal modulation
            spikes = spikes_vl + spikes_a * 0.5
            encoding_info = {**encoding_info_v, **encoding_info_a}
        else:
            spikes = spikes_vl
            encoding_info = encoding_info_v

        # Update node state with the latest activity (for Tier 1 homeostasis)
        self.nodes.update(
            external_activity=spikes, # [batch, output_dim]
            internal_stimuli=fused_features, # [batch, fusion_dim]
            emotional_trigger=encoding_info.get('anxiety', 0.0)
        )
        self.nodes.last_spikes = spikes.detach()
        self.nodes.last_fused_features = fused_features.detach()

        # 5. Continual Learning Processing (Spiking Core + Memory)
        cl_output = self.cl_system(spikes, task_id)

        # 6. Update Biological Phases (Phase 7.3 Integration)
        # Prepare state tensors for the scheduler [batch, nodes, 1]
        batch_size = spikes.size(0)
        energy_tensor = torch.full((batch_size, 1, 1), self.nodes.energy, device=self.device)
        # Activity is derived from sparsity (mean spikes)
        activity_val = spikes.mean().item()
        activity_tensor = torch.full((batch_size, 1, 1), activity_val, device=self.device)
        anxiety_tensor = torch.full((batch_size, 1, 1), self.nodes.anxiety, device=self.device)

        self.phase_scheduler.step(energy_tensor, activity_tensor, anxiety_tensor)

        # 6. Biological Monitoring (Modulation based on state)
        # Energy consumption is already handled in self.nodes.update()

        # Increase anxiety if energy is low
        if self.nodes.energy < 3.0:
            self.nodes.anxiety += 0.05

        # Combine everything into final output dict
        final_output = {
            'logits': cl_output,
            'predictions': cl_output.argmax(dim=-1),
            'fused_features': fused_features,
            'combined_features': self.cl_system.last_combined_features,
            'spikes': spikes,
            'energy': self.nodes.energy,
            'phase': self.phase_scheduler.node_phases[0].item(),
            'encoding_info': encoding_info,
            'cl_info': {'logits': cl_output},
            'vl_output': vl_output if 'vl_output' in locals() else None
        }

        return final_output

    def _get_spike_loader(self, data_loader: torch.utils.data.DataLoader):
        """Helper to create a loader that yields (spikes, labels) for the spiking core."""
        self.eval()
        spikes_list = []
        labels_list = []

        with torch.no_grad():
            for batch in data_loader:
                if len(batch) == 4:
                    images, text, audio, labels = batch
                else:
                    images, text, labels = batch
                    audio = None

                # Extract spikes using the forward pass logic
                images = images.to(self.device)
                text = text.to(self.device)
                vl_output = self.vl_model(images, text)
                fused = vl_output['fused_features']
                projected = self.multimodal_projection(fused)
                spikes_vl, _ = self.visual_spike_encoder(projected)

                if audio is not None:
                    spikes_a, _ = self.audio_spike_encoder(audio.to(self.device))
                    spikes = (spikes_vl + spikes_a * 0.5).clone().detach()
                else:
                    spikes = spikes_vl.clone().detach()

                spikes_list.append(spikes.cpu())
                labels_list.append(labels.clone().detach().cpu())

        all_spikes = torch.cat(spikes_list, dim=0)
        all_labels = torch.cat(labels_list, dim=0)
        return DataLoader(TensorDataset(all_spikes, all_labels), batch_size=data_loader.batch_size)

    def learn_task(
        self,
        train_loader: torch.utils.data.DataLoader,
        task_id: int,
        epochs: int = 5
    ):
        """
        Trains the system on a multimodal task using continual learning strategies.
        """
        optimizer = torch.optim.Adam(self.parameters(), lr=0.001)
        criterion = nn.CrossEntropyLoss()

        self.train()
        for epoch in range(epochs):
            total_loss = 0
            for batch in train_loader:
                if len(batch) == 4:
                    images, text_tokens, audio, labels = batch
                else:
                    images, text_tokens, labels = batch
                    audio = None

                optimizer.zero_grad()
                output = self.forward(images, text_tokens, audio, task_id)
                prediction = output['prediction']

                loss = criterion(prediction, labels.to(self.device))

                # Dynamic Plasticity Adjustment
                surprise_factor = torch.clamp(loss.detach(), 0.1, 5.0) / 2.0
                dynamic_strength = self.cl_config.consolidation_strength / (1.0 + surprise_factor)

                if self.cl_system.synaptic_consolidation:
                    cons_loss = self.cl_system.synaptic_consolidation.consolidation_loss(
                        consolidation_strength=dynamic_strength.item()
                    )
                    loss += cons_loss

                loss.backward()
                optimizer.step()
                total_loss += loss.item()

                self.cl_system.episodic_memory.store(
                    output['combined_features'].detach(),
                    labels,
                    task_id
                )

            logger.info(f"Task {task_id}, Epoch {epoch+1}/{epochs}, Loss: {total_loss/len(train_loader):.4f} (Plasticity: {1.0/(1.0+surprise_factor.item()):.2f})")

        # Update Fisher Information using Spikes
        if self.cl_system.synaptic_consolidation:
            spike_loader = self._get_spike_loader(train_loader)
            self.cl_system.synaptic_consolidation.estimate_fisher_information(spike_loader)

    def evaluate_task(self, data_loader: torch.utils.data.DataLoader) -> float:
        """Evaluate performance on a specific multimodal task."""
        self.eval()
        correct = 0
        total = 0

        with torch.no_grad():
            for batch in data_loader:
                if len(batch) == 4:
                    images, text_tokens, audio, labels = batch
                else:
                    images, text_tokens, labels = batch
                    audio = None

                output = self.forward(images, text_tokens, audio)
                pred = output['prediction'].argmax(dim=1, keepdim=True)
                correct += pred.eq(labels.to(self.device).view_as(pred)).sum().item()
                total += labels.size(0)

        return correct / total if total > 0 else 0.0
