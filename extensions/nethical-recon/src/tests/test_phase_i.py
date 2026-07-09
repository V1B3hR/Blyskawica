"""Tests for Phase I - Pro Recon Plugins."""

import json
from pathlib import Path
from uuid import uuid4

import pytest

from nethical_recon.adapters import (
    AmassAdapter,
    FfufAdapter,
    HttpxAdapter,
    MasscanAdapter,
    NucleiAdapter,
    ToolPlugin,
)
from nethical_recon.core.models import Confidence, Severity


class TestToolPlugin:
    """Test base ToolPlugin interface."""

    def test_base_plugin_is_abstract(self):
        """Test that ToolPlugin cannot be instantiated directly."""
        with pytest.raises(TypeError):
            ToolPlugin("test", "/usr/bin/test")


class TestMasscanAdapter:
    """Test masscan adapter."""

    def test_initialization(self):
        """Test adapter initialization."""
        adapter = MasscanAdapter()
        assert adapter.tool_name == "masscan"
        assert adapter.tool_path == "masscan"

    def test_validate_target_valid_ip(self):
        """Test validation of valid IP targets."""
        adapter = MasscanAdapter()

        is_valid, msg = adapter.validate_target("192.168.1.1")
        assert is_valid

        is_valid, msg = adapter.validate_target("10.0.0.0/24")
        assert is_valid

        is_valid, msg = adapter.validate_target("192.168.1.1-254")
        assert is_valid

    def test_validate_target_invalid(self):
        """Test validation of invalid targets."""
        adapter = MasscanAdapter()

        is_valid, msg = adapter.validate_target("example.com")
        assert not is_valid
        assert "IP address" in msg

    def test_build_command(self):
        """Test command building."""
        adapter = MasscanAdapter()
        output_path = Path("/tmp/test.json")

        cmd = adapter.build_command("192.168.1.1", output_path)

        assert "masscan" in cmd[0]
        assert "192.168.1.1" in cmd
        assert "-oJ" in cmd
        assert str(output_path) in cmd

    def test_parse_output(self):
        """Test parsing masscan output."""
        adapter = MasscanAdapter()

        # Masscan JSON format
        output = """{"ip": "192.168.1.1", "timestamp": "1234567890", "ports": [{"port": 22, "proto": "tcp", "status": "open"}]}
{"ip": "192.168.1.2", "timestamp": "1234567891", "ports": [{"port": 80, "proto": "tcp", "status": "open"}]}"""

        parsed = adapter.parse_output(output)

        assert "hosts" in parsed
        assert len(parsed["hosts"]) == 2
        assert parsed["hosts"][0]["ip"] == "192.168.1.1"
        assert parsed["hosts"][0]["port"] == 22

    def test_to_findings(self):
        """Test conversion to findings."""
        adapter = MasscanAdapter()
        run_id = uuid4()
        evidence_id = uuid4()

        parsed_data = {"hosts": [{"ip": "192.168.1.1", "port": 22, "protocol": "tcp", "state": "open"}]}

        findings = adapter.to_findings(parsed_data, run_id, evidence_id)

        assert len(findings) == 1
        assert findings[0].title == "Open TCP Port 22"
        assert findings[0].affected_asset == "192.168.1.1"
        assert findings[0].port == 22
        assert findings[0].category == "open_port"

    def test_severity_assessment(self):
        """Test port severity assessment."""
        adapter = MasscanAdapter()

        # Critical port
        assert adapter._assess_port_severity(445, "tcp") == Severity.CRITICAL

        # High risk port
        assert adapter._assess_port_severity(22, "tcp") == Severity.HIGH

        # Privileged port
        assert adapter._assess_port_severity(443, "tcp") == Severity.MEDIUM

        # High port
        assert adapter._assess_port_severity(8080, "tcp") == Severity.LOW


