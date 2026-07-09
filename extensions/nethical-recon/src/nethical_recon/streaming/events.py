"""
Event Definitions

Event schemas for the streaming system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4


class EventType(Enum):
    """Event types."""

    ASSET_DISCOVERED = "asset_discovered"
    VULNERABILITY_FOUND = "vulnerability_found"
    ALERT_GENERATED = "alert_generated"
    SCAN_COMPLETED = "scan_completed"
    ANOMALY_DETECTED = "anomaly_detected"
    CISA_ALERT_RECEIVED = "cisa_alert_received"


@dataclass
class BaseEvent:
    """Base event class."""

    event_id: UUID = field(default_factory=uuid4)
    event_type: EventType = EventType.ASSET_DISCOVERED
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source: str = "nethical-recon"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AssetDiscoveredEvent(BaseEvent):
    """Asset discovered event."""

    asset_id: str = ""
    asset_type: str = ""
    ip_address: str = ""
    hostname: str = ""
    ports: list[int] = field(default_factory=list)

    def __post_init__(self):
        self.event_type = EventType.ASSET_DISCOVERED


@dataclass
class VulnerabilityFoundEvent(BaseEvent):
    """Vulnerability found event."""

    vulnerability_id: str = ""
    cve_id: str = ""
    asset_id: str = ""
    severity: str = ""
    is_kev: bool = False
    risk_score: float = 0.0

    def __post_init__(self):
        self.event_type = EventType.VULNERABILITY_FOUND


@dataclass
class AlertGeneratedEvent(BaseEvent):
    """Alert generated event."""

    alert_id: str = ""
    alert_type: str = ""
    severity: str = ""
    title: str = ""
    message: str = ""

    def __post_init__(self):
        self.event_type = EventType.ALERT_GENERATED


@dataclass
class ScanCompletedEvent(BaseEvent):
    """Scan completed event."""

    scan_id: str = ""
    scan_type: str = ""
    target: str = ""
    assets_found: int = 0
    vulnerabilities_found: int = 0
    duration_seconds: float = 0.0

    def __post_init__(self):
        self.event_type = EventType.SCAN_COMPLETED


@dataclass
class AnomalyDetectedEvent(BaseEvent):
    """Anomaly detected event."""

    anomaly_id: str = ""
    anomaly_type: str = ""
    asset_id: str = ""
    confidence: float = 0.0
    description: str = ""

    def __post_init__(self):
        self.event_type = EventType.ANOMALY_DETECTED


@dataclass
class CISAAlertReceivedEvent(BaseEvent):
    """CISA alert received event."""

    alert_id: str = ""
    alert_type: str = ""
    severity: str = ""
    is_shields_up: bool = False
    cve_ids: list[str] = field(default_factory=list)

    def __post_init__(self):
        self.event_type = EventType.CISA_ALERT_RECEIVED
