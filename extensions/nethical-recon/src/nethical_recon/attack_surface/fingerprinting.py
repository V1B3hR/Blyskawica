"""
Technology Fingerprinting and Detection

Provides capabilities for detecting technologies, frameworks, CMS platforms,
and services running on target hosts.
"""

import logging
import re
from dataclasses import dataclass, field
from typing import Any

import requests


@dataclass
class TechnologySignature:
    """Represents a technology detection signature."""

    name: str
    category: str  # web_server, framework, cms, language, database, etc.
    patterns: dict[str, list[str]] = field(default_factory=dict)  # header/body patterns
    confidence: float = 0.0  # 0.0 - 1.0


@dataclass
class DetectionResult:
    """Result of technology detection."""

    technology: str
    category: str
    version: str | None = None
    confidence: float = 0.0
    evidence: list[str] = field(default_factory=list)


class TechnologyFingerprinter:
    """
    Technology Fingerprinter

    Detects technologies, frameworks, and platforms through passive
    and semi-active analysis of HTTP headers, responses, and patterns.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.signatures = self._load_signatures()

    def _load_signatures(self) -> list[TechnologySignature]:
        """Load technology detection signatures."""
        return [
            # Web Servers
            TechnologySignature(
                name="nginx",
                category="web_server",
                patterns={"header": [r"nginx/(\d+\.\d+\.\d+)"], "body": []},
            ),
            TechnologySignature(
                name="Apache",
                category="web_server",
                patterns={"header": [r"Apache/(\d+\.\d+\.\d+)"], "body": []},
            ),
            TechnologySignature(
                name="IIS",
                category="web_server",
                patterns={"header": [r"Microsoft-IIS/(\d+\.\d+)"], "body": []},
            ),
            # Frameworks
            TechnologySignature(
                name="Express.js",
                category="framework",
                patterns={"header": [r"X-Powered-By: Express"], "body": []},
            ),
            TechnologySignature(
                name="Django",
                category="framework",
                patterns={"header": [r"X-Django-Version: (\d+\.\d+)"], "body": [r"csrfmiddlewaretoken"]},
            ),
            TechnologySignature(
                name="Laravel",
                category="framework",
                patterns={"header": [r"X-Powered-By: PHP"], "body": [r"laravel_session"]},
            ),
            TechnologySignature(
                name="Ruby on Rails",
                category="framework",
                patterns={"header": [r"X-Powered-By: Phusion Passenger"], "body": [r"_rails_session"]},
            ),
            TechnologySignature(
                name="ASP.NET",
                category="framework",
                patterns={"header": [r"X-AspNet-Version: (\d+\.\d+)"], "body": [r"__VIEWSTATE"]},
            ),
            # CMS Platforms
            TechnologySignature(
                name="WordPress",
                category="cms",
                patterns={
                    "header": [],
                    "body": [r"wp-content", r"wp-includes", r"wordpress"],
                },
            ),
            TechnologySignature(
                name="Joomla",
                category="cms",
                patterns={
                    "header": [],
                    "body": [r"Joomla!", r"com_content", r"option=com_"],
                },
            ),
            TechnologySignature(
                name="Drupal",
                category="cms",
                patterns={
                    "header": [r"X-Generator: Drupal"],
                    "body": [r"Drupal.settings", r"drupal.js"],
                },
            ),
            # Programming Languages
            TechnologySignature(
                name="PHP",
                category="language",
                patterns={"header": [r"X-Powered-By: PHP/(\d+\.\d+)"], "body": []},
            ),
            TechnologySignature(
                name="Python",
                category="language",
                patterns={"header": [r"Server: Werkzeug", r"Server: Gunicorn"], "body": []},
            ),
            TechnologySignature(
                name="Node.js",
                category="language",
                patterns={"header": [r"X-Powered-By: Express"], "body": []},
            ),
        ]

    def fingerprint(
        self, url: str, headers: dict[str, str] | None = None, body: str | None = None
    ) -> list[DetectionResult]:
        """
        Fingerprint technologies from URL, headers, and body.

        Args:
            url: Target URL
            headers: Optional HTTP headers dict
            body: Optional HTTP response body

        Returns:
            List of detection results
        """
        self.logger.info(f"Fingerprinting technologies for {url}")
        results = []

        # If headers/body not provided, fetch them
        if headers is None or body is None:
            try:
                response = requests.get(url, timeout=10, allow_redirects=True)
                headers = dict(response.headers)
                body = response.text
            except Exception as e:
                self.logger.error(f"Failed to fetch {url}: {e}")
                return results

        # Check each signature
        for sig in self.signatures:
            detection = self._check_signature(sig, headers, body)
            if detection:
                results.append(detection)

        self.logger.info(f"Detected {len(results)} technologies")
        return results

    def _check_signature(
        self, signature: TechnologySignature, headers: dict[str, str], body: str
    ) -> DetectionResult | None:
        """Check if a signature matches the given headers/body."""
        evidence = []
        version = None

        # Check header patterns
        for pattern in signature.patterns.get("header", []):
            for header, value in headers.items():
                match = re.search(pattern, value, re.IGNORECASE)
                if match:
                    evidence.append(f"Header {header}: {value}")
                    if match.groups():
                        version = match.group(1)

        # Check body patterns
        for pattern in signature.patterns.get("body", []):
            if re.search(pattern, body, re.IGNORECASE):
                evidence.append(f"Body pattern: {pattern}")

        if evidence:
            confidence = min(1.0, len(evidence) * 0.3)
            return DetectionResult(
                technology=signature.name,
                category=signature.category,
                version=version,
                confidence=confidence,
                evidence=evidence,
            )

        return None


class ServiceDetector:
    """
    Service Detection

    Detects running services on ports using banner grabbing
    and protocol analysis.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def detect_service(self, host: str, port: int, protocol: str = "tcp") -> dict[str, Any]:
        """
        Detect service running on a specific port.

        Args:
            host: Target host
            port: Target port
            protocol: Protocol (tcp/udp)

        Returns:
            Service detection result
        """
        self.logger.info(f"Detecting service on {host}:{port}/{protocol}")

        result = {
            "host": host,
            "port": port,
            "protocol": protocol,
            "service": None,
            "version": None,
            "banner": None,
        }

        # Common port mappings
        common_ports = {
            21: "ftp",
            22: "ssh",
            23: "telnet",
            25: "smtp",
            53: "dns",
            80: "http",
            110: "pop3",
            143: "imap",
            443: "https",
            445: "smb",
            3306: "mysql",
            5432: "postgresql",
            6379: "redis",
            8080: "http-proxy",
            27017: "mongodb",
        }

        # Initial guess based on port
        result["service"] = common_ports.get(port, "unknown")

        return result

    def analyze_ports(self, host: str, ports: list[int]) -> list[dict[str, Any]]:
        """
        Analyze multiple ports on a host.

        Args:
            host: Target host
            ports: List of ports to analyze

        Returns:
            List of service detection results
        """
        self.logger.info(f"Analyzing {len(ports)} ports on {host}")
        results = []

        for port in ports:
            result = self.detect_service(host, port)
            results.append(result)

        return results


