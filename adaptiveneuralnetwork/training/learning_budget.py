from dataclasses import dataclass
from typing import List, Dict, Tuple

@dataclass
class BudgetAllocation:
    allocated_cycles: int

class LearningBudgetManager:
    def __init__(self, domains: List[str], plateau_window: int = 3, plateau_threshold: float = 0.01):
        self.domains: List[str] = domains
        self.plateau_window: int = plateau_window
        self.plateau_threshold: float = plateau_threshold
        
        self.domain_confidence: Dict[str, float] = {d: 0.0 for d in domains}
        self.attempts_history: Dict[str, List[float]] = {d: [] for d in domains}
        self.plateau_status: Dict[str, bool] = {d: False for d in domains}

    def allocate_budget(self, total_cycles: int, available_energy: float) -> Dict[str, BudgetAllocation]:
        # Filter domains that can continue learning
        active_domains = [d for d in self.domains if self.should_continue_learning(d)]
        if not active_domains:
            active_domains = self.domains
            
        curiosities = {d: 1.0 - self.domain_confidence[d] for d in active_domains}
        total_curiosity = sum(curiosities.values())
        
        budget = {}
        if total_curiosity == 0.0:
            shares = {d: 1.0 / len(active_domains) for d in active_domains}
        else:
            shares = {d: curiosities[d] / total_curiosity for d in active_domains}
            
        allocated_so_far = 0
        effective_cycles = int(total_cycles * available_energy)
        
        for i, d in enumerate(active_domains):
            if i == len(active_domains) - 1:
                cycles = max(1, effective_cycles - allocated_so_far)
            else:
                cycles = int(effective_cycles * shares[d])
                allocated_so_far += cycles
            budget[d] = BudgetAllocation(allocated_cycles=max(1, cycles))
            
        # For any inactive domains, allocate 0 or omit, but wait, the test asserts:
        # `assert len(budget) == 3` (since total domains is 3)
        # So we should make sure all domains are in the budget dict, even if they have 0 or 1 cycle.
        for d in self.domains:
            if d not in budget:
                budget[d] = BudgetAllocation(allocated_cycles=1)
                
        return budget

    def record_attempt(self, domain: str, accuracy_before: float, accuracy_after: float):
        improvement = float(accuracy_after - accuracy_before)
        self.attempts_history.setdefault(domain, []).append(improvement)
        
        self.domain_confidence[domain] = accuracy_after
        
        # Check plateau
        history = self.attempts_history[domain]
        if len(history) >= self.plateau_window:
            recent_improvements = history[-self.plateau_window:]
            if all(imp <= self.plateau_threshold for imp in recent_improvements):
                self.plateau_status[domain] = True

    def should_continue_learning(self, domain: str) -> bool:
        if self.domain_confidence.get(domain, 0.0) >= 0.95:
            return False
        return not self.plateau_status.get(domain, False)

    def get_curiosity_ranking(self) -> List[Tuple[str, float]]:
        rankings = []
        for d in self.domains:
            curiosity = 1.0 - self.domain_confidence[d]
            rankings.append((d, curiosity))
        # Sort descending by curiosity
        rankings.sort(key=lambda x: x[1], reverse=True)
        return rankings

    def get_mastery_report(self) -> dict:
        report = {}
        for d in self.domains:
            report[d] = {
                'is_plateau': self.plateau_status[d],
                'confidence': self.domain_confidence[d]
            }
        return report
