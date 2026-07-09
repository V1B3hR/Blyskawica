"""
AI Reporter

Generates comprehensive reports including CVSS scores, executive summaries,
remediation recommendations, and bird activity reports.
"""

import logging
from datetime import datetime
from typing import Any


class AIReporter:
    """
    📝 AI Report Generator

    Generates:
    • CVSS-style threat reports
    • Executive summaries
    • Remediation plans
    • Bird activity reports
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def generate_cvss_report(self, threat_data: dict[str, Any]) -> dict[str, Any]:
        """
        Generate CVSS-style vulnerability report

        Args:
            threat_data: Threat information

        Returns:
            CVSS-style report
        """
        # Simplified CVSS scoring
        base_score = threat_data.get("threat_score", 5.0)

        # Map to CVSS severity
        if base_score >= 9.0:
            severity = "CRITICAL"
            rating = "Critical"
        elif base_score >= 7.0:
            severity = "HIGH"
            rating = "High"
        elif base_score >= 4.0:
            severity = "MEDIUM"
            rating = "Medium"
        else:
            severity = "LOW"
            rating = "Low"

        return {
            "cvss_version": "3.1",
            "base_score": base_score,
            "severity": severity,
            "rating": rating,
            "vector_string": self._generate_vector_string(threat_data),
            "threat_id": threat_data.get("id", "unknown"),
            "description": threat_data.get("description", "No description available"),
            "impact": self._assess_impact(threat_data),
            "exploitability": self._assess_exploitability(threat_data),
            "timestamp": datetime.now().isoformat(),
        }

    def _generate_vector_string(self, threat_data: dict[str, Any]) -> str:
        """Generate CVSS vector string"""
        # Simplified vector - in production, this would be more detailed
        return f"NETHICAL:1.0/S:{threat_data.get('severity', 'M')[0]}/C:{threat_data.get('confidence', 0.5):.1f}"

    def _assess_impact(self, threat_data: dict[str, Any]) -> dict[str, str]:
        """Assess CIA (Confidentiality, Integrity, Availability) impact"""
        impact_level = threat_data.get("impact", "MEDIUM")

        # Map based on threat type
        threat_type = threat_data.get("type", "unknown")

        if threat_type == "magpie":  # Data stealer
            return {"confidentiality": "HIGH", "integrity": "LOW", "availability": "NONE"}
        elif threat_type == "snake":  # Rootkit
            return {"confidentiality": "HIGH", "integrity": "HIGH", "availability": "HIGH"}
        elif threat_type == "parasite":  # Cryptominer
            return {"confidentiality": "NONE", "integrity": "LOW", "availability": "HIGH"}
        else:
            return {"confidentiality": "MEDIUM", "integrity": "MEDIUM", "availability": "MEDIUM"}

    def _assess_exploitability(self, threat_data: dict[str, Any]) -> dict[str, str]:
        """Assess exploitability metrics"""
        confidence = threat_data.get("confidence", 0.5)

        if confidence >= 0.8:
            complexity = "LOW"
        elif confidence >= 0.5:
            complexity = "MEDIUM"
        else:
            complexity = "HIGH"

        return {"attack_complexity": complexity, "privileges_required": "LOW", "user_interaction": "NONE"}

    def generate_executive_summary(self, session_data: dict[str, Any]) -> str:
        """
        Generate executive summary for hunting session

        Args:
            session_data: Session information including threats, actions, etc.

        Returns:
            Formatted executive summary
        """
        threats = session_data.get("threats", [])
        stains = session_data.get("stains", [])
        birds = session_data.get("birds", {})
        forest = session_data.get("forest", {})

        critical_threats = sum(1 for t in threats if t.get("severity") == "CRITICAL")
        high_threats = sum(1 for t in threats if t.get("severity") == "HIGH")

        summary = f"""
🦅 NETHICAL HUNTER - EXECUTIVE SUMMARY
{'='*70}

📅 Session Date: {session_data.get('start_time', datetime.now().isoformat())}
⏱️  Duration: {session_data.get('duration', 'N/A')}
👤 Hunter: {session_data.get('hunter', 'Unknown')}

🎯 THREAT OVERVIEW
{'='*70}
Total Threats Detected: {len(threats)}
  🔴 Critical: {critical_threats}
  🟠 High: {high_threats}
  🟡 Medium: {len(threats) - critical_threats - high_threats}

🎨 STAIN REPORT
{'='*70}
Total Stains Created: {len(stains)}
  🔴 Malware: {sum(1 for s in stains if s.get('marker_type') == 'MALWARE')}
  🖤 Crows: {sum(1 for s in stains if s.get('marker_type') == 'CROW')}
  🤎 Squirrels: {sum(1 for s in stains if s.get('marker_type') == 'SQUIRREL')}
  🟠 Suspicious IPs: {sum(1 for s in stains if s.get('marker_type') == 'SUSPICIOUS_IP')}

