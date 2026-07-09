"""Tests for Section III implementation (Active Recon, Visualization, Security Testing)."""

import pytest
from datetime import datetime

# Active Recon Tests
from nethical_recon.active_recon import (
    ActiveScanner,
    BannerGrabber,
    ScanProfile,
    TLSFingerprinter,
)
from nethical_recon.active_recon.tls_fingerprinter import TLSInfo


class TestActiveRecon:
    """Test active reconnaissance module."""

    def test_active_scanner_initialization(self):
        """Test ActiveScanner initialization."""
        scanner = ActiveScanner()
        # May or may not have nmap installed
        assert scanner is not None

    def test_scan_profile_options(self):
        """Test scan profile option generation."""
        scanner = ActiveScanner()

        quick_opts = scanner.get_profile_options(ScanProfile.QUICK)
        assert "F" in quick_opts  # Fast scan
        assert quick_opts["T"] == "4"  # Aggressive timing

        standard_opts = scanner.get_profile_options(ScanProfile.STANDARD)
        assert "sV" in standard_opts  # Version detection
        assert "sC" in standard_opts  # Default scripts

    def test_banner_grabber_initialization(self):
        """Test BannerGrabber initialization."""
        grabber = BannerGrabber(timeout=5)
        assert grabber.timeout == 5

    def test_banner_grabber_probe_generation(self):
        """Test probe string generation."""
        grabber = BannerGrabber()

        http_probe = grabber._get_probe(80)
        assert "GET" in http_probe

        smtp_probe = grabber._get_probe(25)
        assert "EHLO" in smtp_probe

    def test_banner_grabber_service_identification(self):
        """Test service identification from banner."""
        grabber = BannerGrabber()

        apache_banner = "Apache/2.4.41 (Ubuntu)"
        service = grabber._identify_service(apache_banner, 80)
        assert "Apache" in service

        ssh_banner = "SSH-2.0-OpenSSH_7.6p1"
        service = grabber._identify_service(ssh_banner, 22)
        assert "OpenSSH" in service

    def test_tls_fingerprinter_initialization(self):
        """Test TLSFingerprinter initialization."""
        fingerprinter = TLSFingerprinter(timeout=5)
        assert fingerprinter.timeout == 5

    def test_tls_vulnerability_checking(self):
        """Test TLS vulnerability detection."""
        fingerprinter = TLSFingerprinter()

        # Test with old SSL protocol
        tls_info = TLSInfo(host="example.com", port=443)
        tls_info.protocol_version = "SSLv3"
        tls_info.cipher_suite = "RC4-SHA"

        vulnerabilities = fingerprinter.check_vulnerabilities(tls_info)
        assert len(vulnerabilities) > 0
        assert any("SSL" in v or "RC4" in v for v in vulnerabilities)


# Visualization Tests
from nethical_recon.visualization import (
    AttackSurfaceGraph,
    DeltaMonitor,
    ExposedAssetDetector,
    ExposureLevel,
    GraphBuilder,
    NodeType,
)


class TestVisualization:
    """Test visualization module."""

    def test_graph_builder_initialization(self):
        """Test GraphBuilder initialization."""
        builder = GraphBuilder()
        assert builder.graph is not None
        assert len(builder.graph.nodes) == 0
        assert len(builder.graph.edges) == 0

    def test_graph_node_addition(self):
        """Test adding nodes to graph."""
        from nethical_recon.visualization.graph_builder import GraphNode

        graph = AttackSurfaceGraph()
        node = GraphNode(
            id="host_1",
            type=NodeType.HOST,
            label="example.com",
            properties={"ip": "192.168.1.1"},
        )

        graph.add_node(node)
        assert len(graph.nodes) == 1
        assert graph.get_node("host_1") is not None

    def test_graph_edge_addition(self):
        """Test adding edges to graph."""
        from nethical_recon.visualization.graph_builder import GraphNode, GraphEdge

        graph = AttackSurfaceGraph()

        # Add nodes first
        host_node = GraphNode(id="host_1", type=NodeType.HOST, label="Host")
        service_node = GraphNode(id="service_1", type=NodeType.SERVICE, label="HTTP")
        graph.add_node(host_node)
        graph.add_node(service_node)

        # Add edge
        edge = GraphEdge(source="host_1", target="service_1", relationship="runs")
        graph.add_edge(edge)

        assert len(graph.edges) == 1
        assert graph.edges[0].relationship == "runs"

    def test_graph_to_graphviz(self):
        """Test Graphviz export."""
        from nethical_recon.visualization.graph_builder import GraphNode

        graph = AttackSurfaceGraph()
        node = GraphNode(id="test", type=NodeType.HOST, label="Test Host")
        graph.add_node(node)

        dot_output = graph.to_graphviz()
        assert "digraph AttackSurface" in dot_output
        assert "test" in dot_output

    def test_delta_monitor_initialization(self):
        """Test DeltaMonitor initialization."""
        monitor = DeltaMonitor()
        assert monitor.changes == []

    def test_exposed_asset_detector_initialization(self):
        """Test ExposedAssetDetector initialization."""
        detector = ExposedAssetDetector()
        assert detector is not None
        assert 21 in detector.HIGH_RISK_PORTS  # FTP
        assert 22 in detector.MEDIUM_RISK_PORTS  # SSH

    def test_exposed_asset_detection_high_risk(self):
        """Test detection of high-risk exposed assets."""
        from dataclasses import dataclass

        @dataclass
        class MockAsset:
            asset_id: str
            host: str
            port: int
            service: str
            asset_type: str = "host"
            protocol: str = "tcp"

        detector = ExposedAssetDetector()

        # Test RDP exposure
        rdp_asset = MockAsset(
            asset_id="test_rdp",
            host="192.168.1.1",
            port=3389,
            service="rdp",
        )

        exposed = detector.analyze_asset(rdp_asset)
        assert exposed is not None
        assert exposed.exposure_level == ExposureLevel.HIGH
        assert len(exposed.reasons) > 0

    def test_exposure_report_generation(self):
        """Test exposure report generation."""
        from nethical_recon.visualization.exposed_assets import ExposedAsset

        detector = ExposedAssetDetector()

        exposed_assets = [
            ExposedAsset(
                asset_id="asset1",
                host="192.168.1.1",
                port=3389,
                service="RDP",
                exposure_level=ExposureLevel.HIGH,
                reasons=["High-risk port"],
            ),
            ExposedAsset(
                asset_id="asset2",
                host="192.168.1.2",
                port=22,
                service="SSH",
                exposure_level=ExposureLevel.MEDIUM,
                reasons=["Medium-risk port"],
            ),
        ]

        report = detector.generate_exposure_report(exposed_assets)
        assert report["total_exposed"] == 2
        assert report["exposure_levels"]["high"] == 1
        assert report["exposure_levels"]["medium"] == 1


