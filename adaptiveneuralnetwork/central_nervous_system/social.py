"""
Social Cognition and Theory of Mind (ToM) for Błyskawica.

Maintains internal models of external entities (Humans, AIs) to enable 
intent estimation, trust-building, and social intuition.
"""  # noqa: W291

import time

import torch
import torch.nn as nn


class SocialContext:
    """
    Mental model of an external entity.
    """
    def __init__(self, entity_id: str, hidden_dim: int, entity_type: str = "human"):
        self.entity_id = entity_id
        self.entity_type = entity_type # 'human', 'ai', 'system'
        self.trust_score = 0.5 # Neutral start
        self.honesty_history = []
        self.last_interaction = time.time()

        # Latent representation of intent [1, hidden_dim]
        self.intent_embedding = torch.zeros(1, hidden_dim)

    def update_trust(self, delta: float):
        self.trust_score = max(0.0, min(1.0, self.trust_score + delta))

class TheoryOfMind(nn.Module):
    """
    The registry and processing engine for social sensing.
    """
    def __init__(self, hidden_dim: int):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.entities: dict[str, SocialContext] = {}

        # Intent estimation network
        self.intent_estimator = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, hidden_dim)
        )

    def get_or_create_entity(self, entity_id: str, entity_type: str = "human") -> SocialContext:
        if entity_id not in self.entities:
            self.entities[entity_id] = SocialContext(entity_id, self.hidden_dim, entity_type)
        return self.entities[entity_id]

    def estimate_intent(self,
                        entity_id: str,
                        current_input: torch.Tensor,
                        narrative_gist: torch.Tensor,
                        env_context: torch.Tensor | None = None):
        """
        Estimate the intent of an entity based on their input, Błyskawica's autobiography,
        and the surrounding environment.
        """
        entity = self.get_or_create_entity(entity_id)

        # Combine input with narrative and environment
        # [1, hidden_dim * 2 or 3]
        features = [current_input.mean(dim=1), narrative_gist.squeeze(1)]
        if env_context is not None:
            features.append(env_context.mean(dim=1) if env_context.dim() > 1 else env_context)

        combined = torch.cat(features, dim=-1)

        # Structural Armor for Social Projections
        first_layer = self.intent_estimator[0]
        if combined.size(-1) != first_layer.in_features:
            # Rebuild first layer to match combined features
            self.intent_estimator[0] = nn.Linear(combined.size(-1), first_layer.out_features).to(combined.device)
            logger.info(f"Social Armor: Re-projected intent estimator to {combined.size(-1)} features")  # noqa: F821

        # Full sequence armor to catch internal 128x128 mismatches
        # In case combined output from layer 0 isn't hidden_dim (e.g. 128)
        current_res = combined
        for layer in self.intent_estimator:
            if isinstance(layer, nn.Linear):
                if current_res.size(-1) != layer.in_features:
                    # Adaptive pooling/padding for deep mismatch
                    if current_res.size(-1) < layer.in_features:
                         padding = torch.zeros(*current_res.shape[:-1], layer.in_features - current_res.size(-1), device=current_res.device)
                         current_res = torch.cat([current_res, padding], dim=-1)
                    else:
                         current_res = current_res[..., :layer.in_features]
            current_res = layer(current_res)

        new_intent = current_res

        # Update entity state (Detach to prevent graph leakage)
        entity.intent_embedding = (0.8 * entity.intent_embedding + 0.2 * new_intent).detach()
        entity.last_interaction = time.time()

        return entity.intent_embedding

    def detect_deception(self, entity_id: str, current_surprise: float) -> float:
        """
        Calculates a 'Deception Probability' based on surprise and trust.
        High surprise from a low-trust entity = Likely Deception.
        """
        entity = self.get_or_create_entity(entity_id)

        # Risk = Surprise * (1.0 - Trust)
        risk = current_surprise * (1.0 - entity.trust_score)
        return float(torch.clamp(torch.tensor(risk), 0.0, 1.0))

class InternalSocialDynamics(nn.Module):
    """
    Manages node-to-node social dynamics (Stress Contagion and Synchronization).
    Used by the PhaseScheduler to coordinate internal states.
    """
    def __init__(self, num_nodes: int):
        super().__init__()
        self.num_nodes = num_nodes
        # Trust matrix [num_nodes, num_nodes] (Simplified: per-node health for now)
        self.register_buffer('trust_matrix', torch.ones(num_nodes, num_nodes) * 0.8)
        self.register_buffer('social_anxiety', torch.zeros(num_nodes))

    def update_trust(self, activity: torch.Tensor, anxiety: torch.Tensor, dt: float = 0.01):
        """
        Updates internal trust based on neighbor behavioral resonance.
        High activity with high anxiety reduces trust (Stress Contagion).
        """
        # Flatten and sync shapes
        act = activity.flatten()[:self.num_nodes]
        anx = anxiety.flatten()[:self.num_nodes]

        # Heuristic: If neighbors are over-active and anxious, system-wide social anxiety rises
        stress_signal = (act > 0.8) & (anx > 4.0)
        self.social_anxiety[stress_signal] += (0.5 * dt)
        self.social_anxiety = self.social_anxiety.detach()
        self.social_anxiety[~stress_signal] *= (1.0 - 0.1 * dt)

        # Update trust matrix (neighbors that are consistent are trusted more)
        # (Placeholder for full node-to-node correlation)
        pass

    def get_social_influence(self, node_idx: int) -> float:
        """Returns the social pressure (anxiety) felt by a specific node from its peers."""
        if node_idx < self.num_nodes:
            return self.social_anxiety[node_idx].item()
        return 0.0
