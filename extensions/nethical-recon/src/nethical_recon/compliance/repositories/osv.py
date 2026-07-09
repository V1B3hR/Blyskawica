"""
OSV (Open Source Vulnerabilities) Connector

Integrates with OSV.dev for open source vulnerability data.
"""

import logging
from typing import Any, Optional

import requests

logger = logging.getLogger(__name__)


class OSVConnector:
    """
    OSV Connector.

    Integrates with OSV.dev for open source vulnerability data.

    Features:
    - Vulnerability lookup by ID
    - Package vulnerability queries
    - Ecosystem-specific searches
    """

    OSV_API_BASE = "https://api.osv.dev/v1"

    def __init__(self):
        """Initialize OSV connector."""
        self.session = requests.Session()

    def get_vulnerability(self, vuln_id: str) -> Optional[dict[str, Any]]:
        """
        Get vulnerability by ID.

        Args:
            vuln_id: Vulnerability ID (e.g., "GHSA-xxxx-xxxx-xxxx")

        Returns:
            Vulnerability data if found
        """
        try:
            logger.info(f"Fetching vulnerability {vuln_id} from OSV")

            url = f"{self.OSV_API_BASE}/vulns/{vuln_id}"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            return self._parse_vulnerability(response.json())

        except Exception as e:
            logger.error(f"Failed to fetch vulnerability from OSV: {e}")
            return None

    def query_package(
        self,
        package_name: str,
        ecosystem: str,
        version: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Query vulnerabilities for a package.

        Args:
            package_name: Package name
            ecosystem: Ecosystem (npm, PyPI, Go, etc.)
            version: Optional package version

        Returns:
            List of vulnerabilities
        """
        try:
            logger.info(f"Querying OSV for {ecosystem}/{package_name}")

            url = f"{self.OSV_API_BASE}/query"
            payload = {
                "package": {
                    "name": package_name,
                    "ecosystem": ecosystem,
                }
            }

            if version:
                payload["version"] = version

            response = self.session.post(url, json=payload, timeout=30)
            response.raise_for_status()

            data = response.json()
            vulns = data.get("vulns", [])

            return [self._parse_vulnerability(v) for v in vulns]

        except Exception as e:
            logger.error(f"Failed to query OSV: {e}")
            return []

    def _parse_vulnerability(self, vuln_data: dict[str, Any]) -> dict[str, Any]:
        """Parse OSV vulnerability data."""
        vuln_id = vuln_data.get("id", "")

        # Extract severity
        severity_data = vuln_data.get("severity", [])
        severity = None
        if severity_data and len(severity_data) > 0:
            severity = severity_data[0].get("score")

        # Extract aliases (CVE IDs)
        aliases = vuln_data.get("aliases", [])

        # Extract affected packages
        affected = vuln_data.get("affected", [])
        packages = []
        for aff in affected:
            package = aff.get("package", {})
            packages.append(
                {
                    "ecosystem": package.get("ecosystem"),
                    "name": package.get("name"),
                }
            )

        return {
            "id": vuln_id,
            "summary": vuln_data.get("summary", ""),
            "details": vuln_data.get("details", ""),
            "severity": severity,
            "aliases": aliases,
            "affected_packages": packages,
            "published": vuln_data.get("published"),
            "modified": vuln_data.get("modified"),
            "source": "OSV",
        }
