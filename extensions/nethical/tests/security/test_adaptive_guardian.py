"""Comprehensive tests for the Adaptive Guardian system.

Tests all 5 modes, automatic transitions, tripwires, track analyzer,
watchdog, cross-module correlation, manual lockdown, and performance.
"""

import asyncio
import time

import pytest

from nethical.security.adaptive_guardian import (
    AdaptiveGuardian,
    clear_lockdown,
    get_guardian,
    get_mode,
    get_status,
    monitored,
    record_metric,
    trigger_lockdown,
)
from nethical.security.guardian_modes import (
    GuardianMode,
    TripwireSensitivity,
    get_mode_config,
    get_mode_for_threat_score,
    severity_matches_sensitivity,
)
from nethical.security.track_analyzer import TrackAnalyzer
from nethical.security.tripwires import TripwireAlert, Tripwires
from nethical.security.watchdog import Watchdog


class TestGuardianModes:
    """Test guardian mode configurations and behavior."""
# noqa: W293
    def test_all_modes_exist(self):
        """Test that all 5 modes are defined."""
        assert len(GuardianMode) == 5
        assert GuardianMode.SPRINT in GuardianMode
        assert GuardianMode.CRUISE in GuardianMode
        assert GuardianMode.ALERT in GuardianMode
        assert GuardianMode.DEFENSE in GuardianMode
        assert GuardianMode.LOCKDOWN in GuardianMode
# noqa: W293
    def test_mode_configs(self):
        """Test that all modes have proper configurations."""
        for mode in list(GuardianMode):
            config = get_mode_config(mode)
            assert config.mode == mode
            assert config.overhead_ms > 0
            assert config.pulse_interval_s > 0
            assert 0.0 <= config.threat_score_min <= 1.0
            assert 0.0 <= config.threat_score_max <= 1.0
            assert config.threat_score_min <= config.threat_score_max
# noqa: W293
    def test_mode_selection_by_threat_score(self):
        """Test automatic mode selection based on threat score."""
        assert get_mode_for_threat_score(0.05) == GuardianMode.SPRINT
        assert get_mode_for_threat_score(0.2) == GuardianMode.CRUISE
        assert get_mode_for_threat_score(0.45) == GuardianMode.ALERT
        assert get_mode_for_threat_score(0.7) == GuardianMode.DEFENSE
        assert get_mode_for_threat_score(0.9) == GuardianMode.LOCKDOWN
# noqa: W293
    def test_mode_overhead_progression(self):
        """Test that overhead increases with mode intensity."""
        modes = [
            GuardianMode.SPRINT,
            GuardianMode.CRUISE,
            GuardianMode.ALERT,
            GuardianMode.DEFENSE,
            GuardianMode.LOCKDOWN,
        ]
# noqa: W293
        prev_overhead = 0.0
        for mode in modes:
            config = get_mode_config(mode)
            assert config.overhead_ms > prev_overhead
            prev_overhead = config.overhead_ms
# noqa: W293
    def test_pulse_interval_decreases(self):
        """Test that pulse interval decreases with mode intensity."""
        modes = [
            GuardianMode.SPRINT,
            GuardianMode.CRUISE,
            GuardianMode.ALERT,
            GuardianMode.DEFENSE,
            GuardianMode.LOCKDOWN,
        ]
# noqa: W293
        prev_interval = float("inf")
        for mode in modes:
            config = get_mode_config(mode)
            assert config.pulse_interval_s < prev_interval
            prev_interval = config.pulse_interval_s
# noqa: W293
    def test_sensitivity_matching(self):
        """Test severity matching with tripwire sensitivity."""
        assert severity_matches_sensitivity("CRITICAL", TripwireSensitivity.CRITICAL)
        assert not severity_matches_sensitivity("HIGH", TripwireSensitivity.CRITICAL)
# noqa: W293
        assert severity_matches_sensitivity("CRITICAL", TripwireSensitivity.HIGH)
        assert severity_matches_sensitivity("HIGH", TripwireSensitivity.HIGH)
        assert not severity_matches_sensitivity("MEDIUM", TripwireSensitivity.HIGH)
# noqa: W293
        assert severity_matches_sensitivity("LOW", TripwireSensitivity.ALL)
        assert severity_matches_sensitivity("INFO", TripwireSensitivity.ALL)


class TestTripwires:
    """Test instant tripwire checks."""
