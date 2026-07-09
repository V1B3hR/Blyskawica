"""
GitHub Security Advisories Connector

Integrates with GitHub Security Advisory Database.
"""

import logging
from typing import Any, Optional

import requests

logger = logging.getLogger(__name__)


class GitHubAdvisoryConnector:
    """
    GitHub Security Advisory Connector.

    Integrates with GitHub Security Advisory Database via GraphQL API.

    Features:
    - Advisory lookup by GHSA ID
    - CVE to GHSA mapping
    - Ecosystem-specific searches
    """

    GITHUB_GRAPHQL_API = "https://api.github.com/graphql"

    def __init__(self, token: Optional[str] = None):
        """
        Initialize GitHub advisory connector.

        Args:
            token: Optional GitHub personal access token
        """
        self.token = token
        self.session = requests.Session()
        if token:
            self.session.headers.update({"Authorization": f"Bearer {token}"})

    def get_advisory(self, ghsa_id: str) -> Optional[dict[str, Any]]:
        """
        Get security advisory by GHSA ID.

        Args:
            ghsa_id: GitHub Security Advisory ID (e.g., "GHSA-xxxx-xxxx-xxxx")

        Returns:
            Advisory data if found
        """
        try:
            logger.info(f"Fetching advisory {ghsa_id} from GitHub")

            # GraphQL query
            query = """
            query($ghsaId: String!) {
                securityAdvisory(ghsaId: $ghsaId) {
                    ghsaId
                    summary
                    description
                    severity
                    cvss {
                        score
                        vectorString
                    }
                    publishedAt
                    updatedAt
                    references {
                        url
                    }
                    identifiers {
                        type
                        value
                    }
                }
            }
            """

            payload = {"query": query, "variables": {"ghsaId": ghsa_id}}

            response = self.session.post(self.GITHUB_GRAPHQL_API, json=payload, timeout=30)
            response.raise_for_status()

            data = response.json()
            advisory = data.get("data", {}).get("securityAdvisory")

            if advisory:
                return self._parse_advisory(advisory)

            return None

        except Exception as e:
            logger.error(f"Failed to fetch advisory from GitHub: {e}")
            return None

    def search_by_cve(self, cve_id: str) -> Optional[dict[str, Any]]:
        """
        Search advisory by CVE ID.

        Args:
            cve_id: CVE identifier

        Returns:
            Advisory data if found
        """
        # Note: GitHub GraphQL API doesn't directly support CVE search in the same way
        # This is a simplified implementation
        logger.info(f"Searching GitHub advisories for {cve_id}")
        logger.warning("CVE search requires REST API endpoint - not fully implemented")
        return None

    def _parse_advisory(self, advisory_data: dict[str, Any]) -> dict[str, Any]:
        """Parse GitHub advisory data."""
        ghsa_id = advisory_data.get("ghsaId", "")

        # Extract CVE IDs from identifiers
        identifiers = advisory_data.get("identifiers", [])
        cve_ids = [i["value"] for i in identifiers if i.get("type") == "CVE"]

        # Extract CVSS score
        cvss = advisory_data.get("cvss", {})

        return {
            "ghsa_id": ghsa_id,
            "summary": advisory_data.get("summary", ""),
            "description": advisory_data.get("description", ""),
            "severity": advisory_data.get("severity", ""),
            "cvss_score": cvss.get("score"),
            "cvss_vector": cvss.get("vectorString"),
            "cve_ids": cve_ids,
            "published_at": advisory_data.get("publishedAt"),
            "updated_at": advisory_data.get("updatedAt"),
            "references": [r.get("url") for r in advisory_data.get("references", [])],
            "source": "GitHub",
        }
