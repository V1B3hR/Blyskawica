"""
Event Streaming Module

Provides event streaming capabilities for real-time monitoring and scalability.
Supports multiple backends: Kafka, NATS, Redis Streams.
"""

from .events import (
    AlertGeneratedEvent,
    AnomalyDetectedEvent,
    AssetDiscoveredEvent,
    CISAAlertReceivedEvent,
    ScanCompletedEvent,
    VulnerabilityFoundEvent,
)
from .manager import EventStreamManager

__all__ = [
    "EventStreamManager",
    "AssetDiscoveredEvent",
    "VulnerabilityFoundEvent",
    "AlertGeneratedEvent",
    "ScanCompletedEvent",
    "AnomalyDetectedEvent",
    "CISAAlertReceivedEvent",
]