🦅 BIRD ACTIVITY
{'='*70}
Eagle Assessments: {birds.get('eagle', {}).get('assessments', 0)}
Falcon Alerts: {birds.get('falcon', {}).get('alerts', 0)}
Owl Night Watches: {birds.get('owl', {}).get('watches', 0)}
Sparrow Checks: {birds.get('sparrow', {}).get('checks', 0)}

🌳 FOREST HEALTH
{'='*70}
Total Trees: {forest.get('total_trees', 0)}
Healthy Trees: {forest.get('healthy_trees', 0)}
Compromised Trees: {forest.get('compromised_trees', 0)}
Health Score: {forest.get('health_score', 0)}/100

📊 KEY FINDINGS
{'='*70}
{self._format_key_findings(threats, stains)}

🎯 RECOMMENDATIONS
{'='*70}
{self._format_recommendations(session_data)}

{'='*70}
Report Generated: {datetime.now().isoformat()}
"""
        return summary.strip()

    def _format_key_findings(self, threats: list[dict], stains: list[dict]) -> str:
        """Format key findings section"""
        findings = []

        # Top 3 threats by score
        sorted_threats = sorted(threats, key=lambda t: t.get("threat_score", 0), reverse=True)[:3]
        for i, threat in enumerate(sorted_threats, 1):
            findings.append(
                f"{i}. {threat.get('description', 'Unknown threat')} (Score: {threat.get('threat_score', 0)})"
            )

        if not findings:
            findings.append("No significant threats detected")

        return "\n".join(findings)

    def _format_recommendations(self, session_data: dict[str, Any]) -> str:
        """Format recommendations section"""
        recommendations = []

        threats = session_data.get("threats", [])
        forest = session_data.get("forest", {})

        critical_count = sum(1 for t in threats if t.get("severity") == "CRITICAL")
        health_score = forest.get("health_score", 100)

        if critical_count > 0:
            recommendations.append(f"• URGENT: Address {critical_count} critical threat(s) immediately")
            recommendations.append("• Deploy all defensive nanobots")
            recommendations.append("• Activate Eagle mode for strategic oversight")

        if health_score < 70:
            recommendations.append("• Forest health is degraded - increase monitoring")
            recommendations.append("• Deploy Owl for enhanced night watch")

        if not threats:
            recommendations.append("• No immediate threats detected")
            recommendations.append("• Maintain current security posture")
            recommendations.append("• Continue routine Sparrow patrols")

        return "\n".join(recommendations)

    def generate_remediation_plan(self, threat_data: dict[str, Any]) -> dict[str, Any]:
        """
        Generate step-by-step remediation plan

        Args:
            threat_data: Threat information

        Returns:
            Remediation plan
        """
        threat_type = threat_data.get("type", "unknown")
        severity = threat_data.get("severity", "MEDIUM")

        steps = []

        # Immediate actions
        if severity in ["CRITICAL", "HIGH"]:
            steps.append(
                {
                    "phase": "IMMEDIATE",
                    "priority": 1,
                    "action": "Isolate affected system(s)",
                    "timeframe": "0-15 minutes",
                    "responsible": "SOC Team",
                }
            )
            steps.append(
                {
                    "phase": "IMMEDIATE",
                    "priority": 2,
                    "action": "Deploy defensive nanobots",
                    "timeframe": "0-15 minutes",
                    "responsible": "Automated",
                }
            )

        # Threat-specific steps
        if threat_type == "crow":
            steps.extend(
                [
                    {
                        "phase": "CONTAINMENT",
                        "priority": 3,
                        "action": "Terminate malicious process",
                        "timeframe": "15-30 minutes",
                        "responsible": "SOC Team",
                    },
                    {
                        "phase": "ERADICATION",
                        "priority": 4,
                        "action": "Remove malware and persistence mechanisms",
                        "timeframe": "30-60 minutes",
                        "responsible": "SOC Team",
                    },
                ]
            )
        elif threat_type == "magpie":
            steps.extend(
                [
                    {
                        "phase": "CONTAINMENT",
                        "priority": 3,
                        "action": "Block data exfiltration paths",
                        "timeframe": "15-30 minutes",
                        "responsible": "Network Team",
                    },
                    {
                        "phase": "ASSESSMENT",
                        "priority": 4,
                        "action": "Identify stolen data",
                        "timeframe": "1-4 hours",
                        "responsible": "Security Team",
                    },
                ]
            )
        elif threat_type == "squirrel":
            steps.extend(
                [
                    {
                        "phase": "CONTAINMENT",
                        "priority": 3,
                        "action": "Block lateral movement paths",
                        "timeframe": "15-30 minutes",
                        "responsible": "Network Team",
                    },
                    {
                        "phase": "INVESTIGATION",
                        "priority": 4,
                        "action": "Map compromised systems",
                        "timeframe": "1-2 hours",
                        "responsible": "SOC Team",
                    },
                ]
            )

        # Recovery steps
        steps.extend(
            [
                {
                    "phase": "RECOVERY",
                    "priority": len(steps) + 1,
                    "action": "Restore from clean backup if needed",
                    "timeframe": "2-4 hours",
                    "responsible": "IT Team",
                },
                {
                    "phase": "RECOVERY",
                    "priority": len(steps) + 2,
                    "action": "Apply security patches",
                    "timeframe": "4-8 hours",
                    "responsible": "IT Team",
                },
            ]
        )

        # Post-incident
        steps.append(
            {
                "phase": "POST-INCIDENT",
                "priority": len(steps) + 1,
                "action": "Conduct post-incident review",
                "timeframe": "24-48 hours",
                "responsible": "Security Team",
            }
        )

        return {
            "threat_id": threat_data.get("id", "unknown"),
            "threat_type": threat_type,
            "severity": severity,
            "plan_created": datetime.now().isoformat(),
            "estimated_total_time": "8-12 hours",
            "steps": steps,
            "success_criteria": self._generate_success_criteria(threat_type),
        }

    def _generate_success_criteria(self, threat_type: str) -> list[str]:
        """Generate success criteria for remediation"""
        criteria = [
            "No malicious activity detected for 72 hours",
            "All affected systems scanned and cleared",
            "All security patches applied",
            "Incident documentation completed",
        ]

        if threat_type == "magpie":
            criteria.append("Data exfiltration paths confirmed blocked")
            criteria.append("Stolen data impact assessed")
        elif threat_type == "squirrel":
            criteria.append("All compromised systems identified and remediated")
            criteria.append("Lateral movement paths secured")

        return criteria

    def generate_bird_report(self, bird_data: dict[str, Any]) -> dict[str, Any]:
        """
        Generate bird activity report

        Args:
            bird_data: Bird activity information

        Returns:
            Bird activity report
        """
        return {
            "report_type": "BIRD_ACTIVITY",
            "timestamp": datetime.now().isoformat(),
            "eagle": self._format_eagle_report(bird_data.get("eagle", {})),
            "falcon": self._format_falcon_report(bird_data.get("falcon", {})),
            "owl": self._format_owl_report(bird_data.get("owl", {})),
            "sparrow": self._format_sparrow_report(bird_data.get("sparrow", {})),
            "summary": self._generate_bird_summary(bird_data),
        }

    def _format_eagle_report(self, eagle_data: dict) -> dict[str, Any]:
        """Format Eagle (strategic) report"""
        return {
            "mode": "STRATEGIC_COMMAND",
            "assessments": eagle_data.get("assessments", 0),
            "decisions": eagle_data.get("decisions", []),
            "strategic_view": eagle_data.get("strategic_view", "Clear skies"),
            "recommendations": eagle_data.get("recommendations", []),
        }

    def _format_falcon_report(self, falcon_data: dict) -> dict[str, Any]:
        """Format Falcon (rapid response) report"""
        return {
            "mode": "RAPID_RESPONSE",
            "alerts": falcon_data.get("alerts", 0),
            "rapid_responses": falcon_data.get("responses", 0),
            "targets_marked": falcon_data.get("targets_marked", 0),
            "average_response_time": falcon_data.get("avg_response_time", "N/A"),
        }

    def _format_owl_report(self, owl_data: dict) -> dict[str, Any]:
        """Format Owl (night watch) report"""
        return {
            "mode": "NIGHT_WATCH",
            "watches": owl_data.get("watches", 0),
            "night_detections": owl_data.get("detections", 0),
            "hidden_threats": owl_data.get("hidden_threats", 0),
            "stealth_operations": owl_data.get("stealth_ops", 0),
        }

    def _format_sparrow_report(self, sparrow_data: dict) -> dict[str, Any]:
        """Format Sparrow (routine check) report"""
        return {
            "mode": "ROUTINE_CHECK",
            "checks": sparrow_data.get("checks", 0),
            "heartbeats": sparrow_data.get("heartbeats", 0),
            "anomalies": sparrow_data.get("anomalies", 0),
            "baseline_status": sparrow_data.get("baseline_status", "NORMAL"),
        }

    def _generate_bird_summary(self, bird_data: dict) -> str:
        """Generate summary of bird activities"""
        total_alerts = sum(
            [
                bird_data.get("eagle", {}).get("assessments", 0),
                bird_data.get("falcon", {}).get("alerts", 0),
                bird_data.get("owl", {}).get("detections", 0),
                bird_data.get("sparrow", {}).get("anomalies", 0),
            ]
        )

        if total_alerts == 0:
            return "All birds report normal activity. Forest is quiet."
        elif total_alerts < 5:
            return f"{total_alerts} alerts raised by bird patrols. Situation under control."
        else:
            return f"{total_alerts} alerts raised. Increased bird activity indicates heightened threat level."
