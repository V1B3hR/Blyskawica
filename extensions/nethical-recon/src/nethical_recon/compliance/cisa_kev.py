"""
CISA Known Exploited Vulnerabilities (KEV) Catalog Integration

Fetches and caches the CISA KEV catalog for vulnerability enrichment and scoring.
KEV vulnerabilities receive increased risk scores and trigger high-priority alerts.
"""

import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Optional

import requests

logger = logging.getLogger(__name__)


@dataclass
class KEVEntry:
    """CISA KEV catalog entry."""

    cve_id: str
    vendor_project: str
    product: str
    vulnerability_name: str
    date_added: str
    short_description: str
    required_action: str
    due_date: Optional[str] = None
    known_ransomware_campaign_use: str = "Unknown"
    notes: str = ""


class CISAKEVClient:
    """
    CISA Known Exploited Vulnerabilities (KEV) Client.

    Fetches and caches the official CISA KEV catalog.
    Updates cache every 24 hours automatically.

    Features:
    - Automatic caching (24-hour refresh)
    - CVE lookup by ID
    - Bulk KEV checking
    - Metadata extraction
    """

    KEV_API_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
    CACHE_DURATION = timedelta(hours=24)

    def __init__(self, cache_file: Optional[str] = None):
        """
        Initialize CISA KEV client.

        Args:
            cache_file: Optional path to cache file (default: in-memory cache)
        """
        self.cache_file = cache_file
        self._cache: dict[str, KEVEntry] = {}
        self._last_update: Optional[datetime] = None
        self._catalog_version: Optional[str] = None
        self._catalog_date: Optional[str] = None

    def update_cache(self, force: bool = False) -> bool:
        """
        Update KEV catalog cache.

        Args:
            force: Force update even if cache is fresh

        Returns:
            True if update was successful
        """
        if not force and self._is_cache_fresh():
            logger.debug("KEV cache is fresh, skipping update")
            return True

        try:
            logger.info("Fetching CISA KEV catalog from API")
            start_time = time.time()

            response = requests.get(self.KEV_API_URL, timeout=30)
            response.raise_for_status()

            data = response.json()

            # Update metadata
            self._catalog_version = data.get("catalogVersion")
            self._catalog_date = data.get("dateReleased")

            # Parse KEV entries
            new_cache = {}
            for vuln in data.get("vulnerabilities", []):
                entry = KEVEntry(
                    cve_id=vuln.get("cveID", ""),
                    vendor_project=vuln.get("vendorProject", ""),
                    product=vuln.get("product", ""),
                    vulnerability_name=vuln.get("vulnerabilityName", ""),
                    date_added=vuln.get("dateAdded", ""),
                    short_description=vuln.get("shortDescription", ""),
                    required_action=vuln.get("requiredAction", ""),
                    due_date=vuln.get("dueDate"),
                    known_ransomware_campaign_use=vuln.get("knownRansomwareCampaignUse", "Unknown"),
                    notes=vuln.get("notes", ""),
                )
                new_cache[entry.cve_id] = entry

            self._cache = new_cache
            self._last_update = datetime.utcnow()

            elapsed = time.time() - start_time
            logger.info(
                f"KEV catalog updated successfully. " f"Loaded {len(self._cache)} vulnerabilities in {elapsed:.2f}s"
            )

            return True

        except Exception as e:
            logger.error(f"Failed to update KEV catalog: {e}")
            return False

    def is_kev(self, cve_id: str) -> bool:
        """
        Check if CVE is in KEV catalog.

        Args:
            cve_id: CVE identifier (e.g., "CVE-2021-44228")

        Returns:
            True if CVE is in KEV catalog
        """
        if not self._cache:
            self.update_cache()

        return cve_id in self._cache

    def get_kev_entry(self, cve_id: str) -> Optional[KEVEntry]:
        """
        Get KEV entry for CVE.

        Args:
            cve_id: CVE identifier

        Returns:
            KEV entry if found, None otherwise
        """
        if not self._cache:
            self.update_cache()

        return self._cache.get(cve_id)

    def get_kev_metadata(self, cve_id: str) -> Optional[dict[str, Any]]:
        """
        Get KEV metadata for CVE.

        Args:
            cve_id: CVE identifier

        Returns:
            Dictionary with KEV metadata, None if not in catalog
        """
        entry = self.get_kev_entry(cve_id)
        if not entry:
            return None

        return {
            "is_kev": True,
            "vendor_project": entry.vendor_project,
            "product": entry.product,
            "vulnerability_name": entry.vulnerability_name,
            "date_added": entry.date_added,
            "required_action": entry.required_action,
            "due_date": entry.due_date,
            "known_ransomware_use": entry.known_ransomware_campaign_use,
            "short_description": entry.short_description,
            "notes": entry.notes,
        }

    def check_multiple_cves(self, cve_ids: list[str]) -> dict[str, bool]:
        """
        Check multiple CVEs against KEV catalog.

        Args:
            cve_ids: List of CVE identifiers

        Returns:
            Dictionary mapping CVE ID to KEV status
        """
        if not self._cache:
            self.update_cache()

        return {cve_id: self.is_kev(cve_id) for cve_id in cve_ids}

    def get_all_kev_entries(self) -> list[KEVEntry]:
        """
        Get all KEV entries.

        Returns:
            List of all KEV entries in catalog
        """
        if not self._cache:
            self.update_cache()

        return list(self._cache.values())

    def get_statistics(self) -> dict[str, Any]:
        """
        Get KEV catalog statistics.

        Returns:
            Statistics about KEV catalog
        """
        if not self._cache:
            self.update_cache()

        return {
            "total_vulnerabilities": len(self._cache),
            "catalog_version": self._catalog_version,
            "catalog_date": self._catalog_date,
            "last_update": self._last_update.isoformat() if self._last_update else None,
            "cache_age_hours": self._get_cache_age_hours(),
        }

    def _is_cache_fresh(self) -> bool:
        """Check if cache is still fresh."""
        if not self._last_update:
            return False

        age = datetime.utcnow() - self._last_update
        return age < self.CACHE_DURATION

    def _get_cache_age_hours(self) -> Optional[float]:
        """Get cache age in hours."""
        if not self._last_update:
            return None

        age = datetime.utcnow() - self._last_update
        return age.total_seconds() / 3600
