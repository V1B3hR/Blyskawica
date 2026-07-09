"""Tests for core domain models."""

from __future__ import annotations

from uuid import uuid4

import pytest

from nethical_recon.core.models import (
    IOC,
    Asset,
    AssetType,
    Confidence,
    Evidence,
    EvidenceType,
    Finding,
    IOCType,
    JobStatus,
    ScanJob,
    Severity,
    Target,
    TargetScope,
    TargetType,
    ToolRun,
    ToolStatus,
)


class TestTarget:
    """Tests for Target model."""

    def test_create_domain_target(self):
        """Test creating a domain target."""
        target = Target(value="example.com", type=TargetType.DOMAIN, scope=TargetScope.IN_SCOPE)
        assert target.value == "example.com"
        assert target.type == TargetType.DOMAIN
        assert target.scope == TargetScope.IN_SCOPE
        assert target.id is not None

    def test_create_ip_target(self):
        """Test creating an IP target."""
        target = Target(value="192.0.2.1", type=TargetType.IP)
        assert target.value == "192.0.2.1"
        assert target.type == TargetType.IP

    def test_create_cidr_target(self):
        """Test creating a CIDR target."""
        target = Target(value="192.0.2.0/24", type=TargetType.CIDR)
        assert target.value == "192.0.2.0/24"
        assert target.type == TargetType.CIDR

    def test_create_url_target(self):
        """Test creating a URL target."""
        target = Target(value="https://example.com", type=TargetType.URL)
        assert target.value == "https://example.com"
        assert target.type == TargetType.URL

    def test_invalid_ip_target(self):
        """Test that invalid IP is rejected."""
        with pytest.raises(ValueError, match="Invalid IP address"):
            Target(value="not-an-ip", type=TargetType.IP)

    def test_invalid_cidr_target(self):
        """Test that invalid CIDR is rejected."""
        with pytest.raises(ValueError, match="Invalid CIDR notation"):
            Target(value="not-a-cidr", type=TargetType.CIDR)

    def test_invalid_url_target(self):
        """Test that invalid URL is rejected."""
        with pytest.raises(ValueError, match="URL must start with"):
            Target(value="not-a-url", type=TargetType.URL)

    def test_target_with_tags(self):
        """Test creating target with tags."""
        target = Target(
            value="example.com", type=TargetType.DOMAIN, tags=["web", "production"], description="Main website"
        )
        assert "web" in target.tags
        assert "production" in target.tags
        assert target.description == "Main website"


class TestScanJob:
    """Tests for ScanJob model."""

    def test_create_scan_job(self):
        """Test creating a scan job."""
        target_id = uuid4()
        job = ScanJob(target_id=target_id, name="Test Scan", tools=["nmap", "nikto"])
        assert job.target_id == target_id
        assert job.name == "Test Scan"
        assert job.status == JobStatus.PENDING
        assert "nmap" in job.tools
        assert "nikto" in job.tools

    def test_scan_job_default_status(self):
        """Test that default status is PENDING."""
        job = ScanJob(target_id=uuid4(), name="Test")
        assert job.status == JobStatus.PENDING


class TestToolRun:
    """Tests for ToolRun model."""

    def test_create_tool_run(self):
        """Test creating a tool run."""
        job_id = uuid4()
        run = ToolRun(job_id=job_id, tool_name="nmap", tool_version="7.94", command="nmap -sV example.com")
        assert run.job_id == job_id
        assert run.tool_name == "nmap"
        assert run.tool_version == "7.94"
        assert run.command == "nmap -sV example.com"
        assert run.status == ToolStatus.PENDING


class TestEvidence:
    """Tests for Evidence model."""

    def test_create_evidence(self):
        """Test creating evidence."""
        run_id = uuid4()
        evidence = Evidence(
            run_id=run_id,
            type=EvidenceType.XML,
            file_path="/tmp/nmap_output.xml",
            checksum_sha256="abc123",
        )
        assert evidence.run_id == run_id
        assert evidence.type == EvidenceType.XML
        assert evidence.file_path == "/tmp/nmap_output.xml"
        assert evidence.checksum_sha256 == "abc123"


class TestFinding:
    """Tests for Finding model."""

    def test_create_finding(self):
        """Test creating a finding."""
        run_id = uuid4()
        finding = Finding(
            run_id=run_id,
            title="Open SSH Port",
            description="SSH service detected",
            severity=Severity.MEDIUM,
            confidence=Confidence.HIGH,
            category="open_port",
            port=22,
        )
        assert finding.run_id == run_id
        assert finding.title == "Open SSH Port"
        assert finding.severity == Severity.MEDIUM
        assert finding.confidence == Confidence.HIGH
        assert finding.port == 22

    def test_finding_with_cve(self):
        """Test finding with CVE IDs."""
        run_id = uuid4()
        finding = Finding(
            run_id=run_id,
            title="Vulnerable Service",
            description="Known vulnerability",
            severity=Severity.HIGH,
            confidence=Confidence.CONFIRMED,
            category="vulnerability",
            cve_ids=["CVE-2023-1234", "CVE-2023-5678"],
        )
        assert len(finding.cve_ids) == 2
        assert "CVE-2023-1234" in finding.cve_ids

    def test_invalid_port_rejected(self):
        """Test that invalid port numbers are rejected."""
        from pydantic import ValidationError

        run_id = uuid4()
        with pytest.raises(ValidationError):
            Finding(
                run_id=run_id,
                title="Test",
                description="Test",
                severity=Severity.INFO,
                confidence=Confidence.LOW,
                category="test",
                port=99999,  # Invalid port
            )


class TestAsset:
    """Tests for Asset model."""

    def test_create_asset(self):
        """Test creating an asset."""
        job_id = uuid4()
        asset = Asset(
            job_id=job_id,
            type=AssetType.HOST,
            value="192.0.2.1",
            ip_address="192.0.2.1",
            hostname="example.com",
        )
        assert asset.job_id == job_id
        assert asset.type == AssetType.HOST
        assert asset.value == "192.0.2.1"
        assert asset.ip_address == "192.0.2.1"
        assert asset.hostname == "example.com"

    def test_create_service_asset(self):
        """Test creating a service asset."""
        job_id = uuid4()
        asset = Asset(
            job_id=job_id,
            type=AssetType.SERVICE,
            value="example.com:443",
            port=443,
            protocol="tcp",
            service_name="https",
        )
        assert asset.type == AssetType.SERVICE
        assert asset.port == 443
        assert asset.service_name == "https"


class TestIOC:
    """Tests for IOC model."""

    def test_create_ioc(self):
        """Test creating an IOC."""
        ioc = IOC(type=IOCType.IP, value="192.0.2.100", threat_level="high", confidence="high", source="threat_feed")
        assert ioc.type == IOCType.IP
        assert ioc.value == "192.0.2.100"
        assert ioc.threat_level == "high"
        assert ioc.is_active is True

    def test_create_domain_ioc(self):
        """Test creating a domain IOC."""
        ioc = IOC(type=IOCType.DOMAIN, value="malicious.com", threat_level="critical")
        assert ioc.type == IOCType.DOMAIN
        assert ioc.value == "malicious.com"

    def test_create_hash_ioc(self):
        """Test creating a file hash IOC."""
        ioc = IOC(
            type=IOCType.FILE_HASH_SHA256,
            value="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            description="Malware sample",
        )
        assert ioc.type == IOCType.FILE_HASH_SHA256
        assert len(ioc.value) == 64
