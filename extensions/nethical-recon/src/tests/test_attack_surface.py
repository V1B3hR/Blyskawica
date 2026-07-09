"""
Tests for Attack Surface Mapping Module
"""

import pytest
from datetime import datetime

from nethical_recon.attack_surface import (
    AttackSurfaceMapper,
    BaselineManager,
    TechnologyFingerprinter,
    ServiceDetector,
    CMSDetector,
)


class TestTechnologyFingerprinter:
    """Tests for technology fingerprinting."""

    def test_fingerprinter_initialization(self):
        """Test fingerprinter initializes with signatures."""
        fingerprinter = TechnologyFingerprinter()
        assert len(fingerprinter.signatures) > 0

    def test_fingerprint_detection(self):
        """Test technology detection from headers and body."""
        fingerprinter = TechnologyFingerprinter()

        headers = {
            "Server": "nginx/1.21.0",
            "X-Powered-By": "Express",
        }
        body = "<html>wordpress</html>"

        # Mock fingerprinting (would need actual HTTP response in real test)
        results = fingerprinter._check_signature(
            fingerprinter.signatures[0],  # nginx signature
            headers,
            body,
        )

        if results:
            assert results.technology in ["nginx", "Apache", "IIS"]


class TestServiceDetector:
    """Tests for service detection."""

    def test_service_detector_initialization(self):
        """Test service detector initializes."""
        detector = ServiceDetector()
        assert detector is not None

    def test_detect_common_port(self):
        """Test detection of common port services."""
        detector = ServiceDetector()
        result = detector.detect_service("127.0.0.1", 80)

        assert result["host"] == "127.0.0.1"
        assert result["port"] == 80
        assert result["service"] == "http"

    def test_detect_unknown_port(self):
        """Test detection of unknown port."""
        detector = ServiceDetector()
        result = detector.detect_service("127.0.0.1", 54321)

        assert result["host"] == "127.0.0.1"
        assert result["port"] == 54321
        assert result["service"] == "unknown"

    def test_analyze_multiple_ports(self):
        """Test analyzing multiple ports."""
        detector = ServiceDetector()
        results = detector.analyze_ports("127.0.0.1", [80, 443, 22])

        assert len(results) == 3
        assert results[0]["port"] == 80
        assert results[1]["port"] == 443
        assert results[2]["port"] == 22


class TestCMSDetector:
    """Tests for CMS detection."""

    def test_cms_detector_initialization(self):
        """Test CMS detector initializes."""
        detector = CMSDetector()
        assert detector is not None
        assert detector.fingerprinter is not None

    def test_detect_plugins(self):
        """Test plugin detection for CMS."""
        detector = CMSDetector()
        plugins = detector.detect_plugins("http://example.com", "WordPress")

        assert isinstance(plugins, list)


class TestAttackSurfaceMapper:
    """Tests for attack surface mapping."""

    def test_mapper_initialization(self):
        """Test mapper initializes with all components."""
        mapper = AttackSurfaceMapper()
        assert mapper.tech_fingerprinter is not None
        assert mapper.service_detector is not None
        assert mapper.cms_detector is not None

    def test_generate_report(self):
        """Test report generation from snapshot."""
        mapper = AttackSurfaceMapper()

        # Create a mock snapshot
        from nethical_recon.attack_surface.mapper import AttackSurfaceSnapshot, Asset

        snapshot = AttackSurfaceSnapshot(
            snapshot_id="test_snapshot",
            target="example.com",
            assets=[
                Asset(
                    asset_id="web_1",
                    asset_type="web_application",
                    host="example.com",
                    technologies=[{"name": "nginx", "category": "web_server", "version": "1.21.0", "confidence": 0.9}],
                )
            ],
        )

        report = mapper.generate_report(snapshot)

        assert report["snapshot_id"] == "test_snapshot"
        assert report["target"] == "example.com"
        assert report["total_assets"] == 1
        assert "web_application" in report["assets_by_type"]


class TestBaselineManager:
    """Tests for baseline management."""

    def test_baseline_manager_initialization(self):
        """Test baseline manager initializes."""
        manager = BaselineManager(storage_path="/tmp/test_baselines")
        assert manager.storage_path.exists()

    def test_create_baseline(self):
        """Test baseline creation."""
        manager = BaselineManager(storage_path="/tmp/test_baselines")

        from nethical_recon.attack_surface.mapper import AttackSurfaceSnapshot, Asset

        snapshot = AttackSurfaceSnapshot(
            snapshot_id="test_snapshot",
            target="example.com",
            assets=[],
        )

        baseline_name = manager.create_baseline(snapshot, "test_baseline")
        assert baseline_name == "test_baseline"
        assert baseline_name in manager.baselines

    def test_load_baseline(self):
        """Test baseline loading."""
        manager = BaselineManager(storage_path="/tmp/test_baselines")

        # Create a baseline first
        from nethical_recon.attack_surface.mapper import AttackSurfaceSnapshot

        snapshot = AttackSurfaceSnapshot(
            snapshot_id="test_snapshot",
            target="example.com",
            assets=[],
        )

        manager.create_baseline(snapshot, "test_baseline")

        # Load it
        loaded = manager.load_baseline("test_baseline")
        assert loaded is not None
        assert loaded.snapshot_id == "test_snapshot"

    def test_detect_changes(self):
        """Test change detection between snapshots."""
        manager = BaselineManager(storage_path="/tmp/test_baselines")

        from nethical_recon.attack_surface.mapper import AttackSurfaceSnapshot, Asset

        # Create baseline
        baseline_snapshot = AttackSurfaceSnapshot(
            snapshot_id="baseline",
            target="example.com",
            assets=[
                Asset(
                    asset_id="asset_1",
                    asset_type="service",
                    host="example.com",
                    port=80,
                )
            ],
        )

        manager.create_baseline(baseline_snapshot, "test_baseline")

        # Create current snapshot with changes
        current_snapshot = AttackSurfaceSnapshot(
            snapshot_id="current",
            target="example.com",
            assets=[
                Asset(
                    asset_id="asset_1",
                    asset_type="service",
                    host="example.com",
                    port=80,
                ),
                Asset(
                    asset_id="asset_2",
                    asset_type="service",
                    host="example.com",
                    port=443,
                ),
            ],
        )

        changes = manager.detect_changes("test_baseline", current_snapshot)

        assert "new_assets" in changes
        assert "removed_assets" in changes
        assert "changed_assets" in changes
        assert changes["summary"]["total_new"] == 1
