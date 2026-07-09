"""
Live Monitor - Real-time monitoring of assets, findings, jobs, and alerts

Provides live updates through WebSocket connections for dashboard real-time monitoring.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
from uuid import UUID


class MonitorEventType(str, Enum):
    """Types of monitor events"""

    ASSET_DISCOVERED = "asset_discovered"
    ASSET_UPDATED = "asset_updated"
    FINDING_CREATED = "finding_created"
    FINDING_UPDATED = "finding_updated"
    JOB_STARTED = "job_started"
    JOB_COMPLETED = "job_completed"
    JOB_FAILED = "job_failed"
    ALERT_TRIGGERED = "alert_triggered"
    METRIC_UPDATED = "metric_updated"


@dataclass
class MonitorEvent:
    """Event for live monitoring"""

    event_type: MonitorEventType
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for WebSocket transmission"""
        return {
            "type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
        }


@dataclass
class LiveMetrics:
    """Current system metrics"""

    total_assets: int = 0
    active_scans: int = 0
    recent_findings: int = 0
    open_alerts: int = 0
    critical_findings: int = 0
    high_findings: int = 0
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "total_assets": self.total_assets,
            "active_scans": self.active_scans,
            "recent_findings": self.recent_findings,
            "open_alerts": self.open_alerts,
            "critical_findings": self.critical_findings,
            "high_findings": self.high_findings,
            "last_updated": self.last_updated.isoformat(),
        }


class LiveMonitor:
    """
    Live monitor for real-time dashboard updates.

    Manages event subscriptions and broadcasts updates to connected clients
    via WebSocket or SSE (Server-Sent Events).
    """

    def __init__(self):
        self.subscribers: Set[Callable] = set()
        self.metrics = LiveMetrics()
        self._event_queue: asyncio.Queue = asyncio.Queue()
        self._running = False

    def subscribe(self, callback: Callable[[MonitorEvent], None]):
        """
        Subscribe to live events.

        Args:
            callback: Function to call when events occur
        """
        self.subscribers.add(callback)

    def unsubscribe(self, callback: Callable[[MonitorEvent], None]):
        """Unsubscribe from live events"""
        self.subscribers.discard(callback)

    async def emit_event(self, event: MonitorEvent):
        """
        Emit event to all subscribers.

        Args:
            event: Event to broadcast
        """
        await self._event_queue.put(event)

    async def emit_asset_discovered(self, asset_id: UUID, asset_type: str, value: str):
        """Emit asset discovered event"""
        event = MonitorEvent(
            event_type=MonitorEventType.ASSET_DISCOVERED,
            data={"asset_id": str(asset_id), "asset_type": asset_type, "value": value},
        )
        await self.emit_event(event)
        self.metrics.total_assets += 1

    async def emit_finding_created(
        self,
        finding_id: UUID,
        title: str,
        severity: str,
        target_id: UUID,
    ):
        """Emit finding created event"""
        event = MonitorEvent(
            event_type=MonitorEventType.FINDING_CREATED,
            data={
                "finding_id": str(finding_id),
                "title": title,
                "severity": severity,
                "target_id": str(target_id),
            },
        )
        await self.emit_event(event)
        self.metrics.recent_findings += 1

        if severity == "critical":
            self.metrics.critical_findings += 1
        elif severity == "high":
            self.metrics.high_findings += 1

    async def emit_job_started(self, job_id: UUID, target_id: UUID):
        """Emit job started event"""
        event = MonitorEvent(
            event_type=MonitorEventType.JOB_STARTED,
            data={"job_id": str(job_id), "target_id": str(target_id)},
        )
        await self.emit_event(event)
        self.metrics.active_scans += 1

    async def emit_job_completed(self, job_id: UUID, status: str, findings_count: int):
        """Emit job completed event"""
        event_type = MonitorEventType.JOB_COMPLETED if status == "completed" else MonitorEventType.JOB_FAILED

        event = MonitorEvent(
            event_type=event_type,
            data={"job_id": str(job_id), "status": status, "findings_count": findings_count},
        )
        await self.emit_event(event)
        self.metrics.active_scans = max(0, self.metrics.active_scans - 1)

    async def emit_alert(self, alert_id: str, message: str, severity: str):
        """Emit alert triggered event"""
        event = MonitorEvent(
            event_type=MonitorEventType.ALERT_TRIGGERED,
            data={"alert_id": alert_id, "message": message, "severity": severity},
        )
        await self.emit_event(event)
        self.metrics.open_alerts += 1

    async def update_metrics(self, **kwargs):
        """Update metrics and emit update event"""
        for key, value in kwargs.items():
            if hasattr(self.metrics, key):
                setattr(self.metrics, key, value)

        self.metrics.last_updated = datetime.now(timezone.utc)

        event = MonitorEvent(
            event_type=MonitorEventType.METRIC_UPDATED,
            data=self.metrics.to_dict(),
        )
        await self.emit_event(event)

    def get_metrics(self) -> LiveMetrics:
        """Get current metrics snapshot"""
        return self.metrics

    async def _process_events(self):
        """Process events from queue and notify subscribers"""
        while self._running:
            try:
                event = await asyncio.wait_for(self._event_queue.get(), timeout=1.0)

                # Notify all subscribers
                for callback in self.subscribers:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(event)
                        else:
                            callback(event)
                    except Exception as e:
                        # Log error but don't stop processing
                        print(f"Error in subscriber callback: {e}")

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"Error processing event: {e}")

    async def start(self):
        """Start live monitoring"""
        if self._running:
            return

        self._running = True
        asyncio.create_task(self._process_events())

    async def stop(self):
        """Stop live monitoring"""
        self._running = False

    def get_event_stream(self) -> asyncio.Queue:
        """
        Get event stream queue for Server-Sent Events (SSE).

        Returns:
            Queue that receives all events
        """
        return self._event_queue


# Global live monitor instance
_live_monitor: Optional[LiveMonitor] = None


def get_live_monitor() -> LiveMonitor:
    """Get or create global live monitor instance"""
    global _live_monitor
    if _live_monitor is None:
        _live_monitor = LiveMonitor()
    return _live_monitor
