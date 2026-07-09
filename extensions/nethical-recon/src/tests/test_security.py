"""Tests for input validation and OWASP compliance modules."""

import pytest

from nethical_recon.security import (
    InputType,
    InputValidator,
    OWASPChecker,
    OWASPLevel,
    SecureLogger,
    ValidationError,
)


class TestInputValidator:
    """Test input validation."""

    def test_validate_ip_address(self):
        validator = InputValidator()

        # Valid IPs
        assert validator.validate_ip_address("192.168.1.1")
        assert validator.validate_ip_address("10.0.0.1")
        assert validator.validate_ip_address("2001:0db8:85a3::8a2e:0370:7334")

        # Invalid IPs
        with pytest.raises(ValidationError):
            validator.validate_ip_address("999.999.999.999")
        with pytest.raises(ValidationError):
            validator.validate_ip_address("not an ip")

    def test_validate_cidr(self):
        validator = InputValidator()

        # Valid CIDR
        assert validator.validate_cidr("192.168.1.0/24")
        assert validator.validate_cidr("10.0.0.0/8")

        # Invalid CIDR
        with pytest.raises(ValidationError):
            validator.validate_cidr("192.168.1.0/99")
        with pytest.raises(ValidationError):
            validator.validate_cidr("not a cidr")

    def test_validate_domain(self):
        validator = InputValidator()

        # Valid domains
        assert validator.validate_domain("example.com")
        assert validator.validate_domain("sub.domain.example.com")

        # Invalid domains
        with pytest.raises(ValidationError):
            validator.validate_domain("not a domain!")
        with pytest.raises(ValidationError):
            validator.validate_domain("a" * 300)  # Too long

    def test_validate_url(self):
        validator = InputValidator()

        # Valid URLs
        assert validator.validate_url("https://example.com")
        assert validator.validate_url("http://example.com/path")

        # Invalid URLs
        with pytest.raises(ValidationError):
            validator.validate_url("ftp://example.com")  # Wrong scheme
        with pytest.raises(ValidationError):
            validator.validate_url("not a url")

    def test_validate_url_ssrf_prevention(self):
        validator = InputValidator(strict_mode=True)

        # Should block localhost
        with pytest.raises(ValidationError):
            validator.validate_url("http://localhost/api")
        with pytest.raises(ValidationError):
            validator.validate_url("http://127.0.0.1/api")

    def test_validate_email(self):
        validator = InputValidator()

        # Valid emails
        assert validator.validate_email("user@example.com")
        assert validator.validate_email("test.user+tag@example.com")

        # Invalid emails
        with pytest.raises(ValidationError):
            validator.validate_email("not an email")
        with pytest.raises(ValidationError):
            validator.validate_email("missing@domain")

    def test_validate_port(self):
        validator = InputValidator()

        # Valid ports
        assert validator.validate_port(80)
        assert validator.validate_port(443)
        assert validator.validate_port(65535)

        # Invalid ports
        with pytest.raises(ValidationError):
            validator.validate_port(0)
        with pytest.raises(ValidationError):
            validator.validate_port(70000)

    def test_sanitize_sql_input(self):
        validator = InputValidator()

        result = validator.sanitize_sql_input("SELECT * FROM users")
        assert not result.validation_passed
        assert result.was_modified

        result = validator.sanitize_sql_input("safe input")
        assert result.validation_passed
        assert not result.was_modified

    def test_sanitize_command_input(self):
        validator = InputValidator()

        result = validator.sanitize_command_input("ls; rm -rf /")
        assert not result.validation_passed
        assert result.was_modified
        assert ";" in result.removed_chars

    def test_sanitize_path(self):
        validator = InputValidator()

        result = validator.sanitize_path("../../etc/passwd")
        assert not result.validation_passed
        assert result.was_modified

    def test_sanitize_alphanumeric(self):
        validator = InputValidator()

        result = validator.sanitize_alphanumeric("test123")
        assert result.validation_passed
        assert not result.was_modified

        result = validator.sanitize_alphanumeric("test@#$123")
        assert not result.validation_passed
        assert result.was_modified

    def test_validate_and_sanitize(self):
        validator = InputValidator()

        # Test IP validation
        result = validator.validate_and_sanitize("192.168.1.1", InputType.IP_ADDRESS)
        assert result.validation_passed

        # Test domain validation
        result = validator.validate_and_sanitize("example.com", InputType.DOMAIN)
        assert result.validation_passed

        # Test SQL sanitization
        result = validator.validate_and_sanitize("DROP TABLE", InputType.SQL_SAFE)
        assert not result.validation_passed


