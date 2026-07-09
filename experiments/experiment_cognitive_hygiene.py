import logging
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset

from adaptiveneuralnetwork.training.trainer import Trainer
from adaptiveneuralnetwork.training.callbacks import LoggingCallback, CognitiveHygieneCallback
from adaptiveneuralnetwork.central_nervous_system.phases import Phase, PhaseScheduler

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockBlyskawica(nn.Module):
    """Mock model with phase scheduler for hygiene testing."""
    def __init__(self, hidden_dim=128):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.fc = nn.Linear(hidden_dim, 10)
        self.phase_scheduler = PhaseScheduler(num_nodes=10, device="cpu")
    
    def forward(self, x):
        return self.fc(x)

def run_hygiene_experiment():
    print("\n=== STARTING COGNITIVE HYGIENE EXPERIMENT (THE WAKE-UP ROUTINE) ===")
    
    # 1. Setup Model and Trainer
    model = MockBlyskawica()
    optimizer = optim.Adam(model.parameters(), lr=0.01)
    criterion = nn.CrossEntropyLoss()
    
    # Add Hygiene Callback (shorter warm-up for demo)
    hygiene_cb = CognitiveHygieneCallback(warm_up_steps=100, device="cpu")
    
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        criterion=criterion,
        callbacks=[LoggingCallback(log_interval=20), hygiene_cb],
        progress_bar=False
    )
    
    # 2. Simulate Training with Phase Transitions
    print("\n[STEP 1] Starting training... Initial post-sleep warm-up should activate.")
    hygiene_cb.on_train_begin(trainer)
    
    # Dummy data
    X = torch.randn(2000, 128)
    y = torch.randint(0, 10, (2000,))
    loader = DataLoader(TensorDataset(X, y), batch_size=10)
    
    # Manually trigger a few batches to see LR warm-up
    trainer.model.train()
    for i, (data, target) in enumerate(loader):
        if i >= 150: break
        
        # Simulate phase transition mid-training
        if i == 50:
            print("\n[TRANSITION] Blyskawica is getting tired... Entering SLEEP phase.")
            # Set all nodes to SLEEP (1)
            model.phase_scheduler.node_phases.fill_(1)
            
        if i == 100:
            print("\n[TRANSITION] Pobudka! Waking up... Bedding was changed, initiating morning warm-up.")
            # Set all nodes to ACTIVE (0)
            model.phase_scheduler.node_phases.fill_(0)
            
        # Standard training step (simplified)
        output = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()
        
        # Manually call hygiene steps as we're not using fit() for fine-grained control
        # In fit(), the callback handles this automatically.
        hygiene_cb.on_batch_begin(i, trainer)
        
        # Log LR every 10 steps
        if i % 10 == 0 or i in [51, 101]:
            current_lr = optimizer.param_groups[0]['lr']
            phase_name = "SLEEP" if model.phase_scheduler.node_phases.float().mean().item() > 0.5 else "ACTIVE"
            print(f"Step {i:3d} | Phase: {phase_name} | LR: {current_lr:.6f}")

    print("\n=== COGNITIVE HYGIENE EXPERIMENT COMPLETE ===")

if __name__ == "__main__":
    run_hygiene_experiment()
