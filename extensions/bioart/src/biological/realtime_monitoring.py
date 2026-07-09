#!/usr/bin/env python3
"""
Real-time DNA Synthesis Monitoring
Advanced monitoring system for DNA synthesis processes with alerts and dashboards
"""

import time
import json
import random
import threading
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime, timedelta
import math
import hashlib
from concurrent.futures import ThreadPoolExecutor

class MonitoringStatus(Enum):
    """Monitoring system status"""
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"

class SynthesisPhase(Enum):
    """DNA synthesis phases"""
    PREPARATION = "preparation"
    ELONGATION = "elongation"
    DEPROTECTION = "deprotection"
    CLEAVAGE = "cleavage"
    PURIFICATION = "purification"
    QUALITY_CONTROL = "quality_control"
    COMPLETED = "completed"
    FAILED = "failed"

class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class MetricType(Enum):
    """Types of synthesis metrics"""
    TEMPERATURE = "temperature"
    PRESSURE = "pressure"
    FLOW_RATE = "flow_rate"
    PH_LEVEL = "ph_level"
    COUPLING_EFFICIENCY = "coupling_efficiency"
    SYNTHESIS_YIELD = "synthesis_yield"
    ERROR_RATE = "error_rate"
    REAGENT_LEVEL = "reagent_level"
    CYCLE_TIME = "cycle_time"
    PURITY = "purity"

@dataclass
class SynthesisMetric:
    """Individual synthesis metric measurement"""
    metric_type: MetricType
    value: float
    unit: str
    timestamp: datetime
    synthesis_job_id: str
    instrument_id: str
    phase: SynthesisPhase
    quality_score: float = 1.0
    
    def is_within_range(self, min_val: float, max_val: float) -> bool:
        """Check if metric is within acceptable range"""
        return min_val <= self.value <= max_val

@dataclass
class Alert:
    """Synthesis monitoring alert"""
    alert_id: str
    synthesis_job_id: str
    alert_level: AlertLevel
    message: str
    metric_type: Optional[MetricType]
    metric_value: Optional[float]
    threshold_value: Optional[float]
    timestamp: datetime
    acknowledged: bool = False
    resolved: bool = False
    resolution_time: Optional[datetime] = None
    actions_taken: List[str] = field(default_factory=list)

@dataclass
class SynthesisJob:
    """DNA synthesis job being monitored"""
    job_id: str
    sequence: str
    instrument_id: str
    operator: str
    started_at: datetime
    estimated_completion: datetime
    current_phase: SynthesisPhase
    current_cycle: int
    total_cycles: int
    synthesis_method: str
    priority: str = "normal"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_progress_percentage(self) -> float:
        """Get synthesis progress percentage"""
        if self.total_cycles == 0:
            return 0.0
        return min((self.current_cycle / self.total_cycles) * 100, 100.0)

@dataclass
class InstrumentStatus:
    """DNA synthesis instrument status"""
    instrument_id: str
    name: str
    model: str
    status: str
    current_job_id: Optional[str]
    temperature: float
    pressure: float
    last_maintenance: datetime
    total_runtime_hours: float
    error_count: int = 0
    
    def needs_maintenance(self) -> bool:
        """Check if instrument needs maintenance"""
        days_since_maintenance = (datetime.now() - self.last_maintenance).days
        return days_since_maintenance > 30 or self.total_runtime_hours > 1000

class ThresholdManager:
    """Manages monitoring thresholds for different metrics"""
    
    def __init__(self):
        self.thresholds = {
            MetricType.TEMPERATURE: {"min": 20.0, "max": 80.0, "optimal": 37.0},
            MetricType.PRESSURE: {"min": 0.8, "max": 2.0, "optimal": 1.2},
            MetricType.FLOW_RATE: {"min": 0.1, "max": 5.0, "optimal": 1.0},
            MetricType.PH_LEVEL: {"min": 6.5, "max": 8.5, "optimal": 7.4},
            MetricType.COUPLING_EFFICIENCY: {"min": 0.95, "max": 1.0, "optimal": 0.99},
            MetricType.SYNTHESIS_YIELD: {"min": 0.80, "max": 1.0, "optimal": 0.95},
            MetricType.ERROR_RATE: {"min": 0.0, "max": 0.05, "optimal": 0.01},
            MetricType.REAGENT_LEVEL: {"min": 0.1, "max": 1.0, "optimal": 0.8},
            MetricType.CYCLE_TIME: {"min": 30.0, "max": 300.0, "optimal": 120.0},
            MetricType.PURITY: {"min": 0.85, "max": 1.0, "optimal": 0.95}
        }
    
    def is_critical(self, metric: SynthesisMetric) -> bool:
        """Check if metric value is critical"""
        if metric.metric_type not in self.thresholds:
            return False
        
        threshold = self.thresholds[metric.metric_type]
        return metric.value < threshold["min"] * 0.9 or metric.value > threshold["max"] * 1.1
    
    def is_warning(self, metric: SynthesisMetric) -> bool:
        """Check if metric value warrants warning"""
        if metric.metric_type not in self.thresholds:
            return False
        
        threshold = self.thresholds[metric.metric_type]
        return (metric.value < threshold["min"] or 
                metric.value > threshold["max"]) and not self.is_critical(metric)
    
    def get_threshold(self, metric_type: MetricType) -> Optional[Dict[str, float]]:
        """Get threshold values for metric type"""
        return self.thresholds.get(metric_type)

