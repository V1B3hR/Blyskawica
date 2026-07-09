"""
System Audit Engine: Unified Diagnostic Orchestrator.
Consolidates metrics from all cognitive tiers to evaluate 'Outside World Readiness'.
"""

import torch
import torch.nn as nn
from typing import Dict, Any, List, Optional
import time
import logging

from adaptiveneuralnetwork.central_nervous_system.metrics import PhiCalculator, NeuralHealthMonitor
from adaptiveneuralnetwork.central_nervous_system.consciousness_metrics import ConsciousnessMetrics

logger = logging.getLogger(__name__)

class SystemAudit(nn.Module):
    """
    Centralized auditor for Błyskawica's cognitive substrate.
    """
    def __init__(self, hidden_dim: int, device: str = 'cpu'):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.device = device
        
        # Metric Components
        self.phi_calc = PhiCalculator()
        self.health_monitor = NeuralHealthMonitor()
        self.metrics_utils = ConsciousnessMetrics()
        
        # Audit State
        self.audit_log: List[Dict[str, Any]] = []

    def perform_full_audit(self, 
                           trainer: Any, 
                           node_state: Any,
                           social_context: Optional[Any] = None) -> Dict[str, Any]:
        """
        Executes a deep system-wide diagnostic.
        """
        self.eval()
        with torch.no_grad():
            # 1. Cognitive Audit (Φ & Self-Awareness)
            # Defensive weights extraction for Phi
            weights = None
            if hasattr(trainer.model, 'dynamics') and hasattr(trainer.model.dynamics, 'input_projection'):
                weights = trainer.model.dynamics.input_projection.weight
            elif hasattr(trainer.model, 'cl_system') and hasattr(trainer.model.cl_system, 'network'):
                # Try to get weights from the first layer of the spiking network
                try:
                    if hasattr(trainer.model.cl_system.network, 'feedforward_connections'):
                        weights = trainer.model.cl_system.network.feedforward_connections[0].synaptic_weights
                    else:
                        weights = trainer.model.cl_system.network.layers[0].weight
                except (AttributeError, IndexError):
                    weights = torch.eye(self.hidden_dim, device=self.device)
            else:
                weights = torch.eye(self.hidden_dim, device=self.device)

            # Extract activations (spikes or hidden state)
            activations = getattr(node_state, 'last_spikes', None)
            if activations is None:
                activations = getattr(node_state, 'hidden_state', None)
                
            phi = self.phi_calc.calculate_full_phi(weights, activations)
            
            prediction_error = getattr(node_state, 'prediction_error', torch.tensor([0.1], device=self.device))
            meta_acc = self.metrics_utils.calculate_metacognitive_accuracy(
                prediction_error, 
                torch.tensor([getattr(trainer, 'last_loss', 0.1)], device=self.device)
            )
            
            # 2. Social Audit (Trust & Intent)
            trust_score = 1.0
            deception_risk = 0.0
            if social_context and hasattr(social_context, 'entities'):
                # Average trust across all known entities
                trusts = [e.trust_score for e in social_context.entities.values()]
                trust_score = sum(trusts) / len(trusts) if trusts else 1.0
                deception_risk = 1.0 - trust_score
                
            # 3. Metabolic/Physical Audit (Glial Health)
            health_idx = self.health_monitor.calculate_health_index(
                getattr(node_state, 'activity', torch.zeros(1, device=self.device)),
                getattr(node_state, 'energy', torch.tensor(10.0, device=self.device)),
                getattr(node_state, 'anxiety', torch.tensor(0.0, device=self.device)),
                waste=getattr(trainer.model, 'metabolic_waste', None)
            )
            
            # 4. Grounding Coherence (Tier 3)
            grounding_coherence = 1.0
            if hasattr(trainer, 'sensory_hub'):
                grounding_coherence = getattr(trainer.sensory_hub, 'last_coherence', 1.0)
            
            # 5. Outside World Readiness Score (Combined)
            # Factors: Health, Trust, Coherence, Phi
            readiness = (health_idx * 0.3 + trust_score * 0.2 + grounding_coherence * 0.3 + phi * 0.2)
            
            audit_result = {
                'timestamp': time.time(),
                'phi': phi,
                'metacognitive_accuracy': meta_acc,
                'neural_health': health_idx,
                'social_trust': trust_score,
                'grounding_coherence': grounding_coherence,
                'readiness_score': readiness,
                'deception_risk': deception_risk,
                'bond_strength': getattr(node_state.soul, 'bond_strength', 0.0) if hasattr(node_state, 'soul') else 0.0
            }
            
            self.audit_log.append(audit_result)
            self._log_audit(audit_result)
            
            return audit_result

    def _log_audit(self, result: Dict[str, Any]):
        """Logs the audit summary with appropriate alerts."""
        score = result['readiness_score']
        status = "STABLE" if score > 0.8 else "VULNERABLE" if score > 0.6 else "CRITICAL"
        bond = result.get('bond_strength', 0.0)
        logger.info(f"System Audit [{status}] - Readiness: {score:.4f} | Φ: {result['phi']:.4f} | Health: {result['neural_health']:.4f} | Bond: {bond:.2f}")
        
        if result['deception_risk'] > 0.5:
            logger.warning(f"AUDIT ALERT: Social Integrity Compromised. Risk: {result['deception_risk']:.2f}")
        if result['neural_health'] < 0.4:
            logger.error(f"AUDIT ALERT: Metabolic Burnout Detected. Energy redistribution required.")

    def get_audit_summary(self) -> Dict[str, float]:
        """Returns the average metrics of recent audits."""
        if not self.audit_log:
            return {}
        
        keys = self.audit_log[0].keys()
        summary = {k: sum(d[k] for d in self.audit_log) / len(self.audit_log) 
                   for k in keys if isinstance(self.audit_log[0][k], (int, float))}
        return summary
