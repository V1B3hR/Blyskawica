"""Attack surface visualization module.

This module provides graph-based visualization of attack surfaces,
including dependency mapping, change tracking, and exposed asset detection.
"""

from .delta_monitor import ChangeType, DeltaMonitor, SurfaceChange
from .exposed_assets import ExposedAssetDetector, ExposureLevel
from .graph_builder import AttackSurfaceGraph, GraphBuilder, NodeType

__all__ = [
    "AttackSurfaceGraph",
    "GraphBuilder",
    "NodeType",
    "DeltaMonitor",
    "ChangeType",
    "SurfaceChange",
    "ExposedAssetDetector",
    "ExposureLevel",
]