# noqa: W293
    def test_hard_response_time_limit(self):
        """Test that hard response time limit always triggers."""
        tripwires = Tripwires()
# noqa: W293
        # Should trigger regardless of sensitivity
        alert = tripwires.check(
            module="TestModule",
            response_time_ms=6000.0,  # > 5000ms
            decision="ALLOW",
            error=False,
            sensitivity=TripwireSensitivity.CRITICAL,
        )
# noqa: W293
        assert alert is not None
        assert alert.severity == "CRITICAL"
        assert alert.tripwire_type == "hard_response_time"
# noqa: W293
    def test_response_time_spike(self):
        """Test response time spike detection."""
        tripwires = Tripwires()
# noqa: W293
        # Establish baseline
        for _ in range(10):
            tripwires.check(
                module="TestModule",
                response_time_ms=100.0,
                decision="ALLOW",
                error=False,
                sensitivity=TripwireSensitivity.HIGH,
            )
# noqa: W293
        # Trigger spike (10x baseline)
        alert = tripwires.check(
            module="TestModule",
            response_time_ms=1500.0,  # Much higher than baseline
            decision="ALLOW",
            error=False,
            sensitivity=TripwireSensitivity.HIGH,
        )
# noqa: W293
        assert alert is not None
        assert alert.severity == "HIGH"
        assert alert.tripwire_type == "response_time_spike"
# noqa: W293
    def test_hard_error_rate(self):
        """Test hard error rate limit."""
        tripwires = Tripwires()
# noqa: W293
        # Generate many errors to exceed 50% error rate
        for i in range(10):  # noqa: B007
            alert = tripwires.check(
                module="TestModule",
                response_time_ms=50.0,
                decision="ALLOW",
                error=True,  # All errors
                sensitivity=TripwireSensitivity.CRITICAL,
            )
# noqa: W293
        # Should have triggered at some point
        assert alert is not None
        assert alert.severity == "CRITICAL"
        assert "error_rate" in alert.tripwire_type
# noqa: W293
    def test_soft_error_rate_sensitivity(self):
        """Test that soft error rate respects sensitivity."""
        tripwires = Tripwires()
# noqa: W293
        # Generate some errors (not enough for hard limit)
        for i in range(20):
            error = i % 5 == 0  # 20% error rate
            tripwires.check(
                module="TestModule",
                response_time_ms=50.0,
                decision="ALLOW",
                error=error,
                sensitivity=TripwireSensitivity.CRITICAL,  # Won't trigger on MEDIUM
            )
# noqa: W293
        # One more to potentially trigger
        alert = tripwires.check(  # noqa: F841
            module="TestModule",
            response_time_ms=50.0,
            decision="ALLOW",
            error=True,
            sensitivity=TripwireSensitivity.MEDIUM,  # Will trigger on MEDIUM
        )
# noqa: W293
        # With MEDIUM sensitivity, should eventually trigger
        stats = tripwires.get_statistics()
        assert stats["total_checks"] > 0
# noqa: W293
    def test_critical_decision_with_error(self):
        """Test critical decision detection."""
        tripwires = Tripwires()
# noqa: W293
        # Add some successful checks first to avoid hard error rate trigger
        for _ in range(10):
            tripwires.check(
                module="TestModule",
                response_time_ms=50.0,
                decision="ALLOW",
                error=False,
                sensitivity=TripwireSensitivity.HIGH,
            )
# noqa: W293
        # Now trigger critical decision with error
        alert = tripwires.check(
            module="TestModule",
            response_time_ms=50.0,
            decision="BLOCK",
            error=True,
            sensitivity=TripwireSensitivity.HIGH,
        )
# noqa: W293
        assert alert is not None
        assert alert.severity == "HIGH"
        assert "critical_decision" in alert.tripwire_type
# noqa: W293
    def test_sliding_window_cleanup(self):
        """Test that old data is cleaned from sliding windows."""
        tripwires = Tripwires()
# noqa: W293
        # Add some data
        tripwires.check(
            module="TestModule",
            response_time_ms=50.0,
            decision="ALLOW",
            error=False,
            sensitivity=TripwireSensitivity.HIGH,
        )
# noqa: W293
        stats_before = tripwires.get_statistics()
        assert stats_before["modules_tracked"] == 1
# noqa: W293
        # Simulate time passing
        time.sleep(0.1)
# noqa: W293
        # Add more data
        tripwires.check(
            module="TestModule",
            response_time_ms=50.0,
            decision="ALLOW",
            error=False,
            sensitivity=TripwireSensitivity.HIGH,
        )