class CMSDetector:
    """
    CMS Detection

    Specialized detector for Content Management Systems.
    Extends TechnologyFingerprinter with CMS-specific checks.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.fingerprinter = TechnologyFingerprinter()

    def detect_cms(self, url: str) -> dict[str, Any]:
        """
        Detect CMS platform.

        Args:
            url: Target URL

        Returns:
            CMS detection result
        """
        self.logger.info(f"Detecting CMS for {url}")

        results = self.fingerprinter.fingerprint(url)
        cms_results = [r for r in results if r.category == "cms"]

        if not cms_results:
            return {
                "detected": False,
                "cms": None,
                "version": None,
                "confidence": 0.0,
            }

        # Return highest confidence CMS
        best_match = max(cms_results, key=lambda x: x.confidence)

        return {
            "detected": True,
            "cms": best_match.technology,
            "version": best_match.version,
            "confidence": best_match.confidence,
            "evidence": best_match.evidence,
        }

    def detect_plugins(self, url: str, cms: str) -> list[str]:
        """
        Detect CMS plugins/extensions.

        Args:
            url: Target URL
            cms: Detected CMS name

        Returns:
            List of detected plugins
        """
        self.logger.info(f"Detecting {cms} plugins for {url}")
        plugins = []

        # Placeholder for plugin detection logic
        # Would include checks for common plugin paths, signatures, etc.

        return plugins
