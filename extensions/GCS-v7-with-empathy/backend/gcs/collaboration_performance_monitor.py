"""
collaboration_performance_monitor.py - Performance Monitoring Dashboard for Human-AI Collaboration

Implements performance monitoring dashboards:
- Real-time collaboration metrics tracking
- Performance trend analysis and visualization
- Collaborative effectiveness measurement
- User satisfaction monitoring
- System health dashboards
- Performance optimization recommendations
"""

import logging
import time
import threading
import json
from typing import Dict, List, Tuple, Any, Optional, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import deque, defaultdict
import statistics
from .human_ai_collaboration import CollaborativeDecision, CollaborationContext, CollaborationMode
from .collaborative_anomaly_detector import CollaborationAnomaly
from .confirmation_automation import ConfirmationRequest


class PerformanceMetric(Enum):
    """Types of performance metrics tracked"""
    RESPONSE_TIME = "response_time"
    DECISION_QUALITY = "decision_quality"
    USER_SATISFACTION = "user_satisfaction"
    TRUST_LEVEL = "trust_level"
    COLLABORATION_EFFECTIVENESS = "collaboration_effectiveness"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"
    AVAILABILITY = "availability"
    RESOURCE_UTILIZATION = "resource_utilization"
    ETHICAL_COMPLIANCE = "ethical_compliance"


class DashboardType(Enum):
    """Types of performance dashboards"""
    REAL_TIME = "real_time"
    HISTORICAL = "historical"
    USER_SPECIFIC = "user_specific"
    SYSTEM_HEALTH = "system_health"
    COMPARATIVE = "comparative"
    EXECUTIVE_SUMMARY = "executive_summary"


@dataclass
class MetricDataPoint:
    """Single metric data point"""
    timestamp: float
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    user_id: Optional[str] = None
    session_id: Optional[str] = None


@dataclass
class PerformanceTrend:
    """Trend analysis for a metric"""
    metric: PerformanceMetric
    time_window: str  # e.g., "1h", "24h", "7d"
    current_value: float
    previous_value: float
    trend_direction: str  # "up", "down", "stable"
    change_percentage: float
    significance_level: float  # statistical significance of trend


@dataclass
class PerformanceAlert:
    """Performance alert for threshold violations"""
    alert_id: str
    metric: PerformanceMetric
    current_value: float
    threshold_value: float
    alert_type: str  # "threshold", "trend", "anomaly"
    severity: str  # "low", "medium", "high", "critical"
    description: str
    recommended_actions: List[str]
    triggered_at: float
    acknowledged: bool = False


@dataclass
class DashboardConfig:
    """Configuration for performance dashboard"""
    dashboard_type: DashboardType
    metrics: List[PerformanceMetric]
    refresh_interval: int = 30  # seconds
    time_range: str = "1h"  # default time range
    user_filters: List[str] = field(default_factory=list)
    alert_thresholds: Dict[PerformanceMetric, Dict[str, float]] = field(default_factory=dict)
    visualization_type: str = "line_chart"


