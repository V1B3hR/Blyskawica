"""
EEG Encoder Architecture (GCS-v7 aligned)

- Temporal Convolutional Network (TCN) backbone for EEG signals
- Optional spatial graph mixing using a cortical adjacency (fast linear message passing)
- Streaming-friendly normalization and GELU activations
- Attention pooling option for richer summary embeddings
- Clean serialization via get_config / from_config

Inputs:
- EEG tensor shaped (batch, channels, timesteps) [default] or (batch, timesteps, channels)
- Optional adjacency matrix (channels x channels) if use_graph=True

Outputs:
- Embedding vector of shape (batch, embedding_dim), or
- Temporal embeddings (batch, timesteps, embed_dim) when return_sequence=True
"""

from typing import Optional, Dict, Any, List, Tuple, Union
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers


def _maybe_transpose_to_time_major(x: tf.Tensor, data_layout: str) -> Tuple[tf.Tensor, bool]:
    """
    Ensures tensor is (batch, timesteps, channels). Returns (tensor, transposed_flag).
    """
    if data_layout == "channels_first":  # (B, C, T) -> (B, T, C)
        return tf.transpose(x, [0, 2, 1]), True
    return x, False


class GraphMixer(layers.Layer):
    """
    Lightweight spatial graph mixing across channels per timestep:
        X_t' = A @ X_t
    where X is (B, T, C) and A is (C, C).
    """
    def __init__(self, adjacency: Optional[tf.Tensor] = None, trainable_matrix: bool = False, name: str = "graph_mixer", **kwargs):
        super().__init__(name=name, **kwargs)
        self._adjacency_init = adjacency
        self.trainable_matrix = trainable_matrix
        self.A = None  # will be built according to channels dimension

    def build(self, input_shape):
        # input_shape: (B, T, C)
        channels = int(input_shape[-1])
        if self._adjacency_init is not None:
            A = tf.convert_to_tensor(self._adjacency_init)
            if A.shape.rank != 2 or (A.shape[-2] is not None and A.shape[-1] is not None and (A.shape[-2] != channels or A.shape[-1] != channels)):
                # If static shape known and mismatched, raise early
                raise ValueError(f"Adjacency shape {A.shape} must be (channels, channels) = ({channels}, {channels}).")
            init = tf.keras.initializers.Constant(A)
        else:
            # Default to identity (no-op) if not provided
            init = tf.keras.initializers.Identity()

        self.A = self.add_weight(
            name="adjacency",
            shape=(channels, channels),
            dtype=self.dtype,
            initializer=init,
            trainable=self.trainable_matrix,
        )
        super().build(input_shape)

    def call(self, x: tf.Tensor) -> tf.Tensor:
        # x: (B, T, C) ; A: (C, C)
        return tf.einsum("btc,ck->btk", x, self.A)

    def get_config(self):
        cfg = super().get_config()
        cfg.update(dict(trainable_matrix=self.trainable_matrix))
        # Note: adjacency matrix is typically large; omit from config for compactness.
        return cfg


class TemporalBlock(layers.Layer):
    """
    Residual TCN block (no temporal downsampling to keep shapes stable):
      - Depthwise separable Conv1D (dilated)
      - GELU activation
      - LayerNorm
      - Dropout
      - Residual 1x1 projection to match channel dims
    """
    def __init__(
        self,
        filters: int,
        kernel_size: int,
        dilation_rate: int = 1,
        dropout: float = 0.1,
        name: str = "tcn_block",
        **kwargs,
    ):
        super().__init__(name=name, **kwargs)
        self.filters = filters
        self.kernel_size = kernel_size
        self.dilation_rate = dilation_rate
        self.dropout_rate = dropout

        self.conv = layers.SeparableConv1D(
            filters=filters,
            kernel_size=kernel_size,
            dilation_rate=dilation_rate,
            padding="same",
            depthwise_initializer="he_normal",
            pointwise_initializer="he_normal",
            name=f"{name}_sepconv",
        )
        self.act = layers.Activation(tf.nn.gelu, name=f"{name}_gelu")
        self.norm = layers.LayerNormalization(epsilon=1e-5, name=f"{name}_ln")
        self.drop = layers.Dropout(dropout, name=f"{name}_drop")

        self.res_proj = layers.Conv1D(
            filters=filters,
            kernel_size=1,
            padding="same",
            kernel_initializer="he_normal",
            name=f"{name}_resproj",
        )

    def call(self, x: tf.Tensor, training: Optional[bool] = None) -> tf.Tensor:
        y = self.conv(x)
        y = self.act(y)
        y = self.norm(y)
        y = self.drop(y, training=training)

        x_proj = self.res_proj(x)
        return x_proj + y

    def get_config(self):
        cfg = super().get_config()
        cfg.update(
            dict(
                filters=self.filters,
                kernel_size=self.kernel_size,
                dilation_rate=self.dilation_rate,
                dropout=self.dropout_rate,
            )
        )
        return cfg