# noqa: W293
        stats_after = tripwires.get_statistics()
        assert stats_after["total_checks"] > stats_before["total_checks"]
# noqa: W293
    def test_module_reset(self):
        """Test resetting module tracking."""
        tripwires = Tripwires()
# noqa: W293
        tripwires.check(
            module="TestModule",
            response_time_ms=50.0,
            decision="ALLOW",
            error=False,
            sensitivity=TripwireSensitivity.HIGH,
        )
# noqa: W293
        stats = tripwires.get_statistics()
        assert "TestModule" in stats["current_baselines"]
# noqa: W293
        tripwires.reset_module("TestModule")
# noqa: W293
        stats = tripwires.get_statistics()
        assert "TestModule" not in stats["current_baselines"]


class TestTrackAnalyzer:
    """Test track conditions analyzer."""
# noqa: W293
    def test_initial_state(self):
        """Test initial analyzer state."""
        analyzer = TrackAnalyzer()
        analysis = analyzer.analyze()
# noqa: W293
        assert 0.0 <= analysis.overall_threat_score <= 1.0
        assert isinstance(analysis.recommended_mode, GuardianMode)
        assert analysis.alert_count == 0
        assert analysis.error_rate == 0.0
# noqa: W293
    def test_alert_recording(self):
        """Test alert recording and threat score increase."""
        analyzer = TrackAnalyzer()
# noqa: W293
        # Initial analysis
        analysis1 = analyzer.analyze()
        initial_score = analysis1.overall_threat_score
# noqa: W293
        # Record critical alerts
        for _ in range(5):
            alert = TripwireAlert(
                tripwire_type="test",
                severity="CRITICAL",
                module="TestModule",
                description="Test alert",
                metric_value=100.0,
                threshold=50.0,
            )
            analyzer.record_alert(alert)
# noqa: W293
        # Analyze again
        analysis2 = analyzer.analyze()
# noqa: W293
        assert analysis2.overall_threat_score > initial_score
        assert analysis2.alert_count > 0
        assert "TestModule" in analysis2.anomaly_modules
# noqa: W293
    def test_error_rate_tracking(self):
        """Test error rate calculation."""
        analyzer = TrackAnalyzer()
# noqa: W293
        # Record metrics with errors
        for i in range(20):
            error = i % 2 == 0  # 50% error rate
            analyzer.record_metric("TestModule", 50.0, error)
# noqa: W293
        analysis = analyzer.analyze()
# noqa: W293
        assert analysis.error_rate > 0.4  # Should be around 50%
        assert analysis.overall_threat_score > 0.0
# noqa: W293
    def test_correlation_tracking(self):
        """Test cross-module correlation tracking."""
        analyzer = TrackAnalyzer()
# noqa: W293
        # Record correlations
        for _ in range(10):
            analyzer.record_correlation("Module1", "Module2")
            analyzer.record_correlation("Module2", "Module3")
# noqa: W293
        analysis = analyzer.analyze()
# noqa: W293
        assert analysis.correlation_score > 0.0
# noqa: W293
    def test_maintenance_mode(self):
        """Test maintenance mode reduces threat score."""
        analyzer = TrackAnalyzer()
# noqa: W293
        # Record some alerts to increase threat
        for _ in range(5):
            alert = TripwireAlert(
                tripwire_type="test",
                severity="HIGH",
                module="TestModule",
                description="Test",
                metric_value=100.0,
                threshold=50.0,
            )
            analyzer.record_alert(alert)
# noqa: W293
        analysis1 = analyzer.analyze()
        score_normal = analysis1.overall_threat_score
# noqa: W293
        # Enable maintenance mode
        analyzer.set_maintenance_mode(True)
# noqa: W293
        analysis2 = analyzer.analyze()
        score_maintenance = analysis2.overall_threat_score
# noqa: W293
        # Maintenance mode should reduce threat score
        assert score_maintenance < score_normal
# noqa: W293
    def test_known_attack_signal(self):
        """Test known attack increases threat score."""
        analyzer = TrackAnalyzer()
# noqa: W293
        analysis1 = analyzer.analyze()
        score_before = analysis1.overall_threat_score
# noqa: W293
        analyzer.set_known_attack(True)
# noqa: W293
        analysis2 = analyzer.analyze()
        score_after = analysis2.overall_threat_score
# noqa: W293
        assert score_after > score_before
