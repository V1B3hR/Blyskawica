import torch
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional

class DriftAlertLevel(Enum):
    STABLE = "stable"
    DRIFTING = "drifting"
    CRITICAL = "critical"

@dataclass
class DriftReport:
    alert_level: DriftAlertLevel
    drift_magnitude: float

class KnowledgeDriftDetector:
    def __init__(self, evaluation_interval: int = 10):
        self.baseline_accuracy: Optional[float] = None
        self.cycle_count: int = 0
        self.drift_history: List[DriftReport] = []
        self.evaluation_interval: int = evaluation_interval
        
        self._sentinel_inputs: Optional[torch.Tensor] = None
        self._sentinel_targets: Optional[torch.Tensor] = None
        self._sentinel_domains: Optional[List[str]] = None

    def register_sentinel_dataset(self, inputs: torch.Tensor, targets: torch.Tensor, domains: Optional[List[str]] = None):
        self._sentinel_inputs = inputs
        self._sentinel_targets = targets
        self._sentinel_domains = domains if domains is not None else ["default"] * len(inputs)

    def _evaluate_model(self, model) -> float:
        if self._sentinel_inputs is None or self._sentinel_targets is None:
            return 0.0
        model.eval()
        with torch.no_grad():
            outputs = model(self._sentinel_inputs)
            predictions = torch.argmax(outputs, dim=1)
            correct = (predictions == self._sentinel_targets).sum().item()
            accuracy = correct / len(self._sentinel_targets)
        return accuracy

    def establish_baseline(self, model) -> float:
        self.baseline_accuracy = self._evaluate_model(model)
        return self.baseline_accuracy

    def evaluate_drift(self, model) -> DriftReport:
        if self.baseline_accuracy is None:
            self.establish_baseline(model)
            
        current_accuracy = self._evaluate_model(model)
        drift_magnitude = float(abs(self.baseline_accuracy - current_accuracy))
        
        # We can cap drift_magnitude to be positive or keep raw difference.
        # If model gets worse, drift_magnitude > 0.
        if drift_magnitude > 0.15:
            alert_level = DriftAlertLevel.CRITICAL
        elif drift_magnitude > 0.05:
            alert_level = DriftAlertLevel.DRIFTING
        else:
            alert_level = DriftAlertLevel.STABLE
            
        report = DriftReport(alert_level=alert_level, drift_magnitude=drift_magnitude)
        self.drift_history.append(report)
        return report

    def step(self, model) -> Optional[DriftReport]:
        self.cycle_count += 1
        if self.cycle_count == 1 or self.cycle_count % self.evaluation_interval == 0:
            return self.evaluate_drift(model)
        return None

    def should_rollback(self) -> bool:
        if not self.drift_history:
            return False
        return self.drift_history[-1].alert_level == DriftAlertLevel.CRITICAL

    def get_status_report(self) -> dict:
        return {
            'cycle_count': self.cycle_count,
            'baseline_accuracy': self.baseline_accuracy,
            'sentinel_size': len(self._sentinel_inputs) if self._sentinel_inputs is not None else 0,
        }
