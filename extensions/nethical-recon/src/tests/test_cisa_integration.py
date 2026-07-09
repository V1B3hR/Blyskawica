"""
Tests for CISA Integration Modules

Tests for KEV client, alerts, policy modes, compliance reporting,
and other CISA-related functionality.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from nethical_recon.compliance import (
    CISAKEVClient,
    KEVEntry,
    CISAAlertFeedClient,
    CISAShieldsUpMonitor,
)
from nethical_recon.compliance.cisa_policy import CISAPolicyMode, CISAPolicyManager
from nethical_recon.compliance.cisa_reporting import CISAComplianceReporter
from nethical_recon.compliance.cisa_mapping import CISACategoryMapper
from nethical_recon.compliance.cisa_attack_surface import CISAAttackSurfaceMonitor
from nethical_recon.plugins import CISABODChecker


class TestCISAKEVClient:
    """Tests for CISA KEV Client."""

    def test_kev_client_initialization(self):
        """Test KEV client initializes correctly."""
        client = CISAKEVClient()
        assert client is not None
        assert client._cache == {}
        assert client._last_update is None

    @patch("nethical_recon.compliance.cisa_kev.requests.get")
    def test_update_cache_success(self, mock_get):
        """Test successful KEV catalog update."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "catalogVersion": "2024.01.14",
            "dateReleased": "2024-01-14",
            "vulnerabilities": [
                {
                    "cveID": "CVE-2021-44228",
                    "vendorProject": "Apache",
                    "product": "Log4j",
                    "vulnerabilityName": "Log4Shell",
                    "dateAdded": "2021-12-10",
                    "shortDescription": "Apache Log4j2 RCE vulnerability",
                    "requiredAction": "Apply updates per vendor instructions",
                    "dueDate": "2021-12-24",
                    "knownRansomwareCampaignUse": "Known",
                    "notes": "",
                }
            ],
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        client = CISAKEVClient()
        result = client.update_cache(force=True)

        assert result is True
        assert len(client._cache) == 1
        assert "CVE-2021-44228" in client._cache

    def test_is_kev_with_empty_cache(self):
        """Test is_kev returns False with empty cache."""
        client = CISAKEVClient()
        assert client.is_kev("CVE-2021-44228") is False

    def test_get_kev_metadata(self):
        """Test getting KEV metadata."""
        client = CISAKEVClient()
        entry = KEVEntry(
            cve_id="CVE-2021-44228",
            vendor_project="Apache",
            product="Log4j",
            vulnerability_name="Log4Shell",
            date_added="2021-12-10",
            short_description="Test",
            required_action="Update",
            due_date="2021-12-24",
        )
        client._cache["CVE-2021-44228"] = entry

        metadata = client.get_kev_metadata("CVE-2021-44228")
        assert metadata is not None
        assert metadata["is_kev"] is True
        assert metadata["cve_id"] == "CVE-2021-44228"

    def test_get_statistics(self):
        """Test getting KEV statistics."""
        client = CISAKEVClient()
        entry = KEVEntry(
            cve_id="CVE-2021-44228",
            vendor_project="Apache",
            product="Log4j",
            vulnerability_name="Log4Shell",
            date_added="2021-12-10",
            short_description="Test",
            required_action="Update",
        )
        client._cache["CVE-2021-44228"] = entry
        client._last_update = datetime.utcnow()

        stats = client.get_statistics()
        assert stats["total_vulnerabilities"] == 1
        assert stats["last_update"] is not None


class TestCISAPolicyManager:
    """Tests for CISA Policy Manager."""

    def test_policy_manager_initialization(self):
        """Test policy manager initializes with default profiles."""
        manager = CISAPolicyManager()
        assert manager._current_mode == CISAPolicyMode.ENTERPRISE

    def test_get_profile(self):
        """Test getting a policy profile."""
        manager = CISAPolicyManager()
        profile = manager.get_profile(CISAPolicyMode.FEDERAL_AGENCY)

        assert profile is not None
        assert profile.mode == CISAPolicyMode.FEDERAL_AGENCY
        assert profile.kev_focus is True
        assert profile.continuous_monitoring is True

    def test_apply_profile(self):
        """Test applying a policy profile."""
        manager = CISAPolicyManager()
        config = manager.apply_profile(CISAPolicyMode.CRITICAL_INFRASTRUCTURE)

        assert config["mode"] == "critical_infrastructure"
        assert manager.get_current_mode() == CISAPolicyMode.CRITICAL_INFRASTRUCTURE