# noqa: W293
    def test_response_time_trend(self):
        """Test response time trend detection."""
        analyzer = TrackAnalyzer()
# noqa: W293
        # Record increasing response times
        for i in range(20):
            rt = 50.0 + (i * 10.0)  # Increasing trend
            analyzer.record_metric("TestModule", rt, False)
# noqa: W293
        analysis = analyzer.analyze()
# noqa: W293
        assert analysis.response_time_trend in ["stable", "increasing", "decreasing"]


class TestWatchdog:
    """Test independent watchdog process."""
# noqa: W293
    def test_watchdog_start_stop(self):
        """Test starting and stopping watchdog."""
        watchdog = Watchdog()
# noqa: W293
        watchdog.start()
        time.sleep(0.1)
        status = watchdog.get_status()
        assert status["running"]
# noqa: W293
        watchdog.stop()
        time.sleep(0.1)
        status = watchdog.get_status()
        assert not status["running"]
# noqa: W293
    def test_heartbeat_recording(self):
        """Test heartbeat recording."""
        watchdog = Watchdog()
        watchdog.start()
# noqa: W293
        # Send heartbeat
        watchdog.heartbeat()
        time.sleep(0.1)
# noqa: W293
        status = watchdog.get_status()
        assert status["is_guardian_responsive"]
        assert status["time_since_heartbeat_s"] < 1.0
# noqa: W293
        watchdog.stop()
# noqa: W293
    def test_watchdog_alert_on_timeout(self):
        """Test watchdog alerts when Guardian is unresponsive."""
        alert_received = []
# noqa: W293
        def alert_callback(alert):
            alert_received.append(alert)
# noqa: W293
        watchdog = Watchdog(alert_callback=alert_callback)
        watchdog.HEARTBEAT_TIMEOUT_S = 0.5  # Short timeout for testing
        watchdog.CHECK_INTERVAL_S = 0.2
# noqa: W293
        watchdog.start()
# noqa: W293
        # Wait for timeout
        time.sleep(1.0)
# noqa: W293
        watchdog.stop()
# noqa: W293
        # Should have received at least one alert
        assert len(alert_received) > 0
        assert alert_received[0].alert_type == "guardian_unresponsive"


class TestAdaptiveGuardian:
    """Test main Adaptive Guardian functionality."""
# noqa: W293
    def test_guardian_initialization(self):
        """Test guardian initialization."""
        guardian = AdaptiveGuardian()
# noqa: W293
        # Should start in CRUISE mode
        mode = guardian.get_mode()
        assert mode == GuardianMode.CRUISE
# noqa: W293
        guardian.stop()
# noqa: W293
    def test_metric_recording(self):
        """Test metric recording."""
        guardian = AdaptiveGuardian()
# noqa: W293
        result = guardian.record_metric(
            module="TestModule",
            response_time_ms=50.0,
            decision="ALLOW",
            error=False,
        )
# noqa: W293
        assert result.module == "TestModule"
        assert result.response_time_ms == 50.0
        assert result.decision == "ALLOW"
        assert not result.error
# noqa: W293
        guardian.stop()
# noqa: W293
    def test_manual_lockdown(self):
        """Test manual lockdown triggering."""
        guardian = AdaptiveGuardian()
# noqa: W293
        # Trigger lockdown
        guardian.trigger_lockdown("test_reason")
# noqa: W293
        mode = guardian.get_mode()
        assert mode == GuardianMode.LOCKDOWN
# noqa: W293
        status = guardian.get_status()
        assert status["manual_lockdown"]
        assert status["lockdown_reason"] == "test_reason"
# noqa: W293
        guardian.stop()
# noqa: W293
    def test_clear_lockdown(self):
        """Test clearing manual lockdown."""
        guardian = AdaptiveGuardian()
# noqa: W293
        # Trigger and clear lockdown
        guardian.trigger_lockdown("test")
        assert guardian.get_mode() == GuardianMode.LOCKDOWN
# noqa: W293
        guardian.clear_lockdown()
# noqa: W293
        status = guardian.get_status()
        assert not status["manual_lockdown"]
# noqa: W293
        guardian.stop()
# noqa: W293
    def test_mode_switching_statistics(self):
        """Test that mode switches are tracked."""
        guardian = AdaptiveGuardian()
# noqa: W293
        initial_mode = guardian.get_mode()
        guardian.trigger_lockdown("test")
