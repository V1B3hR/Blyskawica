"""
Adaptive Neural Network - Biologically inspired neural network with adaptive learning
"""


__version__ = "0.1.0"

try:
    from .api.config import AdaptiveConfig
    from .api.model import AdaptiveModel
    _API_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    AdaptiveConfig = None
    AdaptiveModel = None
    _API_AVAILABLE = False

try:
    from .config import AdaptiveNeuralNetworkConfig, load_config
except (ImportError, ModuleNotFoundError):
    AdaptiveNeuralNetworkConfig = None
    load_config = None

# Optional AutoML components
try:
    from .automl import AdaptiveAutoMLEngine, AutoMLConfig, create_automl_engine
    _AUTOML_AVAILABLE = True
except ImportError:
    _AUTOML_AVAILABLE = False

# Base exports
__all__ = [
    "AdaptiveModel",
    "AdaptiveConfig",
    "AdaptiveNeuralNetworkConfig",
    "load_config",
]

# Add AutoML exports if available
if _AUTOML_AVAILABLE:
    __all__.extend([
        "AdaptiveAutoMLEngine",
        "AutoMLConfig",
        "create_automl_engine"
    ])
