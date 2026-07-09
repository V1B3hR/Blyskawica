"""
Physiological, Voice, and Text Encoders

Simple MLP encoders for non-EEG modalities
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import logging
from typing import Dict, Any, List


class PhysioEncoder(keras.Model):
    """Physiological signal encoder (MLP)"""
    
    def __init__(self,
                 input_dim: int = 24,
                 hidden_dims: List[int] = [64, 128],
                 embedding_dim: int = 128,
                 dropout: float = 0.2,
                 **kwargs):
        super(PhysioEncoder, self).__init__(**kwargs)
        
        self.input_dim = input_dim
        self.hidden_dims = hidden_dims
        self.embedding_dim = embedding_dim
        self.dropout_rate = dropout
        
        # Build layers
        self.dense_layers = []
        self.bn_layers = []
        self.dropout_layers = []
        
        for i, hidden_dim in enumerate(hidden_dims):
            self.dense_layers.append(
                layers.Dense(hidden_dim, activation='relu', name=f'physio_dense_{i}')
            )
            self.bn_layers.append(
                layers.BatchNormalization(name=f'physio_bn_{i}')
            )
            self.dropout_layers.append(
                layers.Dropout(dropout, name=f'physio_dropout_{i}')
            )
        
        self.embedding_layer = layers.Dense(
            embedding_dim, activation=None, name='physio_embedding'
        )
        
        logging.info(f"Physio Encoder initialized: {input_dim} -> {embedding_dim}")
    
    def call(self, inputs, training=None):
        x = inputs
        
        for dense, bn, dropout in zip(self.dense_layers, self.bn_layers, self.dropout_layers):
            x = dense(x)
            x = bn(x, training=training)
            x = dropout(x, training=training)
        
        embedding = self.embedding_layer(x)
        return embedding
    
    def get_config(self):
        config = super().get_config()
        config.update({
            'input_dim': self.input_dim,
            'hidden_dims': self.hidden_dims,
            'embedding_dim': self.embedding_dim,
            'dropout': self.dropout_rate,
        })
        return config


class VoiceEncoder(keras.Model):
    """Voice/audio feature encoder (MLP)"""
    
    def __init__(self,
                 input_dim: int = 128,
                 hidden_dims: List[int] = [256, 256],
                 embedding_dim: int = 256,
                 dropout: float = 0.2,
                 **kwargs):
        super(VoiceEncoder, self).__init__(**kwargs)
        
        self.input_dim = input_dim
        self.hidden_dims = hidden_dims
        self.embedding_dim = embedding_dim
        self.dropout_rate = dropout
        
        # Build layers
        self.dense_layers = []
        self.bn_layers = []
        self.dropout_layers = []
        
        for i, hidden_dim in enumerate(hidden_dims):
            self.dense_layers.append(
                layers.Dense(hidden_dim, activation='relu', name=f'voice_dense_{i}')
            )
            self.bn_layers.append(
                layers.BatchNormalization(name=f'voice_bn_{i}')
            )
            self.dropout_layers.append(
                layers.Dropout(dropout, name=f'voice_dropout_{i}')
            )
        
        self.embedding_layer = layers.Dense(
            embedding_dim, activation=None, name='voice_embedding'
        )
        
        logging.info(f"Voice Encoder initialized: {input_dim} -> {embedding_dim}")
    
    def call(self, inputs, training=None):
        x = inputs
        
        for dense, bn, dropout in zip(self.dense_layers, self.bn_layers, self.dropout_layers):
            x = dense(x)
            x = bn(x, training=training)
            x = dropout(x, training=training)
        
        embedding = self.embedding_layer(x)
        return embedding
    
    def get_config(self):
        config = super().get_config()
        config.update({
            'input_dim': self.input_dim,
            'hidden_dims': self.hidden_dims,
            'embedding_dim': self.embedding_dim,
            'dropout': self.dropout_rate,
        })
        return config


class TextEncoder(keras.Model):
    """Text embedding encoder (MLP)"""
    
    def __init__(self,
                 input_dim: int = 768,
                 hidden_dims: List[int] = [512, 256],
                 embedding_dim: int = 256,
                 dropout: float = 0.2,
                 **kwargs):
        super(TextEncoder, self).__init__(**kwargs)
        
        self.input_dim = input_dim
        self.hidden_dims = hidden_dims
        self.embedding_dim = embedding_dim
        self.dropout_rate = dropout
        
        # Build layers
        self.dense_layers = []
        self.bn_layers = []
        self.dropout_layers = []
        
        for i, hidden_dim in enumerate(hidden_dims):
            self.dense_layers.append(
                layers.Dense(hidden_dim, activation='relu', name=f'text_dense_{i}')
            )
            self.bn_layers.append(
                layers.BatchNormalization(name=f'text_bn_{i}')
            )
            self.dropout_layers.append(
                layers.Dropout(dropout, name=f'text_dropout_{i}')
            )
        
        self.embedding_layer = layers.Dense(
            embedding_dim, activation=None, name='text_embedding'
        )
        
        logging.info(f"Text Encoder initialized: {input_dim} -> {embedding_dim}")
    
    def call(self, inputs, training=None):
        x = inputs
        
        for dense, bn, dropout in zip(self.dense_layers, self.bn_layers, self.dropout_layers):
            x = dense(x)
            x = bn(x, training=training)
            x = dropout(x, training=training)
        
        embedding = self.embedding_layer(x)
        return embedding
    
    def get_config(self):
        config = super().get_config()
        config.update({
            'input_dim': self.input_dim,
            'hidden_dims': self.hidden_dims,
            'embedding_dim': self.embedding_dim,
            'dropout': self.dropout_rate,
        })
        return config


# Factory functions

def create_physio_encoder(config: Dict[str, Any]) -> PhysioEncoder:
    """Create physiological encoder from config"""
    physio_config = config.get('model', {}).get('physio_encoder', {})
    
    return PhysioEncoder(
        input_dim=config.get('physio_features', 24),
        hidden_dims=physio_config.get('hidden_dims', [64, 128]),
        embedding_dim=physio_config.get('embedding_dim', 128),
        dropout=physio_config.get('dropout', 0.2)
    )


def create_voice_encoder(config: Dict[str, Any]) -> VoiceEncoder:
    """Create voice encoder from config"""
    voice_config = config.get('model', {}).get('voice_encoder', {})
    
    return VoiceEncoder(
        input_dim=config.get('voice_features', 128),
        hidden_dims=voice_config.get('hidden_dims', [256, 256]),
        embedding_dim=voice_config.get('embedding_dim', 256),
        dropout=voice_config.get('dropout', 0.2)
    )


def create_text_encoder(config: Dict[str, Any]) -> TextEncoder:
    """Create text encoder from config"""
    text_config = config.get('model', {}).get('text_encoder', {})
    
    return TextEncoder(
        input_dim=config.get('text_features', 768),
        hidden_dims=text_config.get('hidden_dims', [512, 256]),
        embedding_dim=text_config.get('embedding_dim', 256),
        dropout=text_config.get('dropout', 0.2)
    )
