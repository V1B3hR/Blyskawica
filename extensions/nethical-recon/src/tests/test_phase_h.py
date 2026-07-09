"""Tests for Phase H - AI-Driven Threat Intelligence components."""

import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import pytest

from nethical_recon.ai.deduplication import DeduplicationEngine, FindingMerger
from nethical_recon.ai.llm_client import LLMClient, LLMReport
from nethical_recon.ai.threat_intelligence import ThreatFeed, ThreatIntelligenceManager


class TestDeduplicationEngine:
    """Test finding deduplication engine."""

    def test_exact_duplicates(self):
        """Test detection of exact duplicate findings."""
        engine = DeduplicationEngine()

        finding1 = {
            "id": str(uuid4()),
            "title": "Open SSH Port",
            "severity": "high",
            "confidence": "high",
            "category": "open_port",
            "affected_asset": "192.168.1.1",
            "port": 22,
            "service": "ssh",
        }

        finding2 = finding1.copy()
        finding2["id"] = str(uuid4())

        findings = [finding1, finding2]
        unique, groups = engine.deduplicate_findings(findings)

        assert len(unique) == 1
        assert len(groups) == 1
        assert len(groups[0].duplicate_finding_ids) == 1

    def test_similar_findings(self):
        """Test detection of similar but not identical findings."""
        engine = DeduplicationEngine(fuzzy_match_threshold=0.8)

        finding1 = {
            "id": str(uuid4()),
            "title": "SSH Service Detected",
            "severity": "high",
            "confidence": "high",
            "category": "open_port",
            "affected_asset": "192.168.1.1",
            "port": 22,
            "service": "ssh",
        }

        finding2 = {
            "id": str(uuid4()),
            "title": "Open SSH Port Found",
            "severity": "high",
            "confidence": "medium",
            "category": "open_port",
            "affected_asset": "192.168.1.1",
            "port": 22,
            "service": "ssh",
        }

        findings = [finding1, finding2]
        unique, groups = engine.deduplicate_findings(findings)

        assert len(unique) == 1
        assert len(groups) == 1

    def test_different_findings(self):
        """Test that different findings are not merged."""
        engine = DeduplicationEngine()

        finding1 = {
            "id": str(uuid4()),
            "title": "Open SSH Port",
            "severity": "high",
            "category": "open_port",
            "affected_asset": "192.168.1.1",
            "port": 22,
            "service": "ssh",
        }

        finding2 = {
            "id": str(uuid4()),
            "title": "Open HTTP Port",
            "severity": "low",
            "category": "open_port",
            "affected_asset": "192.168.1.2",
            "port": 80,
            "service": "http",
        }

        findings = [finding1, finding2]
        unique, groups = engine.deduplicate_findings(findings)

        assert len(unique) == 2
        assert len(groups) == 0

    def test_text_similarity_calculation(self):
        """Test text similarity calculation."""
        engine = DeduplicationEngine()

        # Identical text
        assert engine._calculate_text_similarity("test", "test") == 1.0

        # Completely different
        assert engine._calculate_text_similarity("foo", "bar") == 0.0

        # Partial overlap
        sim = engine._calculate_text_similarity("open ssh port", "ssh port open")
        assert 0.5 < sim <= 1.0