class TestNucleiAdapter:
    """Test nuclei adapter."""

    def test_initialization(self):
        """Test adapter initialization."""
        adapter = NucleiAdapter()
        assert adapter.tool_name == "nuclei"

    def test_validate_target_url(self):
        """Test URL validation."""
        adapter = NucleiAdapter()

        is_valid, msg = adapter.validate_target("https://example.com")
        assert is_valid

        is_valid, msg = adapter.validate_target("http://192.168.1.1")
        assert is_valid

    def test_build_command(self):
        """Test command building."""
        adapter = NucleiAdapter()
        output_path = Path("/tmp/test.json")

        cmd = adapter.build_command("https://example.com", output_path)

        assert "nuclei" in cmd[0]
        assert "-target" in cmd
        assert "https://example.com" in cmd
        assert "-jsonl" in cmd

    def test_parse_output(self):
        """Test parsing nuclei output."""
        adapter = NucleiAdapter()

        output = """{"template-id": "cve-2021-1234", "info": {"name": "Test Vuln", "severity": "high", "description": "Test"}, "host": "example.com"}
{"template-id": "cve-2021-5678", "info": {"name": "Another Vuln", "severity": "medium"}, "host": "example.com"}"""

        parsed = adapter.parse_output(output)

        assert "vulnerabilities" in parsed
        assert len(parsed["vulnerabilities"]) == 2

    def test_to_findings(self):
        """Test conversion to findings."""
        adapter = NucleiAdapter()
        run_id = uuid4()
        evidence_id = uuid4()

        parsed_data = {
            "vulnerabilities": [
                {
                    "template-id": "test-vuln",
                    "info": {
                        "name": "Test Vulnerability",
                        "severity": "high",
                        "description": "A test vulnerability",
                        "tags": "cve,test",
                    },
                    "host": "example.com",
                }
            ]
        }

        findings = adapter.to_findings(parsed_data, run_id, evidence_id)

        assert len(findings) == 1
        assert findings[0].title == "Test Vulnerability"
        assert findings[0].severity == Severity.HIGH
        assert findings[0].category == "vulnerability"
        assert "nuclei" in findings[0].tags

    def test_severity_mapping(self):
        """Test nuclei severity mapping."""
        adapter = NucleiAdapter()

        assert adapter._map_severity("critical") == Severity.CRITICAL
        assert adapter._map_severity("high") == Severity.HIGH
        assert adapter._map_severity("medium") == Severity.MEDIUM
        assert adapter._map_severity("low") == Severity.LOW
        assert adapter._map_severity("info") == Severity.INFO


class TestHttpxAdapter:
    """Test httpx adapter."""

    def test_initialization(self):
        """Test adapter initialization."""
        adapter = HttpxAdapter()
        assert adapter.tool_name == "httpx"

    def test_validate_target(self):
        """Test target validation."""
        adapter = HttpxAdapter()

        # All targets are valid for httpx
        is_valid, msg = adapter.validate_target("example.com")
        assert is_valid

        is_valid, msg = adapter.validate_target("https://example.com")
        assert is_valid

    def test_build_command(self):
        """Test command building."""
        adapter = HttpxAdapter()
        output_path = Path("/tmp/test.json")

        cmd = adapter.build_command("example.com", output_path)

        assert "httpx" in cmd[0]
        assert "-u" in cmd
        assert "example.com" in cmd
        assert "-json" in cmd

    def test_parse_output(self):
        """Test parsing httpx output."""
        adapter = HttpxAdapter()

        output = """{"url": "https://example.com", "status_code": 200, "title": "Example", "webserver": "nginx"}"""

        parsed = adapter.parse_output(output)

        assert "endpoints" in parsed
        assert len(parsed["endpoints"]) == 1
        assert parsed["endpoints"][0]["url"] == "https://example.com"

    def test_to_findings(self):
        """Test conversion to findings."""
        adapter = HttpxAdapter()
        run_id = uuid4()
        evidence_id = uuid4()

        parsed_data = {
            "endpoints": [
                {
                    "url": "https://example.com",
                    "host": "example.com",
                    "status_code": 200,
                    "title": "Example Domain",
                    "webserver": "nginx/1.19.0",
                    "technologies": ["nginx"],
                }
            ]
        }

        findings = adapter.to_findings(parsed_data, run_id, evidence_id)

        assert len(findings) >= 1  # Base finding + possible security issues
        assert findings[0].category == "web_endpoint"
        assert "httpx" in findings[0].tags


