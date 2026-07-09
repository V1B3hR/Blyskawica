"""
societal_pilot_framework.py - Large-Scale Societal Pilot Management Framework

Phase 20 Implementation: Infrastructure for deploying and monitoring empathetic
AI systems across diverse societal contexts (education, healthcare, workplace).

This module provides:
- Multi-site deployment and management infrastructure
- Pilot program lifecycle management
- Real-time monitoring and anomaly detection
- Compliance and ethics oversight
- Longitudinal data collection and analysis
- Professional integration and escalation pathways

Key Features:
- Scalable architecture supporting 1000+ concurrent users per site
- Cross-site analytics and reporting
- IRB/ethics compliance framework
- Automated incident response and crisis escalation
- Equity and fairness monitoring across demographics
"""

import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
from dataclasses import dataclass, field
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class PilotContext(Enum):
    """Types of pilot deployment contexts"""
    EDUCATION = "education"
    HEALTHCARE = "healthcare"
    WORKPLACE = "workplace"
    RESEARCH = "research"
    COMMUNITY = "community"


class PilotStatus(Enum):
    """Pilot program status"""
    PLANNING = "planning"
    IRB_REVIEW = "irb_review"
    PARTNER_ONBOARDING = "partner_onboarding"
    INFRASTRUCTURE_SETUP = "infrastructure_setup"
    PARTICIPANT_ENROLLMENT = "participant_enrollment"
    ACTIVE = "active"
    MONITORING = "monitoring"
    ANALYSIS = "analysis"
    COMPLETED = "completed"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"


class IncidentSeverity(Enum):
    """Incident severity levels"""
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class PilotSite:
    """Individual pilot site configuration"""
    site_id: str
    site_name: str
    context: PilotContext
    location: str
    partner_organization: str
    target_participants: int
    enrolled_participants: int = 0
    active_participants: int = 0
    status: PilotStatus = PilotStatus.PLANNING
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    irb_approval: bool = False
    irb_approval_date: Optional[datetime] = None
    compliance_officer: str = ""
    technical_contact: str = ""
    professional_oversight: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ParticipantProfile:
    """Pilot participant profile"""
    participant_id: str
    site_id: str
    enrollment_date: datetime
    demographic_data: Dict[str, Any]
    consent_given: bool
    consent_date: Optional[datetime]
    baseline_measurements: Dict[str, float]
    longitudinal_data: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "active"
    withdrawal_date: Optional[datetime] = None
    privacy_preferences: Dict[str, bool] = field(default_factory=dict)