class TestFindingMerger:
    """Test finding merger."""

    def test_merge_evidence_ids(self):
        """Test merging of evidence IDs."""
        merger = FindingMerger()

        primary = {"id": str(uuid4()), "title": "Test Finding", "evidence_ids": [str(uuid4()), str(uuid4())]}

        duplicate = {"id": str(uuid4()), "title": "Test Finding", "evidence_ids": [str(uuid4())]}

        merged = merger.merge_findings(primary, [duplicate])

        assert len(merged["evidence_ids"]) == 3
        assert all(eid in merged["evidence_ids"] for eid in primary["evidence_ids"])

    def test_merge_severity_highest(self):
        """Test that highest severity is kept."""
        merger = FindingMerger()

        primary = {"id": str(uuid4()), "title": "Test", "severity": "medium"}

        dup1 = {"id": str(uuid4()), "title": "Test", "severity": "high"}
        dup2 = {"id": str(uuid4()), "title": "Test", "severity": "low"}

        merged = merger.merge_findings(primary, [dup1, dup2])

        assert merged["severity"] == "high"

    def test_merge_confidence_highest(self):
        """Test that highest confidence is kept."""
        merger = FindingMerger()

        primary = {"id": str(uuid4()), "title": "Test", "confidence": "medium"}

        dup1 = {"id": str(uuid4()), "title": "Test", "confidence": "confirmed"}
        dup2 = {"id": str(uuid4()), "title": "Test", "confidence": "low"}

        merged = merger.merge_findings(primary, [dup1, dup2])

        assert merged["confidence"] == "confirmed"


class TestLLMClient:
    """Test LLM client."""

    def test_initialization_without_key(self):
        """Test initialization without API key."""
        client = LLMClient(api_key=None)
        assert not client.is_available()

    def test_fallback_report_generation(self):
        """Test fallback report generation when LLM unavailable."""
        client = LLMClient(api_key=None)

        findings = [
            {
                "id": str(uuid4()),
                "title": "Critical Vulnerability",
                "severity": "critical",
                "description": "Test vulnerability",
                "evidence_ids": [str(uuid4())],
            }
        ]

        evidence = [{"id": str(uuid4()), "type": "tool_output", "content": "Test evidence content"}]

        report = client._generate_fallback_report(findings, evidence)

        assert isinstance(report, LLMReport)
        assert "1 findings" in report.summary
        assert "critical" in report.summary.lower()
        assert len(report.evidence_references) > 0

    def test_evidence_prompt_building(self):
        """Test building evidence-based prompt."""
        client = LLMClient(api_key="fake-key")

        findings = [
            {
                "id": str(uuid4()),
                "title": "Test Finding",
                "severity": "high",
                "confidence": "high",
                "description": "Test description",
                "affected_asset": "192.168.1.1",
                "evidence_ids": [],
            }
        ]

        evidence = [{"id": str(uuid4()), "type": "tool_output", "tool_name": "nmap", "content": "Port scan results"}]

        context = {"target": "example.com", "scan_type": "full"}

        prompt = client._build_evidence_prompt(findings, evidence, context)

        assert "Test Finding" in prompt
        assert "192.168.1.1" in prompt
        assert "nmap" in prompt
        assert "example.com" in prompt


