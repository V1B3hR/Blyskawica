"""Tests for parsers."""

from __future__ import annotations

from uuid import uuid4

from nethical_recon.core.models import Confidence, Severity
from nethical_recon.core.parsers.nmap_parser import NmapParser


class TestNmapParser:
    """Tests for Nmap parser."""

    def test_parser_can_parse_nmap(self):
        """Test that parser identifies Nmap."""
        parser = NmapParser()
        assert parser.can_parse("nmap")
        assert parser.can_parse("NMAP")
        assert not parser.can_parse("nikto")

    def test_parse_simple_nmap_output(self):
        """Test parsing simple Nmap XML output."""
        parser = NmapParser()
        run_id = uuid4()

        nmap_xml = """<?xml version="1.0"?>
<nmaprun>
    <host>
        <address addr="192.0.2.1" addrtype="ipv4"/>
        <ports>
            <port protocol="tcp" portid="22">
                <state state="open"/>
                <service name="ssh" product="OpenSSH" version="8.2p1"/>
            </port>
            <port protocol="tcp" portid="80">
                <state state="open"/>
                <service name="http" product="nginx" version="1.18.0"/>
            </port>
        </ports>
    </host>
</nmaprun>"""

        findings = parser.parse(nmap_xml, run_id)

        assert len(findings) == 2
        assert all(f.run_id == run_id for f in findings)

        # Check SSH finding
        ssh_finding = next(f for f in findings if f.port == 22)
        assert ssh_finding.title == "Open Port: 22/tcp"
        assert ssh_finding.service == "ssh"
        assert ssh_finding.severity == Severity.MEDIUM
        assert ssh_finding.confidence == Confidence.HIGH
        assert "OpenSSH 8.2p1" in ssh_finding.service_version

        # Check HTTP finding
        http_finding = next(f for f in findings if f.port == 80)
        assert http_finding.title == "Open Port: 80/tcp"
        assert http_finding.service == "http"
        assert http_finding.severity == Severity.MEDIUM

    def test_parse_with_hostname(self):
        """Test parsing Nmap output with hostname."""
        parser = NmapParser()
        run_id = uuid4()

        nmap_xml = """<?xml version="1.0"?>
<nmaprun>
    <host>
        <address addr="192.0.2.1" addrtype="ipv4"/>
        <hostnames>
            <hostname name="example.com"/>
        </hostnames>
        <ports>
            <port protocol="tcp" portid="443">
                <state state="open"/>
                <service name="https"/>
            </port>
        </ports>
    </host>
</nmaprun>"""

        findings = parser.parse(nmap_xml, run_id)

        assert len(findings) == 1
        assert findings[0].affected_asset == "example.com"
        assert findings[0].port == 443

    def test_parse_high_risk_port(self):
        """Test that high-risk ports get HIGH severity."""
        parser = NmapParser()
        run_id = uuid4()

        nmap_xml = """<?xml version="1.0"?>
<nmaprun>
    <host>
        <address addr="192.0.2.1" addrtype="ipv4"/>
        <ports>
            <port protocol="tcp" portid="23">
                <state state="open"/>
                <service name="telnet"/>
            </port>
        </ports>
    </host>
</nmaprun>"""

        findings = parser.parse(nmap_xml, run_id)

        assert len(findings) == 1
        assert findings[0].severity == Severity.HIGH
        assert findings[0].service == "telnet"

    def test_parse_closed_port_ignored(self):
        """Test that closed ports are not included in findings."""
        parser = NmapParser()
        run_id = uuid4()

        nmap_xml = """<?xml version="1.0"?>
<nmaprun>
    <host>
        <address addr="192.0.2.1" addrtype="ipv4"/>
        <ports>
            <port protocol="tcp" portid="22">
                <state state="open"/>
                <service name="ssh"/>
            </port>
            <port protocol="tcp" portid="23">
                <state state="closed"/>
                <service name="telnet"/>
            </port>
        </ports>
    </host>
</nmaprun>"""

        findings = parser.parse(nmap_xml, run_id)

        # Only open port should be in findings
        assert len(findings) == 1
        assert findings[0].port == 22

    def test_parse_invalid_xml(self):
        """Test that invalid XML returns empty list."""
        parser = NmapParser()
        run_id = uuid4()

        invalid_xml = "This is not XML"
        findings = parser.parse(invalid_xml, run_id)

        assert len(findings) == 0

    def test_parse_empty_output(self):
        """Test parsing empty Nmap output."""
        parser = NmapParser()
        run_id = uuid4()

        empty_xml = """<?xml version="1.0"?>
<nmaprun>
</nmaprun>"""

        findings = parser.parse(empty_xml, run_id)

        assert len(findings) == 0
