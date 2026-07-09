"""
LLM Client for Evidence-Based Threat Intelligence

Provides integration with LLMs (OpenAI, etc.) with strict guardrails
to ensure all reports are evidence-based and traceable.
"""

import logging
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

try:
    from openai import OpenAI

    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from nethical_recon.secrets import get_secrets_manager


class EvidenceReference(BaseModel):
    """Reference to evidence supporting an LLM claim."""

    evidence_id: UUID = Field(..., description="Evidence ID")
    finding_id: UUID | None = Field(None, description="Related finding ID")
    excerpt: str = Field(..., description="Relevant excerpt from evidence")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="How relevant this evidence is")


class LLMReport(BaseModel):
    """Structured LLM-generated report with evidence tracking."""

    summary: str = Field(..., description="Executive summary")
    key_findings: list[str] = Field(default_factory=list, description="Key findings list")
    risk_assessment: str = Field(..., description="Risk assessment")
    recommendations: list[str] = Field(default_factory=list, description="Recommended actions")
    evidence_references: list[EvidenceReference] = Field(
        default_factory=list, description="Evidence supporting this report"
    )
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Overall confidence")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class LLMClient:
    """
    LLM Client with Evidence-Based Guardrails

    Ensures all LLM outputs are:
    - Evidence-based (no hallucinations)
    - Traceable (every claim references evidence)
    - Validated (automated checks for consistency)
    """

    def __init__(self, api_key: str | None = None, model: str = "gpt-4o-mini"):
        """
        Initialize LLM client.

        Args:
            api_key: OpenAI API key (if None, loads from secrets manager)
            model: Model name to use
        """
        self.logger = logging.getLogger(__name__)

        if not OPENAI_AVAILABLE:
            self.logger.warning("OpenAI library not available - LLM features disabled")
            self.client = None
            return

        # Load API key from secrets manager if not provided
        if api_key is None:
            secrets = get_secrets_manager()
            api_key = secrets.get("OPENAI_API_KEY")

        if not api_key:
            self.logger.warning("No OpenAI API key found - LLM features disabled")
            self.client = None
        else:
            self.client = OpenAI(api_key=api_key)

        self.model = model

    def is_available(self) -> bool:
        """Check if LLM client is available."""
        return self.client is not None

    def generate_threat_report(
        self, findings: list[dict[str, Any]], evidence: list[dict[str, Any]], context: dict[str, Any] | None = None
    ) -> LLMReport:
        """
        Generate evidence-based threat intelligence report.

        Args:
            findings: List of normalized findings
            evidence: List of evidence records
            context: Additional context (target info, scan config, etc.)

        Returns:
            Structured LLM report with evidence references

        Raises:
            ValueError: If LLM client not available
        """
        if not self.is_available():
            raise ValueError("LLM client not available - check API key configuration")

        # Build evidence-based prompt
        prompt = self._build_evidence_prompt(findings, evidence, context)

        # Call LLM with structured output
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,  # Lower temperature for more consistent output
                max_tokens=2000,
            )

            # Parse response
            content = response.choices[0].message.content
            report = self._parse_llm_response(content, findings, evidence)

            # Validate report has evidence references
            if not report.evidence_references:
                self.logger.warning("LLM report generated without evidence references")

            return report

        except Exception as e:
            self.logger.error(f"Error generating LLM report: {e}")
            # Return fallback report based purely on evidence
            return self._generate_fallback_report(findings, evidence)

    def _get_system_prompt(self) -> str:
        """Get system prompt with guardrails."""
        return """You are a cybersecurity threat intelligence analyst. 

CRITICAL RULES:
1. Base ALL findings ONLY on the provided evidence - never speculate or hallucinate
2. Reference specific evidence IDs for every claim you make
3. If evidence is insufficient, explicitly state that
4. Use precise technical language based on evidence
5. Never mention threats or vulnerabilities not present in the evidence
6. Rate your confidence based on evidence quality and quantity

Your analysis must be traceable - another analyst should be able to verify every claim
by checking the referenced evidence IDs."""

    def _build_evidence_prompt(
        self, findings: list[dict[str, Any]], evidence: list[dict[str, Any]], context: dict[str, Any] | None
    ) -> str:
        """Build prompt from findings and evidence."""
        prompt_parts = ["# Security Assessment\n"]

        # Add context if provided
        if context:
            prompt_parts.append("## Context")
            for key, value in context.items():
                prompt_parts.append(f"- {key}: {value}")
            prompt_parts.append("")

        # Add findings
        prompt_parts.append("## Findings")
        for i, finding in enumerate(findings, 1):
            prompt_parts.append(f"\n### Finding {i}")
            prompt_parts.append(f"- ID: {finding.get('id')}")
            prompt_parts.append(f"- Title: {finding.get('title')}")
            prompt_parts.append(f"- Severity: {finding.get('severity')}")
            prompt_parts.append(f"- Confidence: {finding.get('confidence')}")
            prompt_parts.append(f"- Description: {finding.get('description')}")
            if finding.get("affected_asset"):
                prompt_parts.append(f"- Affected: {finding.get('affected_asset')}")
            if finding.get("evidence_ids"):
                prompt_parts.append(f"- Evidence IDs: {finding.get('evidence_ids')}")

        # Add evidence excerpts
        prompt_parts.append("\n## Evidence")
        for i, ev in enumerate(evidence, 1):
            prompt_parts.append(f"\n### Evidence {i}")
            prompt_parts.append(f"- ID: {ev.get('id')}")
            prompt_parts.append(f"- Type: {ev.get('type')}")
            prompt_parts.append(f"- Tool: {ev.get('tool_name')}")
            # Truncate content if too long
            content = str(ev.get("content", ""))
            if len(content) > 500:
                content = content[:500] + "..."
            prompt_parts.append(f"- Content: {content}")

        prompt_parts.append("\n## Task")
        prompt_parts.append("""Generate a structured threat intelligence report including:
1. Executive Summary (2-3 sentences)
2. Key Findings (bullet points, each referencing evidence IDs)
3. Risk Assessment (based on severity and confidence)
4. Recommendations (actionable, prioritized)
5. Confidence Score (0.0-1.0)

Format your response as:
SUMMARY: <text>
KEY_FINDINGS:
- <finding with [Evidence ID: ...]>
RISK: <assessment>
RECOMMENDATIONS:
- <recommendation>
CONFIDENCE: <score>""")

        return "\n".join(prompt_parts)

    def _parse_llm_response(
        self, content: str, findings: list[dict[str, Any]], evidence: list[dict[str, Any]]
    ) -> LLMReport:
        """Parse LLM response into structured report."""
        lines = content.split("\n")

        summary = ""
        key_findings = []
        risk_assessment = ""
        recommendations = []
        confidence_score = 0.5

        current_section = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith("SUMMARY:"):
                current_section = "summary"
                summary = line.replace("SUMMARY:", "").strip()
            elif line.startswith("KEY_FINDINGS:"):
                current_section = "findings"
            elif line.startswith("RISK:"):
                current_section = "risk"
                risk_assessment = line.replace("RISK:", "").strip()
            elif line.startswith("RECOMMENDATIONS:"):
                current_section = "recommendations"
            elif line.startswith("CONFIDENCE:"):
                try:
                    confidence_score = float(line.replace("CONFIDENCE:", "").strip())
                except ValueError:
                    confidence_score = 0.5
            elif line.startswith("-"):
                item = line[1:].strip()
                if current_section == "findings":
                    key_findings.append(item)
                elif current_section == "recommendations":
                    recommendations.append(item)
            else:
                # Continuation of previous section
                if current_section == "summary" and not summary:
                    summary = line
                elif current_section == "risk" and not risk_assessment:
                    risk_assessment = line

        # Extract evidence references from key findings
        evidence_refs = self._extract_evidence_references(key_findings, findings, evidence)

        return LLMReport(
            summary=summary or "Security assessment completed",
            key_findings=key_findings,
            risk_assessment=risk_assessment or "Risk assessment pending",
            recommendations=recommendations,
            evidence_references=evidence_refs,
            confidence_score=confidence_score,
            metadata={"model": self.model, "finding_count": len(findings), "evidence_count": len(evidence)},
        )

    def _extract_evidence_references(
        self, key_findings: list[str], findings: list[dict[str, Any]], evidence: list[dict[str, Any]]
    ) -> list[EvidenceReference]:
        """Extract evidence references from findings text."""
        refs = []

        # Map evidence IDs mentioned in findings
        for ev in evidence:
            ev_id = ev.get("id")
            if not ev_id:
                continue

            # Check if this evidence is mentioned in any finding
            mentioned = False
            for finding_text in key_findings:
                if str(ev_id) in finding_text:
                    mentioned = True
                    break

            if mentioned:
                content = str(ev.get("content", ""))
                excerpt = content[:200] + "..." if len(content) > 200 else content

                refs.append(
                    EvidenceReference(
                        evidence_id=UUID(str(ev_id)) if isinstance(ev_id, str) else ev_id,
                        excerpt=excerpt,
                        relevance_score=0.8,  # High relevance if explicitly mentioned
                    )
                )

        return refs

    def _generate_fallback_report(self, findings: list[dict[str, Any]], evidence: list[dict[str, Any]]) -> LLMReport:
        """Generate rule-based report when LLM fails."""
        # Count by severity
        severity_counts = {}
        for finding in findings:
            sev = finding.get("severity", "info")
            severity_counts[sev] = severity_counts.get(sev, 0) + 1

        # Build summary
        total = len(findings)
        critical = severity_counts.get("critical", 0)
        high = severity_counts.get("high", 0)

        summary = f"Scan identified {total} findings: {critical} critical, {high} high severity."

        # Extract key findings
        key_findings = []
        for finding in findings[:5]:  # Top 5
            key_findings.append(
                f"{finding.get('title')} - {finding.get('severity')} [Evidence: {finding.get('evidence_ids', [])}]"
            )

        # Risk assessment
        if critical > 0:
            risk = "CRITICAL - Immediate action required"
        elif high > 0:
            risk = "HIGH - Remediation recommended within 24 hours"
        elif severity_counts.get("medium", 0) > 0:
            risk = "MEDIUM - Schedule remediation"
        else:
            risk = "LOW - Monitor for changes"

        # Recommendations
        recommendations = [
            "Review all critical and high severity findings",
            "Prioritize remediation based on asset criticality",
            "Implement monitoring for detected vulnerabilities",
        ]

        # Evidence references
        evidence_refs = []
        for ev in evidence[:10]:  # Top 10
            if ev.get("id"):
                content = str(ev.get("content", ""))
                excerpt = content[:200] + "..." if len(content) > 200 else content
                evidence_refs.append(
                    EvidenceReference(
                        evidence_id=UUID(str(ev["id"])) if isinstance(ev["id"], str) else ev["id"],
                        excerpt=excerpt,
                        relevance_score=0.6,
                    )
                )

        return LLMReport(
            summary=summary,
            key_findings=key_findings,
            risk_assessment=risk,
            recommendations=recommendations,
            evidence_references=evidence_refs,
            confidence_score=0.7,
            metadata={"generator": "fallback", "finding_count": total},
        )
