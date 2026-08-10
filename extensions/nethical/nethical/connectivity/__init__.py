"""
Connectivity Module

Provides satellite and network connectivity systems for Nethical,
including integration with LEO constellations, traditional satellite
networks, GPS/GNSS positioning, and automatic failover.
"""

from .satellite import (
    ConnectionConfig,
    ConnectionMetrics,
    ConnectionState,
    ConnectionType,
    FailoverConfig,
    FailoverEvent,
    # Failover
    FailoverManager,
    Geofence,
    GeofenceType,
    GNSSConstellation,
    # GPS/GNSS
    GPSTracker,
    IridiumProvider,
    KuiperProvider,
    # Latency
    LatencyOptimizer,
    LatencyProfile,
    OneWebProvider,
    Position,
    RequestPriority,
    SatelliteConnectionError,
    # Metrics
    SatelliteMetrics,
    # Base classes
    SatelliteProvider,
    SatelliteTimeoutError,
    SignalQuality,
    # Providers
    StarlinkProvider,
)

__all__ = [
    # Base classes
    "SatelliteProvider",
    "ConnectionState",
    "ConnectionConfig",
    "SatelliteConnectionError",
    "SatelliteTimeoutError",
    # Providers
    "StarlinkProvider",
    "KuiperProvider",
    "OneWebProvider",
    "IridiumProvider",
    # GPS/GNSS
    "GPSTracker",
    "GNSSConstellation",
    "Position",
    "Geofence",
    "GeofenceType",
    # Failover
    "FailoverManager",
    "FailoverConfig",
    "ConnectionType",
    "FailoverEvent",
    # Latency
    "LatencyOptimizer",
    "LatencyProfile",
    "RequestPriority",
    # Metrics
    "SatelliteMetrics",
    "SignalQuality",
    "ConnectionMetrics",
]
