"""API security testing based on OWASP API Security Top 10."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

import requests

from .web_security import TestResult, TestSeverity, TestStatus


class APITestSuite(Enum):
    """API security test suites."""

    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_VALIDATION = "data_validation"
    RATE_LIMITING = "rate_limiting"
    INJECTION = "injection"


@dataclass
class APIEndpoint:
    """API endpoint definition."""

    url: str
    method: str
    auth_required: bool = True


class APISecurityTester:
    """API security tester based on OWASP API Top 10."""

    def __init__(self, timeout: int = 10):
        """Initialize API security tester.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.session = requests.Session()

    def test_authentication(self, endpoint: APIEndpoint) -> list[TestResult]:
        """Test API authentication (API1:2023 Broken Object Level Authorization).

        Args:
            endpoint: API endpoint to test

        Returns:
            List of test results
        """
        results = []

        try:
            # Test without authentication
            response = self.session.request(endpoint.method, endpoint.url, timeout=self.timeout, verify=False)

            if endpoint.auth_required:
                if response.status_code == 200:
                    results.append(
                        TestResult(
                            test_id="api_auth_missing",
                            test_name="API Authentication Required",
                            status=TestStatus.FAIL,
                            severity=TestSeverity.HIGH,
                            description="API endpoint accessible without authentication",
                            details={"endpoint": endpoint.url, "method": endpoint.method},
                            recommendations=["Implement authentication for this endpoint"],
                        )
                    )
                elif response.status_code in [401, 403]:
                    results.append(
                        TestResult(
                            test_id="api_auth_enforced",
                            test_name="API Authentication Enforced",
                            status=TestStatus.PASS,
                            severity=TestSeverity.INFO,
                            description="API endpoint properly requires authentication",
                            details={"endpoint": endpoint.url},
                        )
                    )

        except requests.RequestException as e:
            results.append(
                TestResult(
                    test_id="api_auth_error",
                    test_name="API Authentication Test",
                    status=TestStatus.ERROR,
                    severity=TestSeverity.INFO,
                    description=f"Failed to test authentication: {str(e)}",
                )
            )

        return results

    def test_rate_limiting(self, endpoint: APIEndpoint, requests_count: int = 10) -> list[TestResult]:
        """Test API rate limiting (API4:2023 Unrestricted Resource Consumption).

        Args:
            endpoint: API endpoint to test
            requests_count: Number of requests to send

        Returns:
            List of test results
        """
        results = []

        try:
            status_codes = []
            for _ in range(requests_count):
                response = self.session.request(endpoint.method, endpoint.url, timeout=self.timeout, verify=False)
                status_codes.append(response.status_code)

            # Check if rate limiting was triggered
            if 429 in status_codes:
                results.append(
                    TestResult(
                        test_id="api_rate_limiting_present",
                        test_name="API Rate Limiting",
                        status=TestStatus.PASS,
                        severity=TestSeverity.INFO,
                        description="API endpoint has rate limiting enabled",
                        details={"endpoint": endpoint.url},
                    )
                )
            else:
                results.append(
                    TestResult(
                        test_id="api_rate_limiting_missing",
                        test_name="API Rate Limiting",
                        status=TestStatus.WARNING,
                        severity=TestSeverity.MEDIUM,
                        description="No rate limiting detected on API endpoint",
                        details={"endpoint": endpoint.url, "requests_sent": requests_count},
                        recommendations=["Implement rate limiting to prevent abuse"],
                    )
                )

        except requests.RequestException as e:
            results.append(
                TestResult(
                    test_id="api_rate_limiting_error",
                    test_name="API Rate Limiting Test",
                    status=TestStatus.ERROR,
                    severity=TestSeverity.INFO,
                    description=f"Failed to test rate limiting: {str(e)}",
                )
            )

        return results

    def test_all(self, endpoint: APIEndpoint) -> list[TestResult]:
        """Run all API security tests.

        Args:
            endpoint: API endpoint to test

        Returns:
            List of test results
        """
        results = []

        results.extend(self.test_authentication(endpoint))
        results.extend(self.test_rate_limiting(endpoint))

        return results