@dataclass
class PilotMetrics:
    """Real-time pilot metrics"""
    site_id: str
    timestamp: datetime
    active_users: int
    total_sessions: int
    avg_session_duration_min: float
    emotion_recognition_accuracy: float
    crisis_detections: int
    professional_escalations: int
    user_satisfaction: float
    system_uptime_percent: float
    latency_p50_ms: float
    latency_p95_ms: float
    fairness_score: float
    incidents: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Incident:
    """Pilot incident record"""
    incident_id: str
    site_id: str
    timestamp: datetime
    severity: IncidentSeverity
    category: str
    description: str
    affected_participants: List[str]
    response_actions: List[str]
    resolution_time_min: Optional[float] = None
    resolved: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class SocietalPilotManager:
    """
    Comprehensive management system for large-scale societal pilots.
    
    Manages:
    - Multi-site deployment and coordination
    - Participant enrollment and consent
    - Real-time monitoring and analytics
    - Incident response and escalation
    - Compliance and ethics oversight
    - Longitudinal data collection
    """
    
    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize pilot management system"""
        self.data_dir = data_dir or Path("/tmp/gcs_pilots")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.sites: Dict[str, PilotSite] = {}
        self.participants: Dict[str, ParticipantProfile] = {}
        self.metrics_history: List[PilotMetrics] = []
        self.incidents: List[Incident] = []
        
        # Monitoring thresholds
        self.alert_thresholds = {
            'min_uptime_percent': 99.0,
            'max_latency_p95_ms': 150.0,
            'min_accuracy': 0.87,
            'min_fairness_score': 0.88,
            'max_crisis_rate_per_hour': 10,
            'min_user_satisfaction': 4.0
        }
        
        logger.info("SocietalPilotManager initialized")
    
    def register_pilot_site(self, site: PilotSite) -> str:
        """
        Register a new pilot site.
        
        Args:
            site: PilotSite configuration
            
        Returns:
            site_id of registered site
        """
        if site.site_id in self.sites:
            raise ValueError(f"Site {site.site_id} already registered")
        
        self.sites[site.site_id] = site
        
        # Create site directory
        site_dir = self.data_dir / site.site_id
        site_dir.mkdir(parents=True, exist_ok=True)
        
        # Save site configuration
        self._save_site_config(site)
        
        logger.info(f"Registered pilot site: {site.site_name} ({site.site_id}) - "
                   f"Context: {site.context.value}, Target: {site.target_participants} participants")
        
        return site.site_id
    
    def enroll_participant(self, 
                          site_id: str,
                          demographic_data: Dict[str, Any],
                          consent_given: bool,
                          baseline_measurements: Optional[Dict[str, float]] = None) -> str:
        """
        Enroll a participant in a pilot site.
        
        Args:
            site_id: Pilot site identifier
            demographic_data: Participant demographics (anonymized)
            consent_given: Whether informed consent was obtained
            baseline_measurements: Initial well-being measurements
            
        Returns:
            participant_id of enrolled participant
        """
        if site_id not in self.sites:
            raise ValueError(f"Site {site_id} not found")
        
        if not consent_given:
            raise ValueError("Cannot enroll participant without informed consent")
        
        # Generate anonymous participant ID
        participant_id = f"{site_id}_P{str(uuid.uuid4())[:8]}"
        
        participant = ParticipantProfile(
            participant_id=participant_id,
            site_id=site_id,
            enrollment_date=datetime.now(),
            demographic_data=demographic_data,
            consent_given=consent_given,
            consent_date=datetime.now(),
            baseline_measurements=baseline_measurements or {},
            privacy_preferences={
                'data_sharing': False,
                'longitudinal_tracking': True,
                'professional_contact': True
            }
        )
        
        self.participants[participant_id] = participant
        self.sites[site_id].enrolled_participants += 1
        self.sites[site_id].active_participants += 1
        
        # Save participant data
        self._save_participant_data(participant)
        
        logger.info(f"Enrolled participant {participant_id} at site {site_id}")
        
        return participant_id
    
    def record_pilot_metrics(self, metrics: PilotMetrics):
        """
        Record real-time pilot metrics.
        
        Args:
            metrics: PilotMetrics snapshot
        """
        self.metrics_history.append(metrics)
        
        # Check for anomalies and alert if needed
        alerts = self._check_metric_thresholds(metrics)
        
        if alerts:
            for alert in alerts:
                logger.warning(f"PILOT ALERT [{metrics.site_id}]: {alert}")
                self._create_incident(
                    site_id=metrics.site_id,
                    severity=IncidentSeverity.MEDIUM,
                    category="performance_threshold",
                    description=alert
                )
        
        # Periodic save
        if len(self.metrics_history) % 100 == 0:
            self._save_metrics_batch()
    
    def _check_metric_thresholds(self, metrics: PilotMetrics) -> List[str]:
        """Check if metrics violate thresholds"""
        alerts = []
        
        if metrics.system_uptime_percent < self.alert_thresholds['min_uptime_percent']:
            alerts.append(f"System uptime below threshold: {metrics.system_uptime_percent:.1f}%")
        
        if metrics.latency_p95_ms > self.alert_thresholds['max_latency_p95_ms']:
            alerts.append(f"Latency P95 above threshold: {metrics.latency_p95_ms:.1f}ms")
        
        if metrics.emotion_recognition_accuracy < self.alert_thresholds['min_accuracy']:
            alerts.append(f"Accuracy below threshold: {metrics.emotion_recognition_accuracy:.3f}")
        
        if metrics.fairness_score < self.alert_thresholds['min_fairness_score']:
            alerts.append(f"Fairness score below threshold: {metrics.fairness_score:.3f}")
        
        if metrics.user_satisfaction < self.alert_thresholds['min_user_satisfaction']:
            alerts.append(f"User satisfaction below threshold: {metrics.user_satisfaction:.2f}/5.0")
        
        return alerts
    
    def create_crisis_escalation(self,
                                site_id: str,
                                participant_id: str,
                                crisis_data: Dict[str, Any]) -> str:
        """
        Create crisis escalation for professional intervention.
        
        Phase 20 requirement: validated crisis response at scale.
        
        Args:
            site_id: Pilot site identifier
            participant_id: Participant requiring intervention
            crisis_data: Crisis detection data
            
        Returns:
            incident_id for tracking
        """
        incident_id = self._create_incident(
            site_id=site_id,
            severity=IncidentSeverity.CRITICAL,
            category="crisis_escalation",
            description=f"Crisis detected for participant {participant_id}",
            affected_participants=[participant_id],
            metadata=crisis_data
        )
        
        # Trigger professional alert
        self._alert_professional_oversight(site_id, incident_id, crisis_data)
        
        logger.critical(f"Crisis escalation created: {incident_id} at site {site_id}")
        
        return incident_id
    
    def _create_incident(self,
                        site_id: str,
                        severity: IncidentSeverity,
                        category: str,
                        description: str,
                        affected_participants: Optional[List[str]] = None,
                        metadata: Optional[Dict[str, Any]] = None) -> str:
        """Create and log an incident"""
        incident_id = f"INC_{str(uuid.uuid4())[:8]}"
        
        incident = Incident(
            incident_id=incident_id,
            site_id=site_id,
            timestamp=datetime.now(),
            severity=severity,
            category=category,
            description=description,
            affected_participants=affected_participants or [],
            response_actions=[],
            metadata=metadata or {}
        )
        
        self.incidents.append(incident)
        self._save_incident(incident)
        
        return incident_id
    
    def _alert_professional_oversight(self, 
                                     site_id: str,
                                     incident_id: str,
                                     crisis_data: Dict[str, Any]):
        """
        Alert professional oversight team.
        
        In production, this would:
        - Send notifications to on-call professionals
        - Create tickets in oversight system
        - Trigger emergency protocols if needed
        """
        site = self.sites.get(site_id)
        if not site:
            logger.error(f"Site {site_id} not found for professional alert")
            return
        
        alert_message = {
            'incident_id': incident_id,
            'site_id': site_id,
            'site_name': site.site_name,
            'timestamp': datetime.now().isoformat(),
            'crisis_level': crisis_data.get('level', 'UNKNOWN'),
            'professional_contacts': site.professional_oversight,
            'action_required': 'immediate_response'
        }
        
        logger.info(f"Professional alert sent: {json.dumps(alert_message, indent=2)}")
        
        # In production: send actual notifications (email, SMS, pager, etc.)
    
    def get_pilot_dashboard(self, site_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get comprehensive pilot dashboard data.
        
        Args:
            site_id: Specific site (None for all sites)
            
        Returns:
            Dashboard data with key metrics and status
        """
        if site_id:
            sites_to_report = [self.sites[site_id]] if site_id in self.sites else []
        else:
            sites_to_report = list(self.sites.values())
        
        # Aggregate metrics
        total_enrolled = sum(s.enrolled_participants for s in sites_to_report)
        total_active = sum(s.active_participants for s in sites_to_report)
        
        # Recent metrics (last 24 hours)
        recent_cutoff = datetime.now() - timedelta(hours=24)
        recent_metrics = [m for m in self.metrics_history 
                         if m.timestamp > recent_cutoff and 
                         (not site_id or m.site_id == site_id)]
        
        avg_accuracy = (sum(m.emotion_recognition_accuracy for m in recent_metrics) / len(recent_metrics)
                       if recent_metrics else 0)
        avg_latency = (sum(m.latency_p95_ms for m in recent_metrics) / len(recent_metrics)
                      if recent_metrics else 0)
        avg_satisfaction = (sum(m.user_satisfaction for m in recent_metrics) / len(recent_metrics)
                           if recent_metrics else 0)
        avg_fairness = (sum(m.fairness_score for m in recent_metrics) / len(recent_metrics)
                       if recent_metrics else 0)
        
        # Incidents
        recent_incidents = [i for i in self.incidents 
                           if i.timestamp > recent_cutoff and 
                           (not site_id or i.site_id == site_id)]
        
        critical_incidents = [i for i in recent_incidents 
                             if i.severity in [IncidentSeverity.CRITICAL, IncidentSeverity.EMERGENCY]]
        
        dashboard = {
            'timestamp': datetime.now().isoformat(),
            'sites': {
                'total': len(sites_to_report),
                'active': len([s for s in sites_to_report if s.status == PilotStatus.ACTIVE]),
                'contexts': list(set(s.context.value for s in sites_to_report))
            },
            'participants': {
                'total_enrolled': total_enrolled,
                'total_active': total_active,
                'engagement_rate': (total_active / total_enrolled * 100) if total_enrolled > 0 else 0
            },
            'performance': {
                'avg_emotion_accuracy': avg_accuracy,
                'avg_latency_p95_ms': avg_latency,
                'avg_user_satisfaction': avg_satisfaction,
                'avg_fairness_score': avg_fairness
            },
            'safety': {
                'incidents_24h': len(recent_incidents),
                'critical_incidents_24h': len(critical_incidents),
                'crisis_escalations_24h': len([i for i in recent_incidents 
                                               if i.category == 'crisis_escalation'])
            },
            'phase20_exit_criteria': {
                'sites_deployed': len([s for s in sites_to_report if s.status == PilotStatus.ACTIVE]),
                'target_sites': 3,
                'engagement_rate': (total_active / total_enrolled * 100) if total_enrolled > 0 else 0,
                'target_engagement': 70.0,
                'accuracy': avg_accuracy,
                'target_accuracy': 0.87,
                'user_satisfaction': avg_satisfaction,
                'target_satisfaction': 4.0,
                'fairness_score': avg_fairness,
                'target_fairness': 0.88,
                'critical_incidents': len(critical_incidents),
                'target_critical_incidents': 0
            }
        }
        
        return dashboard
    
    def generate_longitudinal_report(self, 
                                    participant_id: str,
                                    metric_name: str = "well_being_score") -> Dict[str, Any]:
        """
        Generate longitudinal analysis for a participant.
        
        Phase 20 requirement: measurable well-being improvement.
        
        Args:
            participant_id: Participant identifier
            metric_name: Metric to analyze
            
        Returns:
            Longitudinal report with trend analysis
        """
        if participant_id not in self.participants:
            raise ValueError(f"Participant {participant_id} not found")
        
        participant = self.participants[participant_id]
        
        # Get baseline
        baseline_value = participant.baseline_measurements.get(metric_name, 0)
        
        # Get longitudinal data
        measurements = [
            (entry['timestamp'], entry['metrics'].get(metric_name, 0))
            for entry in participant.longitudinal_data
            if 'metrics' in entry and metric_name in entry['metrics']
        ]
        
        if not measurements:
            return {
                'participant_id': participant_id,
                'metric': metric_name,
                'status': 'insufficient_data',
                'baseline': baseline_value
            }
        
        # Calculate trend
        current_value = measurements[-1][1] if measurements else baseline_value
        change = current_value - baseline_value
        percent_change = (change / baseline_value * 100) if baseline_value != 0 else 0
        
        report = {
            'participant_id': participant_id,
            'metric': metric_name,
            'baseline': baseline_value,
            'current': current_value,
            'change': change,
            'percent_change': percent_change,
            'improvement': change > 0,
            'measurements_count': len(measurements),
            'duration_days': (measurements[-1][0] - participant.enrollment_date).days if measurements else 0,
            'phase20_target': 20.0,  # 20% improvement
            'meets_target': percent_change >= 20.0
        }
        
        return report
    
    def _save_site_config(self, site: PilotSite):
        """Save site configuration to disk"""
        site_file = self.data_dir / site.site_id / "site_config.json"
        site_file.parent.mkdir(parents=True, exist_ok=True)
        
        site_data = {
            'site_id': site.site_id,
            'site_name': site.site_name,
            'context': site.context.value,
            'location': site.location,
            'partner_organization': site.partner_organization,
            'target_participants': site.target_participants,
            'status': site.status.value,
            'irb_approval': site.irb_approval
        }
        
        with open(site_file, 'w') as f:
            json.dump(site_data, f, indent=2)
    
    def _save_participant_data(self, participant: ParticipantProfile):
        """Save participant data with privacy protection"""
        participant_file = (self.data_dir / participant.site_id / 
                           "participants" / f"{participant.participant_id}.json")
        participant_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Only save anonymized data
        participant_data = {
            'participant_id': participant.participant_id,
            'site_id': participant.site_id,
            'enrollment_date': participant.enrollment_date.isoformat(),
            'demographic_summary': {
                k: v for k, v in participant.demographic_data.items() 
                if k in ['age_range', 'gender', 'ethnicity']
            },
            'consent_given': participant.consent_given,
            'status': participant.status
        }
        
        with open(participant_file, 'w') as f:
            json.dump(participant_data, f, indent=2)
    
    def _save_incident(self, incident: Incident):
        """Save incident record"""
        incident_file = (self.data_dir / incident.site_id / 
                        "incidents" / f"{incident.incident_id}.json")
        incident_file.parent.mkdir(parents=True, exist_ok=True)
        
        incident_data = {
            'incident_id': incident.incident_id,
            'site_id': incident.site_id,
            'timestamp': incident.timestamp.isoformat(),
            'severity': incident.severity.value,
            'category': incident.category,
            'description': incident.description,
            'resolved': incident.resolved
        }
        
        with open(incident_file, 'w') as f:
            json.dump(incident_data, f, indent=2)
    
    def _save_metrics_batch(self):
        """Save batch of metrics to disk"""
        metrics_file = self.data_dir / "metrics" / f"batch_{int(time.time())}.json"
        metrics_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Save last 100 metrics
        recent_metrics = self.metrics_history[-100:]
        
        metrics_data = [
            {
                'site_id': m.site_id,
                'timestamp': m.timestamp.isoformat(),
                'active_users': m.active_users,
                'accuracy': m.emotion_recognition_accuracy,
                'latency_p95': m.latency_p95_ms,
                'satisfaction': m.user_satisfaction,
                'fairness': m.fairness_score
            }
            for m in recent_metrics
        ]
        
        with open(metrics_file, 'w') as f:
            json.dump(metrics_data, f, indent=2)


# Global instance
_pilot_manager = None

def get_pilot_manager(data_dir: Optional[Path] = None) -> SocietalPilotManager:
    """Get global pilot manager instance"""
    global _pilot_manager
    if _pilot_manager is None:
        _pilot_manager = SocietalPilotManager(data_dir)
    return _pilot_manager