class TestOWASPChecker:
    """Test OWASP compliance checker."""

    def test_check_input_validation(self):
        checker = OWASPChecker()
        check = checker.check_input_validation(has_validator=True, validates_all_inputs=True)
        assert check.passed
        assert check.level == OWASPLevel.LEVEL_1

    def test_check_authentication(self):
        checker = OWASPChecker()
        check = checker.check_authentication(has_auth=True)
        assert check.passed

    def test_check_access_control(self):
        checker = OWASPChecker()
        check = checker.check_access_control(has_rbac=True)
        assert check.passed

    def test_check_logging(self):
        checker = OWASPChecker()
        check = checker.check_logging(has_logging=True)
        assert check.passed

    def test_check_ssrf_protection(self):
        checker = OWASPChecker()
        check = checker.check_ssrf_protection(validates_urls=True)
        assert check.passed

    def test_generate_report(self):
        checker = OWASPChecker()
        checks = [
            checker.check_input_validation(True, True),
            checker.check_authentication(True),
            checker.check_logging(True),
        ]
        report = checker.generate_report(checks)

        assert report.total_checks == 3
        assert report.passed_checks == 3
        assert report.compliance_score == 100.0

    def test_run_basic_checks(self):
        checker = OWASPChecker()
        report = checker.run_basic_checks(
            has_input_validation=True,
            has_authentication=True,
            has_logging=True,
            has_rbac=True,
            uses_tls=True,
            validates_urls=True,
        )

        assert report.total_checks == 6
        assert report.passed_checks == 6
        assert report.compliance_score == 100.0


class TestSecureLogger:
    """Test secure logging."""

    def test_sanitize_log_message(self):
        logger = SecureLogger()

        # Should mask passwords
        message = "User login: password=secret123"
        sanitized = logger.sanitize_log_message(message)
        assert "secret123" not in sanitized
        assert "********" in sanitized

        # Should mask API keys
        message = "API key: api_key=abcd1234"
        sanitized = logger.sanitize_log_message(message)
        assert "abcd1234" not in sanitized

    def test_mask_sensitive_dict(self):
        logger = SecureLogger()

        data = {"username": "user1", "password": "secret", "email": "user@example.com"}
        masked = logger.mask_sensitive_dict(data)

        assert masked["username"] == "user1"
        assert masked["password"] == "********"
        assert masked["email"] == "user@example.com"

    def test_hash_pii(self):
        logger = SecureLogger()

        pii = "user@example.com"
        hashed = logger.hash_pii(pii)

        # Should be a hash
        assert len(hashed) == 64  # SHA256 hex length
        assert hashed != pii

    def test_create_audit_entry(self):
        logger = SecureLogger()

        entry = logger.create_audit_entry(
            event_type="authentication",
            actor="user123",
            action="login",
            resource="api",
            result="success",
            details={"ip": "1.2.3.4", "password": "secret"},
        )

        assert entry["event_type"] == "authentication"
        assert entry["actor"] == "user123"
        assert entry["details"]["password"] == "********"

    def test_format_security_event(self):
        logger = SecureLogger()

        event = logger.format_security_event(
            severity="critical", category="authentication", message="Failed login attempt", context={"attempts": 5}
        )

        assert event["severity"] == "critical"
        assert event["category"] == "authentication"
        assert "context" in event

    def test_should_log_security_event(self):
        logger = SecureLogger()

        # Should log critical events
        assert logger.should_log_security_event("any", "critical")

        # Should log security events
        assert logger.should_log_security_event("authentication", "info")

        # May not log non-security info events
        assert not logger.should_log_security_event("general", "info")
