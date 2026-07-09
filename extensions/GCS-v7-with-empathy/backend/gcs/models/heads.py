"""
Multi-task Output Heads

Regression heads for valence/arousal
Classification head for 28-category emotions
Temperature scaling for calibration
"""

import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import logging
from typing import Dict, List, Tuple


class ValenceHead(keras.Model):
    """Valence regression head (outputs in [-1, 1])"""
    
    def __init__(self,
                 input_dim: int = 512,
                 hidden_dims: List[int] = [256, 128],
                 **kwargs):
        super(ValenceHead, self).__init__(**kwargs)
        
        self.dense_layers = []
        for i, dim in enumerate(hidden_dims):
            self.dense_layers.append(
                layers.Dense(dim, activation='relu', name=f'valence_dense_{i}')
            )
        
        # Output layer with tanh activation for [-1, 1] range
        self.output_layer = layers.Dense(1, activation='tanh', name='valence_output')
        
        logging.info("Valence Head initialized")
    
    def call(self, inputs, training=None):
        x = inputs
        for dense in self.dense_layers:
            x = dense(x)
        output = self.output_layer(x)
        return tf.squeeze(output, axis=-1)  # (batch,)


class ArousalHead(keras.Model):
    """Arousal regression head (outputs in [0, 1])"""
    
    def __init__(self,
                 input_dim: int = 512,
                 hidden_dims: List[int] = [256, 128],
                 **kwargs):
        super(ArousalHead, self).__init__(**kwargs)
        
        self.dense_layers = []
        for i, dim in enumerate(hidden_dims):
            self.dense_layers.append(
                layers.Dense(dim, activation='relu', name=f'arousal_dense_{i}')
            )
        
        # Output layer with sigmoid activation for [0, 1] range
        self.output_layer = layers.Dense(1, activation='sigmoid', name='arousal_output')
        
        logging.info("Arousal Head initialized")
    
    def call(self, inputs, training=None):
        x = inputs
        for dense in self.dense_layers:
            x = dense(x)
        output = self.output_layer(x)
        return tf.squeeze(output, axis=-1)  # (batch,)


class CategoricalHead(keras.Model):
    """Categorical emotion classification head (28 classes)"""
    
    def __init__(self,
                 input_dim: int = 512,
                 hidden_dims: List[int] = [512, 256],
                 num_classes: int = 28,
                 use_temperature_scaling: bool = True,
                 **kwargs):
        super(CategoricalHead, self).__init__(**kwargs)
        
        self.num_classes = num_classes
        self.use_temperature_scaling = use_temperature_scaling
        
        self.dense_layers = []
        for i, dim in enumerate(hidden_dims):
            self.dense_layers.append(
                layers.Dense(dim, activation='relu', name=f'categorical_dense_{i}')
            )
        
        # Logits layer
        self.logits_layer = layers.Dense(num_classes, activation=None, name='categorical_logits')
        
        # Temperature parameter for calibration (initialized to 1.0)
        if use_temperature_scaling:
            self.temperature = tf.Variable(
                1.0, trainable=True, dtype=tf.float32, name='temperature'
            )
        
        logging.info(f"Categorical Head initialized: {num_classes} classes")
    
    def call(self, inputs, training=None, return_logits=False):
        x = inputs
        for dense in self.dense_layers:
            x = dense(x)
        
        logits = self.logits_layer(x)
        
        if return_logits:
            return logits
        
        # Apply temperature scaling
        if self.use_temperature_scaling:
            scaled_logits = logits / self.temperature
        else:
            scaled_logits = logits
        
        # Softmax probabilities
        probs = tf.nn.softmax(scaled_logits, axis=-1)
        
        return probs
    
    def get_logits(self, inputs, training=None):
        """Get raw logits (for loss computation)"""
        return self.call(inputs, training=training, return_logits=True)


class MultiTaskHeads(keras.Model):
    """
    Combined multi-task output heads
    
    Outputs:
    - valence: continuous [-1, 1]
    - arousal: continuous [0, 1]
    - categorical: 28-class probabilities
    """
    
    def __init__(self,
                 input_dim: int = 512,
                 valence_hidden: List[int] = [256, 128],
                 arousal_hidden: List[int] = [256, 128],
                 categorical_hidden: List[int] = [512, 256],
                 num_classes: int = 28,
                 use_temperature_scaling: bool = True,
                 **kwargs):
        super(MultiTaskHeads, self).__init__(**kwargs)
        
        self.valence_head = ValenceHead(input_dim, valence_hidden)
        self.arousal_head = ArousalHead(input_dim, arousal_hidden)
        self.categorical_head = CategoricalHead(
            input_dim, categorical_hidden, num_classes, use_temperature_scaling
        )
        
        logging.info("Multi-task Heads initialized")
    
    def call(self, inputs, training=None):
        """
        Forward pass through all heads
        
        Returns:
            Dictionary with 'valence', 'arousal', 'categorical' outputs
        """
        valence = self.valence_head(inputs, training=training)
        arousal = self.arousal_head(inputs, training=training)
        categorical = self.categorical_head(inputs, training=training)
        
        return {
            'valence': valence,
            'arousal': arousal,
            'categorical': categorical
        }
    
    def get_logits(self, inputs, training=None):
        """Get categorical logits for loss computation"""
        return self.categorical_head.get_logits(inputs, training=training)


def concordance_correlation_coefficient(y_true, y_pred):
    """
    Concordance Correlation Coefficient (CCC) for valence/arousal evaluation
    
    CCC measures agreement between predicted and true continuous values
    Range: [-1, 1], where 1 is perfect agreement
    """
    mean_true = tf.reduce_mean(y_true)
    mean_pred = tf.reduce_mean(y_pred)
    
    var_true = tf.math.reduce_variance(y_true)
    var_pred = tf.math.reduce_variance(y_pred)
    
    covariance = tf.reduce_mean((y_true - mean_true) * (y_pred - mean_pred))
    
    ccc = (2 * covariance) / (var_true + var_pred + (mean_true - mean_pred) ** 2 + tf.keras.backend.epsilon())
    
    return ccc


def create_output_heads(config: Dict) -> MultiTaskHeads:
    """Create output heads from config"""
    heads_config = config.get('model', {}).get('heads', {})
    fusion_config = config.get('model', {}).get('fusion', {})
    
    input_dim = fusion_config.get('hidden_dim', 512)
    
    valence_cfg = heads_config.get('valence', {})
    arousal_cfg = heads_config.get('arousal', {})
    categorical_cfg = heads_config.get('categorical', {})
    
    return MultiTaskHeads(
        input_dim=input_dim,
        valence_hidden=valence_cfg.get('hidden_dims', [256, 128]),
        arousal_hidden=arousal_cfg.get('hidden_dims', [256, 128]),
        categorical_hidden=categorical_cfg.get('hidden_dims', [512, 256]),
        num_classes=categorical_cfg.get('num_classes', 28),
        use_temperature_scaling=heads_config.get('temperature_scaling', True)
    )
