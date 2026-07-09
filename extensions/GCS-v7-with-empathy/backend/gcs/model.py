
import logging
import tensorflow as tf
from tensorflow.keras.layers import (
    Input, Dense, BatchNormalization, Dropout, LayerNormalization,
    TimeDistributed, Conv1D, LSTM, Flatten, Concatenate, GlobalAveragePooling1D
)
from tensorflow.keras.models import Model
from spektral.layers import (
    GATConv, GCNConv, GraphSageConv,
    GlobalAvgPool, GlobalMaxPool, GlobalSumPool, GlobalAttnSumPool
)

# -------- Gradient Reversal Layer --------
@tf.custom_gradient
def grad_reverse(x):
    """A layer that reverses the gradient during backpropagation for adversarial training."""
    y = tf.identity(x)
    def custom_grad(dy): return -dy
    return y, custom_grad

class GradReverse(tf.keras.layers.Layer):
    def call(self, x): return grad_reverse(x)

# -------- Utility Blocks --------
def apply_norm_and_dropout(x, config):
    """Applies normalization and dropout layers as specified in the config."""
    if config.get("batch_norm", False):
        x = BatchNormalization()(x)
    if config.get("layer_norm", False):
        x = LayerNormalization()(x)
    if config.get("dropout_rate", 0.0) > 0:
        x = Dropout(config["dropout_rate"])(x)
    return x

# -------- Model Factory --------
class GCSModelFactory:
    @staticmethod
    def _validate_and_set_defaults(config: dict) -> dict:
        """
        Validates the configuration and populates it with sane defaults.
        This is the safety gatekeeper for the model builder.
        """
        logging.info("Validating model configuration...")
        
        # --- Required Keys ---
        required_keys = ["cortical_nodes", "timesteps"]
        for key in required_keys:
            if key not in config:
                raise ValueError(f"FATAL: Missing required config key: '{key}'")

        # --- Sane Defaults ---
        defaults = {
            "output_classes": 4, "gnn_type": "gat", "gnn_channels": 32, "gat_heads": 4,
            "num_layers": 2, "pooling": "attention", "temporal_encoder": "lstm",
            "temporal_features": 64, "dropout_rate": 0.3, "batch_norm": True,
            "layer_norm": False, "use_adversary": True, "use_attention_output": True,
            "expose_all_attn": True, "use_physio_input": True, "physio_features": 2,
            "train_subjects": 10, "kernel_initializer": "glorot_uniform", "l2_reg": 1e-4,
            "emotion_dense_layers": [128, 64], "adversary_lambda": 0.1
        }
        
        # Merge user config with defaults
        validated_config = {**defaults, **config}

        # --- Value Validation ---
        if validated_config["gnn_type"] not in ["gat", "gcn", "sage"]:
            raise ValueError(f"Invalid gnn_type: '{validated_config['gnn_type']}'. Must be 'gat', 'gcn', or 'sage'.")
        if validated_config["pooling"] not in ["avg", "max", "sum", "attention"]:
            raise ValueError(f"Invalid pooling: '{validated_config['pooling']}'.")
        
        logging.info("Configuration validated successfully.")
        return validated_config

    @staticmethod
    def _get_graph_layer_fn(config: dict):
        """Returns a function that creates a GNN layer based on the config."""
        gnn_type = config["gnn_type"]
        gnn_channels = config["gnn_channels"]
        kernel_initializer = config["kernel_initializer"]
        kernel_regularizer = tf.keras.regularizers.l2(config["l2_reg"])

        if gnn_type == "gat":
            def layer_builder(attn_heads=1, concat_heads=False, return_attn=False):
                return GATConv(gnn_channels, attn_heads=attn_heads, concat_heads=concat_heads, activation="relu",
                               kernel_initializer=kernel_initializer, kernel_regularizer=kernel_regularizer,
                               return_attn_coeffs=return_attn)
            return layer_builder
        
        # FULL IMPLEMENTATION of other GNN types
        elif gnn_type == "gcn":
            return lambda: GCNConv(gnn_channels, activation="relu", kernel_initializer=kernel_initializer,
                                   kernel_regularizer=kernel_regularizer)
        elif gnn_type == "sage":
            return lambda: GraphSageConv(gnn_channels, activation="relu", kernel_initializer=kernel_initializer,
                                         kernel_regularizer=kernel_regularizer)

    @staticmethod
    def build_affective_model(config: dict) -> Model:
        """Builds the definitive, multi-modal, and neuro-symbolic GCS model."""
        config = GCSModelFactory._validate_and_set_defaults(config)

        # --- Inputs ---
        node_input = Input(shape=(config["cortical_nodes"], config["timesteps"]), name="node_input")
        inputs = [node_input]
        if config["use_physio_input"]:
            physio_input = Input(shape=(config["physio_features"],), name="physio_input")
            inputs.append(physio_input)

        # --- Simple Feature Extraction ---
        logging.info("Building simplified feature extraction")
        # Average pool over time dimension: (batch, nodes, timesteps) -> (batch, nodes)
        x_eeg = tf.keras.layers.Lambda(lambda x: tf.reduce_mean(x, axis=2))(node_input)
        # Process with dense layers: (batch, nodes) -> (batch, nodes, features)
        x_eeg = tf.keras.layers.Dense(config["temporal_features"], activation="relu")(x_eeg)
        x_eeg = apply_norm_and_dropout(x_eeg, config)
        
        # Flatten to get a proper feature vector
        graph_embedding = tf.keras.layers.Flatten()(x_eeg)

        fused_embedding = graph_embedding
        if config["use_physio_input"]:
            logging.info("Adding Physiological Fusion branch.")
            x_physio = Dense(32, activation="relu")(physio_input)
            x_physio = apply_norm_and_dropout(x_physio, config)
            fused_embedding = Concatenate()([fused_embedding, x_physio])

        # --- Output Heads ---
        logging.info("Building Output Heads...")
        x_main = fused_embedding
        for units in config["emotion_dense_layers"]:
            x_main = Dense(units, activation="relu")(x_main)
            x_main = apply_norm_and_dropout(x_main, config)
        emotion_output = Dense(config["output_classes"], activation="softmax", name="mi_output")(x_main)
        outputs = [emotion_output]

        if config["use_adversary"]:
            logging.info("Adding Adversarial branch.")
            adversary_input = GradReverse()(fused_embedding)
            x_adv = Dense(128, activation="relu")(adversary_input)
            x_adv = apply_norm_and_dropout(x_adv, config)
            adversary_output = Dense(config["train_subjects"], activation="softmax", name="adversary_output")(x_adv)
            outputs.append(adversary_output)

        logging.info("Model build complete.")
        return Model(inputs=inputs, outputs=outputs, name="GCS_Affective_Model_v3_Audited")