class TestFfufAdapter:
    """Test ffuf adapter."""

    def test_initialization(self):
        """Test adapter initialization."""
        adapter = FfufAdapter()
        assert adapter.tool_name == "ffuf"

    def test_validate_target_with_fuzz(self):
        """Test target validation with FUZZ keyword."""
        adapter = FfufAdapter()

        is_valid, msg = adapter.validate_target("https://example.com/FUZZ")
        assert is_valid

    def test_validate_target_without_fuzz(self):
        """Test target validation without FUZZ keyword."""
        adapter = FfufAdapter()

        is_valid, msg = adapter.validate_target("https://example.com")
        assert not is_valid
        assert "FUZZ" in msg

    def test_build_command(self):
        """Test command building."""
        adapter = FfufAdapter()
        output_path = Path("/tmp/test.json")

        cmd = adapter.build_command("https://example.com/FUZZ", output_path)

        assert "ffuf" in cmd[0]
        assert "-u" in cmd
        assert "https://example.com/FUZZ" in cmd
        assert "-of" in cmd
        assert "json" in cmd

    def test_parse_output(self):
        """Test parsing ffuf output."""
        adapter = FfufAdapter()

        output = json.dumps(
            {
                "results": [
                    {
                        "url": "https://example.com/admin",
                        "status": 200,
                        "length": 1234,
                        "words": 100,
                        "lines": 50,
                        "input": {"FUZZ": "admin"},
                    }
                ]
            }
        )

        parsed = adapter.parse_output(output)

        assert "results" in parsed
        assert len(parsed["results"]) == 1
        assert parsed["results"][0]["status"] == 200

    def test_to_findings(self):
        """Test conversion to findings."""
        adapter = FfufAdapter()
        run_id = uuid4()
        evidence_id = uuid4()

        parsed_data = {
            "results": [
                {
                    "url": "https://example.com/admin",
                    "status": 200,
                    "length": 1234,
                    "words": 100,
                    "lines": 50,
                    "input": {"FUZZ": "admin"},
                }
            ]
        }

        findings = adapter.to_findings(parsed_data, run_id, evidence_id)

        assert len(findings) == 1
        assert "admin" in findings[0].title.lower()
        assert findings[0].category in ["admin_panel", "accessible_content"]
        assert "ffuf" in findings[0].tags


