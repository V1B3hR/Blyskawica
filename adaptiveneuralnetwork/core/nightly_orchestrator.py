import time
import copy
import torch
import torch.nn as nn
import torch.optim as optim
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional

class NightlyPhase(Enum):
    IDLE = "idle"
    TRAINING = "training"
    EVALUATING = "evaluating"
    MERGING = "merging"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class KnowledgeItem:
    item_id: int
    data: torch.Tensor
    target: torch.Tensor
    domain: str
    source: str

@dataclass
class NightlyReport:
    merge_accepted: bool
    merge_reason: str
    duration_seconds: float
    accepted_items: int
    shadow_training_epochs: int
    current_phase: NightlyPhase

class NightlyUpdateOrchestrator:
    def __init__(self, model, acceptance_threshold: float = 0.05, shadow_training_epochs: int = 5):
        self.model = model
        self.acceptance_threshold = acceptance_threshold
        self.shadow_training_epochs = shadow_training_epochs
        self.cycle_count: int = 0
        self.current_phase: NightlyPhase = NightlyPhase.IDLE

    def execute_nightly_cycle(self, knowledge_queue: List[KnowledgeItem]) -> NightlyReport:
        start_time = time.time()
        
        if not knowledge_queue:
            self.cycle_count += 1
            self.current_phase = NightlyPhase.COMPLETED
            duration = time.time() - start_time
            return NightlyReport(
                merge_accepted=False,
                merge_reason="no_novel_knowledge",
                duration_seconds=max(0.001, duration),
                accepted_items=0,
                shadow_training_epochs=self.shadow_training_epochs,
                current_phase=self.current_phase
            )

        try:
            self.current_phase = NightlyPhase.TRAINING
            
            # Clone model for shadow training
            shadow_model = copy.deepcopy(self.model)
            
            # Prepare data
            inputs = torch.stack([item.data for item in knowledge_queue])
            targets = torch.stack([item.target for item in knowledge_queue])
            
            # Optimizer and loss
            optimizer = optim.SGD(shadow_model.parameters(), lr=0.1)
            criterion = nn.CrossEntropyLoss()
            
            # Train shadow model
            shadow_model.train()
            for epoch in range(self.shadow_training_epochs):
                optimizer.zero_grad()
                outputs = shadow_model(inputs)
                loss = criterion(outputs, targets)
                loss.backward()
                optimizer.step()
                
            self.current_phase = NightlyPhase.EVALUATING
            
            # Evaluate performance on new knowledge
            shadow_model.eval()
            self.model.eval()
            
            with torch.no_grad():
                # Original model accuracy
                orig_outputs = self.model(inputs)
                orig_preds = torch.argmax(orig_outputs, dim=1)
                orig_acc = (orig_preds == targets).sum().item() / len(targets)
                
                # Shadow model accuracy
                shadow_outputs = shadow_model(inputs)
                shadow_preds = torch.argmax(shadow_outputs, dim=1)
                shadow_acc = (shadow_preds == targets).sum().item() / len(targets)
                
            delta = shadow_acc - orig_acc
            
            self.current_phase = NightlyPhase.MERGING
            if delta >= self.acceptance_threshold:
                # Merge: load shadow weights into main model
                self.model.load_state_dict(shadow_model.state_dict())
                merge_accepted = True
                merge_reason = f"performance_improvement: shadow={shadow_acc:.3f}, orig={orig_acc:.3f}"
            else:
                merge_accepted = False
                merge_reason = f"no_performance_improvement: shadow={shadow_acc:.3f}, orig={orig_acc:.3f}"
                
            self.current_phase = NightlyPhase.COMPLETED
            
        except Exception as e:
            self.current_phase = NightlyPhase.FAILED
            duration = time.time() - start_time
            return NightlyReport(
                merge_accepted=False,
                merge_reason=f"error during training: {str(e)}",
                duration_seconds=max(0.001, duration),
                accepted_items=len(knowledge_queue),
                shadow_training_epochs=self.shadow_training_epochs,
                current_phase=self.current_phase
            )
            
        self.cycle_count += 1
        duration = time.time() - start_time
        return NightlyReport(
            merge_accepted=merge_accepted,
            merge_reason=merge_reason,
            duration_seconds=max(0.001, duration),
            accepted_items=len(knowledge_queue),
            shadow_training_epochs=self.shadow_training_epochs,
            current_phase=self.current_phase
        )

    def get_status(self) -> dict:
        return {
            'cycle_count': self.cycle_count,
            'current_phase': self.current_phase
        }