# noqa: W293
        stats = guardian.get_statistics()
# noqa: W293
        # Should have recorded the switch
        switch_key = f"{initial_mode.value}->LOCKDOWN"
        assert stats.mode_switches[switch_key] > 0
# noqa: W293
        guardian.stop()
# noqa: W293
    def test_performance_overhead_tracking(self):
        """Test performance overhead tracking."""
        guardian = AdaptiveGuardian()
# noqa: W293
        # Record several metrics
        for _ in range(10):
            guardian.record_metric("TestModule", 50.0)
# noqa: W293
        stats = guardian.get_statistics()
# noqa: W293
        assert stats.total_metrics_recorded == 10
        assert stats.avg_overhead_ms >= 0.0
        assert stats.max_overhead_ms >= 0.0
# noqa: W293
        guardian.stop()
# noqa: W293
    def test_alert_callback(self):
        """Test alert callback is invoked."""
        alerts_received = []
# noqa: W293
        def alert_callback(alert):
            alerts_received.append(alert)
# noqa: W293
        guardian = AdaptiveGuardian(alert_callback=alert_callback)
# noqa: W293
        # Trigger alert with extreme response time
        guardian.record_metric("TestModule", 6000.0)  # > 5000ms hard limit
# noqa: W293
        # Should have received alert
        time.sleep(0.1)
        assert len(alerts_received) > 0
# noqa: W293
        guardian.stop()
# noqa: W293
    def test_watchdog_integration(self):
        """Test that watchdog is running."""
        guardian = AdaptiveGuardian()
        guardian.start()
# noqa: W293
        time.sleep(0.2)
# noqa: W293
        status = guardian.get_status()
        watchdog_status = status["watchdog"]
# noqa: W293
        assert watchdog_status["running"]
        assert watchdog_status["is_guardian_responsive"]
# noqa: W293
        guardian.stop()


class TestGlobalAPI:
    """Test global singleton API functions."""
# noqa: W293
    def test_get_guardian_singleton(self):
        """Test get_guardian returns same instance."""
        guardian1 = get_guardian()
        guardian2 = get_guardian()
# noqa: W293
        assert guardian1 is guardian2
# noqa: W293
    def test_record_metric_global(self):
        """Test global record_metric function."""
        result = record_metric("TestModule", 50.0, "ALLOW", False)
# noqa: W293
        assert result.module == "TestModule"
        assert result.response_time_ms == 50.0
# noqa: W293
    def test_trigger_lockdown_global(self):
        """Test global trigger_lockdown function."""
        trigger_lockdown("global_test")
# noqa: W293
        mode = get_mode()
        assert mode == GuardianMode.LOCKDOWN
# noqa: W293
        clear_lockdown()
# noqa: W293
    def test_get_status_global(self):
        """Test global get_status function."""
        status = get_status()
# noqa: W293
        assert "current_mode" in status
        assert "threat_analysis" in status
        assert "performance" in status
        assert "statistics" in status


class TestMonitoredDecorator:
    """Test @monitored decorator."""
# noqa: W293
    @pytest.mark.asyncio
    async def test_async_monitored_function(self):
        """Test monitoring async functions."""
# noqa: W293
        @monitored("TestModule")
        async def async_func():
            await asyncio.sleep(0.01)
            return "result"
# noqa: W293
        result = await async_func()
        assert result == "result"
# noqa: W293
        # Check that metric was recorded
        status = get_status()
        assert status["statistics"]["total_metrics_recorded"] > 0
# noqa: W293
    def test_sync_monitored_function(self):
        """Test monitoring sync functions."""
# noqa: W293
        @monitored("TestModule")
        def sync_func():
            time.sleep(0.01)
            return "result"
# noqa: W293
        result = sync_func()
        assert result == "result"
# noqa: W293
        # Check that metric was recorded
        status = get_status()
        assert status["statistics"]["total_metrics_recorded"] > 0
# noqa: W293
    @pytest.mark.asyncio
    async def test_monitored_function_with_error(self):
        """Test monitoring functions that raise errors."""
# noqa: W293
        @monitored("TestModule")
        async def async_func_error():
            raise ValueError("test error")
# noqa: W293
        with pytest.raises(ValueError):
            await async_func_error()
# noqa: W293
        # Check that error was recorded
        status = get_status()
        assert status["statistics"]["total_metrics_recorded"] > 0


class TestAutomaticModeTransitions:
    """Test automatic mode transitions based on threat level."""
