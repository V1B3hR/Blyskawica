"""
Consciousness Metrics and Emergence Scoring for Phase 7.5.

Implements simplified Integrated Information Theory (IIT) metrics, Φ (Phi) 
approximations, and metacognitive accuracy tracking.
"""

import torch
import torch.nn as nn
from typing import Dict, Any, List, Optional
import numpy as np

class ConsciousnessMetrics:
    """
    Tracks emergence and integration metrics across the neural substrate.
    """
    @staticmethod
    def calculate_phi_lite(activations: torch.Tensor, connections: torch.Tensor) -> float:
        """
        A simplified approximation of Integrated Information (Phi).
        Measures the effective information integration between sub-systems.
        
        Phi ~ Coordination - Independence
        """
        # Calculate Mutual Information approximation between partitions
        # Split activation into two halves
        mid = activations.size(-1) // 2
        p1 = activations[..., :mid]
        p2 = activations[..., mid:]
        
        # Correlation-based integration metric
        # Ensure we have 2D input for corrcoef [samples, features] -> [2, samples*features]
        v1 = p1.reshape(1, -1)
        v2 = p2.reshape(1, -1)
        correlation = torch.corrcoef(torch.cat([v1, v2], dim=0))
        integration = correlation[0, 1].item() if not torch.isnan(correlation[0, 1]) else 0.0
        
        # Complexity (Structural diversity)
        diversity = torch.std(activations).item()
        
        # Phi Lite = integration * diversity (Coherent Complexity)
        phi = max(0.0, integration * diversity)
        return phi

    @staticmethod
    def calculate_metacognitive_accuracy(prediction_errors: torch.Tensor, 
                                        actual_performance: torch.Tensor) -> float:
        """
        Measure how well the internal predictive model (surprise) matches 
        actual task errors. 
        High accuracy = Good self-model (Self-Awareness).
        """
        # Correlation between surprise (prediction_error) and actual loss
        # normalize
        err = prediction_errors.mean().item()
        perf = actual_performance.mean().item()
        
        # Accuracy is the inverse of the discordance between prediction and reality
        accuracy = 1.0 / (1.0 + abs(err - perf))
        return accuracy

    @staticmethod
    def calculate_emergence_score(social_trust: torch.Tensor, 
                                  global_workspace_salience: torch.Tensor) -> float:
        """
        Measures the influence of collective dynamics.
        """
        trust_integration = social_trust.mean().item()
        governance = global_workspace_salience.mean().item()
        
        return (trust_integration + governance) / 2.0

    @staticmethod
    def calculate_consciousness_coherence(phi: float, 
                                          meta_acc: float, 
                                          emergence: float) -> float:
        """
        A composite metric measuring the overall 'holistic' state of the system.
        """
        return (phi + meta_acc + emergence) / 3.0

    @staticmethod
    def calculate_emotional_appropriateness(anxiety_levels: torch.Tensor, 
                                            surprise_levels: torch.Tensor) -> float:
        """
        Measures if emotional reaction (anxiety) is appropriate for the stimulus (surprise).
        High surprise should correlate with rising anxiety.
        """
        # Correlation between surprise and anxiety
        if anxiety_levels.numel() < 2: return 1.0
        
        # Simple correlation-based appropriateness
        corr = torch.corrcoef(torch.cat([anxiety_levels.flatten().unsqueeze(0), 
                                       surprise_levels.flatten().unsqueeze(0)], dim=0))[0, 1]
        
        return max(0.0, corr.item()) if not torch.isnan(corr) else 0.5
