"""
Complete Multimodal Affective State Recognition Model

Assembles all components:
- Encoders for each modality
- Fusion layer
- Multi-task output heads
- Optional personalization
"""

import tensorflow as tf
from tensorflow import keras
import numpy as np
import logging
from typing import Dict, List, Optional, Tuple

from .encoders_eeg import EEGEncoder, create_eeg_encoder
from .encoders_multimodal import (
    PhysioEncoder, VoiceEncoder, TextEncoder,
    create_physio_encoder, create_voice_encoder, create_text_encoder
)
from .fusion import MultimodalFusion, create_fusion_layer
from .heads import MultiTaskHeads, create_output_heads


class AffectiveModel(keras.Model):
    """
    Complete multimodal affective state recognition model
    
    Architecture:
    1. Modality-specific encoders (EEG, physio, voice, text)
    2. Multimodal fusion layer
    3. Multi-task output heads (valence, arousal, categorical)
    4. Optional personalization (user/cultural embeddings)
    """
    
    def __init__(self,
                 config: Dict,
                 enable_modalities: Optional[Dict[str, bool]] = None,
                 **kwargs):
        """
        Args:
            config: Configuration dictionary
            enable_modalities: Dict specifying which modalities to enable
                              e.g., {'eeg': True, 'physio': True, 'voice': True, 'text': False}
        """
        super(AffectiveModel, self).__init__(**kwargs)
        
        self.config = config
        
        # Determine enabled modalities
        if enable_modalities is None:
            enable_modalities = config.get('modalities', {
                'eeg': True, 'physio': True, 'voice': True, 'text': False
            })
        self.enable_modalities = enable_modalities
        
        # Create encoders
        self.encoders = {}
        
        if enable_modalities.get('eeg', True):
            self.encoders['eeg'] = create_eeg_encoder(config)
            logging.info("EEG encoder enabled")
        
        if enable_modalities.get('physio', True):
            self.encoders['physio'] = create_physio_encoder(config)
            logging.info("Physio encoder enabled")
        
        if enable_modalities.get('voice', True):
            self.encoders['voice'] = create_voice_encoder(config)
            logging.info("Voice encoder enabled")
        
        if enable_modalities.get('text', False):
            self.encoders['text'] = create_text_encoder(config)
            logging.info("Text encoder enabled")
        
        # Create fusion layer
        self.fusion = create_fusion_layer(config)
        
        # Create output heads
        self.heads = create_output_heads(config)
        
        # Optional personalization
        personalization_config = config.get('model', {}).get('personalization', {})
        self.use_personalization = personalization_config.get('enabled', False)
        
        if self.use_personalization:
            self.user_embedding_dim = personalization_config.get('user_embedding_dim', 64)
            self.cultural_embedding_dim = personalization_config.get('cultural_embedding_dim', 32)
            
            # User embedding lookup (will be populated during training)
            self.user_embeddings = {}
            
            # FiLM conditioning layers
            fusion_hidden = config.get('model', {}).get('fusion', {}).get('hidden_dim', 512)
            self.film_scale = keras.layers.Dense(fusion_hidden, name='film_scale')
            self.film_shift = keras.layers.Dense(fusion_hidden, name='film_shift')
            
            logging.info(f"Personalization enabled: user_dim={self.user_embedding_dim}, cultural_dim={self.cultural_embedding_dim}")
        
        logging.info("Affective Model initialized")
    
    def call(self, inputs: Dict[str, tf.Tensor], 
             training=None,
             user_id: Optional[str] = None,
             cultural_context: Optional[str] = None):
        """
        Forward pass
        
        Args:
            inputs: Dictionary with modality tensors:
                - 'eeg': (batch, channels, timesteps)
                - 'physio': (batch, features)
                - 'voice': (batch, features)
                - 'text': (batch, features) [optional]
            training: Whether in training mode
            user_id: User identifier for personalization
            cultural_context: Cultural context identifier
        
        Returns:
            Dictionary with outputs:
                - 'valence': (batch,) in [-1, 1]
                - 'arousal': (batch,) in [0, 1]
                - 'categorical': (batch, 28) probabilities
        """
        # Encode each modality
        embeddings = {}
        
        if 'eeg' in inputs and 'eeg' in self.encoders:
            embeddings['eeg'] = self.encoders['eeg'](inputs['eeg'], training=training)
        
        if 'physio' in inputs and 'physio' in self.encoders:
            embeddings['physio'] = self.encoders['physio'](inputs['physio'], training=training)
        
        if 'voice' in inputs and 'voice' in self.encoders:
            embeddings['voice'] = self.encoders['voice'](inputs['voice'], training=training)
        
        if 'text' in inputs and 'text' in self.encoders:
            embeddings['text'] = self.encoders['text'](inputs['text'], training=training)
        
        # Fuse modalities
        fused = self.fusion(embeddings, training=training)
        
        # Apply personalization if enabled
        if self.use_personalization and user_id is not None:
            # Get or create user embedding
            if user_id not in self.user_embeddings:
                # Initialize random embedding
                self.user_embeddings[user_id] = tf.random.normal([self.user_embedding_dim])
            
            user_emb = self.user_embeddings[user_id]
            
            # FiLM conditioning
            scale = self.film_scale(user_emb)
            shift = self.film_shift(user_emb)
            
            # Apply FiLM: y = scale * x + shift
            fused = fused * scale + shift
        
        # Generate outputs
        outputs = self.heads(fused, training=training)
        
        return outputs
    
    def predict_with_uncertainty(self, 
                                 inputs: Dict[str, tf.Tensor],
                                 mc_samples: int = 15):
        """
        Prediction with epistemic uncertainty via MC Dropout
        
        Returns:
            outputs_mean: Mean predictions
            outputs_std: Standard deviations (uncertainty estimates)
        """
        predictions = []
        
        for _ in range(mc_samples):
            pred = self.call(inputs, training=True)  # Enable dropout
            predictions.append(pred)
        
        # Compute statistics
        valences = tf.stack([p['valence'] for p in predictions], axis=0)
        arousals = tf.stack([p['arousal'] for p in predictions], axis=0)
        categoricals = tf.stack([p['categorical'] for p in predictions], axis=0)
        
        outputs_mean = {
            'valence': tf.reduce_mean(valences, axis=0),
            'arousal': tf.reduce_mean(arousals, axis=0),
            'categorical': tf.reduce_mean(categoricals, axis=0)
        }
        
        outputs_std = {
            'valence': tf.math.reduce_std(valences, axis=0),
            'arousal': tf.math.reduce_std(arousals, axis=0),
            'categorical': tf.math.reduce_std(categoricals, axis=0)
        }
        
        return outputs_mean, outputs_std
    
    def get_config(self):
        """Get model configuration"""
        return {
            'config': self.config,
            'enable_modalities': self.enable_modalities
        }


