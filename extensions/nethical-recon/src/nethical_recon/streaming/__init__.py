"""
Event Streaming Module

Provides event streaming capabilities for real-time monitoring and scalability.
Supports multiple backends: Kafka, NATS, Redis Streams.
"""

from .manager import EventStreamManager
from .events import (
    AssetDiscoveredEvent,
    VulnerabilityFoundEvent,
    AlertGeneratedEvent,
    ScanCompletedEvent,
    AnomalyDetectedEvent,
    CISAAlertReceivedEvent,
)

__all__ = [
    "EventStreamManager",
    "AssetDiscoveredEvent",
    "VulnerabilityFoundEvent",
    "AlertGeneratedEvent",
    "ScanCompletedEvent",
    "AnomalyDetectedEvent",
    "CISAAlertReceivedEvent",
]
