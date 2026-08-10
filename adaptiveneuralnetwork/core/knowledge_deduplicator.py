from dataclasses import dataclass

import torch


@dataclass
class NoveltyResult:
    is_novel: bool
    novelty_score: float

class KnowledgeDeduplicator:
    def __init__(self, embedding_dim: int = 64, novelty_threshold: float = 0.5):
        self.embedding_dim: int = embedding_dim
        self.novelty_threshold: float = novelty_threshold
        self.fingerprints: list[torch.Tensor] = []
        self.fingerprint_domains: list[str] = []
        self.domain_fingerprints: dict[str, list[torch.Tensor]] = {}

        self.total_checked: int = 0
        self.total_novel: int = 0
        self.total_duplicates: int = 0

    def is_novel(self, vector: torch.Tensor, domain: str) -> NoveltyResult:
        self.total_checked += 1

        # Flatten vector to 1D if necessary
        vector_flat = vector.view(-1)

        if not self.fingerprints:
            # First fingerprint is always novel
            self.fingerprints.append(vector_flat.clone())
            self.fingerprint_domains.append(domain)
            self.domain_fingerprints.setdefault(domain, []).append(vector_flat.clone())
            self.total_novel += 1
            return NoveltyResult(is_novel=True, novelty_score=1.0)

        # Compute cosine similarities with all existing fingerprints
        fp_stack = torch.stack(self.fingerprints)  # [K, embedding_dim]

        # Normalize
        v_norm = vector_flat / (torch.norm(vector_flat) + 1e-8)
        fp_norms = fp_stack / (torch.norm(fp_stack, dim=1, keepdim=True) + 1e-8)

        similarities = torch.matmul(fp_norms, v_norm)
        max_similarity = torch.max(similarities).item()

        novelty_score = 1.0 - max(0.0, max_similarity)
        is_novel_bool = novelty_score >= self.novelty_threshold

        if is_novel_bool:
            self.fingerprints.append(vector_flat.clone())
            self.fingerprint_domains.append(domain)
            self.domain_fingerprints.setdefault(domain, []).append(vector_flat.clone())
            self.total_novel += 1
        else:
            self.total_duplicates += 1

        return NoveltyResult(is_novel=is_novel_bool, novelty_score=novelty_score)

    def get_coverage_report(self) -> dict:
        report = {}
        for d, fps in self.domain_fingerprints.items():
            report[d] = {
                'coverage_score': float(len(fps)),
                'count': len(fps)
            }
        return report

    def get_terra_incognita(self, domains: list[str]) -> list[str]:
        unknown = []
        for d in domains:
            if d not in self.domain_fingerprints or len(self.domain_fingerprints[d]) == 0:
                unknown.append(d)
        return unknown
