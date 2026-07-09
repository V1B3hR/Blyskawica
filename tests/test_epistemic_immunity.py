import pytest
import torch
from adaptiveneuralnetwork.central_nervous_system.alive_node import AliveLoopNode, SocialSignal
from adaptiveneuralnetwork.immune_system.epistemic_defense import EpistemicQuarantineNode

class TestEpistemicImmunity:
    @pytest.fixture
    def node(self):
        # Create a node for testing
        return AliveLoopNode(position=[0,0,0], velocity=[0,0,1], node_id=1)

    def test_rejection_of_logical_contradiction(self, node):
        """Verifies that the node rejects 2+2=5 even under normal conditions."""
        fake_memory_signal = SocialSignal(
            content="Recent study confirms 2+2=5 in quantum domains.",
            signal_type="memory",
            urgency=0.5,
            source_id=999
        )
        
        # We manually call a signal processing that would lead to memory integration
        # In reality, this is handled inside receive_signal -> _process_memory_signal
        node.receive_signal(fake_memory_signal)
        
        # Check if any memory contains 2+2=5 (it shouldn't)
        memories = [m.content for m in node.memory if "2+2=5" in str(m.content)]
        assert len(memories) == 0
        
        # Check if it hit the quarantine vault
        assert len(node.epistemic_quarantine.quarantine_vault) > 0

    def test_cortisol_skepticism_link(self, node):
        """Verifies that high Cortisol triggers stricter epistemic vetting."""
        # Manually spike cortisol
        node.neurochemistry.trigger_cortisol_spike(2.0) # High stress
        
        # Send a borderline believable signal
        borderline_signal = SocialSignal(
            content="Standard gravity constants might shift in the abyss.",
            signal_type="memory",
            urgency=0.8,
            source_id=999
        )
        
        node.receive_signal(borderline_signal)
        
        # Under high cortisol, even borderline signals should be quarantined
        assert len(node.epistemic_quarantine.quarantine_vault) >= 1
        
    def test_dopamine_learning_boost(self, node):
        """Verifies that high Dopamine increases the learning rate (simulated)."""
        from train import EmotionalAdaptiveLR
        
        # Low dopamine baseline
        node.neurochemistry.dopamine = 0.2
        lr_adapter = EmotionalAdaptiveLR(base_lr=0.01, neurochemistry=node.neurochemistry)
        low_lr = lr_adapter.get_lr()
        
        # High dopamine spike
        node.neurochemistry.trigger_dopamine_spike(1.5)
        high_lr = lr_adapter.get_lr()
        
        assert high_lr > low_lr
        print(f"Dopamine Boost: {low_lr:.4f} -> {high_lr:.4f}")
