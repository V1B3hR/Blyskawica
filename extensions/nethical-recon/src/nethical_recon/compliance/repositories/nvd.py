"""
NVD (National Vulnerability Database) Connector

Integrates with NIST NVD for vulnerability data.
"""

import logging
from typing import Any, Optional

import requests

logger = logging.getLogger(__name__)


class NVDConnector:
    """
    NVD Connector.

    Integrates with NIST National Vulnerability Database for CVE data.

    Features:
    - CVE lookup by ID
    - Vulnerability search
    - CVSS score retrieval
    - CPE matching
    """

    NVD_API_BASE = "https://services.nvd.nist.gov/rest/json/cves/2.0"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize NVD connector.

        Args:
            api_key: Optional NVD API key for higher rate limits
        """
        self.api_key = api_key
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"apiKey": api_key})

    def get_cve(self, cve_id: str) -> Optional[dict[str, Any]]:
        """
        Get CVE details from NVD.

        Args:
            cve_id: CVE identifier (e.g., "CVE-2021-44228")

        Returns:
            CVE data if found
        """
        try:
            logger.info(f"Fetching CVE {cve_id} from NVD")

            url = f"{self.NVD_API_BASE}?cveId={cve_id}"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            data = response.json()

            if "vulnerabilities" in data and len(data["vulnerabilities"]) > 0:
                vuln = data["vulnerabilities"][0]["cve"]
                return self._parse_cve_data(vuln)

            return None

        except Exception as e:
            logger.error(f"Failed to fetch CVE from NVD: {e}")
            return None

    def _parse_cve_data(self, cve_data: dict[str, Any]) -> dict[str, Any]:
        """Parse NVD CVE data into simplified format."""
        cve_id = cve_data.get("id", "")

        # Extract CVSS scores
        metrics = cve_data.get("metrics", {})
        cvss_v3 = None
        if "cvssMetricV31" in metrics and len(metrics["cvssMetricV31"]) > 0:
            cvss_v3 = metrics["cvssMetricV31"][0]["cvssData"]
        elif "cvssMetricV30" in metrics and len(metrics["cvssMetricV30"]) > 0:
            cvss_v3 = metrics["cvssMetricV30"][0]["cvssData"]

        # Extract description
        descriptions = cve_data.get("descriptions", [])
        description = ""
        for desc in descriptions:
            if desc.get("lang") == "en":
                description = desc.get("value", "")
                break

        return {
            "cve_id": cve_id,
            "description": description,
            "cvss_score": cvss_v3.get("baseScore") if cvss_v3 else None,
            "cvss_severity": cvss_v3.get("baseSeverity") if cvss_v3 else None,
            "published_date": cve_data.get("published"),
            "last_modified": cve_data.get("lastModified"),
            "source": "NVD",
        }

    def search_cves(
        self,
        keyword: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Search CVEs in NVD.

        Args:
            keyword: Search keyword
            severity: Filter by severity (LOW, MEDIUM, HIGH, CRITICAL)
            limit: Maximum results to return

        Returns:
            List of CVE data
        """
        try:
            logger.info(f"Searching NVD with keyword: {keyword}, severity: {severity}")

            params = {"resultsPerPage": min(limit, 100)}

            if keyword:
                params["keywordSearch"] = keyword
            if severity:
                params["cvssV3Severity"] = severity

            response = self.session.get(self.NVD_API_BASE, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            vulnerabilities = data.get("vulnerabilities", [])

            return [self._parse_cve_data(v["cve"]) for v in vulnerabilities[:limit]]

        except Exception as e:
            logger.error(f"Failed to search NVD: {e}")
            return []
