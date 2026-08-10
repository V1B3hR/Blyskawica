"""
Register custom layers from models package with the layer registry.

This module registers all custom model components to make them available
for config-driven model construction.
"""

from adaptiveneuralnetwork.central_nervous_system.layer_registry import layer_registry
from adaptiveneuralnetwork.models.video_models import (
    Conv3D,
    ConvLSTM,
    ConvLSTMCell,
    HybridVideoModel,
    PositionalEncoding,
    VideoTransformer,
)


def register_video_layers():
    """Register video model layers with the global layer registry."""

    # Register ConvLSTM components
    layer_registry.register('convlstm_cell', ConvLSTMCell)
    layer_registry.register('convlstm', ConvLSTM)

    # Register 3D CNN
    layer_registry.register('conv3d_model', Conv3D)

    # Register Transformer components
    layer_registry.register('positional_encoding', PositionalEncoding)
    layer_registry.register('video_transformer', VideoTransformer)

    # Register Hybrid model
    layer_registry.register('hybrid_video', HybridVideoModel)


def register_adaptive_layers():
    """Register adaptive neural network layers with the global layer registry."""

    try:
        from adaptiveneuralnetwork.central_nervous_system.dynamics import (
            AdaptiveDynamics,  # noqa: F401
        )
        from adaptiveneuralnetwork.central_nervous_system.nodes import NodeState  # noqa: F401
        from adaptiveneuralnetwork.central_nervous_system.phases import PhaseScheduler  # noqa: F401

        # Note: These aren't typical nn.Module layers but can be wrapped if needed
        # For now, we'll skip auto-registration since they require specific initialization
        pass
    except ImportError:
        pass


def register_all_custom_layers():
    """Register all custom layers from the models package."""
    register_video_layers()
    register_adaptive_layers()


# Auto-register on import
register_all_custom_layers()
