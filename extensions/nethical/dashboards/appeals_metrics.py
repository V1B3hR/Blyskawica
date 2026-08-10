"""
Appeals Metrics Collector

Collects and computes appeals processing metrics including volume,
resolution times, and outcome distribution.
"""

from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class Appeal:
    """Record of an appeal"""
    appeal_id: str
    decision_id: str
    filed_at: datetime
    resolved_at: datetime | None
    outcome: str | None  # "upheld", "overturned", "modified", "withdrawn"
    resolution_hours: float | None


class AppealsMetricsCollector:
    """
    Appeals Metrics Collector
    
    Tracks appeals processing metrics for governance dashboard.
    """  # noqa: W293

    def __init__(self):
        """Initialize appeals metrics collector"""
        self._appeals: list[Appeal] = []
        self._max_appeals = 10000

    def record_appeal(
        self,
        appeal_id: str,
        decision_id: str,
        filed_at: datetime | None = None,
    ):
        """
        Record a new appeal.
        
        Args:
            appeal_id: Appeal identifier
            decision_id: Original decision ID
            filed_at: Filing timestamp
        """  # noqa: W293
        appeal = Appeal(
            appeal_id=appeal_id,
            decision_id=decision_id,
            filed_at=filed_at or datetime.utcnow(),
            resolved_at=None,
            outcome=None,
            resolution_hours=None,
        )

        self._appeals.append(appeal)

        if len(self._appeals) > self._max_appeals:
            self._appeals.pop(0)

    def resolve_appeal(
        self,
        appeal_id: str,
        outcome: str,
        resolved_at: datetime | None = None,
    ):
        """
        Mark an appeal as resolved.
        
        Args:
            appeal_id: Appeal identifier
            outcome: Resolution outcome
            resolved_at: Resolution timestamp
        """  # noqa: W293
        for appeal in self._appeals:
            if appeal.appeal_id == appeal_id:
                appeal.resolved_at = resolved_at or datetime.utcnow()
                appeal.outcome = outcome
                appeal.resolution_hours = (
                    (appeal.resolved_at - appeal.filed_at).total_seconds() / 3600
                )
                break

    def get_volume_metrics(self) -> dict[str, Any]:
        """
        Get appeal volume metrics.
        
        Returns:
            Volume statistics
        """  # noqa: W293
        total_appeals = len(self._appeals)
        pending_appeals = sum(1 for a in self._appeals if a.resolved_at is None)
        resolved_appeals = total_appeals - pending_appeals

        # Appeals per day
        if self._appeals:
            oldest = min(a.filed_at for a in self._appeals)
            days = max(1, (datetime.utcnow() - oldest).days)
            appeals_per_day = total_appeals / days
        else:
            appeals_per_day = 0.0

        return {
            "total_appeals": total_appeals,
            "pending_appeals": pending_appeals,
            "resolved_appeals": resolved_appeals,
            "appeals_per_day": appeals_per_day,
        }

    def get_resolution_metrics(self) -> dict[str, Any]:
        """
        Get appeal resolution time metrics.
        
        Returns:
            Resolution time statistics
        """  # noqa: W293
        resolved = [a for a in self._appeals if a.resolution_hours is not None]

        if not resolved:
            return {
                "median_hours": 0.0,
                "p95_hours": 0.0,
                "p99_hours": 0.0,
                "slo_target_hours": 72,
                "slo_compliance_rate": 1.0,
                "sample_size": 0,
            }

        resolution_times = sorted(a.resolution_hours for a in resolved)
        n = len(resolution_times)

        median = resolution_times[n // 2]
        p95 = resolution_times[int(n * 0.95)]
        p99 = resolution_times[int(n * 0.99)]

        # Check SLO compliance (72 hours target)
        slo_target = 72
        within_slo = sum(1 for t in resolution_times if t <= slo_target)
        slo_compliance_rate = within_slo / n

        return {
            "median_hours": median,
            "p95_hours": p95,
            "p99_hours": p99,
            "slo_target_hours": slo_target,
            "slo_compliance_rate": slo_compliance_rate,
            "sample_size": n,
            "status": "healthy" if median <= slo_target else "warning",
        }

    def get_outcome_distribution(self) -> dict[str, Any]:
        """
        Get distribution of appeal outcomes.
        
        Returns:
            Outcome distribution
        """  # noqa: W293
        resolved = [a for a in self._appeals if a.outcome is not None]

        if not resolved:
            return {
                "total": 0,
                "distribution": {},
            }

        outcomes = Counter(a.outcome for a in resolved)
        total = len(resolved)

        distribution = {
            outcome: {
                "count": count,
                "percentage": (count / total) * 100,
            }
            for outcome, count in outcomes.items()
        }

        return {
            "total": total,
            "distribution": distribution,
        }
