"""
test_phase20_pilots.py - Test suite for Phase 20 societal pilot framework

Tests large-scale pilot management capabilities including:
- Multi-site deployment and coordination
- Participant enrollment and consent
- Real-time monitoring and metrics
- Incident response and escalation
- Phase 20 exit criteria validation
"""

import unittest
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from societal_pilot_framework import (
    SocietalPilotManager,
    PilotSite,
    PilotContext,
    PilotStatus,
    PilotMetrics,
    IncidentSeverity
)


class TestPhase20Pilots(unittest.TestCase):
    """Test suite for Phase 20 societal pilot framework"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = Path("/tmp/test_pilots")
        self.manager = SocietalPilotManager(data_dir=self.test_dir)
    
    def test_manager_initialization(self):
        """Test pilot manager initializes correctly"""
        self.assertIsNotNone(self.manager)
        self.assertEqual(len(self.manager.sites), 0)
        self.assertTrue(self.test_dir.exists())
        print("✓ Pilot manager initialization successful")
    
    def test_register_pilot_site(self):
        """Test pilot site registration"""
        site = PilotSite(
            site_id="EDU001",
            site_name="University Alpha",
            context=PilotContext.EDUCATION,
            location="California, USA",
            partner_organization="University Alpha",
            target_participants=300,
            irb_approval=True,
            irb_approval_date=datetime.now(),
            compliance_officer="Dr. Smith",
            professional_oversight=["Dr. Johnson (Clinical)", "Dr. Lee (Ethics)"]
        )
        
        site_id = self.manager.register_pilot_site(site)
        
        self.assertEqual(site_id, "EDU001")
        self.assertIn("EDU001", self.manager.sites)
        self.assertEqual(self.manager.sites["EDU001"].context, PilotContext.EDUCATION)
        
        print("✓ Pilot site registration successful")
    
    def test_multiple_site_registration(self):
        """Test registering multiple pilot sites"""
        sites = [
            PilotSite("EDU001", "University Alpha", PilotContext.EDUCATION, "CA, USA", "Univ Alpha", 300),
            PilotSite("HEALTH001", "Medical Center Beta", PilotContext.HEALTHCARE, "NY, USA", "Med Beta", 250),
            PilotSite("WORK001", "TechCorp Gamma", PilotContext.WORKPLACE, "WA, USA", "TechCorp", 400)
        ]
        
        for site in sites:
            site.irb_approval = True
            self.manager.register_pilot_site(site)
        
        self.assertEqual(len(self.manager.sites), 3)
        self.assertIn(PilotContext.EDUCATION, [s.context for s in self.manager.sites.values()])
        self.assertIn(PilotContext.HEALTHCARE, [s.context for s in self.manager.sites.values()])
        self.assertIn(PilotContext.WORKPLACE, [s.context for s in self.manager.sites.values()])
        
        print("✓ Multiple site registration successful (3 contexts)")
    
    def test_participant_enrollment(self):
        """Test participant enrollment with consent"""
        # Register site first
        site = PilotSite("EDU001", "University Alpha", PilotContext.EDUCATION, "CA", "Univ", 300)
        self.manager.register_pilot_site(site)
        
        # Enroll participant
        participant_id = self.manager.enroll_participant(
            site_id="EDU001",
            demographic_data={
                'age_range': '18-25',
                'gender': 'non-binary',
                'ethnicity': 'asian'
            },
            consent_given=True,
            baseline_measurements={
                'well_being_score': 6.5,
                'stress_level': 7.0,
                'academic_performance': 3.2
            }
        )
        
        self.assertIn("EDU001", participant_id)
        self.assertEqual(self.manager.sites["EDU001"].enrolled_participants, 1)
        self.assertEqual(self.manager.sites["EDU001"].active_participants, 1)
        self.assertIn(participant_id, self.manager.participants)
        
        print(f"✓ Participant enrollment successful: {participant_id}")
    
    def test_consent_enforcement(self):
        """Test that enrollment requires consent"""
        site = PilotSite("EDU001", "University Alpha", PilotContext.EDUCATION, "CA", "Univ", 300)
        self.manager.register_pilot_site(site)
        
        # Attempt enrollment without consent
        with self.assertRaises(ValueError):
            self.manager.enroll_participant(
                site_id="EDU001",
                demographic_data={'age_range': '18-25'},
                consent_given=False
            )
        
        print("✓ Consent enforcement validated")
    
    def test_pilot_metrics_recording(self):
        """Test recording and monitoring pilot metrics"""
        site = PilotSite("EDU001", "University Alpha", PilotContext.EDUCATION, "CA", "Univ", 300)
        self.manager.register_pilot_site(site)
        
        # Record metrics
        metrics = PilotMetrics(
            site_id="EDU001",
            timestamp=datetime.now(),
            active_users=150,
            total_sessions=1200,
            avg_session_duration_min=25.3,
            emotion_recognition_accuracy=0.89,
            crisis_detections=3,
            professional_escalations=2,
            user_satisfaction=4.3,
            system_uptime_percent=99.5,
            latency_p50_ms=42.0,
            latency_p95_ms=135.0,
            fairness_score=0.91,
            incidents=0
        )
        
        self.manager.record_pilot_metrics(metrics)
        
        self.assertGreater(len(self.manager.metrics_history), 0)
        print("✓ Pilot metrics recording successful")
    
    def test_metric_threshold_alerts(self):
        """Test automatic alerting on metric threshold violations"""
        site = PilotSite("EDU001", "University Alpha", PilotContext.EDUCATION, "CA", "Univ", 300)
        self.manager.register_pilot_site(site)
        
        # Record metrics with threshold violations
        bad_metrics = PilotMetrics(
            site_id="EDU001",
            timestamp=datetime.now(),
            active_users=50,
            total_sessions=100,
            avg_session_duration_min=10.0,
            emotion_recognition_accuracy=0.80,  # Below threshold (0.87)
            crisis_detections=1,
            professional_escalations=1,
            user_satisfaction=3.5,  # Below threshold (4.0)
            system_uptime_percent=97.0,  # Below threshold (99.0)
            latency_p50_ms=50.0,
            latency_p95_ms=180.0,  # Above threshold (150.0)
            fairness_score=0.85,  # Below threshold (0.88)
            incidents=2
        )
        
        initial_incidents = len(self.manager.incidents)
        self.manager.record_pilot_metrics(bad_metrics)
        
        # Should have created incidents for threshold violations
        self.assertGreater(len(self.manager.incidents), initial_incidents)
        
        print(f"✓ Metric threshold alerting validated ({len(self.manager.incidents)} incidents)")
    
    def test_crisis_escalation(self):
        """Test crisis escalation and professional alerting"""
        site = PilotSite("EDU001", "University Alpha", PilotContext.EDUCATION, "CA", "Univ", 300)
        site.professional_oversight = ["Dr. Johnson", "Dr. Lee"]
        self.manager.register_pilot_site(site)
        
        # Enroll participant
        participant_id = self.manager.enroll_participant(
            site_id="EDU001",
            demographic_data={'age_range': '18-25'},
            consent_given=True
        )
        
        # Create crisis escalation
        incident_id = self.manager.create_crisis_escalation(
            site_id="EDU001",
            participant_id=participant_id,
            crisis_data={
                'level': 'CRITICAL',
                'indicators': ['severe_distress', 'self_harm_language'],
                'confidence': 0.95
            }
        )
        
        self.assertIsNotNone(incident_id)
        self.assertGreater(len(self.manager.incidents), 0)
        
        # Check incident severity
        incident = [i for i in self.manager.incidents if i.incident_id == incident_id][0]
        self.assertEqual(incident.severity, IncidentSeverity.CRITICAL)
        self.assertEqual(incident.category, "crisis_escalation")
        
        print(f"✓ Crisis escalation validated: {incident_id}")
    
    def test_pilot_dashboard(self):
        """Test comprehensive pilot dashboard generation"""
        # Set up multiple sites
        for i, context in enumerate([PilotContext.EDUCATION, PilotContext.HEALTHCARE, PilotContext.WORKPLACE]):
            site = PilotSite(
                f"SITE{i+1:03d}",
                f"Site {i+1}",
                context,
                "USA",
                f"Partner {i+1}",
                300
            )
            site.status = PilotStatus.ACTIVE
            site.irb_approval = True
            self.manager.register_pilot_site(site)
            
            # Enroll participants
            for j in range(200):  # Enroll 200 per site
                self.manager.enroll_participant(
                    site_id=site.site_id,
                    demographic_data={'age_range': '18-65'},
                    consent_given=True
                )
            
            # Record metrics
            metrics = PilotMetrics(
                site_id=site.site_id,
                timestamp=datetime.now(),
                active_users=150,
                total_sessions=1000,
                avg_session_duration_min=20.0,
                emotion_recognition_accuracy=0.88,
                crisis_detections=2,
                professional_escalations=1,
                user_satisfaction=4.2,
                system_uptime_percent=99.7,
                latency_p50_ms=40.0,
                latency_p95_ms=140.0,
                fairness_score=0.90,
                incidents=0
            )
            self.manager.record_pilot_metrics(metrics)
        
        # Get dashboard
        dashboard = self.manager.get_pilot_dashboard()
        
        # Validate dashboard structure
        self.assertIn('sites', dashboard)
        self.assertIn('participants', dashboard)
        self.assertIn('performance', dashboard)
        self.assertIn('safety', dashboard)
        self.assertIn('phase20_exit_criteria', dashboard)
        
        # Check Phase 20 exit criteria
        criteria = dashboard['phase20_exit_criteria']
        self.assertEqual(criteria['sites_deployed'], 3)
        self.assertEqual(criteria['target_sites'], 3)
        self.assertGreaterEqual(criteria['engagement_rate'], 70.0)
        
        print("✓ Pilot dashboard generation successful")
        print(f"  - Sites: {dashboard['sites']['total']} (3 contexts)")
        print(f"  - Participants: {dashboard['participants']['total_enrolled']} enrolled, "
              f"{dashboard['participants']['total_active']} active")
        print(f"  - Engagement: {dashboard['participants']['engagement_rate']:.1f}%")
        print(f"  - Performance: accuracy={dashboard['performance']['avg_emotion_accuracy']:.3f}, "
              f"satisfaction={dashboard['performance']['avg_user_satisfaction']:.2f}")
    
    def test_longitudinal_tracking(self):
        """Test longitudinal well-being tracking"""
        site = PilotSite("EDU001", "University Alpha", PilotContext.EDUCATION, "CA", "Univ", 300)
        self.manager.register_pilot_site(site)
        
        # Enroll participant with baseline
        participant_id = self.manager.enroll_participant(
            site_id="EDU001",
            demographic_data={'age_range': '18-25'},
            consent_given=True,
            baseline_measurements={'well_being_score': 6.0}
        )
        
        # Simulate longitudinal measurements
        participant = self.manager.participants[participant_id]
        for days in [7, 14, 21, 28]:
            participant.longitudinal_data.append({
                'timestamp': datetime.now() + timedelta(days=days),
                'metrics': {
                    'well_being_score': 6.0 + (days * 0.1)  # Gradual improvement
                }
            })
        
        # Generate report
        report = self.manager.generate_longitudinal_report(participant_id, 'well_being_score')
        
        self.assertEqual(report['baseline'], 6.0)
        self.assertGreater(report['current'], report['baseline'])
        self.assertTrue(report['improvement'])
        
        # Check Phase 20 target (20% improvement)
        if report['percent_change'] >= 20.0:
            print(f"✓ Longitudinal tracking validated: {report['percent_change']:.1f}% improvement "
                  f"(meets 20% target)")
        else:
            print(f"✓ Longitudinal tracking validated: {report['percent_change']:.1f}% improvement "
                  f"(target: 20%)")
    
    def test_phase20_exit_criteria(self):
        """Test Phase 20 exit criteria tracking"""
        # Set up 3 active sites
        contexts = [PilotContext.EDUCATION, PilotContext.HEALTHCARE, PilotContext.WORKPLACE]
        for i, context in enumerate(contexts):
            site = PilotSite(f"SITE{i+1:03d}", f"Site {i+1}", context, "USA", f"Partner {i+1}", 300)
            site.status = PilotStatus.ACTIVE
            site.irb_approval = True
            self.manager.register_pilot_site(site)
            
            # Enroll 250 participants (target: 70% of 300 = 210)
            for j in range(250):
                self.manager.enroll_participant(
                    site_id=site.site_id,
                    demographic_data={'age_range': '18-65'},
                    consent_given=True
                )
            
            # Set 220 as active (88% engagement)
            site.active_participants = 220
            
            # Record good metrics
            metrics = PilotMetrics(
                site_id=site.site_id,
                timestamp=datetime.now(),
                active_users=220,
                total_sessions=2000,
                avg_session_duration_min=25.0,
                emotion_recognition_accuracy=0.89,  # > 0.87 target
                crisis_detections=5,
                professional_escalations=4,
                user_satisfaction=4.3,  # > 4.0 target
                system_uptime_percent=99.8,
                latency_p50_ms=38.0,
                latency_p95_ms=145.0,  # < 150 target
                fairness_score=0.90,  # > 0.88 target
                incidents=0
            )
            self.manager.record_pilot_metrics(metrics)
        
        # Get dashboard with exit criteria
        dashboard = self.manager.get_pilot_dashboard()
        criteria = dashboard['phase20_exit_criteria']
        
        print("\n" + "="*60)
        print("Phase 20 Exit Criteria Validation")
        print("="*60)
        print(f"Sites deployed: {criteria['sites_deployed']}/{criteria['target_sites']} "
              f"{'✓' if criteria['sites_deployed'] >= criteria['target_sites'] else '✗'}")
        print(f"Engagement rate: {criteria['engagement_rate']:.1f}%/{criteria['target_engagement']:.1f}% "
              f"{'✓' if criteria['engagement_rate'] >= criteria['target_engagement'] else '✗'}")
        print(f"Accuracy: {criteria['accuracy']:.3f}/{criteria['target_accuracy']:.3f} "
              f"{'✓' if criteria['accuracy'] >= criteria['target_accuracy'] else '✗'}")
        print(f"User satisfaction: {criteria['user_satisfaction']:.2f}/{criteria['target_satisfaction']:.2f} "
              f"{'✓' if criteria['user_satisfaction'] >= criteria['target_satisfaction'] else '✗'}")
        print(f"Fairness score: {criteria['fairness_score']:.2f}/{criteria['target_fairness']:.2f} "
              f"{'✓' if criteria['fairness_score'] >= criteria['target_fairness'] else '✗'}")
        print(f"Critical incidents: {criteria['critical_incidents']}/{criteria['target_critical_incidents']} "
              f"{'✓' if criteria['critical_incidents'] == criteria['target_critical_incidents'] else '✗'}")
        print("="*60 + "\n")
        
        # Validate all criteria
        self.assertGreaterEqual(criteria['sites_deployed'], 3)
        self.assertGreaterEqual(criteria['engagement_rate'], 70.0)
        self.assertGreaterEqual(criteria['accuracy'], 0.87)
        self.assertGreaterEqual(criteria['user_satisfaction'], 4.0)
        self.assertGreaterEqual(criteria['fairness_score'], 0.88)
        self.assertEqual(criteria['critical_incidents'], 0)


if __name__ == '__main__':
    print("\n" + "="*70)
    print("Phase 20: Large-Scale Societal Pilot Test Suite")
    print("="*70 + "\n")
    
    # Run tests
    unittest.main(verbosity=2, exit=False)
    
    print("\n" + "="*70)
    print("Phase 20 Testing Complete")
    print("="*70 + "\n")
