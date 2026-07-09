"""
Compliance Mapping
Maps findings to compliance frameworks (OWASP, NIST, ISO 27001)
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any
from uuid import UUID


class ComplianceFramework(Enum):
    """Supported compliance frameworks"""

    OWASP_TOP_10 = "owasp_top_10"
    NIST_CSF = "nist_csf"
    ISO_27001 = "iso_27001"
    PCI_DSS = "pci_dss"
    GDPR = "gdpr"
    HIPAA = "hipaa"


@dataclass
class ComplianceControl:
    """Compliance control/requirement"""

    control_id: str
    framework: ComplianceFramework
    title: str
    description: str
    category: str


@dataclass
class ComplianceMapping:
    """Mapping between finding and compliance controls"""

    finding_id: UUID
    controls: list[ComplianceControl]
    compliance_score: float
    gaps: list[str]


class ComplianceMapper:
    """
    Maps security findings to compliance frameworks

    Features:
    - Multi-framework support
    - Gap analysis
    - Compliance scoring
    - Audit trail
    """

    def __init__(self):
        """Initialize compliance mapper"""
        self._controls = self._load_controls()

    def _load_controls(self) -> dict[ComplianceFramework, list[ComplianceControl]]:
        """Load compliance controls for all frameworks"""
        controls = {
            ComplianceFramework.OWASP_TOP_10: [
                ComplianceControl(
                    control_id="A01:2021",
                    framework=ComplianceFramework.OWASP_TOP_10,
                    title="Broken Access Control",
                    description="Access control enforces policy",
                    category="Access Control",
                ),
                ComplianceControl(
                    control_id="A02:2021",
                    framework=ComplianceFramework.OWASP_TOP_10,
                    title="Cryptographic Failures",
                    description="Protect sensitive data",
                    category="Cryptography",
                ),
                ComplianceControl(
                    control_id="A03:2021",
                    framework=ComplianceFramework.OWASP_TOP_10,
                    title="Injection",
                    description="Prevent injection flaws",
                    category="Input Validation",
                ),
                ComplianceControl(
                    control_id="A06:2021",
                    framework=ComplianceFramework.OWASP_TOP_10,
                    title="Vulnerable and Outdated Components",
                    description="Keep software up to date",
                    category="Component Security",
                ),
            ],
            ComplianceFramework.NIST_CSF: [
                ComplianceControl(
                    control_id="ID.AM",
                    framework=ComplianceFramework.NIST_CSF,
                    title="Asset Management",
                    description="Identify and manage assets",
                    category="Identify",
                ),
                ComplianceControl(
                    control_id="PR.AC",
                    framework=ComplianceFramework.NIST_CSF,
                    title="Access Control",
                    description="Limit access to assets",
                    category="Protect",
                ),
                ComplianceControl(
                    control_id="DE.CM",
                    framework=ComplianceFramework.NIST_CSF,
                    title="Security Continuous Monitoring",
                    description="Monitor for cybersecurity events",
                    category="Detect",
                ),
                ComplianceControl(
                    control_id="RS.MI",
                    framework=ComplianceFramework.NIST_CSF,
                    title="Mitigation",
                    description="Mitigate detected incidents",
                    category="Respond",
                ),
            ],
            ComplianceFramework.ISO_27001: [
                ComplianceControl(
                    control_id="A.8.1",
                    framework=ComplianceFramework.ISO_27001,
                    title="Inventory of Assets",
                    description="Assets should be identified",
                    category="Asset Management",
                ),
                ComplianceControl(
                    control_id="A.9.1",
                    framework=ComplianceFramework.ISO_27001,
                    title="Access Control Policy",
                    description="Establish access control policy",
                    category="Access Control",
                ),
                ComplianceControl(
                    control_id="A.12.6",
                    framework=ComplianceFramework.ISO_27001,
                    title="Technical Vulnerability Management",
                    description="Manage technical vulnerabilities",
                    category="Vulnerability Management",
                ),
                ComplianceControl(
                    control_id="A.14.2",
                    framework=ComplianceFramework.ISO_27001,
                    title="Security in Development",
                    description="Secure development lifecycle",
                    category="Secure Development",
                ),
            ],
        }
        return controls

    def map_finding(self, finding: dict[str, Any], framework: ComplianceFramework) -> ComplianceMapping:
        """
        Map a finding to compliance controls

        Args:
            finding: Finding dictionary
            framework: Target compliance framework

        Returns:
            Compliance mapping
        """
        finding_id = finding.get("id")
        finding_type = finding.get("type", "").lower()
        description = finding.get("description", "").lower()

        matched_controls: list[ComplianceControl] = []

        if framework not in self._controls:
            raise ValueError(f"Framework {framework} not supported")

        # Match controls based on finding characteristics
        for control in self._controls[framework]:
            if self._matches_control(finding_type, description, control):
                matched_controls.append(control)

        # Calculate compliance score
        total_controls = len(self._controls[framework])
        compliance_score = len(matched_controls) / total_controls if total_controls > 0 else 0.0

        # Identify gaps
        gaps = self._identify_gaps(finding, matched_controls)

        return ComplianceMapping(
            finding_id=finding_id, controls=matched_controls, compliance_score=compliance_score, gaps=gaps
        )

    def _matches_control(self, finding_type: str, description: str, control: ComplianceControl) -> bool:
        """Check if finding matches a compliance control"""
        control_keywords = {
            "access control": ["access", "authorization", "authentication"],
            "cryptography": ["encryption", "crypto", "tls", "ssl"],
            "input validation": ["injection", "xss", "sql", "validation"],
            "vulnerability management": ["vulnerability", "cve", "patch"],
            "asset management": ["asset", "inventory", "discovery"],
            "monitoring": ["monitoring", "logging", "audit"],
        }

        category_lower = control.category.lower()

        for category, keywords in control_keywords.items():
            if category in category_lower:
                if any(kw in finding_type or kw in description for kw in keywords):
                    return True

        return False

    def _identify_gaps(self, finding: dict[str, Any], matched_controls: list[ComplianceControl]) -> list[str]:
        """Identify compliance gaps"""
        gaps: list[str] = []

        severity = finding.get("severity", "MEDIUM")

        if severity in ["CRITICAL", "HIGH"]:
            if not matched_controls:
                gaps.append("No matching compliance controls found")
            else:
                gaps.append(f"High severity finding affects {len(matched_controls)} control(s)")

        if not finding.get("remediation"):
            gaps.append("Missing remediation guidance")

        if not finding.get("evidence"):
            gaps.append("Insufficient evidence for audit trail")

        return gaps

    def generate_compliance_report(
        self, findings: list[dict[str, Any]], framework: ComplianceFramework
    ) -> dict[str, Any]:
        """
        Generate comprehensive compliance report

        Args:
            findings: List of findings
            framework: Target compliance framework

        Returns:
            Compliance report dictionary
        """
        mappings = [self.map_finding(f, framework) for f in findings]

        # Calculate overall compliance score
        total_score = sum(m.compliance_score for m in mappings)
        avg_score = total_score / len(mappings) if mappings else 0.0

        # Collect all affected controls
        affected_controls: dict[str, int] = {}
        for mapping in mappings:
            for control in mapping.controls:
                affected_controls[control.control_id] = affected_controls.get(control.control_id, 0) + 1

        # Collect all gaps
        all_gaps: list[str] = []
        for mapping in mappings:
            all_gaps.extend(mapping.gaps)

        return {
            "framework": framework.value,
            "total_findings": len(findings),
            "compliance_score": avg_score * 100,  # Convert to percentage
            "affected_controls": affected_controls,
            "total_gaps": len(all_gaps),
            "unique_gaps": list(set(all_gaps)),
            "mappings": mappings,
        }

    def get_framework_controls(self, framework: ComplianceFramework) -> list[ComplianceControl]:
        """Get all controls for a framework"""
        return self._controls.get(framework, [])
