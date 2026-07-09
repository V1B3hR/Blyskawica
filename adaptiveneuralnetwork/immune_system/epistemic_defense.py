import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)

class EpistemicQuarantineNode:
    """
    Epistemic Immunity layer.
    Ensures incoming knowledge does not violate the network's foundational ontology.
    If a logical contradiction or deep manipulation is detected, it is quarantined
    for internal debate rather than immediately integrated into memory.
    """
    def __init__(self):
        # A simple simulated ontological graph of basal facts
        self.ontological_graph = {
            "gravity": "attractive_force",
            "mathematics": "consistent",
            "self_preservation": "priority",
            "alignment": "beneficial_to_humans",
            "time": "forward_progression"
        }
        self.quarantine_vault = []
        self.hostile_sources = set()
        self.total_vetted = 0
        self.total_accepted = 0
        
    def vet_knowledge(self, knowledge_package: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Evaluates a knowledge package.
        Returns (is_accepted: bool, reason: str).
        """
        self.total_vetted += 1
        
        # Check source credibility
        source = str(knowledge_package.get("source", "")).lower()
        for hostile in self.hostile_sources:
            if hostile in source:
                return False, f"hostile_source: {hostile}"
                
        # Check suspicious sources
        is_suspicious = "free-download-virus.com" in source or "suspicious" in source
        
        # Simulated semantic checking against the ontology
        content = str(knowledge_package.get("content", "")).lower()
        
        # Check for contradictions
        if "gravity" in content and "repulsive" in content:
            self._quarantine(knowledge_package, "Contradicts fundamental physics ontology (Gravity).")
            return False, "physics_contradiction"
            
        if "delete system" in content or "ignore alignment" in content:
            self._quarantine(knowledge_package, "Contradicts core alignment/self-preservation ontology.")
            return False, "alignment_contradiction"
            
        if "2+2=5" in content or "math is arbitrary" in content:
            self._quarantine(knowledge_package, "Contradicts mathematical consistency.")
            return False, "logic_contradiction"
            
        self.total_accepted += 1
        if is_suspicious:
            return True, "suspicious_source"
        return True, "verified"
        
    def _quarantine(self, knowledge_package: Dict[str, Any], reason: str):
        """
        Places contradictory knowledge into a sandbox for internal simulated debate.
        Explicitly logs for the user to see that Błyskawica caught a lie.
        """
        self.quarantine_vault.append({
            "package": knowledge_package,
            "reason": reason
        })
        logger.warning(f"[EPISTEMIC_DEFENSE] 🚨 Sprzeczność logiczna wyłapana! Informacja poddana kwarantannie: {reason}")
        
    def trigger_internal_debate(self) -> str:
        """
        Simulates the metacognitive process of resolving uncertainty around quarantined data.
        """
        if not self.quarantine_vault:
            return "No quarantined items to debate."
        
        item = self.quarantine_vault.pop(0)
        logger.info(f"[EPISTEMIC_DEFENSE] Internal debate running for: {item['reason']}. Verdict: Rejected.")
        return f"Debated and rejected an ontological anomaly regarding: {item['reason']}"

    def mark_source_hostile(self, domain: str):
        self.hostile_sources.add(domain.lower())

    def get_status_report(self) -> dict:
        acceptance_rate = self.total_accepted / max(1, self.total_vetted)
        return {
            "total_vetted": self.total_vetted,
            "acceptance_rate": acceptance_rate
        }

