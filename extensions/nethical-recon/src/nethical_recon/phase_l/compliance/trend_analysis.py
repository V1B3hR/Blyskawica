"""
Trend Analysis
Analyzes trends in attack surface changes over time
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any


@dataclass
class TrendPoint:
    """Single point in a trend"""

    timestamp: datetime
    value: float
    metadata: dict[str, Any]


@dataclass
class Trend:
    """Trend analysis result"""

    name: str
    period_start: datetime
    period_end: datetime
    data_points: list[TrendPoint]
    direction: str  # increasing, decreasing, stable
    change_percentage: float
    average_value: float


class TrendAnalyzer:
    """
    Analyzes security trends over time

    Features:
    - Attack surface growth tracking
    - Finding severity trends
    - Remediation velocity
    - Risk score evolution
    - Asset coverage trends
    """

    def __init__(self):
        """Initialize trend analyzer"""
        self._historical_data: dict[str, list[TrendPoint]] = {}

    def add_data_point(
        self, metric_name: str, timestamp: datetime, value: float, metadata: dict[str, Any] | None = None
    ):
        """Add a data point for trend analysis"""
        if metric_name not in self._historical_data:
            self._historical_data[metric_name] = []

        point = TrendPoint(timestamp=timestamp, value=value, metadata=metadata or {})
        self._historical_data[metric_name].append(point)

    def analyze_trend(self, metric_name: str, days: int = 30) -> Trend | None:
        """
        Analyze trend for a specific metric

        Args:
            metric_name: Name of metric to analyze
            days: Number of days to analyze

        Returns:
            Trend analysis result
        """
        if metric_name not in self._historical_data:
            return None

        # Filter data points by time range
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)

        data_points = [
            point for point in self._historical_data[metric_name] if start_time <= point.timestamp <= end_time
        ]

        if len(data_points) < 2:
            return None

        # Sort by timestamp
        data_points.sort(key=lambda p: p.timestamp)

        # Calculate statistics
        values = [p.value for p in data_points]
        avg_value = sum(values) / len(values)

        # Determine direction
        first_value = values[0]
        last_value = values[-1]
        change = last_value - first_value
        change_percentage = (change / first_value * 100) if first_value != 0 else 0.0

        if abs(change_percentage) < 5:
            direction = "stable"
        elif change_percentage > 0:
            direction = "increasing"
        else:
            direction = "decreasing"

        return Trend(
            name=metric_name,
            period_start=start_time,
            period_end=end_time,
            data_points=data_points,
            direction=direction,
            change_percentage=change_percentage,
            average_value=avg_value,
        )

    def analyze_attack_surface(self, historical_scans: list[dict[str, Any]]) -> dict[str, Trend]:
        """
        Analyze attack surface changes

        Args:
            historical_scans: List of historical scan results

        Returns:
            Dictionary of trend analyses
        """
        # Track various metrics
        for scan in historical_scans:
            timestamp = scan.get("timestamp", datetime.now())

            # Total assets
            assets = scan.get("assets", [])
            self.add_data_point("total_assets", timestamp, len(assets))

            # Open ports
            open_ports = sum(len(a.get("ports", [])) for a in assets)
            self.add_data_point("open_ports", timestamp, open_ports)

            # Services
            services = sum(len(a.get("services", [])) for a in assets)
            self.add_data_point("total_services", timestamp, services)

            # Vulnerabilities
            vulns = scan.get("vulnerabilities", [])
            self.add_data_point("total_vulnerabilities", timestamp, len(vulns))

        # Analyze all metrics
        trends = {}
        for metric in ["total_assets", "open_ports", "total_services", "total_vulnerabilities"]:
            trend = self.analyze_trend(metric)
            if trend:
                trends[metric] = trend

        return trends

    def analyze_finding_trends(self, historical_findings: list[dict[str, Any]]) -> dict[str, Trend]:
        """Analyze trends in security findings"""
        # Group findings by date and severity
        findings_by_date: dict[datetime, dict[str, int]] = {}

        for finding in historical_findings:
            timestamp = finding.get("created_at", datetime.now())
            # Truncate to date
            date = timestamp.replace(hour=0, minute=0, second=0, microsecond=0)

            if date not in findings_by_date:
                findings_by_date[date] = {"total": 0, "critical": 0, "high": 0, "medium": 0, "low": 0}

            findings_by_date[date]["total"] += 1
            severity = finding.get("severity", "MEDIUM").lower()
            if severity in findings_by_date[date]:
                findings_by_date[date][severity] += 1

        # Add data points
        for date, counts in findings_by_date.items():
            for severity, count in counts.items():
                self.add_data_point(f"findings_{severity}", date, count)

        # Analyze trends
        trends = {}
        for severity in ["total", "critical", "high", "medium", "low"]:
            trend = self.analyze_trend(f"findings_{severity}")
            if trend:
                trends[severity] = trend

        return trends

    def analyze_remediation_velocity(self, historical_findings: list[dict[str, Any]]) -> Trend | None:
        """Analyze how quickly findings are being remediated"""
        # Calculate time to remediation for closed findings
        remediation_times: dict[datetime, list[float]] = {}

        for finding in historical_findings:
            if finding.get("status") == "closed":
                created = finding.get("created_at")
                closed = finding.get("closed_at")

                if created and closed:
                    # Calculate days to remediation
                    days = (closed - created).total_seconds() / 86400

                    # Group by month
                    month = closed.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

                    if month not in remediation_times:
                        remediation_times[month] = []
                    remediation_times[month].append(days)

        # Calculate average remediation time per month
        for month, times in remediation_times.items():
            avg_time = sum(times) / len(times) if times else 0
            self.add_data_point("remediation_velocity", month, avg_time)

        return self.analyze_trend("remediation_velocity", days=180)

    def analyze_risk_score_evolution(self, historical_assessments: list[dict[str, Any]]) -> Trend | None:
        """Analyze how risk score has evolved over time"""
        for assessment in historical_assessments:
            timestamp = assessment.get("timestamp", datetime.now())
            risk_score = assessment.get("risk_score", 0.0)

            self.add_data_point("risk_score", timestamp, risk_score)

        return self.analyze_trend("risk_score", days=90)

    def generate_trend_report(self, trends: dict[str, Trend]) -> dict[str, Any]:
        """Generate comprehensive trend report"""
        report = {"trends": {}, "summary": {"increasing": [], "decreasing": [], "stable": []}}

        for name, trend in trends.items():
            report["trends"][name] = {
                "direction": trend.direction,
                "change_percentage": trend.change_percentage,
                "average_value": trend.average_value,
                "data_points": len(trend.data_points),
            }

            # Categorize by direction
            report["summary"][trend.direction].append(name)

        return report

    def predict_future_value(self, metric_name: str, days_ahead: int = 30) -> float | None:
        """Simple linear prediction of future metric value"""
        trend = self.analyze_trend(metric_name, days=90)

        if not trend or len(trend.data_points) < 2:
            return None

        # Simple linear extrapolation
        values = [p.value for p in trend.data_points]
        avg_daily_change = (values[-1] - values[0]) / len(values)

        predicted_value = values[-1] + (avg_daily_change * days_ahead)
        return max(0, predicted_value)  # Don't predict negative values
