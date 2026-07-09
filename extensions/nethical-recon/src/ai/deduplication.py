"""
Finding Deduplication Engine

Identifies and merges duplicate findings from multiple tools/scans
to reduce noise and improve signal quality.
"""

import logging
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class DuplicateGroup(BaseModel):
    """Group of duplicate findings."""

    primary_finding_id: UUID = Field(..., description="Primary (kept) finding ID")
    duplicate_finding_ids: list[UUID] = Field(default_factory=list, description="Duplicate finding IDs")
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Average similarity score")
    merge_reason: str = Field(..., description="Why these were merged")


class DeduplicationEngine:
    """
    Finding Deduplication Engine

    Uses multiple strategies to identify duplicate findings:
    - Exact match (same asset, port, service, category)
    - Fuzzy match (similar titles/descriptions)
    - Temporal proximity (same finding reported multiple times)
    """

    def __init__(
        self, exact_match_threshold: float = 1.0, fuzzy_match_threshold: float = 0.85, time_window_seconds: int = 3600
    ):
        """
        Initialize deduplication engine.

        Args:
            exact_match_threshold: Score for exact matches (1.0)
            fuzzy_match_threshold: Minimum score for fuzzy matches (0-1)
            time_window_seconds: Time window for temporal deduplication
        """
        self.logger = logging.getLogger(__name__)
        self.exact_match_threshold = exact_match_threshold
        self.fuzzy_match_threshold = fuzzy_match_threshold
        self.time_window_seconds = time_window_seconds

    def deduplicate_findings(self, findings: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[DuplicateGroup]]:
        """
        Deduplicate findings and return unique findings + duplicate groups.

        Args:
            findings: List of finding dictionaries

        Returns:
            Tuple of (unique_findings, duplicate_groups)
        """
        if not findings:
            return [], []

        self.logger.info(f"Deduplicating {len(findings)} findings")

        # Track which findings have been processed
        processed = set()
        unique_findings = []
        duplicate_groups = []

        for i, finding1 in enumerate(findings):
            if i in processed:
                continue

            # This finding is primary
            duplicates = []

            # Compare with remaining findings
            for j, finding2 in enumerate(findings[i + 1 :], start=i + 1):
                if j in processed:
                    continue

                similarity = self._calculate_similarity(finding1, finding2)

                if similarity >= self.fuzzy_match_threshold:
                    duplicates.append((j, finding2, similarity))
                    processed.add(j)

            # Add primary finding to unique list
            unique_findings.append(finding1)

            # Create duplicate group if we found duplicates
            if duplicates:
                group = DuplicateGroup(
                    primary_finding_id=UUID(str(finding1["id"])),
                    duplicate_finding_ids=[UUID(str(dup[1]["id"])) for dup in duplicates],
                    similarity_score=sum(dup[2] for dup in duplicates) / len(duplicates),
                    merge_reason=self._determine_merge_reason(finding1, [d[1] for d in duplicates]),
                )
                duplicate_groups.append(group)

        self.logger.info(
            f"Deduplication complete: {len(unique_findings)} unique, "
            f"{sum(len(g.duplicate_finding_ids) for g in duplicate_groups)} duplicates removed"
        )

        return unique_findings, duplicate_groups

    def _calculate_similarity(self, finding1: dict[str, Any], finding2: dict[str, Any]) -> float:
        """Calculate similarity score between two findings."""
        score = 0.0
        weights = {"asset": 0.25, "port": 0.15, "service": 0.15, "category": 0.20, "severity": 0.10, "title": 0.15}

        # Exact asset match
        if finding1.get("affected_asset") == finding2.get("affected_asset"):
            score += weights["asset"]

        # Exact port match
        if finding1.get("port") and finding1.get("port") == finding2.get("port"):
            score += weights["port"]

        # Exact service match
        if finding1.get("service") and finding1.get("service") == finding2.get("service"):
            score += weights["service"]

        # Exact category match
        if finding1.get("category") == finding2.get("category"):
            score += weights["category"]

        # Exact severity match
        if finding1.get("severity") == finding2.get("severity"):
            score += weights["severity"]

        # Title similarity (simple word overlap)
        title_sim = self._calculate_text_similarity(finding1.get("title", ""), finding2.get("title", ""))
        score += weights["title"] * title_sim

        return min(1.0, score)

    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity based on word overlap."""
        if not text1 or not text2:
            return 0.0

        # Normalize to lowercase and split into words
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        # Jaccard similarity
        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0

    def _determine_merge_reason(self, primary: dict[str, Any], duplicates: list[dict[str, Any]]) -> str:
        """Determine why findings were merged."""
        # Check what they have in common
        reasons = []

        if all(d.get("affected_asset") == primary.get("affected_asset") for d in duplicates):
            reasons.append("same asset")

        if all(d.get("port") == primary.get("port") for d in duplicates if d.get("port")):
            reasons.append("same port")

        if all(d.get("category") == primary.get("category") for d in duplicates):
            reasons.append("same category")

        if all(d.get("service") == primary.get("service") for d in duplicates if d.get("service")):
            reasons.append("same service")

        if len(reasons) == 0:
            return "high similarity score"

        return ", ".join(reasons)


class FindingMerger:
    """Merge duplicate findings into a single consolidated finding."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def merge_findings(self, primary: dict[str, Any], duplicates: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Merge duplicate findings into primary finding.

        Args:
            primary: Primary finding to keep
            duplicates: Duplicate findings to merge

        Returns:
            Merged finding with consolidated data
        """
        merged = primary.copy()

        # Collect all evidence IDs
        all_evidence_ids = set(merged.get("evidence_ids", []))
        for dup in duplicates:
            all_evidence_ids.update(dup.get("evidence_ids", []))
        merged["evidence_ids"] = list(all_evidence_ids)

        # Collect all references
        all_refs = set(merged.get("references", []))
        for dup in duplicates:
            all_refs.update(dup.get("references", []))
        merged["references"] = list(all_refs)

        # Collect all tags
        all_tags = set(merged.get("tags", []))
        for dup in duplicates:
            all_tags.update(dup.get("tags", []))
        merged["tags"] = list(all_tags)

        # Collect all CVEs
        all_cves = set(merged.get("cve_ids", []))
        for dup in duplicates:
            all_cves.update(dup.get("cve_ids", []))
        merged["cve_ids"] = list(all_cves)

        # Collect all CWEs
        all_cwes = set(merged.get("cwe_ids", []))
        for dup in duplicates:
            all_cwes.update(dup.get("cwe_ids", []))
        merged["cwe_ids"] = list(all_cwes)

        # Take highest severity
        severity_order = ["info", "low", "medium", "high", "critical"]
        all_severities = [primary.get("severity", "info")]
        all_severities.extend(d.get("severity", "info") for d in duplicates)

        max_sev_idx = max(severity_order.index(s) if s in severity_order else 0 for s in all_severities)
        merged["severity"] = severity_order[max_sev_idx]

        # Take highest confidence
        confidence_order = ["tentative", "low", "medium", "high", "confirmed"]
        all_confidences = [primary.get("confidence", "medium")]
        all_confidences.extend(d.get("confidence", "medium") for d in duplicates)

        max_conf_idx = max(confidence_order.index(c) if c in confidence_order else 0 for c in all_confidences)
        merged["confidence"] = confidence_order[max_conf_idx]

        # Add metadata about merge
        merged["merged_from"] = [str(d["id"]) for d in duplicates]
        merged["merge_count"] = len(duplicates)

        return merged
