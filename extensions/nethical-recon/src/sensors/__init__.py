"""
Nethical Recon - Sensors Module
Fala 1: Czujniki Ruchu i Wibracji (Motion and Vibration Sensors)
"""

from .auto_tuning import AutoTuningEngine, BaselineProfile
from .base import BaseSensor, SensorStatus
from .correlation_engine import AttackPattern, CorrelationEngine
from .health_monitor import HealthMonitor, HealthStatus, SensorHealthMetrics
from .manager import SensorManager

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
