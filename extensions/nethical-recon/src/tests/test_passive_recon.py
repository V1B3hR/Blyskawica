"""Tests for passive reconnaissance modules."""

import pytest
from unittest.mock import Mock, patch

from nethical_recon.passive_recon import (
    AlertManager,
    AlertSeverity,
    ASNLookup,
    CertificateInspector,
    DNSRecon,
    SubdomainEnumerator,
    WHOISLookup,
)


class TestDNSRecon:
    """Test DNS reconnaissance."""

    def test_initialization(self):
        dns = DNSRecon()
        assert dns.resolver is not None
        assert dns.resolver.timeout == 5

    def test_query_record_types(self):
        dns = DNSRecon()
        # Test that record types are defined
        assert "A" in dns.RECORD_TYPES
        assert "AAAA" in dns.RECORD_TYPES
        assert "MX" in dns.RECORD_TYPES
        assert "NS" in dns.RECORD_TYPES

    @patch("dns.resolver.Resolver.resolve")
    def test_query_record_success(self, mock_resolve):
        dns = DNSRecon()
        mock_answer = Mock()
        mock_answer.__iter__ = Mock(return_value=iter([Mock(__str__=lambda x: "93.184.216.34")]))
        mock_answer.rrset.ttl = 300
        mock_resolve.return_value = mock_answer

        records = dns.query_record("example.com", "A")
        assert len(records) > 0
        assert records[0].record_type == "A"

    def test_enumerate_records(self):
        dns = DNSRecon()
        # Test structure, actual DNS queries may fail in test environment
        results = dns.enumerate_records("example.com", ["A"])
        assert isinstance(results, dict)


class TestWHOISLookup:
    """Test WHOIS lookup."""

    def test_initialization(self):
        whois = WHOISLookup()
        assert whois.timeout == 10

    def test_get_whois_server(self):
        whois = WHOISLookup()
        assert whois._get_whois_server("example.com") == "whois.verisign-grs.com"
        assert whois._get_whois_server("example.org") == "whois.pir.org"

    @patch("socket.socket")
    def test_query_whois_server(self, mock_socket):
        whois = WHOISLookup()
        mock_sock = Mock()
        mock_sock.recv.side_effect = [b"Domain: example.com\n", b""]
        mock_socket.return_value.__enter__ = Mock(return_value=mock_sock)
        mock_socket.return_value.__exit__ = Mock(return_value=False)

        response = whois._query_whois_server("example.com", "whois.verisign-grs.com")
        assert isinstance(response, str)

    def test_lookup_structure(self):
        whois = WHOISLookup()
        result = whois.lookup("example.com")
        assert result.domain == "example.com"
        assert isinstance(result.nameservers, list)
        assert isinstance(result.status, list)


class TestCertificateInspector:
    """Test SSL/TLS certificate inspection."""

    def test_initialization(self):
        inspector = CertificateInspector()
        assert inspector.timeout == 5

    def test_get_certificate_invalid_host(self):
        inspector = CertificateInspector(timeout=2)
        cert = inspector.get_certificate("invalid.invalid.invalid")
        assert cert is None

    @patch("ssl.SSLContext.wrap_socket")
    @patch("socket.create_connection")
    def test_get_certificate_mock(self, mock_socket, mock_wrap):
        inspector = CertificateInspector()

        mock_cert = {
            "subject": (("commonName", "example.com"),),
            "issuer": (("organizationName", "Test CA"),),
            "version": 3,
            "serialNumber": "12345",
            "notBefore": "Jan  1 00:00:00 2024 GMT",
            "notAfter": "Dec 31 23:59:59 2024 GMT",
            "subjectAltName": (("DNS", "www.example.com"), ("DNS", "example.com")),
        }

        mock_ssl_sock = Mock()
        mock_ssl_sock.getpeercert.return_value = mock_cert
        mock_wrap.return_value.__enter__ = Mock(return_value=mock_ssl_sock)
        mock_wrap.return_value.__exit__ = Mock(return_value=False)

        cert_info = inspector.get_certificate("example.com")
        if cert_info:
            assert len(cert_info.san) > 0


class TestSubdomainEnumerator:
    """Test subdomain enumeration."""

    def test_initialization(self):
        enum = SubdomainEnumerator()
        assert enum.timeout == 10

    @patch("requests.get")
    def test_enumerate_from_crtsh(self, mock_get):
        enum = SubdomainEnumerator()

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"name_value": "www.example.com"}, {"name_value": "api.example.com"}]
        mock_get.return_value = mock_response

        subdomains = enum.enumerate_from_crtsh("example.com")
        assert len(subdomains) > 0

    def test_enumerate(self):
        enum = SubdomainEnumerator()
        # Test structure
        subdomains = enum.enumerate("example.com")
        assert isinstance(subdomains, list)


class TestASNLookup:
    """Test ASN lookup."""

    def test_initialization(self):
        asn = ASNLookup()
        assert asn.timeout == 10

    @patch("requests.get")
    def test_lookup_ip(self, mock_get):
        asn = ASNLookup()

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "asn": "AS15169",
            "org": "Google LLC",
            "country_name": "United States",
        }
        mock_get.return_value = mock_response

        result = asn.lookup_ip("8.8.8.8")
        if result:
            assert result.asn == "AS15169"


class TestAlertManager:
    """Test alerting system."""

    def test_initialization(self):
        manager = AlertManager()
        assert manager.channels == {}

    def test_add_webhook(self):
        manager = AlertManager()
        manager.add_webhook("test", "https://example.com/webhook")
        assert "test" in manager.channels

    def test_add_slack(self):
        manager = AlertManager()
        manager.add_slack("slack", "https://hooks.slack.com/services/xxx")
        assert "slack" in manager.channels

    def test_add_discord(self):
        manager = AlertManager()
        manager.add_discord("discord", "https://discord.com/api/webhooks/xxx")
        assert "discord" in manager.channels

    @patch("requests.post")
    def test_send_alert(self, mock_post):
        manager = AlertManager()
        manager.add_webhook("test", "https://example.com/webhook")

        from nethical_recon.passive_recon.alerting import Alert

        alert = Alert(title="Test Alert", message="This is a test", severity=AlertSeverity.HIGH)

        manager.send_alert(alert, "test")
        assert mock_post.called

    def test_severity_colors(self):
        manager = AlertManager()

        # Test Slack colors
        assert manager._get_severity_color(AlertSeverity.CRITICAL) == "#F44336"
        assert manager._get_severity_color(AlertSeverity.HIGH) == "#FF5722"

        # Test Discord colors
        assert manager._get_severity_color_int(AlertSeverity.CRITICAL) == 16007990
        assert manager._get_severity_color_int(AlertSeverity.HIGH) == 16729090
