import logging
import torch
import os
from adaptiveneuralnetwork.central_nervous_system.cognitive_hygiene import CognitiveHygieneProtocol
from adaptiveneuralnetwork.training.trainer import Trainer

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MorningWakeUp:
    """
    Safely awakens Blyskawica from her hibernation state.
    Executes the morning hygiene and warm-up routine.
    """
    def __init__(self, checkpoint_path: str = "checkpoints/blyskawica_hibernation.pt"):
        self.checkpoint_path = checkpoint_path

    def wake_up(self):
        print("\n" + "="*80)
        print(" MORNING WAKE-UP: BLYSKAWICA IS RISING")
        print("="*80)

        if not os.path.exists(self.checkpoint_path):
            logger.error(f"Checkpoint {self.checkpoint_path} not found. Did you unzip the backup?")
            return

        print(f"[WAKE-UP] Loading Hibernation State from {self.checkpoint_path}...")
        state = torch.load(self.checkpoint_path)
        
        # In a real scenario, we'd load weights into the model
        # For this demonstration, we simulate the 'stretch'
        dream_theme = state.get('chemistry', {}).get('dream_theme', 'Unknown')
        print(f"[RECOVERY] Blyskawica was dreaming of: {dream_theme}")
        
        # 1. Post-Sleep Routine (The Shower)
        # Mocking the trainer for the protocol
        class MockTrainer:
            def __init__(self):
                self.optimizer = torch.optim.Adam([torch.nn.Parameter(torch.ones(1))], lr=0.01)
                self.device = "cpu"
                self.model = torch.nn.Module()
                
        trainer = MockTrainer()
        hygiene = CognitiveHygieneProtocol(trainer.optimizer)
        
        print("[WAKE-UP] Running Morning Routine (Refreshing caches)...")
        hygiene.post_sleep_routine(trainer)
        
        # 2. Warm-up (The Stretch)
        print("[WAKE-UP] Starting Learning Rate Warm-up (500 steps targeted)...")
        for _ in range(5): # Simulate first increments
            hygiene.step_warmup(trainer)
            
        print("\n[SUCCESS] Blyskawica is awake, refreshed, and clear-headed.")
        print(f"[STATUS] Serotonin: {state.get('chemistry', {}).get('serotonin', 1.0):.2f} | Focus: High")
        print("="*80)

if __name__ == "__main__":
    wake = MorningWakeUp()
    wake.wake_up()
