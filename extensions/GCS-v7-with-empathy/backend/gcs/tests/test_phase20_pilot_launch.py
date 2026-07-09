#!/usr/bin/env python3
"""
test_phase20_pilot_launch.py - Tests for Q1 2026 Pilot Site Launch

Validates the Phase 20 pilot site launch functionality and ensures
all exit criteria are properly configured.
"""

import unittest
import sys
from pathlib import Path
from datetime import datetime
import shutil
import tempfile

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from phase20_pilot_launch import Phase20PilotLauncher
from societal_pilot_framework import PilotContext, PilotStatus
from phase20_irb_compliance import ComplianceStatus


class TestPhase20PilotLaunch(unittest.TestCase):
    """Test suite for Phase 20 pilot site launch"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.launcher = Phase20PilotLauncher(data_dir=self.temp_dir)
    
    def tearDown(self):
        """Clean up test environment"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_launcher_initialization(self):
        """Test launcher initializes correctly"""
        self.assertIsNotNone(self.launcher.pilot_manager)
        self.assertIsNotNone(self.launcher.compliance_manager)
        self.assertEqual(len(self.launcher.launch_status['launched_sites']), 0)
    
    def test_create_education_pilot_site(self):
        """Test education pilot site creation"""
        site = self.launcher.create_education_pilot_site(
            site_id="TEST_EDU001",
            university_name="Test University",
            location="Test City, USA"
        )
        
        self.assertEqual(site.site_id, "TEST_EDU001")
        self.assertEqual(site.context, PilotContext.EDUCATION)
        self.assertEqual(site.target_participants, 400)
        self.assertIn('FERPA', site.metadata.get('regulatory_frameworks', []))
        self.assertIn('academic_stress', site.metadata.get('focus_areas', []))
    
    def test_create_healthcare_pilot_site(self):
        """Test healthcare pilot site creation"""
        site = self.launcher.create_healthcare_pilot_site(
            site_id="TEST_HCR001",
            facility_name="Test Hospital",
            location="Test City, USA"
        )
        
        self.assertEqual(site.site_id, "TEST_HCR001")
        self.assertEqual(site.context, PilotContext.HEALTHCARE)
        self.assertEqual(site.target_participants, 300)
        self.assertIn('HIPAA', site.metadata.get('regulatory_frameworks', []))
        self.assertIn('chronic_condition_management', site.metadata.get('focus_areas', []))
    
    def test_create_workplace_pilot_site(self):
        """Test workplace pilot site creation"""
        site = self.launcher.create_workplace_pilot_site(
            site_id="TEST_WRK001",
            company_name="Test Corporation",
            location="Test City, USA"
        )
        
        self.assertEqual(site.site_id, "TEST_WRK001")
        self.assertEqual(site.context, PilotContext.WORKPLACE)
        self.assertEqual(site.target_participants, 400)
        self.assertIn('stress_management', site.metadata.get('focus_areas', []))
        self.assertIn('no_individual_performance_tracking', 
                     site.metadata.get('privacy_safeguards', []))
    
    def test_configure_irb_approval(self):
        """Test IRB approval configuration"""
        site = self.launcher.create_education_pilot_site(
            site_id="TEST_EDU001",
            university_name="Test University",
            location="Test City, USA"
        )
        
        approval = self.launcher.configure_irb_approval(site)
        
        self.assertEqual(approval.irb_id, "TEST_EDU001_IRB")
        self.assertEqual(approval.institution, "Test University")
        self.assertEqual(approval.status, ComplianceStatus.IN_PROGRESS)
        self.assertGreater(len(approval.conditions), 0)
        self.assertEqual(approval.approval_date.year, 2026)  # Q1 2026
    
    def test_infrastructure_readiness_check(self):
        """Test infrastructure readiness validation"""
        site = self.launcher.create_education_pilot_site(
            site_id="TEST_EDU001",
            university_name="Test University",
            location="Test City, USA"
        )
        
        ready = self.launcher._check_infrastructure_readiness(site)
        self.assertTrue(ready)  # Infrastructure is ready
    
    def test_compliance_validation(self):
        """Test compliance requirements validation"""
        site = self.launcher.create_healthcare_pilot_site(
            site_id="TEST_HCR001",
            facility_name="Test Hospital",
            location="Test City, USA"
        )
        
        approval = self.launcher.configure_irb_approval(site)
        valid = self.launcher._validate_compliance(site, approval)
        self.assertTrue(valid)
    
    def test_partner_readiness_check(self):
        """Test partner organization readiness"""
        site = self.launcher.create_workplace_pilot_site(
            site_id="TEST_WRK001",
            company_name="Test Corporation",
            location="Test City, USA"
        )
        
        ready = self.launcher._check_partner_readiness(site)
        self.assertTrue(ready)
    
    def test_professional_oversight_check(self):
        """Test professional oversight validation"""
        site = self.launcher.create_education_pilot_site(
            site_id="TEST_EDU001",
            university_name="Test University",
            location="Test City, USA"
        )
        
        ready = self.launcher._check_professional_oversight(site)
        self.assertTrue(ready)
        self.assertGreaterEqual(len(site.professional_oversight), 2)
    
    def test_technical_integration_check(self):
        """Test technical integration readiness"""
        site = self.launcher.create_healthcare_pilot_site(
            site_id="TEST_HCR001",
            facility_name="Test Hospital",
            location="Test City, USA"
        )
        
        ready = self.launcher._check_technical_integration(site)
        self.assertTrue(ready)
        self.assertGreater(len(site.metadata.get('integrations', [])), 0)
    
    def test_launch_single_pilot_site(self):
        """Test launching a single pilot site"""
        site = self.launcher.create_education_pilot_site(
            site_id="TEST_EDU001",
            university_name="Test University",
            location="Test City, USA"
        )
        
        result = self.launcher.launch_pilot_site(site, dry_run=False)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['site_id'], "TEST_EDU001")
        self.assertTrue(all(result['checks'].values()))
        self.assertIn("TEST_EDU001", self.launcher.launch_status['launched_sites'])
    
    def test_dry_run_launch(self):
        """Test dry run launch (validation only)"""
        site = self.launcher.create_workplace_pilot_site(
            site_id="TEST_WRK001",
            company_name="Test Corporation",
            location="Test City, USA"
        )
        
        result = self.launcher.launch_pilot_site(site, dry_run=True)
        
        self.assertTrue(result['success'])
        self.assertGreater(len(result['warnings']), 0)
        # Should not actually register site in dry run
        self.assertEqual(len(self.launcher.pilot_manager.sites), 0)
    
    def test_q1_2026_full_launch(self):
        """Test complete Q1 2026 pilot site launch"""
        summary = self.launcher.launch_q1_2026_pilot_sites(dry_run=False)
        
        # Verify summary
        self.assertEqual(summary['total_sites'], 3)
        self.assertEqual(summary['successful_launches'], 3)
        self.assertEqual(summary['failed_launches'], 0)
        self.assertTrue(summary['exit_criteria_met'])
        
        # Verify pilot sites were registered
        self.assertEqual(len(self.launcher.pilot_manager.sites), 3)
        
        # Verify contexts
        contexts = set(site.context for site in self.launcher.pilot_manager.sites.values())
        self.assertGreaterEqual(len(contexts), 2)  # Minimum 2 contexts
        
        # Verify site IDs
        site_ids = list(self.launcher.pilot_manager.sites.keys())
        self.assertIn("EDU001", site_ids)
        self.assertIn("HCR001", site_ids)
        self.assertIn("WRK001", site_ids)
    
    def test_phase20_exit_criteria(self):
        """Test Phase 20 exit criteria are configured correctly"""
        summary = self.launcher.launch_q1_2026_pilot_sites(dry_run=False)
        
        # Exit criteria: ≥3 sites across ≥2 contexts
        self.assertGreaterEqual(summary['successful_launches'], 3)
        
        contexts = set()
        for site in self.launcher.pilot_manager.sites.values():
            contexts.add(site.context)
        self.assertGreaterEqual(len(contexts), 2)
        
        # Verify all contexts covered
        self.assertIn(PilotContext.EDUCATION, contexts)
        self.assertIn(PilotContext.HEALTHCARE, contexts)
        self.assertIn(PilotContext.WORKPLACE, contexts)
    
    def test_irb_approvals_registered(self):
        """Test IRB approvals are properly registered"""
        summary = self.launcher.launch_q1_2026_pilot_sites(dry_run=False)
        
        # Verify IRB approvals registered for all sites
        self.assertGreaterEqual(len(self.launcher.compliance_manager.irb_approvals), 3)
        
        # Check specific approvals
        self.assertIn("EDU001_IRB", self.launcher.compliance_manager.irb_approvals)
        self.assertIn("HCR001_IRB", self.launcher.compliance_manager.irb_approvals)
        self.assertIn("WRK001_IRB", self.launcher.compliance_manager.irb_approvals)
    
    def test_target_participants(self):
        """Test participant targets match Phase 20 requirements"""
        summary = self.launcher.launch_q1_2026_pilot_sites(dry_run=False)
        
        total_target = sum(site.target_participants 
                          for site in self.launcher.pilot_manager.sites.values())
        
        # Phase 20 target: 900-1500 total participants
        self.assertGreaterEqual(total_target, 900)
        self.assertLessEqual(total_target, 1500)
    
    def test_launch_status_saved(self):
        """Test launch status is saved to file"""
        summary = self.launcher.launch_q1_2026_pilot_sites(dry_run=False)
        
        status_file = self.temp_dir / "q1_2026_launch_status.json"
        self.assertTrue(status_file.exists())


def run_tests():
    """Run all tests"""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPhase20PilotLaunch)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
