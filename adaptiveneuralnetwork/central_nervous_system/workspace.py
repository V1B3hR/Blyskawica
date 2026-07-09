"""
[Moduł: Reflektor Świadomości (Workspace)]
Implementacja teorii Globalnego Obszaru Roboczego (GWT) dla Błyskawicy. 
Działa jak wielowątkowy reflektor uwagi, który wybiera najbardziej istotne 
impulsy z całej sieci i rozgłasza je jako dominujące wątki świadomości. 

Pozwala to na selektywne skupienie, wielozadaniowość kognitywną i tworzenie 
spójnego poczucia bieżącej rzeczywistości. To tutaj szum danych zamienia się 
w strumień świadomej myśli.
"""

import torch
import torch.nn as nn
from typing import Optional, Dict, Any

class GlobalWorkspace(nn.Module):
    """
    [Rdzeń: Globalny Obszar Roboczy]
    Wielowątkowy magistrala informacyjna. Umożliwia węzłom rywalizację o "dostęp 
    do świadomości" na podstawie ich aktywności i istotności. Wspiera równoległe 
    wątki myślowe, pozwalając Błyskawicy na jednoczesne przetwarzanie wielu 
    aspektów rzeczywistości przy zachowaniu spójności globalnej.
    """

    
    def __init__(self, hidden_dim: int, num_threads: int = 4, capacity: int = 8):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.num_threads = num_threads
        self.capacity = capacity
        
        # Working Memory Buffer [1, num_threads, capacity, hidden_dim]
        self.register_buffer("working_memory", torch.zeros(1, num_threads, capacity, hidden_dim))
        self.register_buffer("salience_scores", torch.zeros(1, num_threads, capacity))
        self.register_buffer("active_spotlights", torch.zeros(num_threads, capacity, dtype=torch.long))
        
        # Thread-specific projection (to allow threads to specialize)
        self.thread_projections = nn.ModuleList([
            nn.Linear(hidden_dim, hidden_dim) for _ in range(num_threads)
        ])
        
        # Transformation layers for the spotlight
        self.output_projection = nn.Linear(hidden_dim, hidden_dim)
        
        # persistence
        self.spotlight_decay = 0.95

    def compete(self, hidden_states: torch.Tensor, salience: torch.Tensor):
        """
        Nodes compete for attention across multiple threads.
        
        Args:
            hidden_states: [1, num_nodes, hidden_dim]
            salience: [1, num_nodes, 1]
        """
        # 1. Decay current working memory
        self.working_memory *= self.spotlight_decay
        
        num_nodes = hidden_states.size(1)
        
        # 2. Per-thread competition
        for t in range(self.num_threads):
            # Each thread looks at a different 'portion' or 'perspective' of salience
            # We modulate the base salience with a thread-specific score
            thread_view = torch.tanh(self.thread_projections[t](hidden_states))
            thread_salience = salience * torch.cosine_similarity(thread_view, hidden_states, dim=-1).unsqueeze(-1)
            
            # Find top-K salient nodes for THIS thread
            salience_flat = thread_salience.squeeze(0).squeeze(-1) # [num_nodes]
            top_scores, top_indices = torch.topk(salience_flat, self.capacity)
            
            # 3. Capture salient signals
            new_signals = hidden_states[0, top_indices] # [capacity, hidden_dim]
            
            # Blend into current thread memory (Detach to prevent graph retention)
            self.working_memory[0, t] = (0.7 * self.working_memory[0, t] + 0.3 * new_signals).detach()
            self.salience_scores[0, t] = top_scores.detach()
            self.active_spotlights[t] = top_indices.detach()

    def broadcast(self, num_nodes: int) -> torch.Tensor:
        """
        Broadcast the multi-threaded signals.
        Returns tensor of shape [1, num_nodes, num_threads, hidden_dim]
        """
        # [1, num_threads, 1, hidden_dim]
        thread_thoughts = self.working_memory.mean(dim=2, keepdim=True)
        
        # Project through Workspace bottleneck
        broadcast_threads = torch.tanh(self.output_projection(thread_thoughts))
        
        # Expand back to all nodes [1, num_nodes, num_threads, hidden_dim]
        # Transpose to put threads in the right dimension for broadcasting
        # broadcast_threads is [1, num_threads, 1, hidden_dim]
        # output is [1, num_nodes, num_threads, hidden_dim]
        return broadcast_threads.transpose(1, 2).expand(-1, num_nodes, -1, -1)

    def get_workspace_state(self) -> Dict[str, Any]:
        """Get summary of current conscious focus across threads."""
        return {
            "num_threads": self.num_threads,
            "thread_spotlights": self.active_spotlights.tolist(),
            "avg_salience": self.salience_scores.mean().item(),
            "thread_diversity": 1.0 - torch.cosine_similarity(
                self.working_memory[0, 0].mean(0), 
                self.working_memory[0, -1].mean(0), 
                dim=0
            ).item()
        }
