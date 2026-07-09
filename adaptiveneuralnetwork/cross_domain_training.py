"""
Cross-Domain Trainer for Adaptive Neural Network.

Implements multi-task and zero-shot transfer protocols to evaluate 
the extreme generalization capabilities of the conscious AI system.
"""

import logging
import torch
import torch.nn as nn
from typing import List, Dict, Any, Optional
from .applications.few_shot_learning import FewShotLearningSystem

logger = logging.getLogger(__name__)

class CrossDomainTrainer:
    """
    Trainer for evaluating generalization across disparate domains.
    
    Protocols:
    - Domain Cycling: MNIST -> Synthetic -> CIFAR.
    - Zero-Shot Evaluation: Testing on Domain C after training on A and B.
    - Catastrophic Forgetting Monitoring: Evaluating Domain A after training on B.
    """
    def __init__(self, 
                 model: FewShotLearningSystem,
                 domains: List[str]):
        self.model = model
        self.domains = domains
        self.performance_history = {d: [] for d in domains}
        
    def train_step(self, 
                   domain: str, 
                   batch: Dict[str, torch.Tensor],
                   optimizer: torch.optim.Optimizer) -> Dict[str, Any]:
        """
        Execute a single training step on a specific domain.
        """
        logger.info(f"Training step on domain: {domain}")
        
        # Unpack few-shot episode
        s_x, s_y = batch['support_set']
        q_x, q_y = batch['query_set']
        
        # Training using the model's meta-learning loop
        stats = self.model.meta_learn_maml(s_x, s_y, q_x, q_y, optimizer)
        
        # Record cognitive state
        stats['cognitive_load'] = self.model.cognitive_load.item()
        
        return stats

    def evaluate_generalization(self, 
                                unseen_domain: str, 
                                batch: Dict[str, torch.Tensor]) -> Dict[str, Any]:
        """
        Evaluate zero-shot performance on a domain the model hasn't seen during training.
        """
        self.model.eval()
        logger.info(f"Zero-shot evaluation on: {unseen_domain}")
        
        s_x, s_y = batch['support_set']
        q_x, q_y = batch['query_set']
        
        with torch.no_grad():
            stats = self.model.evaluate_episode(s_x, s_y, q_x, q_y)
            
        return stats