class TestAmassAdapter:
    """Test amass adapter."""

    def test_initialization(self):
        """Test adapter initialization."""
        adapter = AmassAdapter()
        assert adapter.tool_name == "amass"

    def test_validate_target_domain(self):
        """Test domain validation."""
        adapter = AmassAdapter()

        is_valid, msg = adapter.validate_target("example.com")
        assert is_valid

        is_valid, msg = adapter.validate_target("sub.example.com")
        assert is_valid

    def test_validate_target_invalid(self):
        """Test invalid target validation."""
        adapter = AmassAdapter()

        is_valid, msg = adapter.validate_target("https://example.com")
        assert not is_valid

        is_valid, msg = adapter.validate_target("invalid")
        assert not is_valid

    def test_build_command(self):
        """Test command building."""
        adapter = AmassAdapter()
        output_path = Path("/tmp/test.json")

        cmd = adapter.build_command("example.com", output_path)

        assert "amass" in cmd[0]
        assert "enum" in cmd
        assert "-d" in cmd
        assert "example.com" in cmd
        assert "-json" in cmd

    def test_parse_output(self):
        """Test parsing amass output."""
        adapter = AmassAdapter()

        output = """{"name": "www.example.com", "domain": "example.com", "addresses": [{"ip": "192.168.1.1"}], "sources": ["DNS"]}
{"name": "api.example.com", "domain": "example.com", "addresses": [{"ip": "192.168.1.2"}], "sources": ["DNS", "Cert"]}"""

        parsed = adapter.parse_output(output)

        assert "subdomains" in parsed
        assert len(parsed["subdomains"]) == 2

    def test_to_findings(self):
        """Test conversion to findings."""
        adapter = AmassAdapter()
        run_id = uuid4()
        evidence_id = uuid4()

        parsed_data = {
            "subdomains": [
                {
                    "name": "api.example.com",
                    "domain": "example.com",
                    "addresses": [{"ip": "192.168.1.1"}],
                    "sources": ["DNS", "Cert", "Archive"],
                }
            ]
        }

        findings = adapter.to_findings(parsed_data, run_id, evidence_id)

        # Should create subdomain finding + IP resolution finding
        assert len(findings) >= 1
        assert findings[0].category == "subdomain"
        assert "api.example.com" in findings[0].title
        assert "amass" in findings[0].tags

    def test_confidence_assessment(self):
        """Test confidence assessment based on source count."""
        adapter = AmassAdapter()

        # Many sources = high confidence
        assert adapter._assess_confidence(["DNS", "Cert", "Archive", "Web", "API"]) == Confidence.CONFIRMED

        # Few sources = lower confidence
        assert adapter._assess_confidence(["DNS"]) == Confidence.LOW

        # No sources = tentative
        assert adapter._assess_confidence([]) == Confidence.TENTATIVE


class TestPhaseIIntegration:
    """Integration tests for Phase I adapters."""

    def test_all_adapters_available(self):
        """Test that all Phase I adapters are importable."""
        adapters = [MasscanAdapter, NucleiAdapter, HttpxAdapter, FfufAdapter, AmassAdapter]

        for adapter_class in adapters:
            adapter = adapter_class()
            assert adapter.tool_name is not None
            assert hasattr(adapter, "validate_target")
            assert hasattr(adapter, "build_command")
            assert hasattr(adapter, "parse_output")
            assert hasattr(adapter, "to_findings")

    def test_unified_finding_model(self):
        """Test that all adapters produce findings with consistent structure."""
        adapters_and_data = [
            (MasscanAdapter(), {"hosts": [{"ip": "1.1.1.1", "port": 80, "protocol": "tcp", "state": "open"}]}),
            (
                NucleiAdapter(),
                {
                    "vulnerabilities": [
                        {"template-id": "test", "info": {"name": "Test", "severity": "high"}, "host": "example.com"}
                    ]
                },
            ),
            (
                HttpxAdapter(),
                {"endpoints": [{"url": "https://example.com", "status_code": 200, "host": "example.com"}]},
            ),
            (
                FfufAdapter(),
                {
                    "results": [
                        {
                            "url": "https://example.com/test",
                            "status": 200,
                            "length": 100,
                            "words": 10,
                            "lines": 5,
                            "input": {"FUZZ": "test"},
                        }
                    ]
                },
            ),
            (
                AmassAdapter(),
                {
                    "subdomains": [
                        {"name": "sub.example.com", "domain": "example.com", "addresses": [], "sources": ["DNS"]}
                    ]
                },
            ),
        ]

        run_id = uuid4()
        evidence_id = uuid4()

        for adapter, parsed_data in adapters_and_data:
            findings = adapter.to_findings(parsed_data, run_id, evidence_id)

            assert len(findings) > 0

            for finding in findings:
                # Check all findings have required fields
                assert finding.run_id == run_id
                assert finding.title is not None
                assert finding.description is not None
                assert finding.severity is not None
                assert finding.confidence is not None
                assert finding.category is not None
                assert evidence_id in finding.evidence_ids
