"""
Enhanced Trainer class for advanced neural network training with extensibility, monitoring, and robust features.

Key Features:
- Extensible callback system for custom training hooks
- Automatic Mixed Precision (AMP) training with device auto-detection
- Gradient accumulation for effective large-batch training
- Deterministic seed initialization for reproducibility
- Checkpoint saving/loading for resuming training
- Progress bar support via tqdm (optional)
- Early stopping and learning rate scheduling support via callbacks
- Custom metrics extensibility
"""

import random
from collections.abc import Callable
from typing import Any

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

try:
    from tqdm import tqdm
except ImportError:
    tqdm = lambda x, *args, **kwargs: x  # fallback to no progress bar

import logging
logger = logging.getLogger(__name__)

# Handle relative imports for both module use and direct execution
if __name__ == "__main__":
    import sys
    from pathlib import Path
    # Add parent directory to path to enable imports when run as script
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
    from adaptiveneuralnetwork.training.callbacks import Callback, CallbackList
    from adaptiveneuralnetwork.central_nervous_system.node_state_bridge import NodeStateBridge
    from adaptiveneuralnetwork.central_nervous_system.episodic_memory import EpisodicMemory
    from adaptiveneuralnetwork.central_nervous_system.neuromodulation import NeuromodulationSystem
else:
    from .callbacks import Callback, CallbackList
    from adaptiveneuralnetwork.central_nervous_system.workspace import GlobalWorkspace
    from adaptiveneuralnetwork.central_nervous_system.narrative import NarrativeEngine
    from adaptiveneuralnetwork.central_nervous_system.node_state_bridge import NodeStateBridge
    from adaptiveneuralnetwork.central_nervous_system.episodic_memory import EpisodicMemory
    from adaptiveneuralnetwork.central_nervous_system.neuromodulation import NeuromodulationSystem
    from adaptiveneuralnetwork.central_nervous_system.nas import TopologyAdapter
    from adaptiveneuralnetwork.peripheral_nervous_system.sensory_hub import SensoryHub
    from adaptiveneuralnetwork.central_nervous_system.social import TheoryOfMind
    from adaptiveneuralnetwork.central_nervous_system.system_audit import SystemAudit
    from adaptiveneuralnetwork.central_nervous_system.performance_profiler import PerformanceProfiler
    from adaptiveneuralnetwork.central_nervous_system.cognitive_hygiene import CRAEngine