def build_affective_model(config: Dict) -> AffectiveModel:
    """
    Build complete affective model from configuration
    
    Args:
        config: Configuration dictionary (loaded from affective_config.yaml)
    
    Returns:
        AffectiveModel instance
    """
    model = AffectiveModel(config)
    
    # Build model by calling with dummy inputs
    dummy_inputs = create_dummy_inputs(config)
    _ = model(dummy_inputs, training=False)
    
    logging.info(f"Affective model built with {model.count_params():,} parameters")
    
    return model


def create_dummy_inputs(config: Dict) -> Dict[str, tf.Tensor]:
    """Create dummy inputs for model building"""
    modalities = config.get('modalities', {})
    
    inputs = {}
    
    if modalities.get('eeg', True):
        cortical_nodes = config.get('cortical_nodes', 68)
        timesteps = config.get('timesteps', 1000)
        inputs['eeg'] = tf.zeros((1, cortical_nodes, timesteps), dtype=tf.float32)
    
    if modalities.get('physio', True):
        physio_features = config.get('physio_features', 24)
        inputs['physio'] = tf.zeros((1, physio_features), dtype=tf.float32)
    
    if modalities.get('voice', True):
        voice_features = config.get('voice_features', 128)
        inputs['voice'] = tf.zeros((1, voice_features), dtype=tf.float32)
    
    if modalities.get('text', False):
        text_features = config.get('text_features', 768)
        inputs['text'] = tf.zeros((1, text_features), dtype=tf.float32)
    
    return inputs


def compile_affective_model(model: AffectiveModel, config: Dict) -> AffectiveModel:
    """
    Compile model with losses and metrics
    
    Args:
        model: AffectiveModel instance
        config: Configuration dictionary
    
    Returns:
        Compiled model
    """
    training_config = config.get('training', {})
    loss_weights = training_config.get('loss_weights', {
        'valence': 1.0,
        'arousal': 1.0,
        'categorical': 1.0
    })
    
    # Define losses
    losses = {
        'valence': 'mse',
        'arousal': 'mse',
        'categorical': 'sparse_categorical_crossentropy'
    }
    
    # Define metrics
    from .heads import concordance_correlation_coefficient
    
    metrics = {
        'valence': ['mae', concordance_correlation_coefficient],
        'arousal': ['mae', concordance_correlation_coefficient],
        'categorical': ['accuracy']
    }
    
    # Optimizer
    learning_rate = training_config.get('learning_rate', 0.0003)
    optimizer = keras.optimizers.Adam(learning_rate=learning_rate)
    
    # Compile
    model.compile(
        optimizer=optimizer,
        loss=losses,
        loss_weights=loss_weights,
        metrics=metrics
    )
    
    logging.info(f"Model compiled with lr={learning_rate}, loss_weights={loss_weights}")
    
    return model
