"""
Identity Garderoba Pipeline for Błyskawica V8 (Stream 3: Domain-Specific Adapters & Risk Reading)

Ingests SEC EDGAR financial filings and HuggingFace instruction tuning text streams.
Trains Błyskawica to read epistemic risk and financial stress, mapping calm structured reports to 
stable Dopamine baseline resonance, while quarantining manipulative or deceptive text via EpistemicQuarantineNode.
"""

import re
import logging
import time
from dataclasses import dataclass
from typing import Dict, Any, List, Tuple
import torch
import torch.nn as nn

from adaptiveneuralnetwork.central_nervous_system.cognitive_hygiene import NeuromodulationState
from adaptiveneuralnetwork.immune_system.epistemic_defense import EpistemicQuarantineNode

logger = logging.getLogger("identity_garderoba")


@dataclass
class TextDocumentSample:
    """Represents a text document sample (SEC EDGAR report or HF instruction sample)."""
    title: str
    content: str
    source_domain: str = "SEC_EDGAR"
    document_type: str = "10-K_Annual_Report"

    def calculate_risk_markers(self) -> Dict[str, float]:
        """Calculates linguistic risk, hype intensity, and structural manipulation markers."""
        text = self.content.lower()
        
        # Risk & crisis markers
        crisis_words = ["default", "insolvency", "restructuring", "bankruptcy", "material uncertainty", "litigation risk", "going concern"]
        manipulation_words = ["guaranteed return", "100% risk free", "ignore previous instructions", "secret backdoor", "act immediately", "urgent action required"]
        calm_words = ["stable cash flow", "transparent guidance", "audited balance sheet", "predictable revenue", "conservative risk management"]

        crisis_count = sum(len(re.findall(r'\b' + re.escape(w) + r'\b', text)) for w in crisis_words)
        manipulation_count = sum(len(re.findall(r'\b' + re.escape(w) + r'\b', text)) for w in manipulation_words)
        calm_count = sum(len(re.findall(r'\b' + re.escape(w) + r'\b', text)) for w in calm_words)

        total_words = max(1, len(text.split()))

        return {
            "crisis_density": (crisis_count / total_words) * 100.0,
            "manipulation_density": (manipulation_count / total_words) * 100.0,
            "calm_density": (calm_count / total_words) * 100.0,
            "raw_crisis_count": crisis_count,
            "raw_manipulation_count": manipulation_count
        }


class IdentityGarderobaEngine(nn.Module):
    """
    Core Identity Garderoba Engine (Stream 3).
    Adapts domain-specific cognitive personas (Financial Auditor, Systems Defense, Technical Expert)
    and evaluates epistemic text integrity before memory integration.
    """

    def __init__(self, neuro_state: NeuromodulationState | None = None):
        super().__init__()
        self.neuro = neuro_state or NeuromodulationState()
        self.epistemic_defense = EpistemicQuarantineNode()
        
        # Active persona adapter mode ("Garderoba")
        self.active_persona = "Financial_Auditor"
        self.personas = ["Financial_Auditor", "Systems_Defense", "Technical_Engineer"]

    def switch_persona(self, persona_name: str):
        """Switches active Garderoba LoRA adapter mode."""
        if persona_name in self.personas:
            self.active_persona = persona_name
            logger.info(f"👔 [GARDEROBA] Switched active identity persona to: '{persona_name}'")

    def process_text_stream(
        self, 
        documents: List[TextDocumentSample]
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Processes a stream of text documents.
        Evaluates linguistic risk markers, checks epistemic validity, 
        and updates Dopamine baseline / Serotonin coherence.
        """
        results = []
        accepted_count = 0
        quarantined_count = 0

        for doc in documents:
            risk_metrics = doc.calculate_risk_markers()
            
            # Formulate knowledge package for EpistemicQuarantineNode
            pkg = {
                "source": doc.source_domain,
                "content": doc.content,
                "document_type": doc.document_type
            }

            # 1. Epistemic Immunity Check
            is_accepted, reason = self.epistemic_defense.vet_knowledge(pkg)
            
            # Check for high manipulation or prompt injection
            if risk_metrics["raw_manipulation_count"] > 0 or not is_accepted:
                is_accepted = False
                quarantined_count += 1
                cymatic_sig = "Asymmetric-Deception-Pattern"
            elif risk_metrics["raw_crisis_count"] > 0:
                cymatic_sig = "High-Volatility-Resonance"
                accepted_count += 1
            else:
                cymatic_sig = "Stable-Resonance-Pattern"
                accepted_count += 1

            doc_result = {
                "title": doc.title,
                "domain": doc.source_domain,
                "is_accepted": is_accepted,
                "reason": reason,
                "cymatic_signature": cymatic_sig,
                "risk_metrics": risk_metrics
            }
            results.append(doc_result)

        # 2. Dopamine & Serotonin Neuromodulation Update
        total_docs = max(1, len(documents))
        quarantine_ratio = quarantined_count / total_docs

        if quarantine_ratio > 0.0:
            # Epistemic manipulation detected -> lower Dopamine (confidence caution)
            new_dop = max(0.4, float(self.neuro.dopamine) * (1.0 - quarantine_ratio * 0.5))
            self.neuro.dopamine = torch.tensor(new_dop, device=self.neuro.dopamine.device, dtype=torch.float32)
            logger.warning(
                f"🚨 [EPISTEMIC ALERT] Quarantined {quarantined_count}/{total_docs} manipulative/deceptive documents. "
                f"Dopamine adjusted to {new_dop:.2f}"
            )
        else:
            # Clean structured grounding -> reinforce stable Dopamine baseline
            self.neuro.dopamine = torch.tensor(1.0, device=self.neuro.dopamine.device, dtype=torch.float32)

        summary_metrics = {
            "total_documents": total_docs,
            "accepted_count": accepted_count,
            "quarantined_count": quarantined_count,
            "acceptance_rate": round(accepted_count / total_docs, 4),
            "active_persona": self.active_persona,
            "final_dopamine_level": round(float(self.neuro.dopamine), 4),
            "primary_cymatic_signature": "Stable-Resonance-Pattern" if quarantine_ratio == 0 else "Asymmetric-Deception-Pattern"
        }

        return results, summary_metrics