class RealTimeMonitor:
    """
    Real-time DNA Synthesis Monitoring System
    Provides comprehensive monitoring, alerting, and dashboard capabilities
    """
    
    def __init__(self):
        self.monitoring_status = MonitoringStatus.STOPPED
        self.synthesis_jobs: Dict[str, SynthesisJob] = {}
        self.instruments: Dict[str, InstrumentStatus] = {}
        self.metrics_history: List[SynthesisMetric] = []
        self.alerts: List[Alert] = []
        self.threshold_manager = ThresholdManager()
        
        self.monitoring_thread: Optional[threading.Thread] = None
        self.stop_monitoring = threading.Event()
        self.alert_callbacks: List[Callable[[Alert], None]] = []
        
        # Dashboard data
        self.dashboard_data = {
            "active_jobs": 0,
            "total_alerts": 0,
            "critical_alerts": 0,
            "average_yield": 0.0,
            "instrument_utilization": 0.0,
            "last_updated": datetime.now()
        }
        
        # Initialize demo instruments
        self._initialize_demo_instruments()
    
    def _initialize_demo_instruments(self):
        """Initialize demo instruments for testing"""
        demo_instruments = [
            {
                "instrument_id": "SYNTH_001",
                "name": "Applied Biosystems 3900",
                "model": "3900 DNA Synthesizer",
                "temperature": 37.0,
                "pressure": 1.2
            },
            {
                "instrument_id": "SYNTH_002", 
                "name": "BioAutomation MerMade 12",
                "model": "MerMade 12",
                "temperature": 35.5,
                "pressure": 1.1
            },
            {
                "instrument_id": "SYNTH_003",
                "name": "GE Healthcare ÄKTA",
                "model": "ÄKTA oligopilot plus",
                "temperature": 36.8,
                "pressure": 1.3
            }
        ]
        
        for instrument in demo_instruments:
            self.instruments[instrument["instrument_id"]] = InstrumentStatus(
                instrument_id=instrument["instrument_id"],
                name=instrument["name"],
                model=instrument["model"],
                status="idle",
                current_job_id=None,
                temperature=instrument["temperature"],
                pressure=instrument["pressure"],
                last_maintenance=datetime.now() - timedelta(days=random.randint(1, 25)),
                total_runtime_hours=random.uniform(100.0, 800.0)
            )
    
    def start_monitoring(self):
        """Start real-time monitoring"""
        if self.monitoring_status == MonitoringStatus.ACTIVE:
            return
        
        self.monitoring_status = MonitoringStatus.ACTIVE
        self.stop_monitoring.clear()
        
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop)
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        
        print("Real-time monitoring started")
    
    def stop_monitoring_system(self):
        """Stop real-time monitoring"""
        self.monitoring_status = MonitoringStatus.STOPPED
        self.stop_monitoring.set()
        
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5.0)
        
        print("Real-time monitoring stopped")
    
    def pause_monitoring(self):
        """Pause monitoring"""
        self.monitoring_status = MonitoringStatus.PAUSED
        print("Real-time monitoring paused")
    
    def resume_monitoring(self):
        """Resume monitoring"""
        if self.monitoring_status == MonitoringStatus.PAUSED:
            self.monitoring_status = MonitoringStatus.ACTIVE
            print("Real-time monitoring resumed")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while not self.stop_monitoring.is_set():
            try:
                if self.monitoring_status == MonitoringStatus.ACTIVE:
                    self._collect_metrics()
                    self._check_alerts()
                    self._update_dashboard()
                
                time.sleep(1.0)  # Monitor every second
                
            except Exception as e:
                print(f"Monitoring error: {e}")
                self.monitoring_status = MonitoringStatus.ERROR
                time.sleep(5.0)  # Wait before retrying
    
    def _collect_metrics(self):
        """Collect metrics from all active synthesis jobs"""
        current_time = datetime.now()
        
        for job_id, job in self.synthesis_jobs.items():
            if job.current_phase not in [SynthesisPhase.COMPLETED, SynthesisPhase.FAILED]:
                instrument = self.instruments.get(job.instrument_id)
                if instrument:
                    # Simulate metric collection
                    metrics = self._simulate_metrics(job, instrument, current_time)
                    self.metrics_history.extend(metrics)
                    
                    # Keep only recent metrics (last 1000 measurements)
                    if len(self.metrics_history) > 1000:
                        self.metrics_history = self.metrics_history[-1000:]
    
    def _simulate_metrics(self, job: SynthesisJob, instrument: InstrumentStatus, 
                         timestamp: datetime) -> List[SynthesisMetric]:
        """Simulate metric collection from synthesis job"""
        metrics = []
        
        # Base values with some variation
        base_temperature = 37.0 + random.gauss(0, 1.0)
        base_pressure = 1.2 + random.gauss(0, 0.1)
        
        # Create metrics based on synthesis phase
        phase_factors = {
            SynthesisPhase.PREPARATION: {"temp": 0.9, "pressure": 0.8, "yield": 1.0},
            SynthesisPhase.ELONGATION: {"temp": 1.0, "pressure": 1.0, "yield": 0.95},
            SynthesisPhase.DEPROTECTION: {"temp": 1.1, "pressure": 1.2, "yield": 0.90},
            SynthesisPhase.CLEAVAGE: {"temp": 1.2, "pressure": 0.9, "yield": 0.85},
            SynthesisPhase.PURIFICATION: {"temp": 0.8, "pressure": 0.7, "yield": 0.95},
            SynthesisPhase.QUALITY_CONTROL: {"temp": 0.9, "pressure": 0.8, "yield": 1.0}
        }
        
        factor = phase_factors.get(job.current_phase, {"temp": 1.0, "pressure": 1.0, "yield": 0.9})
        
        # Temperature metric
        temp_value = base_temperature * factor["temp"]
        metrics.append(SynthesisMetric(
            metric_type=MetricType.TEMPERATURE,
            value=temp_value,
            unit="°C",
            timestamp=timestamp,
            synthesis_job_id=job.job_id,
            instrument_id=job.instrument_id,
            phase=job.current_phase,
            quality_score=random.uniform(0.9, 1.0)
        ))
        
        # Pressure metric
        pressure_value = base_pressure * factor["pressure"]
        metrics.append(SynthesisMetric(
            metric_type=MetricType.PRESSURE,
            value=pressure_value,
            unit="bar",
            timestamp=timestamp,
            synthesis_job_id=job.job_id,
            instrument_id=job.instrument_id,
            phase=job.current_phase,
            quality_score=random.uniform(0.9, 1.0)
        ))
        
        # Coupling efficiency (only during elongation)
        if job.current_phase == SynthesisPhase.ELONGATION:
            coupling_eff = random.uniform(0.96, 0.995)
            metrics.append(SynthesisMetric(
                metric_type=MetricType.COUPLING_EFFICIENCY,
                value=coupling_eff,
                unit="fraction",
                timestamp=timestamp,
                synthesis_job_id=job.job_id,
                instrument_id=job.instrument_id,
                phase=job.current_phase,
                quality_score=coupling_eff
            ))
        
        # Synthesis yield
        yield_value = factor["yield"] * random.uniform(0.85, 0.98)
        metrics.append(SynthesisMetric(
            metric_type=MetricType.SYNTHESIS_YIELD,
            value=yield_value,
            unit="fraction",
            timestamp=timestamp,
            synthesis_job_id=job.job_id,
            instrument_id=job.instrument_id,
            phase=job.current_phase,
            quality_score=yield_value
        ))
        
        # Flow rate
        flow_rate = 1.0 + random.gauss(0, 0.2)
        metrics.append(SynthesisMetric(
            metric_type=MetricType.FLOW_RATE,
            value=flow_rate,
            unit="mL/min",
            timestamp=timestamp,
            synthesis_job_id=job.job_id,
            instrument_id=job.instrument_id,
            phase=job.current_phase,
            quality_score=random.uniform(0.9, 1.0)
        ))
        
        # Update instrument status
        instrument.temperature = temp_value
        instrument.pressure = pressure_value
        
        return metrics
    
    def _check_alerts(self):
        """Check for alert conditions"""
        recent_metrics = [m for m in self.metrics_history 
                         if (datetime.now() - m.timestamp).seconds < 60]
        
        for metric in recent_metrics:
            alert = self._evaluate_metric_for_alerts(metric)
            if alert:
                self.alerts.append(alert)
                self._trigger_alert_callbacks(alert)
                
                # Limit alerts history
                if len(self.alerts) > 500:
                    self.alerts = self.alerts[-500:]
    
    def _evaluate_metric_for_alerts(self, metric: SynthesisMetric) -> Optional[Alert]:
        """Evaluate metric for alert conditions"""
        if self.threshold_manager.is_critical(metric):
            return self._create_alert(
                metric, AlertLevel.CRITICAL,
                f"Critical {metric.metric_type.value} level: {metric.value} {metric.unit}"
            )
        
        elif self.threshold_manager.is_warning(metric):
            return self._create_alert(
                metric, AlertLevel.WARNING,
                f"Warning {metric.metric_type.value} level: {metric.value} {metric.unit}"
            )
        
        # Check for specific conditions
        if metric.metric_type == MetricType.COUPLING_EFFICIENCY and metric.value < 0.95:
            return self._create_alert(
                metric, AlertLevel.ERROR,
                f"Low coupling efficiency detected: {metric.value:.3f}"
            )
        
        if metric.metric_type == MetricType.SYNTHESIS_YIELD and metric.value < 0.8:
            return self._create_alert(
                metric, AlertLevel.ERROR,
                f"Low synthesis yield: {metric.value:.3f}"
            )
        
        return None
    
    def _create_alert(self, metric: SynthesisMetric, level: AlertLevel, 
                     message: str) -> Alert:
        """Create alert from metric"""
        alert_id = f"ALT_{int(time.time())}_{random.randint(100, 999)}"
        threshold = self.threshold_manager.get_threshold(metric.metric_type)
        threshold_value = None
        
        if threshold:
            if level == AlertLevel.CRITICAL:
                threshold_value = threshold["min"] if metric.value < threshold["optimal"] else threshold["max"]
            elif level == AlertLevel.WARNING:
                threshold_value = threshold["optimal"]
        
        return Alert(
            alert_id=alert_id,
            synthesis_job_id=metric.synthesis_job_id,
            alert_level=level,
            message=message,
            metric_type=metric.metric_type,
            metric_value=metric.value,
            threshold_value=threshold_value,
            timestamp=metric.timestamp
        )
    
    def _trigger_alert_callbacks(self, alert: Alert):
        """Trigger registered alert callbacks"""
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                print(f"Alert callback error: {e}")
    
    def _update_dashboard(self):
        """Update dashboard data"""
        active_jobs = sum(1 for job in self.synthesis_jobs.values() 
                         if job.current_phase not in [SynthesisPhase.COMPLETED, SynthesisPhase.FAILED])
        
        recent_alerts = [a for a in self.alerts 
                        if (datetime.now() - a.timestamp).seconds < 3600]  # Last hour
        
        critical_alerts = sum(1 for a in recent_alerts 
                            if a.alert_level == AlertLevel.CRITICAL)
        
        # Calculate average yield from recent metrics
        yield_metrics = [m for m in self.metrics_history[-100:] 
                        if m.metric_type == MetricType.SYNTHESIS_YIELD]
        avg_yield = sum(m.value for m in yield_metrics) / len(yield_metrics) if yield_metrics else 0.0
        
        # Calculate instrument utilization
        busy_instruments = sum(1 for instr in self.instruments.values() 
                             if instr.current_job_id is not None)
        utilization = busy_instruments / len(self.instruments) if self.instruments else 0.0
        
        self.dashboard_data.update({
            "active_jobs": active_jobs,
            "total_alerts": len(recent_alerts),
            "critical_alerts": critical_alerts,
            "average_yield": avg_yield,
            "instrument_utilization": utilization,
            "last_updated": datetime.now()
        })
    
    def register_synthesis_job(self, job: SynthesisJob) -> bool:
        """Register new synthesis job for monitoring"""
        if job.instrument_id not in self.instruments:
            return False
        
        instrument = self.instruments[job.instrument_id]
        if instrument.current_job_id is not None:
            return False  # Instrument busy
        
        self.synthesis_jobs[job.job_id] = job
        instrument.current_job_id = job.job_id
        instrument.status = "running"
        
        # Create info alert for job start
        start_alert = Alert(
            alert_id=f"ALT_{int(time.time())}_{random.randint(100, 999)}",
            synthesis_job_id=job.job_id,
            alert_level=AlertLevel.INFO,
            message=f"Synthesis job {job.job_id} started on {instrument.name}",
            metric_type=None,
            metric_value=None,
            threshold_value=None,
            timestamp=datetime.now()
        )
        self.alerts.append(start_alert)
        
        return True
    
    def update_job_progress(self, job_id: str, current_cycle: int, 
                          current_phase: SynthesisPhase):
        """Update synthesis job progress"""
        if job_id in self.synthesis_jobs:
            job = self.synthesis_jobs[job_id]
            job.current_cycle = current_cycle
            job.current_phase = current_phase
            
            # Check if job completed
            if current_phase in [SynthesisPhase.COMPLETED, SynthesisPhase.FAILED]:
                instrument = self.instruments.get(job.instrument_id)
                if instrument:
                    instrument.current_job_id = None
                    instrument.status = "idle"
                
                # Create completion alert
                completion_alert = Alert(
                    alert_id=f"ALT_{int(time.time())}_{random.randint(100, 999)}",
                    synthesis_job_id=job_id,
                    alert_level=AlertLevel.INFO,
                    message=f"Synthesis job {job_id} {current_phase.value}",
                    metric_type=None,
                    metric_value=None,
                    threshold_value=None,
                    timestamp=datetime.now()
                )
                self.alerts.append(completion_alert)
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed status of synthesis job"""
        if job_id not in self.synthesis_jobs:
            return None
        
        job = self.synthesis_jobs[job_id]
        recent_metrics = [m for m in self.metrics_history 
                         if m.synthesis_job_id == job_id and 
                         (datetime.now() - m.timestamp).seconds < 300]  # Last 5 minutes
        
        job_alerts = [a for a in self.alerts 
                     if a.synthesis_job_id == job_id and 
                     (datetime.now() - a.timestamp).seconds < 3600]  # Last hour
        
        return {
            "job_id": job_id,
            "sequence": job.sequence[:50] + "..." if len(job.sequence) > 50 else job.sequence,
            "sequence_length": len(job.sequence),
            "instrument_id": job.instrument_id,
            "current_phase": job.current_phase.value,
            "progress_percentage": job.get_progress_percentage(),
            "current_cycle": job.current_cycle,
            "total_cycles": job.total_cycles,
            "started_at": job.started_at.isoformat(),
            "estimated_completion": job.estimated_completion.isoformat(),
            "recent_metrics_count": len(recent_metrics),
            "recent_alerts_count": len(job_alerts),
            "operator": job.operator
        }
    
    def get_instrument_status(self, instrument_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed instrument status"""
        if instrument_id not in self.instruments:
            return None
        
        instrument = self.instruments[instrument_id]
        recent_metrics = [m for m in self.metrics_history 
                         if m.instrument_id == instrument_id and 
                         (datetime.now() - m.timestamp).seconds < 300]
        
        return {
            "instrument_id": instrument_id,
            "name": instrument.name,
            "model": instrument.model,
            "status": instrument.status,
            "current_job_id": instrument.current_job_id,
            "temperature": instrument.temperature,
            "pressure": instrument.pressure,
            "last_maintenance": instrument.last_maintenance.isoformat(),
            "needs_maintenance": instrument.needs_maintenance(),
            "total_runtime_hours": instrument.total_runtime_hours,
            "error_count": instrument.error_count,
            "recent_metrics_count": len(recent_metrics)
        }
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get current dashboard data"""
        return self.dashboard_data.copy()
    
    def get_recent_alerts(self, hours: int = 1, 
                         level_filter: Optional[AlertLevel] = None) -> List[Dict[str, Any]]:
        """Get recent alerts with optional level filter"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        alerts = [a for a in self.alerts if a.timestamp >= cutoff_time]
        
        if level_filter:
            alerts = [a for a in alerts if a.alert_level == level_filter]
        
        return [
            {
                "alert_id": alert.alert_id,
                "synthesis_job_id": alert.synthesis_job_id,
                "level": alert.alert_level.value,
                "message": alert.message,
                "timestamp": alert.timestamp.isoformat(),
                "acknowledged": alert.acknowledged,
                "resolved": alert.resolved,
                "metric_type": alert.metric_type.value if alert.metric_type else None,
                "metric_value": alert.metric_value,
                "threshold_value": alert.threshold_value
            }
            for alert in sorted(alerts, key=lambda x: x.timestamp, reverse=True)
        ]
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge alert"""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                return True
        return False
    
    def resolve_alert(self, alert_id: str, resolution_notes: str = "") -> bool:
        """Resolve alert"""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.resolved = True
                alert.resolution_time = datetime.now()
                if resolution_notes:
                    alert.actions_taken.append(resolution_notes)
                return True
        return False
    
    def get_metrics_history(self, job_id: Optional[str] = None, 
                           metric_type: Optional[MetricType] = None,
                           hours: int = 1) -> List[Dict[str, Any]]:
        """Get metrics history with optional filters"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        metrics = [m for m in self.metrics_history if m.timestamp >= cutoff_time]
        
        if job_id:
            metrics = [m for m in metrics if m.synthesis_job_id == job_id]
        
        if metric_type:
            metrics = [m for m in metrics if m.metric_type == metric_type]
        
        return [
            {
                "metric_type": metric.metric_type.value,
                "value": metric.value,
                "unit": metric.unit,
                "timestamp": metric.timestamp.isoformat(),
                "synthesis_job_id": metric.synthesis_job_id,
                "instrument_id": metric.instrument_id,
                "phase": metric.phase.value,
                "quality_score": metric.quality_score
            }
            for metric in sorted(metrics, key=lambda x: x.timestamp)
        ]
    
    def register_alert_callback(self, callback: Callable[[Alert], None]):
        """Register callback for alert notifications"""
        self.alert_callbacks.append(callback)
    
    def get_monitoring_statistics(self) -> Dict[str, Any]:
        """Get comprehensive monitoring statistics"""
        total_jobs = len(self.synthesis_jobs)
        active_jobs = sum(1 for job in self.synthesis_jobs.values() 
                         if job.current_phase not in [SynthesisPhase.COMPLETED, SynthesisPhase.FAILED])
        
        completed_jobs = sum(1 for job in self.synthesis_jobs.values() 
                           if job.current_phase == SynthesisPhase.COMPLETED)
        
        failed_jobs = sum(1 for job in self.synthesis_jobs.values() 
                        if job.current_phase == SynthesisPhase.FAILED)
        
        total_alerts = len(self.alerts)
        alert_levels = {}
        for level in AlertLevel:
            alert_levels[level.value] = sum(1 for a in self.alerts if a.alert_level == level)
        
        # Calculate uptime
        uptime_hours = 0.0
        if self.monitoring_status == MonitoringStatus.ACTIVE:
            uptime_hours = 24.0  # Simulated uptime
        
        return {
            "monitoring_status": self.monitoring_status.value,
            "total_jobs_monitored": total_jobs,
            "active_jobs": active_jobs,
            "completed_jobs": completed_jobs,
            "failed_jobs": failed_jobs,
            "success_rate": completed_jobs / total_jobs if total_jobs > 0 else 0.0,
            "total_alerts": total_alerts,
            "alert_breakdown": alert_levels,
            "total_instruments": len(self.instruments),
            "active_instruments": sum(1 for i in self.instruments.values() if i.status == "running"),
            "metrics_collected": len(self.metrics_history),
            "system_uptime_hours": uptime_hours,
            "dashboard_last_updated": self.dashboard_data["last_updated"].isoformat()
        }
    
    def export_monitoring_data(self, hours: int = 24) -> Dict[str, Any]:
        """Export comprehensive monitoring data"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_metrics = [m for m in self.metrics_history if m.timestamp >= cutoff_time]
        recent_alerts = [a for a in self.alerts if a.timestamp >= cutoff_time]
        
        return {
            "export_timestamp": datetime.now().isoformat(),
            "time_range_hours": hours,
            "synthesis_jobs": [asdict(job) for job in self.synthesis_jobs.values()],
            "instruments": [asdict(instr) for instr in self.instruments.values()],
            "metrics": [asdict(metric) for metric in recent_metrics],
            "alerts": [asdict(alert) for alert in recent_alerts],
            "dashboard_data": self.dashboard_data,
            "monitoring_statistics": self.get_monitoring_statistics()
        }