class AttentionPooling1D(layers.Layer):
    """
    Attention pooling over time:
        alpha_t = softmax(w^T tanh(Wx_t + b))
        y = sum_t alpha_t * x_t
    """
    def __init__(self, hidden_units: int = 128, name: str = "attn_pool", **kwargs):
        super().__init__(name=name, **kwargs)
        self.hidden_units = hidden_units
        self.dense_h = layers.Dense(hidden_units, activation="tanh", name=f"{name}_h")
        self.dense_a = layers.Dense(1, activation=None, name=f"{name}_a")

    def call(self, x: tf.Tensor) -> tf.Tensor:
        # x: (B, T, C)
        h = self.dense_h(x)        # (B, T, H)
        logits = self.dense_a(h)   # (B, T, 1)
        weights = tf.nn.softmax(logits, axis=1)  # (B, T, 1)
        return tf.reduce_sum(weights * x, axis=1)  # (B, C)

    def get_config(self):
        cfg = super().get_config()
        cfg.update(dict(hidden_units=self.hidden_units))
        return cfg


class EEGEncoder(keras.Model):
    """
    EEG encoder using residual TCN with optional spatial graph mixing.

    Config:
      - temporal_filters: List[int]
      - kernel_sizes: List[int]
      - dilations: Optional[List[int]] (defaults to powers of 2)
      - embedding_dim: int
      - dropout: float
      - use_graph: bool
      - trainable_graph: bool (if True, adjacency becomes learnable)
      - pooling: 'avg' | 'max' | 'attn'
      - return_sequence: bool (return (B, T, C_embed) instead of pooled embedding)
      - data_layout: 'channels_first' | 'channels_last' for inputs

    Inputs:
      - Tensor (B, C, T) if channels_first or (B, T, C) if channels_last
      - Or dict with:
          {'eeg': Tensor, 'adjacency': Tensor[C, C]} to override built-in adjacency
    """
    def __init__(
        self,
        input_shape: Tuple[int, int],  # (channels, timesteps)
        temporal_filters: List[int] = (64, 128, 128),
        kernel_sizes: List[int] = (7, 5, 3),
        dilations: Optional[List[int]] = None,
        embedding_dim: int = 256,
        dropout: float = 0.3,
        use_graph: bool = False,
        trainable_graph: bool = False,
        pooling: str = "attn",
        return_sequence: bool = False,
        data_layout: str = "channels_first",
        adjacency: Optional[tf.Tensor] = None,
        name: str = "EEGEncoder",
        **kwargs,
    ):
        super().__init__(name=name, **kwargs)
        if len(temporal_filters) != len(kernel_sizes):
            raise ValueError("temporal_filters and kernel_sizes must be the same length.")

        self.input_shape_eeg = tuple(input_shape)
        self.channels, self.timesteps = self.input_shape_eeg

        self.temporal_filters = list(temporal_filters)
        self.kernel_sizes = list(kernel_sizes)
        self.dilations = list(dilations) if dilations is not None else [2**i for i in range(len(self.temporal_filters))]
        if len(self.dilations) != len(self.temporal_filters):
            raise ValueError("dilations must match the length of temporal_filters when provided.")

        self.embedding_dim = int(embedding_dim)
        self.dropout_rate = float(dropout)
        self.use_graph = bool(use_graph)
        self.trainable_graph = bool(trainable_graph)
        self.pooling = pooling
        self.return_sequence = bool(return_sequence)
        self.data_layout = data_layout
        self._adjacency_init = adjacency

        # Layers
        self.graph_mixer = GraphMixer(adjacency=adjacency, trainable_matrix=self.trainable_graph, name="graph_mixer") if self.use_graph else None

        self.tcn_blocks: List[TemporalBlock] = []
        for i, (f, k, d) in enumerate(zip(self.temporal_filters, self.kernel_sizes, self.dilations)):
            self.tcn_blocks.append(
                TemporalBlock(
                    filters=f,
                    kernel_size=k,
                    dilation_rate=d,
                    dropout=self.dropout_rate,
                    name=f"tcn_block_{i}",
                )
            )

        # Optional pooling head
        if not self.return_sequence:
            if self.pooling == "avg":
                self.pool = layers.GlobalAveragePooling1D(name="global_avg_pool")
            elif self.pooling == "max":
                self.pool = layers.GlobalMaxPooling1D(name="global_max_pool")
            elif self.pooling == "attn":
                self.pool = AttentionPooling1D(hidden_units=max(64, self.temporal_filters[-1] // 2), name="attn_pool")
            else:
                raise ValueError("pooling must be one of {'avg','max','attn'}")

        # Projection head
        self.proj_norm = layers.LayerNormalization(epsilon=1e-5, name="proj_ln")
        self.proj_drop = layers.Dropout(self.dropout_rate, name="proj_drop")
        self.embedding_layer = layers.Dense(self.embedding_dim, activation=None, name="eeg_embedding")

    def call(self, inputs: Union[tf.Tensor, Dict[str, tf.Tensor]], training: Optional[bool] = None) -> tf.Tensor:
        # Unpack inputs
        if isinstance(inputs, dict):
            x = inputs.get("eeg")
            adj_override = inputs.get("adjacency", None)
        else:
            x = inputs
            adj_override = None

        if x is None:
            raise ValueError("EEGEncoder.call expects 'eeg' tensor or a tensor input.")

        # Ensure time-major (B, T, C)
        x, _ = _maybe_transpose_to_time_major(x, data_layout=self.data_layout)

        # Spatial graph mixing (if enabled)
        if self.graph_mixer is not None:
            if adj_override is not None:
                A = tf.convert_to_tensor(adj_override, dtype=x.dtype)
                # Runtime shape checks (raise if mismatch)
                tf.debugging.assert_equal(tf.shape(A)[-1], tf.shape(x)[-1], message="Adjacency last dim must match channels.")
                tf.debugging.assert_equal(tf.shape(A)[-2], tf.shape(x)[-1], message="Adjacency first dim must match channels.")
                x = tf.einsum("btc,ck->btk", x, A)
            else:
                x = self.graph_mixer(x)

        # Temporal blocks
        for block in self.tcn_blocks:
            x = block(x, training=training)

        # Return sequence or pooled summary
        if self.return_sequence:
            x = self.proj_norm(x)
            x = self.proj_drop(x, training=training)
            return self.embedding_layer(x)  # (B, T, D)
        else:
            x = self.pool(x)
            x = self.proj_norm(x)
            x = self.proj_drop(x, training=training)
            return self.embedding_layer(x)  # (B, D)

    def get_config(self):
        cfg = super().get_config()
        cfg.update(
            {
                "input_shape": self.input_shape_eeg,
                "temporal_filters": self.temporal_filters,
                "kernel_sizes": self.kernel_sizes,
                "dilations": self.dilations,
                "embedding_dim": self.embedding_dim,
                "dropout": self.dropout_rate,
                "use_graph": self.use_graph,
                "trainable_graph": self.trainable_graph,
                "pooling": self.pooling,
                "return_sequence": self.return_sequence,
                "data_layout": self.data_layout,
                # adjacency omitted for compactness; pass at runtime if needed
            }
        )
        return cfg

    @classmethod
    def from_config(cls, config):
        return cls(**config)


def create_eeg_encoder(config: Dict[str, Any]) -> EEGEncoder:
    """
    Factory function to create EEG encoder from config.

    Expected config structure:
    {
      'cortical_nodes': int,
      'timesteps': int,
      'model': {
        'eeg_encoder': {
          'temporal_filters': [64, 128, 128],
          'kernel_sizes': [7, 5, 3],
          'dilations': [1, 2, 4],
          'embedding_dim': 256,
          'dropout': 0.3,
          'use_graph': false,
          'trainable_graph': false,
          'pooling': 'attn',
          'return_sequence': false,
          'data_layout': 'channels_first'
        }
      }
    }
    """
    eeg_cfg = config.get("model", {}).get("eeg_encoder", {})

    cortical_nodes = int(config.get("cortical_nodes", 68))
    timesteps = int(config.get("timesteps", 1000))  # default aligns with repo usage

    input_shape = (cortical_nodes, timesteps)

    encoder = EEGEncoder(
        input_shape=input_shape,
        temporal_filters=eeg_cfg.get("temporal_filters", [64, 128, 128]),
        kernel_sizes=eeg_cfg.get("kernel_sizes", [7, 5, 3]),
        dilations=eeg_cfg.get("dilations", None),  # defaults to powers of 2
        embedding_dim=eeg_cfg.get("embedding_dim", 256),
        dropout=eeg_cfg.get("dropout", 0.3),
        use_graph=eeg_cfg.get("use_graph", False),
        trainable_graph=eeg_cfg.get("trainable_graph", False),
        pooling=eeg_cfg.get("pooling", "attn"),
        return_sequence=eeg_cfg.get("return_sequence", False),
        data_layout=eeg_cfg.get("data_layout", "channels_first"),
        # adjacency can be provided here or at call-time in inputs dict
    )
    return encoder


# Optional smoke test (safe to keep in a notebook cell; remove if embedding into the repo file)
if __name__ == "__main__":
    encoder = create_eeg_encoder({
        "cortical_nodes": 68,
        "timesteps": 1000,
        "model": {"eeg_encoder": {"use_graph": True, "pooling": "attn"}}
    })
    x = tf.random.normal([2, 68, 1000])  # (B, C, T)
    A = tf.eye(68)
    z = encoder({"eeg": x, "adjacency": A})
    print("Embedding shape:", z.shape)
