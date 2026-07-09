"""
Tests for cost tracking module.

Tests cost tracking, budgets, alerts, and statistics.
"""

import pytest
from src.core.cost import (
    CostTracker,
    CostBudget,
    OperationCost,
    get_cost_tracker,
)


def test_track_operation():
    """Test tracking a single operation."""
    tracker = CostTracker()
    
    op = tracker.track_operation(
        operation_name="encode",
        duration_seconds=0.5,
        cost_units=10.0,
        metadata={"bytes": 1024}
    )
    
    assert op.operation_name == "encode"
    assert op.duration_seconds == 0.5
    assert op.cost_units == 10.0
    assert op.metadata["bytes"] == 1024


def test_get_total_cost():
    """Test getting total cost."""
    tracker = CostTracker()
    
    tracker.track_operation("encode", 0.1, 5.0)
    tracker.track_operation("decode", 0.1, 3.0)
    tracker.track_operation("encode", 0.1, 7.0)
    
    total = tracker.get_total_cost()
    assert total == 15.0
    
    # Filter by operation
    encode_cost = tracker.get_total_cost("encode")
    assert encode_cost == 12.0


def test_get_operation_count():
    """Test getting operation count."""
    tracker = CostTracker()
    
    tracker.track_operation("encode", 0.1, 5.0)
    tracker.track_operation("decode", 0.1, 3.0)
    tracker.track_operation("encode", 0.1, 7.0)
    
    total_count = tracker.get_operation_count()
    assert total_count == 3
    
    encode_count = tracker.get_operation_count("encode")
    assert encode_count == 2


def test_cost_per_100_jobs():
    """Test cost per 100 jobs calculation."""
    tracker = CostTracker()
    
    # Add 10 operations with 1.0 cost each
    for i in range(10):
        tracker.track_operation("encode", 0.1, 1.0)
    
    cost_per_100 = tracker.get_cost_per_100_jobs()
    # Total cost: 10, Total operations: 10
    # Average cost per operation: 10/10 = 1.0
    # Cost per 100: 1.0 * 100 = 100.0
    assert cost_per_100 == 100.0


def test_set_budget():
    """Test setting a budget."""
    tracker = CostTracker()
    
    budget = CostBudget(
        name="test_budget",
        max_cost=100.0,
        warning_threshold_percent=80.0
    )
    
    tracker.set_budget(budget)
    
    # Should not raise
    status = tracker.check_budget("test_budget")
    assert status["budget_name"] == "test_budget"
    assert status["max_cost"] == 100.0


def test_budget_check_ok():
    """Test budget check with OK status."""
    tracker = CostTracker()
    
    budget = CostBudget(name="test", max_cost=100.0)
    tracker.set_budget(budget)
    
    # Add operations below threshold
    tracker.track_operation("test", 0.1, 50.0)
    
    status = tracker.check_budget("test")
    assert status["status"] == "ok"
    assert status["percent_used"] == 50.0
    assert status["remaining"] == 50.0


def test_budget_check_warning():
    """Test budget check with warning status."""
    tracker = CostTracker()
    
    budget = CostBudget(
        name="test",
        max_cost=100.0,
        warning_threshold_percent=80.0
    )
    tracker.set_budget(budget)
    
    # Add operations to trigger warning
    tracker.track_operation("test", 0.1, 85.0)
    
    status = tracker.check_budget("test")
    assert status["status"] == "warning"
    assert status["percent_used"] == 85.0


def test_budget_check_critical():
    """Test budget check with critical status."""
    tracker = CostTracker()
    
    budget = CostBudget(
        name="test",
        max_cost=100.0,
        critical_threshold_percent=95.0
    )
    tracker.set_budget(budget)
    
    # Add operations to trigger critical
    tracker.track_operation("test", 0.1, 98.0)
    
    status = tracker.check_budget("test")
    assert status["status"] == "critical"
    assert status["percent_used"] == 98.0


def test_budget_alerts():
    """Test budget alert callbacks."""
    tracker = CostTracker()
    
    alerts = []
    
    def alert_callback(level, budget, current_cost, percent_used):
        alerts.append({
            "level": level,
            "budget_name": budget.name,
            "current_cost": current_cost,
            "percent_used": percent_used,
        })
    
    tracker.register_alert_callback(alert_callback)
    
    budget = CostBudget(
        name="test",
        max_cost=100.0,
        warning_threshold_percent=80.0
    )
    tracker.set_budget(budget)
    
    # Trigger warning
    tracker.track_operation("test", 0.1, 85.0)
    tracker.check_budget("test")
    
    assert len(alerts) == 1
    assert alerts[0]["level"] == "warning"
    assert alerts[0]["percent_used"] == 85.0


def test_get_statistics():
    """Test getting cost statistics."""
    tracker = CostTracker()
    
    tracker.track_operation("encode", 0.5, 10.0)
    tracker.track_operation("encode", 0.3, 8.0)
    tracker.track_operation("decode", 0.2, 5.0)
    
    stats = tracker.get_statistics()
    
    assert stats["total_operations"] == 3
    assert stats["total_cost"] == 23.0
    assert stats["average_cost"] == 23.0 / 3
    
    # Check by-operation stats
    assert "encode" in stats["by_operation"]
    assert "decode" in stats["by_operation"]
    
    encode_stats = stats["by_operation"]["encode"]
    assert encode_stats["count"] == 2
    assert encode_stats["total_cost"] == 18.0
    assert encode_stats["avg_cost"] == 9.0


def test_get_report():
    """Test formatted cost report."""
    tracker = CostTracker()
    
    tracker.track_operation("encode", 0.5, 10.0)
    tracker.track_operation("decode", 0.2, 5.0)
    
    report = tracker.get_report()
    
    assert "COST TRACKING REPORT" in report
    assert "Total Operations: 2" in report
    assert "encode" in report
    assert "decode" in report


def test_clear_operations():
    """Test clearing tracked operations."""
    tracker = CostTracker()
    
    tracker.track_operation("encode", 0.1, 5.0)
    tracker.track_operation("decode", 0.1, 3.0)
    
    assert tracker.get_operation_count() == 2
    
    tracker.clear()
    
    assert tracker.get_operation_count() == 0
    assert tracker.get_total_cost() == 0.0


def test_operation_duration_ms():
    """Test operation duration in milliseconds."""
    tracker = CostTracker()
    
    op = tracker.track_operation("test", 0.5, 10.0)
    
    assert op.duration_ms == 500.0


def test_global_cost_tracker():
    """Test global cost tracker accessor."""
    tracker1 = get_cost_tracker()
    assert tracker1 is not None
    
    # Should return same instance
    tracker2 = get_cost_tracker()
    assert tracker1 is tracker2


def test_budget_not_found():
    """Test checking non-existent budget."""
    tracker = CostTracker()
    
    with pytest.raises(ValueError, match="Budget not found"):
        tracker.check_budget("nonexistent")


def test_empty_statistics():
    """Test statistics with no operations."""
    tracker = CostTracker()
    
    stats = tracker.get_statistics()
    
    assert stats["total_operations"] == 0
    assert stats["total_cost"] == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
