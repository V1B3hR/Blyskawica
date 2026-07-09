"""Web security testing based on OWASP WSTG."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

import requests


class TestSeverity(Enum):
    """Test result severity levels."""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TestStatus(Enum):
    """Test status."""

    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    SKIP = "skip"
    ERROR = "error"


@dataclass
class TestResult:
    """Result from a security test."""

    test_id: str
    test_name: str
    status: TestStatus
    severity: TestSeverity
    description: str
    details: dict[str, Any] = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class SecurityTest:
    """Security test definition."""

    test_id: str
    name: str
    description: str
    category: str
    owasp_ref: Optional[str] = None


class WebSecurityTester:
    """Web security tester based on OWASP WSTG."""

    def __init__(self, timeout: int = 10):
        """Initialize web security tester.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Nethical-Recon-Security-Scanner"})

    def test_security_headers(self, url: str) -> list[TestResult]:
        """Test for security headers (OWASP WSTG-CONF-06).

        Args:
            url: Target URL

        Returns:
            List of test results
        """
        results = []

        try:
            response = self.session.get(url, timeout=self.timeout, verify=False)
            headers = response.headers

            # Required security headers
            required_headers = {
                "X-Content-Type-Options": {
                    "expected": "nosniff",
                    "severity": TestSeverity.MEDIUM,
                    "description": "Prevents MIME type sniffing",
                },
                "X-Frame-Options": {
                    "expected": ["DENY", "SAMEORIGIN"],
                    "severity": TestSeverity.MEDIUM,
                    "description": "Prevents clickjacking attacks",
                },
                "Strict-Transport-Security": {
                    "expected": None,  # Just check presence
                    "severity": TestSeverity.HIGH,
                    "description": "Enforces HTTPS connections",
                },
                "Content-Security-Policy": {
                    "expected": None,
                    "severity": TestSeverity.HIGH,
                    "description": "Mitigates XSS and injection attacks",
                },
                "X-XSS-Protection": {
                    "expected": "1; mode=block",
                    "severity": TestSeverity.LOW,
                    "description": "Legacy XSS protection (deprecated but still useful)",
                },
            }

            for header_name, config in required_headers.items():
                if header_name in headers:
                    header_value = headers[header_name]
                    expected = config["expected"]

                    if expected is None:
                        # Just check presence
                        results.append(
                            TestResult(
                                test_id=f"header_{header_name.lower().replace('-', '_')}",
                                test_name=f"Security Header: {header_name}",
                                status=TestStatus.PASS,
                                severity=TestSeverity.INFO,
                                description=f"{header_name} header is present",
                                details={"header": header_name, "value": header_value},
                            )
                        )
                    elif isinstance(expected, list):
                        if any(exp in header_value for exp in expected):
                            results.append(
                                TestResult(
                                    test_id=f"header_{header_name.lower().replace('-', '_')}",
                                    test_name=f"Security Header: {header_name}",
                                    status=TestStatus.PASS,
                                    severity=TestSeverity.INFO,
                                    description=f"{header_name} header is properly configured",
                                    details={"header": header_name, "value": header_value},
                                )
                            )
                        else:
                            results.append(
                                TestResult(
                                    test_id=f"header_{header_name.lower().replace('-', '_')}",
                                    test_name=f"Security Header: {header_name}",
                                    status=TestStatus.WARNING,
                                    severity=config["severity"],
                                    description=f"{header_name} header has unexpected value",
                                    details={"header": header_name, "value": header_value, "expected": expected},
                                    recommendations=[f"Set {header_name} to one of: {', '.join(expected)}"],
                                )
                            )
                    else:
                        if expected in header_value:
                            results.append(
                                TestResult(
                                    test_id=f"header_{header_name.lower().replace('-', '_')}",
                                    test_name=f"Security Header: {header_name}",
                                    status=TestStatus.PASS,
                                    severity=TestSeverity.INFO,
                                    description=f"{header_name} header is properly configured",
                                    details={"header": header_name, "value": header_value},
                                )
                            )
                        else:
                            results.append(
                                TestResult(
                                    test_id=f"header_{header_name.lower().replace('-', '_')}",
                                    test_name=f"Security Header: {header_name}",
                                    status=TestStatus.WARNING,
                                    severity=config["severity"],
                                    description=f"{header_name} header has unexpected value",
                                    details={"header": header_name, "value": header_value, "expected": expected},
                                    recommendations=[f"Set {header_name} to: {expected}"],
                                )
                            )
                else:
                    results.append(
                        TestResult(
                            test_id=f"header_{header_name.lower().replace('-', '_')}",
                            test_name=f"Security Header: {header_name}",
                            status=TestStatus.FAIL,
                            severity=config["severity"],
                            description=f"{header_name} header is missing - {config['description']}",
                            details={"header": header_name},
                            recommendations=[f"Add {header_name} header to responses"],
                        )
                    )

        except requests.RequestException as e:
            results.append(
                TestResult(
                    test_id="security_headers_error",
                    test_name="Security Headers Test",
                    status=TestStatus.ERROR,
                    severity=TestSeverity.INFO,
                    description=f"Failed to test security headers: {str(e)}",
                )
            )

        return results

    def test_information_disclosure(self, url: str) -> list[TestResult]:
        """Test for information disclosure (OWASP WSTG-INFO-05).

        Args:
            url: Target URL

        Returns:
            List of test results
        """
        results = []

        try:
            response = self.session.get(url, timeout=self.timeout, verify=False)
            headers = response.headers

            # Check for information disclosure in headers
            disclosure_headers = ["Server", "X-Powered-By", "X-AspNet-Version", "X-AspNetMvc-Version"]

            for header in disclosure_headers:
                if header in headers:
                    results.append(
                        TestResult(
                            test_id=f"info_disclosure_{header.lower().replace('-', '_')}",
                            test_name=f"Information Disclosure: {header}",
                            status=TestStatus.WARNING,
                            severity=TestSeverity.LOW,
                            description=f"{header} header reveals server information",
                            details={"header": header, "value": headers[header]},
                            recommendations=[f"Remove or obfuscate {header} header"],
                        )
                    )

            # Check for version disclosure in response body
            version_patterns = [
                (r"WordPress [\d.]+", "WordPress version disclosed"),
                (r"Joomla! [\d.]+", "Joomla version disclosed"),
                (r"Drupal [\d.]+", "Drupal version disclosed"),
                (r"powered by [\w\s]+ [\d.]+", "Technology version disclosed"),
            ]

            for pattern, description in version_patterns:
                matches = re.findall(pattern, response.text, re.IGNORECASE)
                if matches:
                    results.append(
                        TestResult(
                            test_id="info_disclosure_version",
                            test_name="Information Disclosure: Version",
                            status=TestStatus.WARNING,
                            severity=TestSeverity.LOW,
                            description=description,
                            details={"matches": matches[:3]},  # Limit to first 3
                            recommendations=["Remove version information from public pages"],
                        )
                    )
                    break  # Only report once

        except requests.RequestException as e:
            results.append(
                TestResult(
                    test_id="info_disclosure_error",
                    test_name="Information Disclosure Test",
                    status=TestStatus.ERROR,
                    severity=TestSeverity.INFO,
                    description=f"Failed to test for information disclosure: {str(e)}",
                )
            )

        return results

    def test_all(self, url: str) -> list[TestResult]:
        """Run all security tests.

        Args:
            url: Target URL

        Returns:
            List of all test results
        """
        results = []

        results.extend(self.test_security_headers(url))
        results.extend(self.test_information_disclosure(url))

        return results

    def get_failed_tests(self, results: list[TestResult]) -> list[TestResult]:
        """Get failed tests from results.

        Args:
            results: List of test results

        Returns:
            List of failed tests
        """
        return [r for r in results if r.status == TestStatus.FAIL]

    def get_summary(self, results: list[TestResult]) -> dict[str, Any]:
        """Generate test summary.

        Args:
            results: List of test results

        Returns:
            Summary dictionary
        """
        return {
            "total_tests": len(results),
            "passed": len([r for r in results if r.status == TestStatus.PASS]),
            "failed": len([r for r in results if r.status == TestStatus.FAIL]),
            "warnings": len([r for r in results if r.status == TestStatus.WARNING]),
            "errors": len([r for r in results if r.status == TestStatus.ERROR]),
            "severity_counts": {
                "critical": len([r for r in results if r.severity == TestSeverity.CRITICAL]),
                "high": len([r for r in results if r.severity == TestSeverity.HIGH]),
                "medium": len([r for r in results if r.severity == TestSeverity.MEDIUM]),
                "low": len([r for r in results if r.severity == TestSeverity.LOW]),
            },
        }
