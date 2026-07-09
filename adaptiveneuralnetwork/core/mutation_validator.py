import copy
from enum import Enum
from dataclasses import dataclass
from typing import Callable, Optional

class MutationVerdict(Enum):
    ACCEPTED = "accepted"
    NEUTRAL = "neutral"
    REJECTED = "rejected"

@dataclass
class MutationRecord:
    verdict: MutationVerdict
    rollback_performed: bool
    pre_fitness: float
    post_fitness: float
    mutation_type: str

class MutationValidator:
    def __init__(self, initial_rate: float = 0.10, acceptance_threshold: float = 0.0, max_consecutive_rejects: int = 5):
        self.current_rate: float = initial_rate
        self.acceptance_threshold: float = acceptance_threshold
        self.max_consecutive_rejects: int = max_consecutive_rejects
        
        self.mutation_counter: int = 0
        self.consecutive_rejects: int = 0
        self.accepted_mutations: int = 0
        self.total_mutations: int = 0
        self.mutations_paused: bool = False

    def should_mutate(self) -> bool:
        return not self.mutations_paused

    def create_snapshot(self, model) -> dict:
        return copy.deepcopy(model.state_dict())

    def validate_mutation(self, model, pre_snapshot: dict, fitness_fn: Callable[[], float], mutation_type: str) -> MutationRecord:
        self.mutation_counter += 1
        self.total_mutations += 1
        
        # Take a snapshot of the mutated state so we can restore it if accepted
        mutated_snapshot = self.create_snapshot(model)
        
        # 1. Evaluate fitness post-mutation
        post_fitness = fitness_fn()
        
        # 2. Restore pre-mutation state and evaluate pre-mutation fitness
        model.load_state_dict(pre_snapshot)
        pre_fitness = fitness_fn()
        
        delta = post_fitness - pre_fitness
        
        if delta >= self.acceptance_threshold:
            # Accept the mutation: restore mutated weights
            model.load_state_dict(mutated_snapshot)
            verdict = MutationVerdict.ACCEPTED if delta > 0.0 else MutationVerdict.NEUTRAL
            rollback_performed = False
            self.consecutive_rejects = 0
            self.accepted_mutations += 1
            # Adaptive rate: increase rate on success
            self.current_rate = min(0.5, self.current_rate + 0.01)
        else:
            # Reject: keep the restored pre-mutation state
            verdict = MutationVerdict.REJECTED
            rollback_performed = True
            self.consecutive_rejects += 1
            # Adaptive rate: decrease rate on failure
            self.current_rate = max(0.01, self.current_rate - 0.02)
            if self.consecutive_rejects >= self.max_consecutive_rejects:
                self.mutations_paused = True
                
        return MutationRecord(
            verdict=verdict,
            rollback_performed=rollback_performed,
            pre_fitness=pre_fitness,
            post_fitness=post_fitness,
            mutation_type=mutation_type
        )

    def get_status_report(self) -> dict:
        acceptance_ratio = self.accepted_mutations / max(1, self.total_mutations)
        return {
            'current_mutation_rate': self.current_rate,
            'acceptance_ratio': acceptance_ratio,
            'mutation_counter': self.mutation_counter,
            'mutations_paused': self.mutations_paused,
        }