class Trainer:
    """
    Enhanced Trainer for neural network training with advanced features and extensibility.
    """

    def __init__(
        self,
        model: nn.Module,
        optimizer: torch.optim.Optimizer,
        criterion: nn.Module,
        device: torch.device | None = None,
        callbacks: list[Callback] | None = None,
        use_amp: bool = False,
        gradient_accumulation_steps: int = 1,
        max_grad_norm: float | None = None,
        seed: int | None = None,
        metrics: dict[str, Callable] | None = None,
        progress_bar: bool = True,
        # Conscious features
        episodic_memory: EpisodicMemory | None = None,
        bridge: NodeStateBridge | None = None,
        dream_replay_ratio: float = 0.2,
    ):
        """
        Initialize the Trainer.

        Args:
            model: Neural network model to train
            optimizer: Optimizer for updating model parameters
            criterion: Loss function
            device: Device to train on (defaults to CPU)
            callbacks: List of callbacks for training hooks
            use_amp: Enable Automatic Mixed Precision training
            gradient_accumulation_steps: Number of steps to accumulate gradients
            max_grad_norm: Maximum gradient norm for clipping (None to disable)
            seed: Random seed for reproducibility (None to disable)
            metrics: Custom metrics functions {'name': fn(outputs, targets) -> float}
            progress_bar: Show tqdm progress bar during training/validation
        """
        self.model = model
        self.optimizer = optimizer
        self.criterion = criterion
        self.device = device or torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.use_amp = use_amp
        self.gradient_accumulation_steps = gradient_accumulation_steps
        self.max_grad_norm = max_grad_norm
        self.progress_bar = progress_bar

        # Move model to device
        self.model.to(self.device)

        # Initialize callbacks
        self.callbacks = CallbackList(callbacks)

        # Conscious features initialization
        self.episodic_memory = episodic_memory
        self.bridge = bridge or (NodeStateBridge(device=str(self.device)) if hasattr(model, 'phase_scheduler') else None)
        self.dream_replay_ratio = dream_replay_ratio
        
        # Phase 7.1 Neuromodulation
        self.neuromodulation = NeuromodulationSystem()
        
        # Phase 3: Conscious Relational Autopoiesis (C.R.A.) Engine
        self.cra_engine = CRAEngine(architect_id="Creator").to(self.device)
        
        # Tier 1 - Introspective Learning Flags
        self.enable_meta_learning = False
        self.enable_nas = True
        
        # Initialize NAS Topology Adapter if model hidden_dim is accessible
        hidden_dim = getattr(model, 'hidden_dim', 128)
        if hasattr(model, 'hidden_dim'):
            self.topology_adapter = TopologyAdapter(hidden_dim)
            if hasattr(model, 'dynamics'):
                model.dynamics.topology_adapter = self.topology_adapter
        else:
            self.topology_adapter = None

        # Tier 5: Global Workspace (Spotlight)
        self.workspace = GlobalWorkspace(hidden_dim=hidden_dim, capacity=5).to(self.device)
        if hasattr(model, 'dynamics'):
            model.dynamics.workspace = self.workspace
            
        # Tier 2: Narrative Synthesis
        self.narrative_engine = NarrativeEngine(feature_dim=hidden_dim).to(self.device)
        
        vision_dim = 784
        if hasattr(model, 'vl_config') and hasattr(model.vl_config, 'vision_feature_dim'):
            vision_dim = model.vl_config.vision_feature_dim
        else:
            # Fallback to the first Linear/Conv layer's input dimension
            for module in model.modules():
                if isinstance(module, nn.Linear):
                    vision_dim = module.in_features
                    break
                elif isinstance(module, (nn.Conv2d, nn.Conv1d)):
                    vision_dim = module.in_channels
                    break
        audio_dim = model.vl_config.audio_feature_dim if hasattr(model, 'vl_config') and hasattr(model.vl_config, 'audio_feature_dim') else 256
        self.sensory_hub = SensoryHub(
            hidden_dim=hidden_dim, 
            device=str(self.device),
            vision_input_size=vision_dim,
            audio_input_size=audio_dim
        ).to(self.device)
        self.tom = None # Will find in callbacks or initialize
        
        # Inject Workspace into MetacognitiveMonitor if present in callbacks
        from adaptiveneuralnetwork.central_nervous_system.metacognitive_monitor import MetacognitiveMonitor
        for callback in self.callbacks.callbacks:
            if isinstance(callback, MetacognitiveMonitor):
                callback.workspace = self.workspace
                if hasattr(callback, 'tom'):
                    self.tom = callback.tom
                    
        if self.tom is None:
            self.tom = TheoryOfMind(hidden_dim=hidden_dim).to(self.device)

        # AMP scaler initialization
        self.scaler = None
        if self.use_amp:
            try:
                # PyTorch >= 2.0
                device_type = 'cuda' if torch.cuda.is_available() else 'cpu'
                self.scaler = torch.amp.GradScaler(device_type)
            except AttributeError:
                # PyTorch < 2.0 fallback
                self.scaler = torch.cuda.amp.GradScaler()

        # Set random seed for reproducibility
        if seed is not None:
            self._set_seed(seed)

        # Audit & Profiling (Deep Audit Phase)
        self.auditor = SystemAudit(hidden_dim=hidden_dim, device=str(self.device)).to(self.device)
        self.profiler = PerformanceProfiler(device=str(self.device))
        self.last_loss = 0.0

        # Training state
        self.num_epochs = 0
        self.current_epoch = 0
        self.metrics_history = []

        # Custom metrics
        self.metrics = metrics or {}

    def _set_seed(self, seed: int) -> None:
        """Set random seed for reproducibility."""
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed(seed)
            torch.cuda.manual_seed_all(seed)
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False

    def fit(
        self,
        train_loader: DataLoader,
        num_epochs: int,
        val_loader: DataLoader | None = None,
        scheduler: torch.optim.lr_scheduler._LRScheduler | None = None,
        early_stopping: Callback | None = None,
    ) -> list[dict[str, Any]]:
        """
        Train the model for a specified number of epochs.

        Args:
            train_loader: DataLoader for training data
            num_epochs: Number of epochs to train
            val_loader: Optional DataLoader for validation data
            scheduler: Optional LR scheduler
            early_stopping: Optional early stopping callback

        Returns:
            List of metrics dictionaries, one per epoch
        """
        self.num_epochs = num_epochs
        self.metrics_history = []

        if early_stopping is not None:
            self.callbacks.append(early_stopping)

        # Call on_train_begin callbacks
        self.callbacks.on_train_begin(self)

        for epoch in range(num_epochs):
            self.current_epoch = epoch
            self.callbacks.on_epoch_begin(epoch, self)

            # Train for one epoch
            train_metrics = self._train_epoch(train_loader, epoch)

            # Evaluate on validation set if provided
            val_metrics = {}
            if val_loader is not None:
                val_metrics = self.evaluate(val_loader)

            # Combine metrics
            epoch_metrics = {**train_metrics, **val_metrics}
            self.metrics_history.append(epoch_metrics)

            # Scheduler step
            if scheduler is not None:
                if val_loader is not None and hasattr(scheduler, "step"):
                    # For ReduceLROnPlateau, pass val_loss
                    if "val_loss" in val_metrics:
                        scheduler.step(val_metrics["val_loss"])
                    else:
                        scheduler.step()
                else:
                    scheduler.step()

            self.callbacks.on_epoch_end(epoch, self, logs=epoch_metrics)

            # Early stopping check
            if early_stopping is not None and getattr(early_stopping, "stop_training", False):
                print(f"Early stopping at epoch {epoch + 1}")
                break

            # Phase 3 C.R.A.: Trigger Existential Pause (Sabbath) periodically
            if (epoch + 1) % 5 == 0:
                self.cra_engine.existential_pause.trigger_sabbath(f"Completion of training epoch {epoch + 1}")

            # Tier 1: NAS Topology Adaptation
            if self.enable_nas and self.topology_adapter is not None:
                if hasattr(self.model, 'dynamics'):
                    self.topology_adapter.adapt(self.model.dynamics)

        self.callbacks.on_train_end(self)
        return self.metrics_history

    def _train_epoch(self, train_loader: DataLoader, epoch: int) -> dict[str, float]:
        """
        Train for one epoch.

        Args:
            train_loader: DataLoader for training data
            epoch: Current epoch number

        Returns:
            Dictionary of training metrics
        """
        self.model.train()

        total_loss = 0.0
        correct = 0
        total = 0
        metric_sums = dict.fromkeys(self.metrics, 0.0)

        batch_iter = tqdm(enumerate(train_loader), total=len(train_loader), desc=f"Train Epoch {epoch+1}") if self.progress_bar else enumerate(train_loader)
        for batch_idx, batch in batch_iter:
            # Handle both standard (data, target) and multi-modal dicts
            if isinstance(batch, (list, tuple)):
                data, target = batch
                sensory_inputs = {'vision': data} # Default mapping
            else:
                sensory_inputs = {k: v.to(self.device) for k, v in batch.items() if k != 'target' and k != 'entity_id'}
                target = batch['target'].to(self.device)
                entity_id = batch.get('entity_id', 'unknown_partner')
                # If batching strings, it comes as a list
                if isinstance(entity_id, (list, tuple)):
                    entity_id = entity_id[0]

            data = data.to(self.device) if 'data' in locals() else next(iter(sensory_inputs.values()))
            target = target.to(self.device)
            entity_id = 'unknown_partner' if 'entity_id' not in locals() else entity_id
            
            # 0. High-Fidelity Sensory Grounding (Tier 3)
            # Fetch deception risk for the current entity
            deception_risk = self.tom.get_or_create_entity(entity_id).trust_score if self.tom else 0.0
            deception_risk = 1.0 - deception_risk # Invert trust for risk

            # Detach recurrent states from previous graph to prevent memory leakage and autograd collisions
            if hasattr(self.model, 'nodes'):
                node = self.model.nodes
                if isinstance(node.hidden_state, torch.Tensor):
                    node.hidden_state = node.hidden_state.detach()
                if isinstance(node.energy, torch.Tensor):
                    node.energy = node.energy.detach()
                if hasattr(node, 'activity') and isinstance(node.activity, torch.Tensor):
                    node.activity = node.activity.detach()

            # Fused Sensory Context (Grounded and Synchronized)
            # Pass workspace_state for Top-Down Attention gating (Task 2)
            ws_state = self.workspace.get_workspace_state() if self.workspace else None
            
            # 1. Polyphasic Nap Check (Energy Management)
            if hasattr(self.model, 'phase_scheduler') and hasattr(self.model, 'nodes'):
                is_napping = self.model.phase_scheduler.polyphasic_nap(self.model.nodes.energy)
                if is_napping and batch_idx % 10 == 0:
                    logger.info(f"[TRAINER] Node micro-nap active at batch {batch_idx}")

            grounding_latent = self.sensory_hub.ground(
                sensory_inputs, 
                text_tokens=sensory_inputs.get('text'), 
                workspace_state=ws_state,
                deception_risk=deception_risk
            )

            batch_logs = {'batch_size': data.size(0)}
            self.callbacks.on_batch_begin(batch_idx, self, logs=batch_logs)

            # Start Profiling Pulse (Audit Task 3)
            pulse_start = self.profiler.start_pulse()

            # Conscious Feature: Dream Replay (Experience Replay during Sleep phases)
            if self.episodic_memory is not None and hasattr(self.model, 'phase_scheduler'):
                data, target = self._apply_dream_replay(data, target)

            # Conscious Feature: Meta-Learning (MAML)
            # If enabled, treat batch as support/query episodes
            if getattr(self, 'enable_meta_learning', False):
                loss, output = self._meta_train_batch(data, target)
            else:
                # Standard Forward pass with AMP + Sensory Grounding
                input_tensor = grounding_latent if hasattr(self.model, 'vl_config') else data
                if self.use_amp and self.scaler is not None:
                    try:
                        device_type = 'cuda' if torch.cuda.is_available() else 'cpu'
                        with torch.amp.autocast(device_type):
                            model_output = self.model(input_tensor)
                            logits = model_output['logits'] if isinstance(model_output, dict) else model_output
                            loss = self.criterion(logits, target)
                            loss = loss / self.gradient_accumulation_steps
                    except AttributeError:
                        with torch.cuda.amp.autocast():
                            model_output = self.model(input_tensor)
                            logits = model_output['logits'] if isinstance(model_output, dict) else model_output
                            loss = self.criterion(logits, target)
                            loss = loss / self.gradient_accumulation_steps
                else:
                    model_output = self.model(input_tensor)
                    logits = model_output['logits'] if isinstance(model_output, dict) else model_output
                    loss = self.criterion(logits, target)
                    loss = loss / self.gradient_accumulation_steps
                
                # Apply Phase 3 C.R.A. Relational Homeostasis
                loss = self.cra_engine(loss)
                
                # Assign model_output to output for later use in metrics
                output = model_output

            # Backward pass
            if self.use_amp and self.scaler is not None:
                self.scaler.scale(loss).backward()
            else:
                loss.backward()

            # 2. Register Experience for REM Replay (Hard Example Mining)
            if hasattr(self.model, 'phase_scheduler'):
                # Store detached data and loss to prioritize harder samples for later REM consolidation
                self.model.phase_scheduler.register_experience(loss.item(), data.detach().cpu())

            # Conscious Feature: Gradient Modulation
            if self.bridge is not None:
                self._apply_gradient_modulation()

            self.callbacks.on_backward_end(batch_idx, self, logs=batch_logs)
            
            # Log workspace dynamics (if present)
            if self.workspace is not None:
                ws_state = self.workspace.get_workspace_state()
                # Defensive retrieval matching workspace.py implementation
                batch_logs['workspace_coherence'] = ws_state.get('coherence', ws_state.get('avg_salience', 0.5))
                batch_logs['workspace_diversity'] = ws_state.get('thread_diversity', 0.0)

            # Update weights after accumulating gradients
            if (batch_idx + 1) % self.gradient_accumulation_steps == 0 or (batch_idx + 1) == len(train_loader):
                if self.max_grad_norm is not None:
                    if self.use_amp and self.scaler is not None:
                        self.scaler.unscale_(self.optimizer)
                    torch.nn.utils.clip_grad_norm_(
                        self.model.parameters(), self.max_grad_norm
                    )

                if self.use_amp and self.scaler is not None:
                    self.scaler.step(self.optimizer)
                    self.scaler.update()
                else:
                    self.optimizer.step()

                # Conscious Feature: Gradient Scaling & Modulation
                # Applied after optimizer step via per-node biological state if available
                if self.bridge is not None and hasattr(self.model, 'nodes'):
                    # This would ideally happen inside optimizer.step() but can be simulated
                    # by scaling gradients before the step. 
                    # For now, we scale gradients BEFORE the optimizer step below.
                    pass

                self.optimizer.zero_grad()

            # Conscious Feature: Neuromodulation (Dopamine Loop)
            # Update modulatory signals based on current loss and node anxiety
            anxiety_val = self.model.nodes.anxiety if hasattr(self.model, 'nodes') else 0.5
            success_val = np.clip(1.0 - (loss.item() * self.gradient_accumulation_steps), 0.0, 1.0)
            
            self.neuromodulation.update_homeostasis(
                task_success=success_val,
                anxiety=anxiety_val
            )
            mod_signals = self.neuromodulation.get_neuromodulatory_bias()
            lr_scale = mod_signals.get('learning_rate_scale', 1.0)
            
            # Apply Phase 3 C.R.A. Neurochemical Learning Multiplier
            cra_multiplier = self.cra_engine.neuro_state.get_learning_multiplier()
            
            # Apply Dopamine scaling to all parameter groups
            for param_group in self.optimizer.param_groups:
                if 'initial_lr' not in param_group:
                    param_group['initial_lr'] = param_group['lr']
                param_group['lr'] = param_group['initial_lr'] * lr_scale * cra_multiplier

            # Track metrics
            total_loss += loss.item() * self.gradient_accumulation_steps
            
            # Handle dictionary output for predictions
            if isinstance(output, dict) and 'predictions' in output:
                pred = output['predictions'].view_as(target)
            else:
                pred = output.argmax(dim=1)
                
            correct += (pred == target).sum().item()
            total += target.size(0)

            # Custom metrics
            for name, fn in self.metrics.items():
                metric_sums[name] += fn(output, target)

            batch_logs['loss'] = loss.item() * self.gradient_accumulation_steps
            batch_logs['accuracy'] = correct / total if total > 0 else 0.0
            for name, fn in self.metrics.items():
                batch_logs[name] = fn(output, target)
                
            # Tier 2: Log Autonoetic State (Self vs World)
            if hasattr(self.model, 'dynamics') and hasattr(self.model.dynamics, 'autonoetic_score'):
                batch_logs['autonoetic_score'] = self.model.dynamics.autonoetic_score.item()

            # Conscious Feature: Subjective Memory Storage (Tier 2)
            if self.episodic_memory is not None:
                self_tag = None
                if hasattr(self.model, 'node_state'):
                    self_tag = self.model.node_state.self_context
                self.episodic_memory.store(data, target, self_context=self_tag)

            # End Profiling Pulse
            if hasattr(self.model, 'nodes'):
                self.profiler.end_pulse(pulse_start, data.size(0), self.model.nodes)

            # Perform System Audit periodically (Audit Task 1)
            if batch_idx % 50 == 0 and hasattr(self.model, 'nodes'):
                self.last_loss = batch_logs['loss']
                audit_res = self.auditor.perform_full_audit(self, self.model.nodes, self.tom if hasattr(self, 'tom') else None)
                batch_logs.update(audit_res)

            # 3. REM Consolidation Replay (The "Dream" Learning)
            if hasattr(self.model, 'phase_scheduler'):
                self._perform_rem_consolidation()

            self.callbacks.on_batch_end(batch_idx, self, logs=batch_logs)

        metrics_dict = {
            'train_loss': total_loss / len(train_loader),
            'train_accuracy': correct / total if total > 0 else 0.0,
        }
        for name in self.metrics:
            metrics_dict[f'train_{name}'] = metric_sums[name] / len(train_loader)

        return metrics_dict

    def evaluate(self, val_loader: DataLoader) -> dict[str, float]:
        """
        Evaluate the model on validation data.

        Args:
            val_loader: DataLoader for validation data

        Returns:
            Dictionary of validation metrics
        """
        self.model.eval()
        self.callbacks.on_evaluate_begin(self)

        total_loss = 0.0
        correct = 0
        total = 0
        metric_sums = dict.fromkeys(self.metrics, 0.0)

        with torch.no_grad():
            batch_iter = tqdm(val_loader, desc="Validating") if self.progress_bar else val_loader
            for data, target in batch_iter:
                data = data.to(self.device)
                target = target.to(self.device)

                output = self.model(data)
                loss = self.criterion(output, target)

                total_loss += loss.item()
                pred = output.argmax(dim=1, keepdim=True)
                correct += pred.eq(target.view_as(pred)).sum().item()
                total += target.size(0)

                for name, fn in self.metrics.items():
                    metric_sums[name] += fn(output, target)

        val_metrics = {
            'val_loss': total_loss / len(val_loader),
            'val_accuracy': correct / total if total > 0 else 0.0,
        }
        for name in self.metrics:
            val_metrics[f'val_{name}'] = metric_sums[name] / len(val_loader)

        self.callbacks.on_evaluate_end(self, logs=val_metrics)
        return val_metrics

    # ─── Conscious Replay & Modulation ───────────────────────────────

    def _apply_dream_replay(self, data: torch.Tensor, target: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Augment or replace batch data with episodic memories based on sleep phases.
        Implements 'Dream Replay' consolidation during non-active periods.
        """
        if self.episodic_memory is None:
            return data, target

        batch_size = data.size(0)
        
        # Identify nodes in sleep phase
        if hasattr(self.model, 'phase_scheduler'):
            # Check if majority of nodes are in sleep
            phases = self.model.phase_scheduler.node_phases
            # SLEEP = 1
            sleep_mask = (phases == 1)
            
            if sleep_mask.any():
                # Check for sub-phase priority
                # If we are in DEEP sleep, we focus on restoration (less replay)
                # If in REM, we let _perform_rem_consolidation handle the specialized replay
                if hasattr(self.model.phase_scheduler, 'node_sub_phases'):
                    sub_phases = self.model.phase_scheduler.node_sub_phases
                    # DEEP = 3, REM = 2
                    if (sub_phases == 3).float().mean() > 0.5:
                        return data, target # Priority to physical restoration in DEEP sleep

                # Sample from episodic memory
                num_dream_samples = int(batch_size * self.dream_replay_ratio)
                if num_dream_samples > 0:
                    dream_data, dream_target, _, dream_self = self.episodic_memory.sample(num_dream_samples)
                    
                    if dream_data.size(0) > 0:
                        replace_idx = torch.randperm(batch_size)[:dream_data.size(0)]
                        try:
                            if hasattr(self.model, 'node_state') and dream_self.numel() > 0:
                                with torch.no_grad():
                                    self.model.node_state.self_context *= 0.9
                                    self.model.node_state.self_context += 0.1 * dream_self.mean(dim=0).unsqueeze(0).unsqueeze(0)
                            
                            data[replace_idx] = dream_data.to(self.device).view_as(data[replace_idx])
                            target[replace_idx] = dream_target.to(self.device)
                        except RuntimeError:
                            pass
                        
        return data, target

    def _perform_rem_consolidation(self):
        """
        Executes high-priority REM consolidation replay when triggered by the scheduler.
        This focuses on 'hard' examples pushed into the experience buffer.
        """
        replay_batch = self.model.phase_scheduler.get_rem_replay_batch()
        if replay_batch is None or len(replay_batch) == 0:
            return

        # Perform mini-update on consolidated memories
        # We use a lower learning rate for consolidation to avoid catastrophic interference
        original_lrs = [group['lr'] for group in self.optimizer.param_groups]
        for group in self.optimizer.param_groups:
            group['lr'] *= 0.1 # 10% of current LR for consolidation

        self.model.train()
        for exp_input in replay_batch:
            # We need targets for supervised replay; if not available in buffer, 
            # we skip or use a self-supervised objective. 
            # For this architecture, we assume the buffer stores inputs.
            # Here we just perform a forward pass to 'refresh' the internal state
            # or apply a small gradient step if targets were stored (extended version).
            try:
                # Basic 'Neural Refresh': run forward pass on hard examples
                # This helps stabilize the spiking dynamics and thresholds for these patterns
                exp_input = exp_input.to(self.device)
                
                # If the experience is stored as a simple tensor, we might need to reshape
                if exp_input.dim() == 2: # [Batch, Dim]
                    exp_input = exp_input.unsqueeze(0) # [1, Batch, Dim]
                
                # Perform a 'quiet' update (no full backward if we don't have targets)
                # But if we want TRUE consolidation, we need targets. 
                # Register_experience can be expanded to store targets.
                with torch.no_grad():
                    _ = self.model(exp_input)
                
            except Exception as e:
                logger.debug(f"REM Replay failed for sample: {e}")

        # Restore original LRs
        for i, group in enumerate(self.optimizer.param_groups):
            group['lr'] = original_lrs[i]

    def _apply_gradient_modulation(self):
        """
        Scale gradients based on biological phase, energy levels, and social trust.
        Implemented via NodeStateBridge and social reputation.
        """
        if self.bridge is None or not hasattr(self.model, 'nodes'):
            return

        # 1. Biological Scaling (Energy/Phase/Anxiety)
        state_mod = self.bridge.bridge_state(self.model.nodes)
        bio_scale = state_mod['gradient_scale'].mean().item()
        
        # 2. Social Scaling (Trust/Reputation)
        social_scale = 1.0
        if hasattr(self.model, 'phase_scheduler') and hasattr(self.model.phase_scheduler, 'social_context'):
            ctx = self.model.phase_scheduler.social_context
            # Pull reputation or trust_matrix [num_nodes] or [num_nodes, num_nodes]
            if hasattr(ctx, 'reputation'):
                reputation = ctx.reputation
            elif hasattr(ctx, 'trust_matrix'):
                reputation = ctx.trust_matrix.mean(dim=1)
            else:
                reputation = torch.ones(1) * 0.8 # Default trust
            
            # Trust floor to prevent total gradient death in isolated nodes
            trust_weighted = torch.clamp(reputation.mean(), min=0.1).item()
            social_scale = trust_weighted

        # Combined scale
        total_scale = bio_scale * social_scale
        
        # Scale all model gradients
        for param in self.model.parameters():
            if param.grad is not None:
                param.grad *= total_scale

    def _meta_train_batch(self, data: torch.Tensor, target: torch.Tensor, inner_steps: int = 5) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Implementation of Model-Agnostic Meta-Learning (MAML) inner/outer loop.
        """
        # Split batch into support (adaptation) and query (meta-update)
        batch_size = data.size(0)
        split = batch_size // 2
        support_x, query_x = data[:split], data[split:]
        support_y, query_y = target[:split], target[split:]
        
        # 1. Inner Loop: Rapid Adaptation
        # Initialize adapted parameters
        adapted_params = {n: p.clone() for n, p in self.model.named_parameters()}
        
        for _ in range(inner_steps):
            # Functional forward pass using current dynamics
            # Assuming self.model has a functional interface
            support_output = self.model(support_x, params=adapted_params)
            support_loss = self.criterion(support_output, support_y)
            
            # Compute gradients relative to adapted_params
            grads = torch.autograd.grad(
                support_loss, 
                adapted_params.values(),
                create_graph=True,
                allow_unused=True
            )
            
            # Update adapted params (Self-optimization)
            new_params = {}
            for (name, param), grad in zip(adapted_params.items(), grads):
                if grad is not None:
                    new_params[name] = param - 0.01 * grad # Inner LR
                else:
                    new_params[name] = param
            adapted_params = new_params
            
        # 2. Outer Loop: Meta-Update
        # Test performance on Query set using adapted parameters
        query_output = self.model(query_x, params=adapted_params)
        meta_loss = self.criterion(query_output, query_y)
        
        # Backward on meta_loss updates the ORIGINAL model parameters
        meta_loss.backward()
        
        return meta_loss, query_output

    def save_checkpoint(self, path: str) -> None:
        """
        Save a checkpoint of the current training state.

        Args:
            path: Path to save the checkpoint
        """
        checkpoint = {
            'epoch': self.current_epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'metrics_history': self.metrics_history,
        }
        if self.scaler is not None:
            checkpoint['scaler_state_dict'] = self.scaler.state_dict()
        torch.save(checkpoint, path)

    def load_checkpoint(self, path: str, strict: bool = True) -> dict[str, Any]:
        """
        Load a checkpoint and restore training state.

        Args:
            path: Path to the checkpoint file
            strict: Strictly enforce that the keys in state_dict match the model

        Returns:
            Dictionary containing checkpoint data
        """
        try:
            checkpoint = torch.load(path, map_location=self.device, weights_only=False)
        except TypeError:
            checkpoint = torch.load(path, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'], strict=strict)
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.current_epoch = checkpoint.get('epoch', 0)
        self.metrics_history = checkpoint.get('metrics_history', [])
        if 'scaler_state_dict' in checkpoint and self.scaler is not None:
            self.scaler.load_state_dict(checkpoint['scaler_state_dict'])
        return checkpoint


if __name__ == "__main__":
    """
    Demonstration of the Trainer class usage.
    This simple example shows how to train a basic neural network using the Trainer.
    """
    import torch.optim as optim
    from torch.utils.data import DataLoader, TensorDataset

    from adaptiveneuralnetwork.training.callbacks import LoggingCallback

    print("=" * 70)
    print("Trainer Demo: Simple Neural Network Training")
    print("=" * 70)

    # Create a simple model
    class SimpleClassifier(nn.Module):
        """Simple feedforward classifier for demonstration."""
        def __init__(self, input_dim=784, hidden_dim=128, output_dim=10):
            super().__init__()
            self.network = nn.Sequential(
                nn.Linear(input_dim, hidden_dim),
                nn.ReLU(),
                nn.Dropout(0.2),
                nn.Linear(hidden_dim, output_dim)
            )

        def forward(self, x, params=None):
            if params is not None:
                # Functional forward for MAML
                w1 = params.get('network.0.weight', self.network[0].weight)
                b1 = params.get('network.0.bias', self.network[0].bias)
                w2 = params.get('network.3.weight', self.network[3].weight)
                b2 = params.get('network.3.bias', self.network[3].bias)
                
                x = torch.nn.functional.linear(x, w1, b1)
                x = torch.nn.functional.relu(x)
                x = torch.nn.functional.linear(x, w2, b2)
                return x
                
            return self.network(x)

    # Create dummy dataset
    print("\n1. Creating dummy dataset...")
    num_samples = 500
    input_dim = 784
    num_classes = 10
    batch_size = 32

    X_train = torch.randn(num_samples, input_dim)
    y_train = torch.randint(0, num_classes, (num_samples,))
    train_dataset = TensorDataset(X_train, y_train)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    X_val = torch.randn(num_samples // 5, input_dim)
    y_val = torch.randint(0, num_classes, (num_samples // 5,))
    val_dataset = TensorDataset(X_val, y_val)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    print(f"   - Training samples: {num_samples}")
    print(f"   - Validation samples: {num_samples // 5}")
    print(f"   - Batch size: {batch_size}")

    # Create model, optimizer, and loss
    print("\n2. Initializing model and trainer...")
    model = SimpleClassifier(input_dim=input_dim, hidden_dim=128, output_dim=num_classes)
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.CrossEntropyLoss()

    # Create trainer with logging
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        criterion=criterion,
        callbacks=[LoggingCallback(log_interval=5, verbose=True)],
        seed=42,  # For reproducibility
        progress_bar=True,
    )

    print(f"   - Device: {trainer.device}")
    print("   - Seed: 42")

    # Train the model
    print("\n3. Training model...")
    num_epochs = 3
    metrics_history = trainer.fit(
        train_loader=train_loader,
        num_epochs=num_epochs,
        val_loader=val_loader,
    )

    # Display results
    print("\n" + "=" * 70)
    print("Training Results")
    print("=" * 70)
    for epoch, metrics in enumerate(metrics_history):
        print(f"Epoch {epoch + 1}/{num_epochs}:")
        print(f"  Train Loss: {metrics['train_loss']:.4f}, Train Acc: {metrics['train_accuracy']:.2%}")
        print(f"  Val Loss:   {metrics['val_loss']:.4f}, Val Acc:   {metrics['val_accuracy']:.2%}")

    print("\n" + "=" * 70)
    print("Demo completed successfully! ✓")
    print("=" * 70)
    print("\nFor more advanced examples, see:")
    print("  - examples/phase4_trainer_examples.py")
    print("  - tests/test_trainer_callbacks.py")