class TestCISAComplianceReporter:
    """Tests for CISA Compliance Reporter."""

    def test_reporter_initialization(self):
        """Test reporter initializes correctly."""
        reporter = CISAComplianceReporter()
        assert reporter is not None
        assert len(reporter._reports) == 0

    def test_generate_report(self):
        """Test generating a compliance report."""
        reporter = CISAComplianceReporter()

        kev_vulns = [
            {
                "cve_id": "CVE-2021-44228",
                "status": "open",
                "is_overdue": True,
                "severity": "critical",
            }
        ]

        report = reporter.generate_report(
            organization="Test Org",
            policy_mode="enterprise",
            kev_vulnerabilities=kev_vulns,
            active_alerts=[],
            compliance_data={},
        )

        assert report is not None
        assert report.organization == "Test Org"
        assert report.executive_summary["total_kev_vulnerabilities"] == 1
        assert report.executive_summary["open_kev_vulnerabilities"] == 1

    def test_render_html(self):
        """Test rendering report as HTML."""
        reporter = CISAComplianceReporter()

        report = reporter.generate_report(
            organization="Test Org",
            policy_mode="enterprise",
            kev_vulnerabilities=[],
            active_alerts=[],
            compliance_data={},
        )

        html = reporter.render_html(report)
        assert html is not None
        assert "Test Org" in html
        assert "CISA Compliance Report" in html


class TestCISACategoryMapper:
    """Tests for CISA Category Mapper."""

    def test_mapper_initialization(self):
        """Test mapper initializes correctly."""
        mapper = CISACategoryMapper()
        assert mapper is not None

    def test_map_finding(self):
        """Test mapping a finding to CISA categories."""
        mapper = CISACategoryMapper()

        mapping = mapper.map_finding(
            finding_id="finding-1",
            finding_type="vulnerability",
            risk_score=95.0,
            description="Critical KEV vulnerability",
        )

        assert mapping is not None
        assert mapping.cisa_severity.value == "critical"
        assert mapping.cisa_recommendation is not None

    def test_get_coverage_report(self):
        """Test getting coverage report."""
        mapper = CISACategoryMapper()

        # Map some findings to track coverage
        mapper.map_finding("f1", "vulnerability", 80.0)
        mapper.map_finding("f2", "network", 60.0)

        coverage = mapper.get_coverage_report()
        assert coverage is not None
        assert "monitored_categories" in coverage
        assert coverage["monitored_categories"] >= 2


class TestCISAAttackSurfaceMonitor:
    """Tests for CISA Attack Surface Monitor."""

    def test_monitor_initialization(self):
        """Test monitor initializes correctly."""
        monitor = CISAAttackSurfaceMonitor()
        assert monitor is not None

    def test_categorize_asset(self):
        """Test categorizing an asset."""
        monitor = CISAAttackSurfaceMonitor()

        area = monitor.categorize_asset(
            asset_id="asset-1",
            asset_type="web server",
            asset_metadata={"internet_facing": True},
        )

        assert area is not None

    def test_get_coverage_report(self):
        """Test getting attack surface coverage report."""
        monitor = CISAAttackSurfaceMonitor()

        coverage = monitor.get_coverage_report()
        assert coverage is not None
        assert "total_areas" in coverage
        assert coverage["total_areas"] == 6  # 6 CISA attack surface areas


class TestCISABODChecker:
    """Tests for CISA BOD Checker Plugin."""

    def test_bod_checker_initialization(self):
        """Test BOD checker initializes correctly."""
        checker = CISABODChecker()
        assert checker is not None

    def test_check_bod_22_01(self):
        """Test BOD 22-01 compliance check."""
        kev_client = CISAKEVClient()
        checker = CISABODChecker(kev_client=kev_client)

        result = checker.check_bod_22_01(vulnerabilities=[])

        assert result is not None
        assert result.directive.value == "bod_22_01"
        assert result.compliance_percentage == 100.0  # No vulnerabilities = 100% compliant

    def test_check_bod_23_01(self):
        """Test BOD 23-01 compliance check."""
        checker = CISABODChecker()

        assets = [
            {"id": "asset-1", "inventoried": True, "last_scan": "2024-01-14"},
            {"id": "asset-2", "inventoried": True, "last_scan": "2024-01-14"},
        ]

        result = checker.check_bod_23_01(assets=assets, scan_coverage=95.0)

        assert result is not None
        assert result.directive.value == "bod_23_01"
        assert result.compliant is True

    def test_check_bod_18_01(self):
        """Test BOD 18-01 compliance check."""
        checker = CISABODChecker()

        email_config = {"dmarc": True, "spf": True, "dkim": True}
        web_config = {"https_enforced": True, "hsts": True}

        result = checker.check_bod_18_01(email_config=email_config, web_config=web_config)

        assert result is not None
        assert result.directive.value == "bod_18_01"
        assert result.compliant is True
        assert result.compliance_percentage == 100.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
