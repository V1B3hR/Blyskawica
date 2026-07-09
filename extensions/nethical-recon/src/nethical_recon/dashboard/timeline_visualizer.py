"""
Timeline Visualizer - Recon activity timeline

Creates timeline data structures for visualizing reconnaissance activities
over time, including scans, findings, and events.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID


class EventType(str, Enum):
    """Types of timeline events"""

    SCAN_STARTED = "scan_started"
    SCAN_COMPLETED = "scan_completed"
    SCAN_FAILED = "scan_failed"
    FINDING_CREATED = "finding_created"
    FINDING_UPDATED = "finding_updated"
    ALERT_TRIGGERED = "alert_triggered"
    TARGET_ADDED = "target_added"
    PLAYBOOK_EXECUTED = "playbook_executed"


class SeverityLevel(str, Enum):
    """Severity levels for timeline events"""

    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class TimelineEvent:
    """Single event in timeline"""

    id: str
    timestamp: datetime
    event_type: EventType
    title: str
    description: Optional[str] = None
    severity: SeverityLevel = SeverityLevel.INFO
    metadata: Dict[str, Any] = field(default_factory=dict)
    duration: Optional[timedelta] = None  # For events with duration

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "event_type": self.event_type.value,
            "title": self.title,
            "description": self.description,
            "severity": self.severity.value,
            "metadata": self.metadata,
            "duration": self.duration.total_seconds() if self.duration else None,
        }


class TimelineVisualizer:
    """
    Timeline visualizer for reconnaissance activities.

    Creates timeline data for various visualization formats:
    - Linear timeline (chronological events)
    - Gantt chart (overlapping activities)
    - Event stream (real-time updates)
    """

    def __init__(self):
        self.events: List[TimelineEvent] = []

    def add_event(self, event: TimelineEvent):
        """Add event to timeline"""
        self.events.append(event)

    def add_scan_event(
        self,
        scan_id: UUID,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        status: str = "completed",
        target: Optional[str] = None,
    ):
        """Add scan event to timeline"""
        event_type = EventType.SCAN_COMPLETED if status == "completed" else EventType.SCAN_FAILED
        severity = SeverityLevel.SUCCESS if status == "completed" else SeverityLevel.ERROR

        duration = None
        if end_time:
            duration = end_time - start_time

        event = TimelineEvent(
            id=f"scan-{scan_id}",
            timestamp=start_time,
            event_type=event_type,
            title=f"Scan {status}: {target or scan_id}",
            description=f"Scan job {scan_id} {status}",
            severity=severity,
            duration=duration,
            metadata={"scan_id": str(scan_id), "status": status, "target": target},
        )
        self.add_event(event)

    def add_finding_event(
        self,
        finding_id: UUID,
        timestamp: datetime,
        title: str,
        severity: str,
        target: Optional[str] = None,
    ):
        """Add finding event to timeline"""
        severity_map = {
            "critical": SeverityLevel.CRITICAL,
            "high": SeverityLevel.ERROR,
            "medium": SeverityLevel.WARNING,
            "low": SeverityLevel.INFO,
            "info": SeverityLevel.INFO,
        }

        event = TimelineEvent(
            id=f"finding-{finding_id}",
            timestamp=timestamp,
            event_type=EventType.FINDING_CREATED,
            title=title,
            description=f"Finding discovered: {title}",
            severity=severity_map.get(severity.lower(), SeverityLevel.INFO),
            metadata={"finding_id": str(finding_id), "severity": severity, "target": target},
        )
        self.add_event(event)

    def add_alert_event(
        self,
        alert_id: str,
        timestamp: datetime,
        message: str,
        severity: str = "warning",
    ):
        """Add alert event to timeline"""
        severity_map = {
            "critical": SeverityLevel.CRITICAL,
            "high": SeverityLevel.ERROR,
            "medium": SeverityLevel.WARNING,
            "low": SeverityLevel.INFO,
        }

        event = TimelineEvent(
            id=f"alert-{alert_id}",
            timestamp=timestamp,
            event_type=EventType.ALERT_TRIGGERED,
            title=f"Alert: {message}",
            description=message,
            severity=severity_map.get(severity.lower(), SeverityLevel.WARNING),
            metadata={"alert_id": alert_id, "severity": severity},
        )
        self.add_event(event)

    def add_playbook_event(
        self,
        playbook_id: str,
        timestamp: datetime,
        playbook_name: str,
        status: str = "success",
    ):
        """Add playbook execution event"""
        severity = SeverityLevel.SUCCESS if status == "success" else SeverityLevel.ERROR

        event = TimelineEvent(
            id=f"playbook-{playbook_id}",
            timestamp=timestamp,
            event_type=EventType.PLAYBOOK_EXECUTED,
            title=f"Playbook: {playbook_name}",
            description=f"Executed playbook: {playbook_name}",
            severity=severity,
            metadata={"playbook_id": playbook_id, "playbook_name": playbook_name, "status": status},
        )
        self.add_event(event)

    def get_events(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        event_types: Optional[List[EventType]] = None,
        severity_levels: Optional[List[SeverityLevel]] = None,
        limit: Optional[int] = None,
    ) -> List[TimelineEvent]:
        """
        Get filtered and sorted events.

        Args:
            start_date: Filter events after this date
            end_date: Filter events before this date
            event_types: Filter by event types
            severity_levels: Filter by severity levels
            limit: Maximum number of events to return

        Returns:
            Sorted list of timeline events
        """
        filtered = self.events

        # Apply filters
        if start_date:
            filtered = [e for e in filtered if e.timestamp >= start_date]

        if end_date:
            filtered = [e for e in filtered if e.timestamp <= end_date]

        if event_types:
            filtered = [e for e in filtered if e.event_type in event_types]

        if severity_levels:
            filtered = [e for e in filtered if e.severity in severity_levels]

        # Sort by timestamp (most recent first)
        filtered.sort(key=lambda e: e.timestamp, reverse=True)

        # Apply limit
        if limit:
            filtered = filtered[:limit]

        return filtered

    def to_linear_format(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Export timeline in linear format for sequential visualization.

        Returns:
            List of event dictionaries sorted by time
        """
        events = self.get_events(start_date=start_date, end_date=end_date, limit=limit)
        return [event.to_dict() for event in events]

    def to_gantt_format(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """
        Export timeline in Gantt chart format for duration-based visualization.

        Only includes events with duration (e.g., scans).

        Returns:
            List of tasks with start and end times
        """
        events = self.get_events(start_date=start_date, end_date=end_date)

        gantt_items = []
        for event in events:
            if event.duration:
                gantt_items.append(
                    {
                        "id": event.id,
                        "name": event.title,
                        "start": event.timestamp.isoformat(),
                        "end": (event.timestamp + event.duration).isoformat(),
                        "type": event.event_type.value,
                        "severity": event.severity.value,
                        **event.metadata,
                    }
                )

        return gantt_items

    def get_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get timeline statistics"""
        events = self.get_events(start_date=start_date, end_date=end_date)

        event_counts = {}
        for event_type in EventType:
            count = sum(1 for e in events if e.event_type == event_type)
            event_counts[event_type.value] = count

        severity_counts = {}
        for severity in SeverityLevel:
            count = sum(1 for e in events if e.severity == severity)
            severity_counts[severity.value] = count

        return {
            "total_events": len(events),
            "event_types": event_counts,
            "severity_levels": severity_counts,
            "time_range": {
                "start": min(e.timestamp for e in events).isoformat() if events else None,
                "end": max(e.timestamp for e in events).isoformat() if events else None,
            },
        }

    def clear(self):
        """Clear all events"""
        self.events.clear()