class TestThreatIntelligenceManager:
    """Test threat intelligence manager."""

    def test_feed_registration(self):
        """Test threat feed registration."""
        manager = ThreatIntelligenceManager()

        feed = ThreatFeed(name="test-feed", source="https://test.com/feed", feed_type="custom")

        manager.register_feed(feed)

        assert "test-feed" in manager.feeds
        assert manager.feeds["test-feed"].source == "https://test.com/feed"

    def test_stix_export(self):
        """Test STIX 2.1 export."""
        manager = ThreatIntelligenceManager()

        findings = [
            {
                "id": str(uuid4()),
                "title": "Open SSH Port",
                "severity": "high",
                "confidence": "high",
                "description": "SSH service detected",
                "affected_asset": "192.168.1.1",
                "port": 22,
                "category": "open_port",
                "discovered_at": datetime.utcnow().isoformat() + "Z",
                "tags": ["ssh", "network"],
            }
        ]

        stix_bundle = manager.export_to_stix(findings)

        assert stix_bundle["type"] == "bundle"
        assert len(stix_bundle["objects"]) >= 2  # identity + indicator

        # Find the indicator
        indicator = None
        for obj in stix_bundle["objects"]:
            if obj["type"] == "indicator":
                indicator = obj
                break

        assert indicator is not None
        assert indicator["spec_version"] == "2.1"
        assert "Open SSH Port" in indicator["name"]
        assert "severity:high" in indicator["labels"]

    def test_json_export(self):
        """Test JSON export."""
        manager = ThreatIntelligenceManager()

        findings = [{"id": str(uuid4()), "title": "Test Finding", "severity": "medium"}]

        json_output = manager.export_to_json(findings)

        data = json.loads(json_output)
        assert "metadata" in data
        assert "findings" in data
        assert data["metadata"]["finding_count"] == 1

    def test_markdown_export(self):
        """Test Markdown export."""
        manager = ThreatIntelligenceManager()

        findings = [
            {
                "id": str(uuid4()),
                "title": "Critical Vulnerability",
                "severity": "critical",
                "confidence": "high",
                "description": "Test vulnerability description",
                "affected_asset": "example.com",
                "category": "vulnerability",
                "evidence_ids": [str(uuid4())],
            },
            {
                "id": str(uuid4()),
                "title": "Info Finding",
                "severity": "info",
                "confidence": "medium",
                "description": "Informational finding",
                "category": "info",
            },
        ]

        context = {"target": "example.com", "scan_date": "2025-12-27"}

        markdown = manager.export_to_markdown(findings, context)

        assert "# Threat Intelligence Report" in markdown
        assert "Critical Vulnerability" in markdown
        assert "example.com" in markdown
        assert "## Summary" in markdown
        assert "### CRITICAL Severity" in markdown

    def test_stix_pattern_building(self):
        """Test STIX pattern building."""
        manager = ThreatIntelligenceManager()

        # Test with IP and port
        finding = {"affected_asset": "192.168.1.1", "port": 22, "service": "ssh"}

        pattern = manager._build_stix_pattern(finding)

        assert "192.168.1.1" in pattern
        assert "22" in pattern
        assert "ssh" in pattern


class TestPhaseHIntegration:
    """Integration tests for Phase H components."""

    def test_end_to_end_workflow(self):
        """Test complete workflow: findings -> dedup -> LLM report -> STIX export."""
        # Create test findings with duplicates
        findings = [
            {
                "id": str(uuid4()),
                "title": "Open SSH Port",
                "severity": "high",
                "confidence": "high",
                "category": "open_port",
                "affected_asset": "192.168.1.1",
                "port": 22,
                "service": "ssh",
                "description": "SSH service detected",
                "evidence_ids": [str(uuid4())],
                "tags": ["ssh"],
                "discovered_at": datetime.utcnow().isoformat() + "Z",
            },
            {
                "id": str(uuid4()),
                "title": "SSH Service Found",
                "severity": "high",
                "confidence": "medium",
                "category": "open_port",
                "affected_asset": "192.168.1.1",
                "port": 22,
                "service": "ssh",
                "description": "SSH service detected",
                "evidence_ids": [str(uuid4())],
                "tags": ["ssh"],
                "discovered_at": datetime.utcnow().isoformat() + "Z",
            },
        ]

        # Step 1: Deduplicate
        dedup = DeduplicationEngine()
        unique_findings, dup_groups = dedup.deduplicate_findings(findings)

        assert len(unique_findings) == 1
        assert len(dup_groups) == 1

        # Step 2: Generate LLM report (fallback)
        llm_client = LLMClient(api_key=None)
        evidence = [
            {
                "id": findings[0]["evidence_ids"][0],
                "type": "tool_output",
                "tool_name": "nmap",
                "content": "Port 22/tcp open ssh",
            }
        ]

        report = llm_client._generate_fallback_report(unique_findings, evidence)

        assert isinstance(report, LLMReport)
        assert len(report.evidence_references) > 0

        # Step 3: Export to STIX
        threat_intel = ThreatIntelligenceManager()
        stix_bundle = threat_intel.export_to_stix(unique_findings)

        assert stix_bundle["type"] == "bundle"
        assert len(stix_bundle["objects"]) >= 2
