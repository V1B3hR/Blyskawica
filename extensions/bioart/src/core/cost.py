"""
Cost tracking and budget management for Bioart operations.

Implements M2 requirement: "Instrument cost/time per iteration; budgets; anomaly alerts"
"""

import time
import threading
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone

from . import get_logger, get_config


logger = get_logger("cost")


@dataclass
class OperationCost:
    """Cost information for a single operation."""
    operation_name: str
    start_time: float
    end_time: float
    duration_seconds: float
    cost_units: float  # Abstract cost units
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def duration_ms(self) -> float:
        """Duration in milliseconds."""
        return self.duration_seconds * 1000


@dataclass
class CostBudget:
    """Budget configuration for cost tracking."""
    name: str
    max_cost: float
    warning_threshold_percent: float = 80.0
    critical_threshold_percent: float = 95.0


class CostTracker:
    """
    Tracks operation costs and enforces budgets.

    Features:
    - Per-operation cost tracking
    - Budget enforcement with alerts
    - Aggregated statistics
    - Thread-safe operations
    """

    def __init__(self):
        """Initialize cost tracker."""
        self._operations: List[OperationCost] = []
        self._lock = threading.RLock()
        self._budgets: Dict[str, CostBudget] = {}
        self._alert_callbacks: List[Callable[[str, CostBudget, float, float], None]] = []

    def track_operation(
        self,
        operation_name: str,
        duration_seconds: float,
        cost_units: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> OperationCost:
        """
        Track a completed operation.

        Args:
            operation_name: Name of the operation
            duration_seconds: Duration in seconds
            cost_units: Cost in abstract units
            metadata: Additional metadata

        Returns:
            OperationCost record
        """
        now = time.time()
        operation = OperationCost(
            operation_name=operation_name,
            start_time=now - duration_seconds,
            end_time=now,
            duration_seconds=duration_seconds,
            cost_units=cost_units,
            metadata=metadata or {}
        )

        with self._lock:
            self._operations.append(operation)

        logger.debug(
            f"Tracked operation: {operation_name}",
            duration_ms=operation.duration_ms,
            cost_units=cost_units,
            **metadata or {}
        )

        return operation

    def set_budget(self, budget: CostBudget) -> None:
        """
        Set a cost budget.

        Args:
            budget: Budget configuration
        """
        with self._lock:
            self._budgets[budget.name] = budget
        logger.info(f"Set budget: {budget.name}", max_cost=budget.max_cost)

    def get_total_cost(self, operation_filter: Optional[str] = None) -> float:
        """
        Get total cost across all or filtered operations.

        Args:
            operation_filter: Filter by operation name prefix (uses startswith match)

        Returns:
            Total cost in units
        """
        with self._lock:
            if operation_filter:
                return sum(
                    op.cost_units
                    for op in self._operations
                    if op.operation_name.startswith(operation_filter)
                )
            return sum(op.cost_units for op in self._operations)

    def get_operation_count(self, operation_filter: Optional[str] = None) -> int:
        """
        Get count of tracked operations.

        Args:
            operation_filter: Filter by operation name prefix (uses startswith match)

        Returns:
            Operation count
        """
        with self._lock:
            if operation_filter:
                return sum(
                    1 for op in self._operations
                    if op.operation_name.startswith(operation_filter)
                )
            return len(self._operations)

    def get_cost_per_100_jobs(self, operation_filter: Optional[str] = None) -> float:
        """
        Calculate cost per 100 jobs.

        Args:
            operation_filter: Filter by operation name prefix (uses startswith match)

        Returns:
            Cost per 100 jobs
        """
        count = self.get_operation_count(operation_filter)
        if count == 0:
            return 0.0

        total_cost = self.get_total_cost(operation_filter)
        return (total_cost / count) * 100

    def check_budget(self, budget_name: str) -> Dict[str, Any]:
        """
        Check budget status and generate alerts if needed.

        Args:
            budget_name: Name of budget to check

        Returns:
            Dictionary with budget status
        """
        with self._lock:
            if budget_name not in self._budgets:
                raise ValueError(f"Budget not found: {budget_name}")

            budget = self._budgets[budget_name]
            current_cost = self.get_total_cost()
            percent_used = (current_cost / budget.max_cost * 100) if budget.max_cost > 0 else 0

            status = {
                "budget_name": budget_name,
                "max_cost": budget.max_cost,
                "current_cost": current_cost,
                "percent_used": percent_used,
                "remaining": budget.max_cost - current_cost,
                "status": "ok"
            }

            # Check thresholds
            if percent_used >= budget.critical_threshold_percent:
                status["status"] = "critical"
                self._fire_alert("critical", budget, current_cost, percent_used)
            elif percent_used >= budget.warning_threshold_percent:
                status["status"] = "warning"
                self._fire_alert("warning", budget, current_cost, percent_used)

            return status

    def _fire_alert(
        self,
        alert_level: str,
        budget: CostBudget,
        current_cost: float,
        percent_used: float
    ) -> None:
        """Fire budget alert."""
        logger.warning(
            f"Budget {alert_level}: {budget.name}",
            budget_name=budget.name,
            max_cost=budget.max_cost,
            current_cost=current_cost,
            percent_used=percent_used,
            alert_level=alert_level
        )

        # Call registered callbacks
        for callback in self._alert_callbacks:
            try:
                callback(alert_level, budget, current_cost, percent_used)
            except Exception as e:
                logger.error(f"Alert callback failed: {e}")

    def register_alert_callback(
        self,
        callback: Callable[[str, CostBudget, float, float], None]
    ) -> None:
        """
        Register callback for budget alerts.

        Args:
            callback: Function with signature (level: str, budget: CostBudget,
                     current_cost: float, percent_used: float) -> None
        """
        self._alert_callbacks.append(callback)

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get aggregated cost statistics.

        Returns:
            Dictionary with statistics
        """
        with self._lock:
            if not self._operations:
                return {
                    "total_operations": 0,
                    "total_cost": 0.0,
                    "total_duration_seconds": 0.0,
                }

            total_cost = sum(op.cost_units for op in self._operations)
            total_duration = sum(op.duration_seconds for op in self._operations)
            avg_cost = total_cost / len(self._operations)
            avg_duration = total_duration / len(self._operations)

            # Group by operation name
            by_operation: Dict[str, Dict[str, Any]] = {}
            for op in self._operations:
                if op.operation_name not in by_operation:
                    by_operation[op.operation_name] = {
                        "count": 0,
                        "total_cost": 0.0,
                        "total_duration": 0.0,
                    }

                stats = by_operation[op.operation_name]
                stats["count"] += 1
                stats["total_cost"] += op.cost_units
                stats["total_duration"] += op.duration_seconds

            # Calculate averages per operation
            for name, stats in by_operation.items():
                stats["avg_cost"] = stats["total_cost"] / stats["count"]
                stats["avg_duration"] = stats["total_duration"] / stats["count"]

            return {
                "total_operations": len(self._operations),
                "total_cost": total_cost,
                "total_duration_seconds": total_duration,
                "average_cost": avg_cost,
                "average_duration_seconds": avg_duration,
                "cost_per_100_jobs": self.get_cost_per_100_jobs(),
                "by_operation": by_operation,
            }

    def get_report(self) -> str:
        """
        Get formatted cost report.

        Returns:
            Formatted report string
        """
        stats = self.get_statistics()

        report = ["=" * 80]
        report.append("COST TRACKING REPORT")
        report.append("=" * 80)
        report.append(f"Total Operations: {stats['total_operations']}")
        report.append(f"Total Cost: {stats['total_cost']:.2f} units")
        report.append(f"Total Duration: {stats['total_duration_seconds']:.2f} seconds")
        report.append(f"Average Cost: {stats['average_cost']:.4f} units/operation")
        report.append(f"Cost per 100 Jobs: {stats['cost_per_100_jobs']:.2f} units")
        report.append("-" * 80)

        if stats["by_operation"]:
            report.append("BY OPERATION:")
            for name, op_stats in stats["by_operation"].items():
                report.append(f"  {name}:")
                report.append(f"    Count: {op_stats['count']}")
                report.append(f"    Total Cost: {op_stats['total_cost']:.2f} units")
                report.append(f"    Avg Cost: {op_stats['avg_cost']:.4f} units")
                report.append(f"    Avg Duration: {op_stats['avg_duration']:.4f} seconds")

        report.append("=" * 80)

        # Check budgets
        with self._lock:
            if self._budgets:
                report.append("\nBUDGET STATUS:")
                for budget_name in self._budgets:
                    status = self.check_budget(budget_name)
                    report.append(f"  {budget_name}:")
                    report.append(f"    Max: {status['max_cost']:.2f} units")
                    report.append(f"    Current: {status['current_cost']:.2f} units")
                    report.append(f"    Used: {status['percent_used']:.1f}%")
                    report.append(f"    Remaining: {status['remaining']:.2f} units")
                    report.append(f"    Status: {status['status'].upper()}")

        return "\n".join(report)

    def clear(self) -> None:
        """Clear all tracked operations."""
        with self._lock:
            self._operations.clear()
        logger.info("Cost tracker cleared")


# Global cost tracker
_global_tracker: Optional[CostTracker] = None


def get_cost_tracker() -> CostTracker:
    """
    Get global cost tracker instance.

    Returns:
        CostTracker instance
    """
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = CostTracker()

        # Set up budget from config
        config = get_config()
        if config.cost.cost_per_100_jobs_budget is not None:
            budget = CostBudget(
                name="default",
                max_cost=config.cost.cost_per_100_jobs_budget,
                warning_threshold_percent=config.cost.alert_threshold_percent,
            )
            _global_tracker.set_budget(budget)

    return _global_tracker
