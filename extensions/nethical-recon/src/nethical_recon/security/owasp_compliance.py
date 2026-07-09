"""OWASP ASVS compliance checker for Nethical Recon.

This module implements OWASP Application Security Verification Standard (ASVS)
Level 1 and Level 2 compliance checks.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


class OWASPLevel(Enum):
    """OWASP ASVS compliance levels."""

    LEVEL_1 = "level_1"  # Opportunistic
    LEVEL_2 = "level_2"  # Standard
    LEVEL_3 = "level_3"  # Advanced


class OWASPCategory(Enum):
    """OWASP Top 10 categories."""

    BROKEN_ACCESS_CONTROL = "A01:2021-Broken Access Control"
    CRYPTOGRAPHIC_FAILURES = "A02:2021-Cryptographic Failures"
    INJECTION = "A03:2021-Injection"
    INSECURE_DESIGN = "A04:2021-Insecure Design"
    SECURITY_MISCONFIGURATION = "A05:2021-Security Misconfiguration"
    VULNERABLE_COMPONENTS = "A06:2021-Vulnerable and Outdated Components"
    IDENTIFICATION_AUTH_FAILURES = "A07:2021-Identification and Authentication Failures"
    SOFTWARE_DATA_INTEGRITY_FAILURES = "A08:2021-Software and Data Integrity Failures"
    SECURITY_LOGGING_MONITORING = "A09:2021-Security Logging and Monitoring Failures"
    SSRF = "A10:2021-Server-Side Request Forgery"


@dataclass
class ComplianceCheck:
    """Represents a single OWASP compliance check."""

    id: str
    category: OWASPCategory
    level: OWASPLevel
    title: str
    description: str
    passed: bool
    details: Optional[str] = None


@dataclass
class ComplianceReport:
    """OWASP compliance report."""

    level: OWASPLevel
    total_checks: int
    passed_checks: int
    failed_checks: int
    compliance_score: float
    checks: list[ComplianceCheck]


class OWASPChecker:
    """Checks OWASP ASVS compliance for Nethical Recon components.

    Implements basic compliance checking for:
    - V1: Architecture, Design and Threat Modeling
    - V2: Authentication
    - V3: Session Management
    - V4: Access Control
    - V5: Input Validation
    - V7: Error Handling and Logging
    - V8: Data Protection
    - V9: Communications
    - V12: File and Resources
    - V13: API and Web Service
    """

    def __init__(self, target_level: OWASPLevel = OWASPLevel.LEVEL_2):
        """Initialize OWASP checker.

        Args:
            target_level: Target OWASP ASVS level for compliance
        """
        self.target_level = target_level
        self.checks: list[ComplianceCheck] = []

    def check_input_validation(self, has_validator: bool, validates_all_inputs: bool) -> ComplianceCheck:
        """Check V5: Input Validation Requirements (ASVS 5.1.1).

        Args:
            has_validator: Whether input validation is implemented
            validates_all_inputs: Whether all inputs are validated

        Returns:
            ComplianceCheck result
        """
        passed = has_validator and validates_all_inputs
        return ComplianceCheck(
            id="ASVS-5.1.1",
            category=OWASPCategory.INJECTION,
            level=OWASPLevel.LEVEL_1,
            title="Input Validation",
            description="Application validates all input data from untrusted sources",
            passed=passed,
            details="Input validator present and used" if passed else "Missing input validation",
        )

    def check_output_encoding(self, has_encoding: bool) -> ComplianceCheck:
        """Check V5: Output Encoding (ASVS 5.3.1).

        Args:
            has_encoding: Whether output encoding is implemented

        Returns:
            ComplianceCheck result
        """
        passed = has_encoding
        return ComplianceCheck(
            id="ASVS-5.3.1",
            category=OWASPCategory.INJECTION,
            level=OWASPLevel.LEVEL_1,
            title="Output Encoding",
            description="Application properly encodes all output to prevent injection",
            passed=passed,
            details="Output encoding implemented" if passed else "Missing output encoding",
        )

    def check_authentication(self, has_auth: bool, multi_factor: bool = False) -> ComplianceCheck:
        """Check V2: Authentication (ASVS 2.1.1).

        Args:
            has_auth: Whether authentication is implemented
            multi_factor: Whether multi-factor authentication is available

        Returns:
            ComplianceCheck result
        """
        if self.target_level == OWASPLevel.LEVEL_1:
            passed = has_auth
            detail = "Authentication present" if passed else "Missing authentication"
        else:
            passed = has_auth and multi_factor
            detail = (
                "Authentication with MFA" if passed else "Authentication present but MFA not implemented or not checked"
            )

        return ComplianceCheck(
            id="ASVS-2.1.1",
            category=OWASPCategory.IDENTIFICATION_AUTH_FAILURES,
            level=OWASPLevel.LEVEL_1 if not multi_factor else OWASPLevel.LEVEL_2,
            title="Authentication",
            description="Application implements secure authentication mechanisms",
            passed=passed,
            details=detail,
        )

    def check_session_management(self, has_session_mgmt: bool, secure_cookies: bool = False) -> ComplianceCheck:
        """Check V3: Session Management (ASVS 3.1.1).

        Args:
            has_session_mgmt: Whether session management is implemented
            secure_cookies: Whether secure session cookies are used

        Returns:
            ComplianceCheck result
        """
        if self.target_level == OWASPLevel.LEVEL_1:
            passed = has_session_mgmt
        else:
            passed = has_session_mgmt and secure_cookies

        return ComplianceCheck(
            id="ASVS-3.1.1",
            category=OWASPCategory.IDENTIFICATION_AUTH_FAILURES,
            level=OWASPLevel.LEVEL_1,
            title="Session Management",
            description="Application implements secure session management",
            passed=passed,
            details="Session management implemented" if passed else "Session management issues detected",
        )

    def check_access_control(self, has_rbac: bool, principle_of_least_privilege: bool = False) -> ComplianceCheck:
        """Check V4: Access Control (ASVS 4.1.1).

        Args:
            has_rbac: Whether role-based access control is implemented
            principle_of_least_privilege: Whether least privilege is enforced

        Returns:
            ComplianceCheck result
        """
        if self.target_level == OWASPLevel.LEVEL_1:
            passed = has_rbac
        else:
            passed = has_rbac and principle_of_least_privilege

        return ComplianceCheck(
            id="ASVS-4.1.1",
            category=OWASPCategory.BROKEN_ACCESS_CONTROL,
            level=OWASPLevel.LEVEL_1,
            title="Access Control",
            description="Application enforces access control at a trusted service layer",
            passed=passed,
            details="RBAC implemented" if passed else "Access control not properly implemented",
        )

    def check_logging(
        self, has_logging: bool, secure_logging: bool = False, audit_trail: bool = False
    ) -> ComplianceCheck:
        """Check V7: Error Handling and Logging (ASVS 7.1.1).

        Args:
            has_logging: Whether logging is implemented
            secure_logging: Whether logging is done securely (no sensitive data)
            audit_trail: Whether audit trail is maintained

        Returns:
            ComplianceCheck result
        """
        if self.target_level == OWASPLevel.LEVEL_1:
            passed = has_logging
        else:
            passed = has_logging and secure_logging and audit_trail

        return ComplianceCheck(
            id="ASVS-7.1.1",
            category=OWASPCategory.SECURITY_LOGGING_MONITORING,
            level=OWASPLevel.LEVEL_1,
            title="Security Logging",
            description="Application logs security events with sufficient detail",
            passed=passed,
            details="Logging implemented" if passed else "Logging not properly configured",
        )

    def check_crypto(self, uses_strong_crypto: bool, proper_key_mgmt: bool = False) -> ComplianceCheck:
        """Check V8: Data Protection (ASVS 8.1.1).

        Args:
            uses_strong_crypto: Whether strong cryptography is used
            proper_key_mgmt: Whether proper key management is in place

        Returns:
            ComplianceCheck result
        """
        if self.target_level == OWASPLevel.LEVEL_1:
            passed = uses_strong_crypto
        else:
            passed = uses_strong_crypto and proper_key_mgmt

        return ComplianceCheck(
            id="ASVS-8.1.1",
            category=OWASPCategory.CRYPTOGRAPHIC_FAILURES,
            level=OWASPLevel.LEVEL_1,
            title="Cryptography",
            description="Application uses approved cryptographic algorithms",
            passed=passed,
            details="Strong cryptography in use" if passed else "Weak or missing cryptography",
        )

    def check_communications_security(self, uses_tls: bool, tls_version_current: bool = False) -> ComplianceCheck:
        """Check V9: Communications (ASVS 9.1.1).

        Args:
            uses_tls: Whether TLS is used for communications
            tls_version_current: Whether current TLS version (1.2+) is enforced

        Returns:
            ComplianceCheck result
        """
        if self.target_level == OWASPLevel.LEVEL_1:
            passed = uses_tls
        else:
            passed = uses_tls and tls_version_current

        return ComplianceCheck(
            id="ASVS-9.1.1",
            category=OWASPCategory.CRYPTOGRAPHIC_FAILURES,
            level=OWASPLevel.LEVEL_1,
            title="Communications Security",
            description="Application uses TLS for all sensitive communications",
            passed=passed,
            details="TLS enabled" if passed else "TLS not properly configured",
        )

    def check_ssrf_protection(self, validates_urls: bool, blocks_private_ips: bool = False) -> ComplianceCheck:
        """Check protection against SSRF attacks (OWASP Top 10 A10:2021).

        Args:
            validates_urls: Whether URLs are validated
            blocks_private_ips: Whether private IPs are blocked

        Returns:
            ComplianceCheck result
        """
        if self.target_level == OWASPLevel.LEVEL_1:
            passed = validates_urls
        else:
            passed = validates_urls and blocks_private_ips

        return ComplianceCheck(
            id="OWASP-A10",
            category=OWASPCategory.SSRF,
            level=OWASPLevel.LEVEL_1,
            title="SSRF Protection",
            description="Application prevents Server-Side Request Forgery",
            passed=passed,
            details="SSRF protection enabled" if passed else "SSRF protection not implemented",
        )

    def generate_report(self, checks: list[ComplianceCheck]) -> ComplianceReport:
        """Generate compliance report from checks.

        Args:
            checks: List of compliance checks

        Returns:
            ComplianceReport with summary and details
        """
        total = len(checks)
        passed = sum(1 for check in checks if check.passed)
        failed = total - passed
        score = (passed / total * 100) if total > 0 else 0.0

        return ComplianceReport(
            level=self.target_level,
            total_checks=total,
            passed_checks=passed,
            failed_checks=failed,
            compliance_score=score,
            checks=checks,
        )

    def run_basic_checks(
        self,
        has_input_validation: bool = False,
        has_authentication: bool = False,
        has_logging: bool = False,
        has_rbac: bool = False,
        uses_tls: bool = False,
        validates_urls: bool = False,
    ) -> ComplianceReport:
        """Run basic OWASP compliance checks.

        Args:
            has_input_validation: Whether input validation is implemented
            has_authentication: Whether authentication is implemented
            has_logging: Whether logging is implemented
            has_rbac: Whether RBAC is implemented
            uses_tls: Whether TLS is used
            validates_urls: Whether URL validation is implemented

        Returns:
            ComplianceReport with results
        """
        checks = [
            self.check_input_validation(has_input_validation, has_input_validation),
            self.check_authentication(has_authentication),
            self.check_access_control(has_rbac),
            self.check_logging(has_logging),
            self.check_communications_security(uses_tls),
            self.check_ssrf_protection(validates_urls),
        ]

        return self.generate_report(checks)
