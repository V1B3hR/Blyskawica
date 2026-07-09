"""
Nethical Recon - Sensors Module
Fala 1: Czujniki Ruchu i Wibracji (Motion and Vibration Sensors)
"""

from .base import BaseSensor, SensorStatus
from .manager import SensorManager
from .correlation_engine import CorrelationEngine, AttackPattern
from .auto_tuning import AutoTuningEngine, BaselineProfile
from .health_monitor import HealthMonitor, HealthStatus, SensorHealthMetrics

__all__ = [
    "BaseSensor",
    "SensorStatus",
    "SensorManager",
    "CorrelationEngine",
    "AttackPattern",
    "AutoTuningEngine",
    "BaselineProfile",
    "HealthMonitor",
    "HealthStatus",
    "SensorHealthMetrics",
]
