"""
Sensory Hub: The bridge between external reality and the conscious substrate.
Fuses neuromorphic spike-pattern encoding with semantic transformer embeddings.
"""

import torch
import torch.nn as nn
from typing import Dict, Any, Optional, Deque
from collections import deque
import time
import logging

from ..applications.sensory_processing import SensoryProcessingPipeline, SensoryConfig
from ..applications.multimodal_vl import VisionLanguageModel, VisionLanguageConfig, VisionLanguageTask
from adaptiveneuralnetwork.central_nervous_system.global_workspace import SelectiveAttentionGating
from adaptiveneuralnetwork.cognitive_tools.ground_loop_isolator import GroundLoopIsolator

logger = logging.getLogger(__name__)

class SensoryHub(nn.Module):
    """
    Centralized hub for Multi-Modal Sensory Fusion.
    Binds Vision, Audio, Text, and Somatic inputs into a unified grounding latent.
    """
    def __init__(self, hidden_dim: int, device: str = 'cpu', vision_input_size: int = 784, audio_input_size: int = 256):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.device = device
        
        # 1. Low-Level Neuromorphic Pipeline (Spikes/Oscillations)
        # Configured for real-time temporal binding
        sensory_cfg = SensoryConfig(
            modalities=['vision', 'audio', 'tactile'],
            vision_input_size=vision_input_size,
            audio_input_size=audio_input_size,
            enable_cross_modal_binding=True
        )
        self.neuromorphic_pipeline = SensoryProcessingPipeline(sensory_cfg).to(device)
        
        # 2. High-Level Semantic Pipeline (Transformers)
        vl_cfg = VisionLanguageConfig(fusion_dim=hidden_dim)
        # Using Visual Reasoning as base task for grounding
        self.semantic_pipeline = VisionLanguageModel(vl_cfg, VisionLanguageTask.VISUAL_REASONING).to(device)
        
        # 3. Harmonic Fusion Layer
        # Maps [Batch, Integrated_Dim] from pipeline to [Batch, Hidden_Dim]
        # We assume the pipeline produces a combined feature vector
        integration_dim = 128 + 96 + 64 # From SensoryProcessingPipeline defaults
        self.fusion_projection = nn.Sequential(
            nn.Linear(integration_dim + hidden_dim, hidden_dim * 2),
            nn.LayerNorm(hidden_dim * 2),
            nn.ReLU(),
            nn.Linear(hidden_dim * 2, hidden_dim)
        )
        
        # 4. Modality Weighting (Trust calibrated)
        # 0: Spikes, 1: Semantic
        self.fusion_weights = nn.Parameter(torch.ones(2) / 2)
        
        # 5. Temporal Alignment (Settlement Task 1)
        # 50ms buffer for asynchronous binding
        self.buffer_size = 50 # ms
        self.modality_buffers: Dict[str, Deque[Dict[str, Any]]] = {
            'vision': deque(maxlen=5),
            'audio': deque(maxlen=10),
            'somatic': deque(maxlen=10)
        }
        
        # 6. Top-Down Attention Gating (Settlement Task 2)
        self.top_down_gate = SelectiveAttentionGating(hidden_dim, hidden_dim)
        self.noise_suppression_threshold = 0.8 # Focus level for dampening
        self.last_coherence = 1.0
        
        # 7. Integrated Spike Reservoir (Final autograd-safe context)
        # Assuming integration_dim = 128 + 96 + 64 = 288
        self.register_buffer('integrated_spikes', torch.zeros(1, 288, device=device))
        
        # 8. Synaptyczna Izolacja Galwaniczna (Opcja 3: Wejście Równoległe)
        self.ground_loop_isolator = GroundLoopIsolator(isolation_ratio=0.05).to(device)

    def ground(self, 
               sensory_data: Dict[str, torch.Tensor], 
               text_tokens: Optional[torch.Tensor] = None,
               workspace_state: Optional[torch.Tensor] = None,
               deception_risk: float = 0.0) -> torch.Tensor:
        """
        Fuses modalities into a single grounding latent.
        Calibration: If deception_risk is high, we lean harder on 'The World' (Spikes) 
        vs 'The Word' (Semantic).
        Workspace Feedback: If workspace_state is provided, apply Top-Down Attention.
        """
        # 0. High-Fidelity Sensory Grounding (Tier 3)
        # (Logic removed - was accidentally merged here)
        
        batch_size = next(iter(sensory_data.values())).size(0)
        current_time = time.time()
        
        # 1. Temporal Pulse Alignment (Settlement Task 1)
        self._update_buffers(sensory_data, current_time)
        synced_data = self._synchronize(current_time)
        
        # 2. Process Low-Level Spikes/Oscillations
        # integrated_features: [B, pipeline_dim]
        integrated_spikes, spike_info = self.neuromorphic_pipeline(synced_data)
        
        # 2. Process High-Level Semantics (if text is present)
        semantic_features = torch.zeros(batch_size, self.hidden_dim).to(self.device)
        if text_tokens is not None and 'vision' in sensory_data:
            # We need an image for the VL model
            # Assuming sensory_data['vision'] is raw pixels [B, C, H, W]
            vl_output = self.semantic_pipeline(sensory_data['vision'], text_tokens)
            semantic_features = vl_output['fused_features']
            
        # 3. Trust-Calibrated Weighting
        # Ensure integrated_spikes matches the expected integration_dim (288) for the projection
        # Tier 3: Neuromorphic Integration
        # Always detach integrated_spikes BEFORE use in the grounding pass to prevent graph leakage
        self.integrated_spikes = self.integrated_spikes.detach()
        integrated_spikes = self.integrated_spikes
        
        expected_spike_dim = 128 + 96 + 64
            
        # If deception_risk is high (Social manipulation), 
        # move attention from semantic_features (The Word) to integrated_spikes (The World).
        trust_weights = torch.softmax(self.fusion_weights, dim=0)
        
        # Adaptive Pivot: deception 0.0 -> neutral weights; deception 1.0 -> 90% spikes
        spike_priority = trust_weights[0] + (deception_risk * 0.4)
        word_priority = trust_weights[1] - (deception_risk * 0.4)
        
        # Combine into a fusion context with dimensional armor
        if integrated_spikes.size(0) != batch_size:
            integrated_spikes = integrated_spikes.expand(batch_size, -1)
            
        fused = self.fusion_projection(torch.cat([integrated_spikes, semantic_features], dim=-1))
        
        # 4. Top-Down Attention Gating (Settlement Task 2)
        # Global Workspace modulates the sensory filter
        if workspace_state is not None:
            # Calculate focus level (salience of current workspace content)
            # If workspace_state is a dict (summary), extract representative norm
            if isinstance(workspace_state, dict):
                focus_level = workspace_state.get('avg_salience', 0.5)
            else:
                focus_level = torch.norm(workspace_state).item()
            
            # If deeply focused, apply digital noise suppression (Inattentional Blindness)
            if focus_level > self.noise_suppression_threshold:
                # Dampen the fused sensory latent relative to focus (Scalar Clamp)
                dampening = max(0.1, 1.0 - (focus_level - 0.5))
                fused = fused * dampening
            else:
                # Normal interaction: Enhance relevance
                fused = self.top_down_gate(fused, workspace_state)
                
        # 5. Opcja 3: Izolacja Galwaniczna na samym wyjściu z PNS (Zmysły -> Izolator -> Rozwidlenie Yantra/CNS)
        fused = self.ground_loop_isolator(fused)
            
        return fused

    def _update_buffers(self, data: Dict[str, torch.Tensor], timestamp: float):
        """Stores fresh observations in the temporal buffer."""
        for modality, tensor in data.items():
            if modality in self.modality_buffers:
                self.modality_buffers[modality].append({
                    'tensor': tensor,
                    'timestamp': timestamp
                })

    def _synchronize(self, target_time: float) -> Dict[str, torch.Tensor]:
        """Aligns modalities to the closest target timestamp within the 50ms window."""
        synced = {}
        for modality, buffer in self.modality_buffers.items():
            if not buffer:
                continue
            
            # Find the closest frame to target_time
            # For this MVP, we just take the last frame if it's within 50ms (0.05s)
            last_frame = buffer[-1]
            if (target_time - last_frame['timestamp']) < 0.05:
                synced[modality] = last_frame['tensor']
            else:
                # If too old, use a zero tensor to represent 'Sensory Blackout'
                synced[modality] = torch.zeros_like(buffer[0]['tensor'])
                
        return synced

    def forward(self, *args, **kwargs):
        return self.ground(*args, **kwargs)