class CollaborationPerformanceMonitor:
    """
    Performance monitoring system for human-AI collaboration.
    
    Provides real-time monitoring, trend analysis, and performance dashboards
    for collaborative decision-making systems.
    """
    
    def __init__(self, data_retention_hours: int = 168):  # Default: 7 days
        """
        Initialize the performance monitor
        
        Args:
            data_retention_hours: How long to keep historical data
        """
        self.logger = logging.getLogger(__name__)
        self.data_retention_hours = data_retention_hours
        
        # Metric storage
        self.metrics_data: Dict[PerformanceMetric, deque] = {
            metric: deque(maxlen=10000) for metric in PerformanceMetric
        }
        
        # User-specific metrics
        self.user_metrics: Dict[str, Dict[PerformanceMetric, deque]] = defaultdict(
            lambda: {metric: deque(maxlen=1000) for metric in PerformanceMetric}
        )
        
        # Performance baselines and thresholds
        self.performance_baselines: Dict[PerformanceMetric, float] = {}
        self.alert_thresholds: Dict[PerformanceMetric, Dict[str, float]] = self._initialize_thresholds()
        
        # Active alerts and trends
        self.active_alerts: List[PerformanceAlert] = []
        self.performance_trends: Dict[PerformanceMetric, PerformanceTrend] = {}
        
        # Dashboard configurations
        self.dashboard_configs: Dict[str, DashboardConfig] = {}
        
        # Background processing
        self.monitor_thread = None
        self.shutdown_flag = threading.Event()
        
        # Callbacks for alerts and updates
        self.alert_callbacks: List[Callable] = []
        self.dashboard_update_callbacks: List[Callable] = []
        
        # Performance optimization recommendations
        self.optimization_recommendations: List[Dict[str, Any]] = []
        
        self.logger.info("Collaboration Performance Monitor initialized")

    def start_monitoring(self):
        """Start background performance monitoring"""
        if self.monitor_thread is None or not self.monitor_thread.is_alive():
            self.shutdown_flag.clear()
            self.monitor_thread = threading.Thread(target=self._monitoring_loop)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            self.logger.info("Performance monitoring started")

    def stop_monitoring(self):
        """Stop background performance monitoring"""
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.shutdown_flag.set()
            self.monitor_thread.join(timeout=5.0)
            self.logger.info("Performance monitoring stopped")

    def record_collaboration_decision(self, decision: CollaborativeDecision):
        """
        Record metrics from a collaborative decision
        
        Args:
            decision: Completed collaborative decision
        """
        timestamp = decision.timestamp
        user_id = decision.context.user_id
        
        # Calculate and record various metrics
        if hasattr(decision, 'response_time') and decision.response_time:
            self._record_metric(PerformanceMetric.RESPONSE_TIME, decision.response_time, 
                              timestamp, user_id, decision.context.session_id)
        
        # Decision quality (based on ethical assessment and outcome)
        if decision.ethical_assessment:
            ethical_score = decision.ethical_assessment.overall_ethical_score
            self._record_metric(PerformanceMetric.ETHICAL_COMPLIANCE, ethical_score,
                              timestamp, user_id, decision.context.session_id)
            
        # Trust level from context
        trust_level = decision.context.trust_level
        self._record_metric(PerformanceMetric.TRUST_LEVEL, trust_level,
                          timestamp, user_id, decision.context.session_id)
        
        # Collaboration effectiveness based on decision outcome
        effectiveness_score = self._calculate_decision_effectiveness(decision)
        self._record_metric(PerformanceMetric.COLLABORATION_EFFECTIVENESS, effectiveness_score,
                          timestamp, user_id, decision.context.session_id)

    def record_confirmation_metrics(self, confirmation: ConfirmationRequest):
        """
        Record metrics from confirmation requests
        
        Args:
            confirmation: Completed confirmation request
        """
        if confirmation.response_time:
            self._record_metric(PerformanceMetric.RESPONSE_TIME, confirmation.response_time,
                              confirmation.requested_at, confirmation.context.user_id,
                              confirmation.context.session_id)

    def record_anomaly_detection(self, anomaly: CollaborationAnomaly):
        """
        Record metrics from anomaly detection
        
        Args:
            anomaly: Detected collaboration anomaly
        """
        # Record as error rate increase
        current_error_rate = self._calculate_current_error_rate()
        self._record_metric(PerformanceMetric.ERROR_RATE, current_error_rate + 0.1,
                          anomaly.detected_at, anomaly.context.user_id,
                          anomaly.context.session_id)

    def record_user_satisfaction(self, user_id: str, satisfaction_score: float,
                               session_id: Optional[str] = None):
        """
        Record user satisfaction metrics
        
        Args:
            user_id: User identifier
            satisfaction_score: Satisfaction score (0.0-1.0)
            session_id: Optional session identifier
        """
        self._record_metric(PerformanceMetric.USER_SATISFACTION, satisfaction_score,
                          time.time(), user_id, session_id)

    def get_real_time_dashboard(self, dashboard_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get real-time performance dashboard data
        
        Args:
            dashboard_id: Optional specific dashboard configuration
            
        Returns:
            Dashboard data with current metrics and visualizations
        """
        current_time = time.time()
        dashboard_data = {
            "timestamp": current_time,
            "dashboard_type": "real_time",
            "metrics": {},
            "alerts": [],
            "trends": {},
            "system_health": {}
        }
        
        # Current metric values
        for metric in PerformanceMetric:
            recent_value = self._get_recent_metric_value(metric, window_seconds=300)  # 5 minutes
            if recent_value is not None:
                dashboard_data["metrics"][metric.value] = {
                    "current_value": recent_value,
                    "baseline": self.performance_baselines.get(metric, 0.0),
                    "trend": self._calculate_short_term_trend(metric)
                }
        
        # Active alerts
        dashboard_data["alerts"] = [
            {
                "metric": alert.metric.value,
                "severity": alert.severity,
                "description": alert.description,
                "value": alert.current_value,
                "threshold": alert.threshold_value
            }
            for alert in self.active_alerts
        ]
        
        # Performance trends
        dashboard_data["trends"] = {
            metric.value: {
                "direction": trend.trend_direction,
                "change_percentage": trend.change_percentage,
                "significance": trend.significance_level
            }
            for metric, trend in self.performance_trends.items()
        }
        
        # System health overview
        dashboard_data["system_health"] = self._generate_system_health_summary()
        
        return dashboard_data

    def get_historical_dashboard(self, time_range: str = "24h", 
                               user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get historical performance dashboard data
        
        Args:
            time_range: Time range for historical data ("1h", "24h", "7d", "30d")
            user_id: Optional user filter
            
        Returns:
            Historical dashboard data with trends and analysis
        """
        time_range_seconds = self._parse_time_range(time_range)
        start_time = time.time() - time_range_seconds
        
        dashboard_data = {
            "timestamp": time.time(),
            "dashboard_type": "historical",
            "time_range": time_range,
            "user_filter": user_id,
            "metrics_history": {},
            "trends": {},
            "performance_summary": {}
        }
        
        # Historical data for each metric
        for metric in PerformanceMetric:
            metric_data = self._get_metric_history(metric, start_time, user_id)
            if metric_data:
                dashboard_data["metrics_history"][metric.value] = {
                    "data_points": len(metric_data),
                    "values": [point.value for point in metric_data],
                    "timestamps": [point.timestamp for point in metric_data],
                    "average": statistics.mean([point.value for point in metric_data]),
                    "median": statistics.median([point.value for point in metric_data]),
                    "min": min([point.value for point in metric_data]),
                    "max": max([point.value for point in metric_data])
                }
        
        # Trend analysis
        dashboard_data["trends"] = self._calculate_historical_trends(time_range_seconds, user_id)
        
        # Performance summary
        dashboard_data["performance_summary"] = self._generate_performance_summary(
            time_range_seconds, user_id
        )
        
        return dashboard_data

    def get_user_performance_dashboard(self, user_id: str) -> Dict[str, Any]:
        """
        Get user-specific performance dashboard
        
        Args:
            user_id: User identifier
            
        Returns:
            User-specific performance data and insights
        """
        dashboard_data = {
            "user_id": user_id,
            "timestamp": time.time(),
            "dashboard_type": "user_specific",
            "personal_metrics": {},
            "collaboration_patterns": {},
            "recommendations": []
        }
        
        # Personal metrics
        if user_id in self.user_metrics:
            user_data = self.user_metrics[user_id]
            for metric, data_points in user_data.items():
                if data_points:
                    recent_values = [dp.value for dp in list(data_points)[-10:]]  # Last 10 values
                    dashboard_data["personal_metrics"][metric.value] = {
                        "recent_average": statistics.mean(recent_values),
                        "trend": self._calculate_user_metric_trend(user_id, metric),
                        "percentile_rank": self._calculate_user_percentile(user_id, metric)
                    }
        
        # Collaboration patterns
        dashboard_data["collaboration_patterns"] = self._analyze_user_collaboration_patterns(user_id)
        
        # Personalized recommendations
        dashboard_data["recommendations"] = self._generate_user_recommendations(user_id)
        
        return dashboard_data

    def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """
        Get performance optimization recommendations
        
        Returns:
            List of optimization recommendations with priorities
        """
        return self.optimization_recommendations

    def create_performance_alert(self, metric: PerformanceMetric, threshold_type: str,
                               threshold_value: float, severity: str = "medium") -> str:
        """
        Create a performance alert threshold
        
        Args:
            metric: Performance metric to monitor
            threshold_type: Type of threshold ("min", "max", "change")
            threshold_value: Threshold value
            severity: Alert severity level
            
        Returns:
            Alert ID
        """
        alert_id = f"alert_{metric.value}_{int(time.time())}"
        
        if metric not in self.alert_thresholds:
            self.alert_thresholds[metric] = {}
            
        self.alert_thresholds[metric][threshold_type] = threshold_value
        
        self.logger.info(f"Created performance alert {alert_id} for {metric.value}")
        return alert_id

    # Private helper methods
    
    def _record_metric(self, metric: PerformanceMetric, value: float, timestamp: float,
                      user_id: Optional[str] = None, session_id: Optional[str] = None):
        """Record a metric data point"""
        data_point = MetricDataPoint(
            timestamp=timestamp,
            value=value,
            user_id=user_id,
            session_id=session_id
        )
        
        # Store in global metrics
        self.metrics_data[metric].append(data_point)
        
        # Store in user-specific metrics
        if user_id:
            self.user_metrics[user_id][metric].append(data_point)
        
        # Check for threshold violations
        self._check_threshold_violations(metric, value)

    def _initialize_thresholds(self) -> Dict[PerformanceMetric, Dict[str, float]]:
        """Initialize default alert thresholds"""
        return {
            PerformanceMetric.RESPONSE_TIME: {"max": 5.0, "change": 2.0},
            PerformanceMetric.ERROR_RATE: {"max": 0.1, "change": 0.05},
            PerformanceMetric.TRUST_LEVEL: {"min": 0.3, "change": -0.2},
            PerformanceMetric.USER_SATISFACTION: {"min": 0.6, "change": -0.3},
            PerformanceMetric.COLLABORATION_EFFECTIVENESS: {"min": 0.5, "change": -0.2},
            PerformanceMetric.ETHICAL_COMPLIANCE: {"min": 0.7, "change": -0.1}
        }

    def _get_recent_metric_value(self, metric: PerformanceMetric, 
                               window_seconds: int = 300) -> Optional[float]:
        """Get most recent metric value within time window"""
        current_time = time.time()
        recent_data = [
            dp for dp in self.metrics_data[metric]
            if current_time - dp.timestamp <= window_seconds
        ]
        
        if recent_data:
            return statistics.mean([dp.value for dp in recent_data])
        return None

    def _calculate_decision_effectiveness(self, decision: CollaborativeDecision) -> float:
        """Calculate effectiveness score for a decision"""
        effectiveness = 0.5  # Base score
        
        # Positive factors
        if decision.execution_status == "approved":
            effectiveness += 0.3
        if decision.ethical_assessment and decision.ethical_assessment.overall_ethical_score > 0.8:
            effectiveness += 0.2
        if hasattr(decision, 'response_time') and decision.response_time and decision.response_time < 10.0:
            effectiveness += 0.1
            
        # Negative factors
        if decision.execution_status == "rejected":
            effectiveness -= 0.2
        if decision.execution_status == "timeout":
            effectiveness -= 0.3
            
        return max(0.0, min(1.0, effectiveness))

    def _calculate_current_error_rate(self) -> float:
        """Calculate current system error rate"""
        # Simple implementation - could be more sophisticated
        recent_errors = len([
            dp for dp in self.metrics_data[PerformanceMetric.ERROR_RATE]
            if time.time() - dp.timestamp <= 3600  # Last hour
        ])
        
        return min(1.0, recent_errors / 100.0)  # Normalize to 0-1

    def _calculate_short_term_trend(self, metric: PerformanceMetric) -> str:
        """Calculate short-term trend for metric"""
        recent_data = list(self.metrics_data[metric])[-20:]  # Last 20 data points
        
        if len(recent_data) < 5:
            return "insufficient_data"
            
        first_half = [dp.value for dp in recent_data[:len(recent_data)//2]]
        second_half = [dp.value for dp in recent_data[len(recent_data)//2:]]
        
        first_avg = statistics.mean(first_half)
        second_avg = statistics.mean(second_half)
        
        if abs(second_avg - first_avg) / first_avg < 0.05:
            return "stable"
        elif second_avg > first_avg:
            return "increasing"
        else:
            return "decreasing"

    def _generate_system_health_summary(self) -> Dict[str, Any]:
        """Generate overall system health summary"""
        health_summary = {
            "overall_status": "healthy",
            "critical_alerts": len([a for a in self.active_alerts if a.severity == "critical"]),
            "performance_score": 0.8,  # Default good score
            "availability": 0.99,
            "recommendations_count": len(self.optimization_recommendations)
        }
        
        # Adjust overall status based on alerts
        if health_summary["critical_alerts"] > 0:
            health_summary["overall_status"] = "critical"
        elif len(self.active_alerts) > 5:
            health_summary["overall_status"] = "degraded"
            
        return health_summary

    def _parse_time_range(self, time_range: str) -> int:
        """Parse time range string to seconds"""
        time_units = {
            "h": 3600,
            "d": 86400,
            "w": 604800,
            "m": 2628000  # 30.4 days
        }
        
        if time_range[-1] in time_units:
            return int(time_range[:-1]) * time_units[time_range[-1]]
        else:
            return 3600  # Default to 1 hour

    def _get_metric_history(self, metric: PerformanceMetric, start_time: float,
                          user_id: Optional[str] = None) -> List[MetricDataPoint]:
        """Get metric history within time range"""
        if user_id and user_id in self.user_metrics:
            data_source = self.user_metrics[user_id][metric]
        else:
            data_source = self.metrics_data[metric]
            
        return [dp for dp in data_source if dp.timestamp >= start_time]

    def _calculate_historical_trends(self, time_range_seconds: int, 
                                   user_id: Optional[str] = None) -> Dict[str, Any]:
        """Calculate historical trends for metrics"""
        trends = {}
        
        for metric in PerformanceMetric:
            metric_data = self._get_metric_history(
                metric, time.time() - time_range_seconds, user_id
            )
            
            if len(metric_data) > 10:
                values = [dp.value for dp in metric_data]
                
                # Simple linear trend calculation
                first_quarter = values[:len(values)//4]
                last_quarter = values[-len(values)//4:]
                
                if first_quarter and last_quarter:
                    trend_change = (statistics.mean(last_quarter) - statistics.mean(first_quarter))
                    trends[metric.value] = {
                        "change": trend_change,
                        "direction": "up" if trend_change > 0 else "down" if trend_change < 0 else "stable",
                        "data_points": len(metric_data)
                    }
                    
        return trends

    def _generate_performance_summary(self, time_range_seconds: int, 
                                    user_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate performance summary for time period"""
        summary = {
            "time_period": f"{time_range_seconds // 3600} hours",
            "total_interactions": 0,
            "average_response_time": 0.0,
            "user_satisfaction": 0.0,
            "error_rate": 0.0,
            "key_insights": []
        }
        
        # Calculate summaries from historical data
        response_time_data = self._get_metric_history(
            PerformanceMetric.RESPONSE_TIME, time.time() - time_range_seconds, user_id
        )
        if response_time_data:
            summary["average_response_time"] = statistics.mean([dp.value for dp in response_time_data])
            summary["total_interactions"] = len(response_time_data)
        
        satisfaction_data = self._get_metric_history(
            PerformanceMetric.USER_SATISFACTION, time.time() - time_range_seconds, user_id
        )
        if satisfaction_data:
            summary["user_satisfaction"] = statistics.mean([dp.value for dp in satisfaction_data])
        
        return summary

    def _analyze_user_collaboration_patterns(self, user_id: str) -> Dict[str, Any]:
        """Analyze collaboration patterns for specific user"""
        patterns = {
            "preferred_collaboration_modes": [],
            "peak_activity_hours": [],
            "response_time_patterns": {},
            "decision_quality_trends": {}
        }
        
        # This would analyze user-specific data patterns
        # For now, return basic structure
        return patterns

    def _generate_user_recommendations(self, user_id: str) -> List[Dict[str, Any]]:
        """Generate personalized recommendations for user"""
        recommendations = []
        
        # Analyze user metrics and generate recommendations
        if user_id in self.user_metrics:
            user_data = self.user_metrics[user_id]
            
            # Check response times
            response_times = [dp.value for dp in user_data[PerformanceMetric.RESPONSE_TIME]]
            if response_times and statistics.mean(response_times) > 5.0:
                recommendations.append({
                    "type": "performance",
                    "priority": "medium",
                    "title": "Improve Response Times",
                    "description": "Your average response time is above optimal range",
                    "suggested_actions": [
                        "Review decision-making process",
                        "Consider using confirmation shortcuts for trusted actions"
                    ]
                })
        
        return recommendations

    def _calculate_user_metric_trend(self, user_id: str, metric: PerformanceMetric) -> str:
        """Calculate trend for user-specific metric"""
        if user_id not in self.user_metrics:
            return "no_data"
            
        recent_data = list(self.user_metrics[user_id][metric])[-10:]
        if len(recent_data) < 5:
            return "insufficient_data"
            
        first_half = recent_data[:len(recent_data)//2]
        second_half = recent_data[len(recent_data)//2:]
        
        first_avg = statistics.mean([dp.value for dp in first_half])
        second_avg = statistics.mean([dp.value for dp in second_half])
        
        change = (second_avg - first_avg) / first_avg if first_avg > 0 else 0
        
        if abs(change) < 0.05:
            return "stable"
        elif change > 0:
            return "improving"
        else:
            return "declining"

    def _calculate_user_percentile(self, user_id: str, metric: PerformanceMetric) -> float:
        """Calculate user's percentile rank for metric"""
        if user_id not in self.user_metrics:
            return 0.5
            
        user_recent_avg = statistics.mean([
            dp.value for dp in list(self.user_metrics[user_id][metric])[-10:]
        ]) if self.user_metrics[user_id][metric] else 0.5
        
        # Compare against all users
        all_user_averages = []
        for uid, user_data in self.user_metrics.items():
            if user_data[metric]:
                avg = statistics.mean([dp.value for dp in list(user_data[metric])[-10:]])
                all_user_averages.append(avg)
        
        if len(all_user_averages) < 2:
            return 0.5
            
        sorted_averages = sorted(all_user_averages)
        user_rank = sum(1 for avg in sorted_averages if avg <= user_recent_avg)
        
        return user_rank / len(sorted_averages)

    def _check_threshold_violations(self, metric: PerformanceMetric, value: float):
        """Check if metric value violates alert thresholds"""
        if metric not in self.alert_thresholds:
            return
            
        thresholds = self.alert_thresholds[metric]
        
        # Check maximum threshold
        if "max" in thresholds and value > thresholds["max"]:
            self._create_threshold_alert(metric, value, thresholds["max"], "max")
            
        # Check minimum threshold
        if "min" in thresholds and value < thresholds["min"]:
            self._create_threshold_alert(metric, value, thresholds["min"], "min")

    def _create_threshold_alert(self, metric: PerformanceMetric, current_value: float,
                              threshold_value: float, threshold_type: str):
        """Create a threshold violation alert"""
        alert_id = f"threshold_{metric.value}_{int(time.time())}"
        
        # Determine severity based on how much threshold is exceeded
        if threshold_type == "max":
            excess_ratio = (current_value - threshold_value) / threshold_value
        else:  # min
            excess_ratio = (threshold_value - current_value) / threshold_value
            
        if excess_ratio > 0.5:
            severity = "critical"
        elif excess_ratio > 0.2:
            severity = "high"
        else:
            severity = "medium"
        
        alert = PerformanceAlert(
            alert_id=alert_id,
            metric=metric,
            current_value=current_value,
            threshold_value=threshold_value,
            alert_type="threshold",
            severity=severity,
            description=f"{metric.value} {threshold_type} threshold violation: {current_value:.2f} vs {threshold_value:.2f}",
            recommended_actions=self._get_metric_improvement_actions(metric),
            triggered_at=time.time()
        )
        
        self.active_alerts.append(alert)
        
        # Trigger alert callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                self.logger.error(f"Error in alert callback: {e}")

    def _get_metric_improvement_actions(self, metric: PerformanceMetric) -> List[str]:
        """Get recommended actions for metric improvement"""
        action_map = {
            PerformanceMetric.RESPONSE_TIME: [
                "Optimize system performance",
                "Review processing algorithms",
                "Scale up resources"
            ],
            PerformanceMetric.ERROR_RATE: [
                "Review error logs",
                "Implement additional validation",
                "Update error handling procedures"
            ],
            PerformanceMetric.USER_SATISFACTION: [
                "Collect user feedback",
                "Review user interface design",
                "Analyze user behavior patterns"
            ],
            PerformanceMetric.TRUST_LEVEL: [
                "Increase system transparency",
                "Improve error communication",
                "Provide better explanations"
            ]
        }
        
        return action_map.get(metric, ["Monitor closely", "Investigate root cause"])

    def _monitoring_loop(self):
        """Background monitoring loop for performance analysis"""
        while not self.shutdown_flag.is_set():
            try:
                current_time = time.time()
                
                # Clean up old data
                cutoff_time = current_time - (self.data_retention_hours * 3600)
                for metric in PerformanceMetric:
                    # Remove old data points
                    while (self.metrics_data[metric] and 
                           self.metrics_data[metric][0].timestamp < cutoff_time):
                        self.metrics_data[metric].popleft()
                
                # Calculate performance trends
                self._update_performance_trends()
                
                # Generate optimization recommendations
                self._update_optimization_recommendations()
                
                # Clean up resolved alerts
                self._cleanup_resolved_alerts()
                
                time.sleep(60)  # Run every minute
                
            except Exception as e:
                self.logger.error(f"Error in performance monitoring loop: {e}")
                time.sleep(300)  # Wait longer on error

    def _update_performance_trends(self):
        """Update performance trend calculations"""
        for metric in PerformanceMetric:
            if len(self.metrics_data[metric]) > 20:
                # Calculate trend over recent data
                recent_data = list(self.metrics_data[metric])[-50:]  # Last 50 points
                values = [dp.value for dp in recent_data]
                
                # Simple trend calculation
                first_half = values[:len(values)//2]
                second_half = values[len(values)//2:]
                
                if first_half and second_half:
                    first_avg = statistics.mean(first_half)
                    second_avg = statistics.mean(second_half)
                    
                    change_pct = ((second_avg - first_avg) / first_avg * 100) if first_avg > 0 else 0
                    
                    trend = PerformanceTrend(
                        metric=metric,
                        time_window="recent",
                        current_value=second_avg,
                        previous_value=first_avg,
                        trend_direction="up" if change_pct > 5 else "down" if change_pct < -5 else "stable",
                        change_percentage=change_pct,
                        significance_level=min(1.0, abs(change_pct) / 20.0)
                    )
                    
                    self.performance_trends[metric] = trend

    def _update_optimization_recommendations(self):
        """Update performance optimization recommendations"""
        self.optimization_recommendations.clear()
        
        # Analyze trends and generate recommendations
        for metric, trend in self.performance_trends.items():
            if trend.trend_direction == "down" and trend.significance_level > 0.5:
                if metric == PerformanceMetric.RESPONSE_TIME:
                    self.optimization_recommendations.append({
                        "priority": "high",
                        "category": "performance",
                        "title": "Response Time Degradation",
                        "description": f"Response times have increased by {trend.change_percentage:.1f}%",
                        "actions": self._get_metric_improvement_actions(metric)
                    })

    def _cleanup_resolved_alerts(self):
        """Clean up old or resolved alerts"""
        current_time = time.time()
        self.active_alerts = [
            alert for alert in self.active_alerts
            if current_time - alert.triggered_at < 3600 or not alert.acknowledged  # Keep for 1 hour or until ack'd
        ]

    # Public callback registration methods
    
    def register_alert_callback(self, callback: Callable):
        """Register callback for performance alerts"""
        self.alert_callbacks.append(callback)
        
    def register_dashboard_update_callback(self, callback: Callable):
        """Register callback for dashboard updates"""
        self.dashboard_update_callbacks.append(callback)

    def shutdown(self):
        """Shutdown the performance monitor"""
        self.stop_monitoring()
        self.logger.info("Collaboration Performance Monitor shutdown complete")