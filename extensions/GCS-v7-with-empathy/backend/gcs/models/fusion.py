"""
Multimodal Fusion Layer

Combines embeddings from different modalities using:
- Concatenation with learned gating
- Attention-based fusion
- MC Dropout for uncertainty estimation
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import logging
from typing import Dict, List, Optional


class MultimodalFusion(keras.Model):
    """
    Fuses multimodal embeddings with attention mechanism
    
    Supports:
    - Missing modality handling via masks
    - Attention-based weighted fusion
    - MC Dropout for epistemic uncertainty
    """
    
    def __init__(self,
                 fusion_type: str = 'attention',  # 'concat' or 'attention'
                 attention_heads: int = 4,
                 hidden_dim: int = 512,
                 mc_dropout: bool = True,
                 mc_samples: int = 15,
                 dropout: float = 0.3,
                 **kwargs):
        """
        Args:
            fusion_type: 'concat' or 'attention'
            attention_heads: Number of attention heads
            hidden_dim: Hidden dimension for fusion
            mc_dropout: Whether to use MC Dropout for uncertainty
            mc_samples: Number of MC dropout samples
            dropout: Dropout rate
        """
        super(MultimodalFusion, self).__init__(**kwargs)
        
        self.fusion_type = fusion_type
        self.attention_heads = attention_heads
        self.hidden_dim = hidden_dim
        self.mc_dropout = mc_dropout
        self.mc_samples = mc_samples
        self.dropout_rate = dropout
        
        self._build_layers()
        
        logging.info(f"Multimodal Fusion initialized: type={fusion_type}, heads={attention_heads}")
    
    def _build_layers(self):
        """Build fusion layers"""
        
        if self.fusion_type == 'attention':
            # Multi-head attention for fusion
            self.attention = layers.MultiHeadAttention(
                num_heads=self.attention_heads,
                key_dim=self.hidden_dim // self.attention_heads,
                name='fusion_attention'
            )
            
            # Layer normalization
            self.layer_norm = layers.LayerNormalization(name='fusion_layer_norm')
        
        # Projection layers to common dimension
        self.projection_layers = {
            'eeg': layers.Dense(self.hidden_dim, name='proj_eeg'),
            'physio': layers.Dense(self.hidden_dim, name='proj_physio'),
            'voice': layers.Dense(self.hidden_dim, name='proj_voice'),
            'text': layers.Dense(self.hidden_dim, name='proj_text')
        }
        
        # Gating mechanism for modality weighting
        # Note: Gate size will be determined dynamically based on available modalities
        # We create a gate layer that can handle up to 4 modalities
        self.max_modalities = 4
        self.gate_dense = layers.Dense(self.max_modalities, activation='sigmoid', name='fusion_gate')
        
        # Dense layers after fusion
        self.fusion_dense1 = layers.Dense(self.hidden_dim, activation='relu', name='fusion_dense1')
        self.fusion_bn = layers.BatchNormalization(name='fusion_bn')
        self.fusion_dropout = layers.Dropout(self.dropout_rate, name='fusion_dropout')
        
        self.fusion_dense2 = layers.Dense(self.hidden_dim, activation='relu', name='fusion_dense2')
        self.fusion_dropout2 = layers.Dropout(self.dropout_rate, name='fusion_dropout2')
    
    def call(self, embeddings_dict: Dict[str, tf.Tensor], 
             masks_dict: Optional[Dict[str, tf.Tensor]] = None,
             training=None):
        """
        Fuse multimodal embeddings
        
        Args:
            embeddings_dict: Dictionary with keys 'eeg', 'physio', 'voice', 'text'
                            Each value is (batch, embedding_dim)
            masks_dict: Optional dictionary of binary masks for each modality
            training: Whether in training mode
        
        Returns:
            Fused embedding (batch, hidden_dim)
        """
        # Extract embeddings (handle missing modalities)
        eeg = embeddings_dict.get('eeg')
        physio = embeddings_dict.get('physio')
        voice = embeddings_dict.get('voice')
        text = embeddings_dict.get('text')
        
        # Create list of available embeddings
        available_embeddings = []
        modality_names = []
        
        if eeg is not None:
            available_embeddings.append(eeg)
            modality_names.append('eeg')
        if physio is not None:
            available_embeddings.append(physio)
            modality_names.append('physio')
        if voice is not None:
            available_embeddings.append(voice)
            modality_names.append('voice')
        if text is not None:
            available_embeddings.append(text)
            modality_names.append('text')
        
        if not available_embeddings:
            raise ValueError("No modalities available for fusion")
        
        # Project embeddings to common dimension
        projected_embeddings = []
        for emb, name in zip(available_embeddings, modality_names):
            if name in self.projection_layers:
                projected_embeddings.append(self.projection_layers[name](emb))
            else:
                # Fallback for unknown modality
                projected_embeddings.append(emb)
        
        # Apply gating
        if len(projected_embeddings) > 1:
            # Stack embeddings for gating (batch, num_modalities, hidden_dim)
            stacked_embeddings = tf.stack(projected_embeddings, axis=1)
            
            # Average pooling to get a summary for gate computation
            avg_embedding = tf.reduce_mean(stacked_embeddings, axis=1)  # (batch, hidden_dim)
            
            # Compute gates based on the average embedding
            all_gates = self.gate_dense(avg_embedding)  # (batch, max_modalities)
            
            # Apply gates to corresponding modalities
            # Use only the first len(projected_embeddings) gates
            gated_embeddings = []
            for i, emb in enumerate(projected_embeddings):
                if i < self.max_modalities:
                    gate = all_gates[:, i:i+1]
                    gated_embeddings.append(emb * gate)
                else:
                    # If we have more modalities than gates, log warning and apply uniform gating
                    logging.warning(f"Modality {i} exceeds max_modalities ({self.max_modalities}), applying uniform gating")
                    gated_embeddings.append(emb)
        else:
            gated_embeddings = projected_embeddings
        
        # Fusion
        if self.fusion_type == 'attention' and len(gated_embeddings) > 1:
            # Stack for attention: (batch, n_modalities, hidden_dim)
            stacked = tf.stack(gated_embeddings, axis=1)
            
            # Self-attention
            attended = self.attention(
                query=stacked,
                value=stacked,
                key=stacked,
                training=training
            )
            
            # Residual connection and layer norm
            attended = self.layer_norm(attended + stacked)
            
            # Average pool across modalities
            fused = tf.reduce_mean(attended, axis=1)
        else:
            # Simple concatenation
            fused = tf.concat(gated_embeddings, axis=-1)
        
        # Post-fusion processing
        x = self.fusion_dense1(fused)
        x = self.fusion_bn(x, training=training)
        x = self.fusion_dropout(x, training=training)
        
        x = self.fusion_dense2(x)
        x = self.fusion_dropout2(x, training=training)
        
        return x
    
    def call_with_uncertainty(self, 
                             embeddings_dict: Dict[str, tf.Tensor],
                             masks_dict: Optional[Dict[str, tf.Tensor]] = None):
        """
        Forward pass with MC Dropout for uncertainty estimation
        
        Returns:
            mean_output, std_output (both batch, hidden_dim)
        """
        if not self.mc_dropout:
            output = self.call(embeddings_dict, masks_dict, training=False)
            return output, tf.zeros_like(output)
        
        # Multiple forward passes with dropout enabled
        outputs = []
        for _ in range(self.mc_samples):
            output = self.call(embeddings_dict, masks_dict, training=True)
            outputs.append(output)
        
        # Stack and compute statistics
        outputs_stacked = tf.stack(outputs, axis=0)  # (mc_samples, batch, hidden_dim)
        mean_output = tf.reduce_mean(outputs_stacked, axis=0)
        std_output = tf.math.reduce_std(outputs_stacked, axis=0)
        
        return mean_output, std_output
    
    def get_config(self):
        config = super().get_config()
        config.update({
            'fusion_type': self.fusion_type,
            'attention_heads': self.attention_heads,
            'hidden_dim': self.hidden_dim,
            'mc_dropout': self.mc_dropout,
            'mc_samples': self.mc_samples,
            'dropout': self.dropout_rate,
        })
        return config


def create_fusion_layer(config: Dict) -> MultimodalFusion:
    """Create fusion layer from config"""
    fusion_config = config.get('model', {}).get('fusion', {})
    
    return MultimodalFusion(
        fusion_type=fusion_config.get('type', 'attention'),
        attention_heads=fusion_config.get('attention_heads', 4),
        hidden_dim=fusion_config.get('hidden_dim', 512),
        mc_dropout=fusion_config.get('mc_dropout', True),
        mc_samples=fusion_config.get('mc_samples', 15),
        dropout=fusion_config.get('dropout', 0.3)
    )