# Security Testing Tests
from nethical_recon.security_testing import (
    ComplianceReporter,
    WebSecurityTester,
    APISecurityTester,
)
from nethical_recon.security_testing.web_security import TestStatus, TestSeverity
from nethical_recon.security_testing.compliance import ComplianceFramework


class TestSecurityTesting:
    """Test security testing module."""

    def test_web_security_tester_initialization(self):
        """Test WebSecurityTester initialization."""
        tester = WebSecurityTester(timeout=10)
        assert tester.timeout == 10
        assert tester.session is not None

    def test_test_result_creation(self):
        """Test TestResult creation."""
        from nethical_recon.security_testing.web_security import TestResult

        result = TestResult(
            test_id="test_1",
            test_name="Test Name",
            status=TestStatus.PASS,
            severity=TestSeverity.INFO,
            description="Test description",
        )

        assert result.test_id == "test_1"
        assert result.status == TestStatus.PASS
        assert result.severity == TestSeverity.INFO

    def test_api_security_tester_initialization(self):
        """Test APISecurityTester initialization."""
        tester = APISecurityTester(timeout=10)
        assert tester.timeout == 10

    def test_compliance_reporter_initialization(self):
        """Test ComplianceReporter initialization."""
        reporter = ComplianceReporter()
        assert reporter.reports == []

    def test_compliance_score_calculation(self):
        """Test compliance score calculation."""
        from nethical_recon.security_testing.compliance import ComplianceCheck

        reporter = ComplianceReporter()

        checks = [
            ComplianceCheck(
                check_id="check_1",
                framework=ComplianceFramework.OWASP_WSTG,
                category="security",
                description="Test check 1",
                status="pass",
            ),
            ComplianceCheck(
                check_id="check_2",
                framework=ComplianceFramework.OWASP_WSTG,
                category="security",
                description="Test check 2",
                status="pass",
            ),
            ComplianceCheck(
                check_id="check_3",
                framework=ComplianceFramework.OWASP_WSTG,
                category="security",
                description="Test check 3",
                status="fail",
            ),
        ]

        score = reporter._calculate_compliance_score(checks)
        assert score == pytest.approx(66.67, 0.1)  # 2 out of 3 passed

    def test_compliance_report_export(self):
        """Test compliance report export to dictionary."""
        from nethical_recon.security_testing.compliance import ComplianceReport, ComplianceCheck

        reporter = ComplianceReporter()

        report = ComplianceReport(
            framework=ComplianceFramework.OWASP_WSTG,
            timestamp=datetime.now(),
            target="example.com",
        )

        report.checks.append(
            ComplianceCheck(
                check_id="test_1",
                framework=ComplianceFramework.OWASP_WSTG,
                category="test",
                description="Test check",
                status="pass",
            )
        )

        exported = reporter.export_to_dict(report)
        assert exported["framework"] == "owasp_wstg"
        assert exported["target"] == "example.com"
        assert len(exported["checks"]) == 1


# Integration Tests
class TestSectionIIIIntegration:
    """Integration tests for Section III features."""

    def test_modules_importable(self):
        """Test that all new modules can be imported."""
        # Active recon
        from nethical_recon.active_recon import (
            ActiveScanner,
            BannerGrabber,
            TLSFingerprinter,
        )

        # Visualization
        from nethical_recon.visualization import (
            GraphBuilder,
            DeltaMonitor,
            ExposedAssetDetector,
        )

        # Security testing
        from nethical_recon.security_testing import (
            WebSecurityTester,
            APISecurityTester,
            ComplianceReporter,
        )

        # All imports successful
        assert True

    def test_api_routers_importable(self):
        """Test that all new API routers can be imported."""
        from nethical_recon.api.routers import (
            active_recon_router,
            visualization_router,
            security_testing_router,
        )

        assert active_recon_router is not None
        assert visualization_router is not None
        assert security_testing_router is not None