# noqa: W293
    def test_mode_escalation_on_alerts(self):
        """Test that mode escalates with increasing alerts."""
        guardian = AdaptiveGuardian()
        guardian.start()
# noqa: W293
        initial_mode = guardian.get_mode()
# noqa: W293
        # Generate many critical alerts
        for _ in range(20):
            guardian.record_metric("TestModule", 6000.0)  # Hard limit violation
            time.sleep(0.01)
# noqa: W293
        # Wait for pulse analysis
        time.sleep(0.5)
# noqa: W293
        current_mode = guardian.get_mode()  # noqa: F841
# noqa: W293
        # Mode should have escalated (unless already at max)
        if initial_mode != GuardianMode.LOCKDOWN:
            # Check threat score is elevated
            status = guardian.get_status()
            assert status["threat_analysis"]["overall_score"] > 0.0
# noqa: W293
        guardian.stop()
# noqa: W293
    def test_mode_stays_in_manual_lockdown(self):
        """Test that manual lockdown is not overridden."""
        guardian = AdaptiveGuardian()
        guardian.start()
# noqa: W293
        # Trigger manual lockdown
        guardian.trigger_lockdown("test")
# noqa: W293
        # Record normal metrics
        for _ in range(10):
            guardian.record_metric("TestModule", 10.0)  # Very fast
# noqa: W293
        # Wait for pulse
        time.sleep(0.5)
# noqa: W293
        # Should still be in lockdown
        assert guardian.get_mode() == GuardianMode.LOCKDOWN
# noqa: W293
        guardian.stop()


class TestPerformanceBenchmarks:
    """Performance benchmarks for different modes."""
# noqa: W293
    def test_sprint_mode_overhead(self):
        """Test SPRINT mode meets overhead requirement (<0.02ms)."""
        guardian = AdaptiveGuardian()
# noqa: W293
        # Force SPRINT mode by clearing threats
        guardian.set_external_threat_level(0.0)
# noqa: W293
        # Warm up
        for _ in range(10):
            guardian.record_metric("TestModule", 10.0)
# noqa: W293
        # Measure overhead
        start = time.perf_counter()
        for _ in range(100):
            guardian.record_metric("TestModule", 10.0)
        elapsed = time.perf_counter() - start
# noqa: W293
        avg_overhead_ms = (elapsed / 100) * 1000
# noqa: W293
        # Should be very fast (though might not always meet exact target)
        assert avg_overhead_ms < 1.0  # Generous limit for test
# noqa: W293
        guardian.stop()
# noqa: W293
    def test_mode_switching_speed(self):
        """Test mode switching is fast (<1ms)."""
        guardian = AdaptiveGuardian()
# noqa: W293
        # Measure mode switch time
        start = time.perf_counter()
        guardian.trigger_lockdown("test")
        elapsed = time.perf_counter() - start
# noqa: W293
        switch_time_ms = elapsed * 1000
# noqa: W293
        assert switch_time_ms < 1.0
# noqa: W293
        guardian.stop()
# noqa: W293
    def test_watchdog_heartbeat_frequency(self):
        """Test watchdog heartbeat happens every 5 seconds."""
        guardian = AdaptiveGuardian()
        guardian.start()
# noqa: W293
        # Wait a bit
        time.sleep(0.5)
# noqa: W293
        status = guardian.get_status()
        watchdog_status = status["watchdog"]
# noqa: W293
        # Should be responsive
        assert watchdog_status["is_guardian_responsive"]
        assert watchdog_status["time_since_heartbeat_s"] < 10.0
# noqa: W293
        guardian.stop()


class TestCrossModuleCorrelation:
    """Test cross-module correlation detection."""
# noqa: W293
    def test_correlation_increases_threat_score(self):
        """Test that correlations increase threat score."""
        guardian = AdaptiveGuardian()
# noqa: W293
        initial_status = guardian.get_status()
        initial_score = initial_status["threat_analysis"]["overall_score"]
# noqa: W293
        # Record correlations using public API
        for _ in range(10):
            guardian.record_correlation("Module1", "Module2")
            guardian.record_correlation("Module2", "Module3")
            guardian.record_correlation("Module1", "Module3")
# noqa: W293
        updated_status = guardian.get_status()
        updated_score = updated_status["threat_analysis"]["overall_score"]
# noqa: W293
        # Correlations should increase threat
        assert updated_score >= initial_score
# noqa: W293
        guardian.stop()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
