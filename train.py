#!/usr/bin/env python3
"""
Unified Training Entry Point for Adaptive Neural Network

This script provides a consolidated training interface that replaces multiple
scattered training scripts. It supports:
- Configuration-driven workflows (YAML/JSON)
- Multiple datasets (MNIST, Kaggle datasets, custom)
- CLI with subcommands
- Flexible parameter overrides

Usage:
    # Train with config file
    python train.py --config config/training/mnist.yaml
    
    # Train with dataset name and custom parameters
    python train.py --dataset mnist --epochs 20 --batch-size 128
    
    # List available datasets
    python train.py --list-datasets
    
Examples:
    python train.py --config config/training/kaggle_default.yaml
    python train.py --dataset annomi --data-path data/annomi --epochs 10
    python train.py --config config/training/quick_test.yaml --device cpu
"""

import argparse
import json
import logging
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Inline configuration classes to avoid package dependencies
@dataclass
class DatasetConfig:
    """Configuration for dataset loading and preprocessing."""
    name: str = "mnist"
    data_path: str | None = None
    batch_size: int = 64
    num_workers: int = 4
    shuffle: bool = True
    train_split: float = 0.8
    val_split: float = 0.1
    test_split: float = 0.1
    seed: int = 42
    augmentation: bool = False
    augmentation_params: dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelConfig:
    """Configuration for model architecture."""
    name: str = "adaptive"
    input_dim: int = 784
    hidden_dim: int = 128
    output_dim: int = 10
    num_nodes: int = 64
    dropout: float = 0.1
    activation: str = "relu"
    model_params: dict[str, Any] = field(default_factory=dict)


@dataclass
class OptimizerConfig:
    """Configuration for optimizer."""
    name: str = "adam"
    learning_rate: float = 1e-3
    weight_decay: float = 1e-4
    momentum: float = 0.9
    betas: tuple = (0.9, 0.999)
    eps: float = 1e-8
    scheduler: str | None = None
    scheduler_params: dict[str, Any] = field(default_factory=dict)


@dataclass
class TrainingConfig:
    """Configuration for training process."""
    epochs: int = 10
    max_steps: int | None = None
    gradient_accumulation_steps: int = 1
    max_grad_norm: float = 1.0
    use_amp: bool = False
    checkpoint_dir: str = "checkpoints"
    save_every_n_epochs: int = 1
    keep_last_n_checkpoints: int = 3
    log_every_n_steps: int = 10
    log_dir: str = "logs"
    verbose: bool = False
    device: str = "cuda"
    seed: int = 42
    early_stopping: bool = False
    early_stopping_patience: int = 5
    early_stopping_metric: str = "val_loss"


class EmotionalAdaptiveLR:
    """
    Adapts the learning rate based on the neurochemical state of the network.
    Curiosity (Dopamine) increases LR for exploratory learning.
    Stability (Serotonin) stabilizes LR for consolidation.
    Stress (Cortisol) decreases LR to prevent 'panic training' during attacks.
    """
    def __init__(self, base_lr: float, neurochemistry: Any):
        self.base_lr = base_lr
        self.neuro = neurochemistry

    def get_lr(self) -> float:
        # Dopamine (0.0 - 2.0) -> Multiplier 1.0 to 2.0
        dopamine_boost = 1.0 + (max(0, self.neuro.dopamine - 0.2) * 0.5)
        
        # Cortisol (0.0 - 2.0) -> Penalty 1.0 to 0.2
        cortisol_penalty = max(0.2, 1.0 - (self.neuro.cortisol * 0.4))
        
        # Serotonin (0.0 - 1.0) -> Damping factor
        serotonin_stability = 0.9 + (self.neuro.serotonin * 0.1)
        
        return self.base_lr * dopamine_boost * cortisol_penalty * serotonin_stability



@dataclass
class EvaluationConfig:
    """Configuration for model evaluation."""
    metrics: list[str] = field(default_factory=lambda: ["accuracy", "loss"])
    batch_size: int = 128
    save_predictions: bool = False
    output_dir: str = "outputs"


@dataclass
class WorkflowConfig:
    """Complete workflow configuration combining all components."""
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    optimizer: OptimizerConfig = field(default_factory=OptimizerConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    evaluation: EvaluationConfig = field(default_factory=EvaluationConfig)

    @classmethod
    def from_yaml(cls, yaml_path: str | Path) -> "WorkflowConfig":
        """Load configuration from YAML file."""
        yaml_path = Path(yaml_path)
        with open(yaml_path) as f:
            config_dict = yaml.safe_load(f)
        return cls.from_dict(config_dict)

    @classmethod
    def from_json(cls, json_path: str | Path) -> "WorkflowConfig":
        """Load configuration from JSON file."""
        json_path = Path(json_path)
        with open(json_path) as f:
            config_dict = json.load(f)
        return cls.from_dict(config_dict)

    @classmethod
    def from_dict(cls, config_dict: dict[str, Any]) -> "WorkflowConfig":
        """Create configuration from dictionary."""
        dataset_config = DatasetConfig(**config_dict.get("dataset", {}))
        model_config = ModelConfig(**config_dict.get("model", {}))
        optimizer_config = OptimizerConfig(**config_dict.get("optimizer", {}))
        training_config = TrainingConfig(**config_dict.get("training", {}))
        evaluation_config = EvaluationConfig(**config_dict.get("evaluation", {}))

        return cls(
            dataset=dataset_config,
            model=model_config,
            optimizer=optimizer_config,
            training=training_config,
            evaluation=evaluation_config
        )

    def to_yaml(self, yaml_path: str | Path) -> None:
        """Save configuration to YAML file."""
        yaml_path = Path(yaml_path)
        yaml_path.parent.mkdir(parents=True, exist_ok=True)
        config_dict = self.to_dict()

        # Convert tuples to lists for YAML serialization
        if isinstance(config_dict.get('optimizer', {}).get('betas'), tuple):
            config_dict['optimizer']['betas'] = list(config_dict['optimizer']['betas'])

        with open(yaml_path, "w") as f:
            yaml.dump(config_dict, f, default_flow_style=False, indent=2, sort_keys=False)

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "dataset": asdict(self.dataset),
            "model": asdict(self.model),
            "optimizer": asdict(self.optimizer),
            "training": asdict(self.training),
            "evaluation": asdict(self.evaluation)
        }


# Dataset registry
AVAILABLE_DATASETS = {
    "mnist": "MNIST handwritten digits (28x28 grayscale images)",
    "cifar10": "CIFAR-10 natural images (32x32 color images)",
    "annomi": "ANNOMI Motivational Interviewing dataset (text)",
    "mental_health": "Mental Health dataset (text)",
    "vr_driving": "VR Driving simulation dataset",
    "autvi": "Automotive Vehicle Inspection dataset",
    "digakust": "Digital Acoustic Analysis dataset",
    "synthetic": "Synthetic dataset for testing",
    "curriculum": "Phase 2A Curriculum (Hardware Awareness -> Ethics)",
}


def list_datasets():
    """Display available datasets."""
    print("\n" + "=" * 70)
    print("Available Datasets")
    print("=" * 70)
    for name, description in AVAILABLE_DATASETS.items():
        print(f"  {name:20s} - {description}")
    print("=" * 70 + "\n")


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for training script."""
    parser = argparse.ArgumentParser(
        description="Unified training script for Adaptive Neural Network",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --config config/training/mnist.yaml
  %(prog)s --dataset annomi --data-path data/annomi --epochs 10
  %(prog)s --config config/training/quick_test.yaml --device cpu
  %(prog)s --list-datasets
        """
    )

    # Configuration file or dataset selection
    config_group = parser.add_mutually_exclusive_group()
    config_group.add_argument(
        "--config", "-c",
        type=str,
        help="Path to YAML/JSON configuration file"
    )
    config_group.add_argument(
        "--dataset", "-d",
        type=str,
        choices=list(AVAILABLE_DATASETS.keys()),
        help="Dataset name (will use default configuration)"
    )

    # List datasets
    parser.add_argument(
        "--list-datasets",
        action="store_true",
        help="List available datasets and exit"
    )

    # Dataset parameters
    parser.add_argument("--data-path", type=str, help="Path to dataset")
    parser.add_argument("--batch-size", type=int, help="Training batch size")
    parser.add_argument("--num-workers", type=int, help="Number of data loader workers")

    # Model parameters
    parser.add_argument("--model", type=str, help="Model name")
    parser.add_argument("--hidden-dim", type=int, help="Hidden dimension size")
    parser.add_argument("--num-nodes", type=int, help="Number of nodes")

    # Training parameters
    parser.add_argument("--epochs", type=int, help="Number of training epochs")
    parser.add_argument("--learning-rate", "--lr", type=float, help="Learning rate")
    parser.add_argument("--weight-decay", type=float, help="Weight decay")
    parser.add_argument("--device", type=str, help="Device (cuda/cpu)")
    parser.add_argument("--seed", type=int, help="Random seed")

    # Advanced options
    parser.add_argument("--use-amp", action="store_true", help="Use automatic mixed precision")
    parser.add_argument("--checkpoint-dir", type=str, help="Checkpoint directory")
    parser.add_argument("--log-dir", type=str, help="Log directory")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    # Output
    parser.add_argument("--output-dir", type=str, help="Output directory for results")
    parser.add_argument("--save-config", type=str, help="Save resolved configuration to file")

    return parser


def load_config(args: argparse.Namespace) -> WorkflowConfig:
    """Load and merge configuration from file and CLI arguments."""
    # Load base configuration
    if args.config:
        logger.info(f"Loading configuration from: {args.config}")
        config_path = Path(args.config)
        if config_path.suffix in ['.yaml', '.yml']:
            config = WorkflowConfig.from_yaml(config_path)
        elif config_path.suffix == '.json':
            config = WorkflowConfig.from_json(config_path)
        else:
            raise ValueError(f"Unsupported config format: {config_path.suffix}")
    elif args.dataset:
        logger.info(f"Using default configuration for dataset: {args.dataset}")
        # Create default configuration
        config = WorkflowConfig()
        config.dataset.name = args.dataset
    else:
        raise ValueError("Either --config or --dataset must be specified")

    # Override with CLI arguments
    if args.data_path is not None:
        config.dataset.data_path = args.data_path
    if args.batch_size is not None:
        config.dataset.batch_size = args.batch_size
    if args.num_workers is not None:
        config.dataset.num_workers = args.num_workers

    if args.model is not None:
        config.model.name = args.model
    if args.hidden_dim is not None:
        config.model.hidden_dim = args.hidden_dim
    if args.num_nodes is not None:
        config.model.num_nodes = args.num_nodes

    if args.epochs is not None:
        config.training.epochs = args.epochs
    if args.learning_rate is not None:
        config.optimizer.learning_rate = args.learning_rate
    if args.weight_decay is not None:
        config.optimizer.weight_decay = args.weight_decay
    if args.device is not None:
        config.training.device = args.device
    if args.seed is not None:
        config.training.seed = args.seed
        config.dataset.seed = args.seed

    if args.use_amp:
        config.training.use_amp = True
    if args.checkpoint_dir is not None:
        config.training.checkpoint_dir = args.checkpoint_dir
    if args.log_dir is not None:
        config.training.log_dir = args.log_dir
    if args.verbose:
        config.training.verbose = True

    if args.output_dir is not None:
        config.evaluation.output_dir = args.output_dir

    return config


def print_config(config: WorkflowConfig):
    """Pretty print configuration."""
    print("\n" + "=" * 70)
    print("Training Configuration")
    print("=" * 70)
    print(f"Dataset:     {config.dataset.name}")
    print(f"Data Path:   {config.dataset.data_path or 'default'}")
    print(f"Batch Size:  {config.dataset.batch_size}")
    print(f"Model:       {config.model.name}")
    print(f"Hidden Dim:  {config.model.hidden_dim}")
    print(f"Num Nodes:   {config.model.num_nodes}")
    print(f"Optimizer:   {config.optimizer.name}")
    print(f"LR:          {config.optimizer.learning_rate}")
    print(f"Epochs:      {config.training.epochs}")
    print(f"Device:      {config.training.device}")
    print(f"Seed:        {config.training.seed}")
    print(f"AMP:         {config.training.use_amp}")
    print("=" * 70 + "\n")


def train_with_config(config: WorkflowConfig):
    """Execute training with the given configuration."""
    logger.info("Starting training...")
    logger.info(f"Dataset: {config.dataset.name}")

    try:
        import torch
        from torch.utils.data import DataLoader, TensorDataset
        from adaptiveneuralnetwork.training.trainer import Trainer

        # 1. Resolve seed
        torch.manual_seed(config.training.seed)

        # 2. Load dataset
        train_loader = None
        if config.dataset.name == "mnist":
            try:
                from torchvision import datasets, transforms
                transform = transforms.Compose([
                    transforms.ToTensor(),
                    transforms.Normalize((0.1307,), (0.3081,))
                ])
                train_dataset = datasets.MNIST('data', train=True, download=True, transform=transform)
                train_loader = DataLoader(train_dataset, batch_size=config.dataset.batch_size, shuffle=config.dataset.shuffle)
            except Exception as e:
                logger.warning(f"Could not load MNIST dataset: {e}. Falling back to synthetic.")
        elif config.dataset.name == "annomi":
            try:
                from adaptiveneuralnetwork.data.kaggle_datasets import load_annomi_dataset
                data_path = config.dataset.data_path or "data/annomi"
                train_dataset = load_annomi_dataset(data_path)
                train_loader = DataLoader(train_dataset, batch_size=config.dataset.batch_size, shuffle=config.dataset.shuffle)
            except Exception as e:
                logger.warning(f"Could not load ANNOMI dataset: {e}. Falling back to synthetic.")
        elif config.dataset.name == "curriculum":
            from blyskawica_start import start_blyskawica
            logger.info("Delegating to main Phase 2A curriculum training...")
            start_blyskawica()
            return

        if train_loader is None:
            logger.warning(f"Using synthetic/mock training loader for dataset '{config.dataset.name}'...")
            X = torch.randn(100, config.model.input_dim)
            y = torch.randint(0, config.model.output_dim, (100,))
            train_dataset = TensorDataset(X, y)
            train_loader = DataLoader(train_dataset, batch_size=config.dataset.batch_size, shuffle=config.dataset.shuffle)

        # 3. Instantiate Model
        from adaptiveneuralnetwork.api.model import AdaptiveModel
        from adaptiveneuralnetwork.api.config import AdaptiveConfig
        
        adaptive_config = AdaptiveConfig(
            input_dim=config.model.input_dim,
            hidden_dim=config.model.hidden_dim,
            output_dim=config.model.output_dim,
            num_nodes=config.model.num_nodes,
            device=config.training.device
        )
        model = AdaptiveModel(adaptive_config)

        # 4. Optimizer and Trainer Setup
        optimizer = torch.optim.Adam(
            model.parameters(), 
            lr=config.optimizer.learning_rate, 
            weight_decay=config.optimizer.weight_decay
        )
        criterion = torch.nn.CrossEntropyLoss()
        
        trainer = Trainer(
            model=model,
            optimizer=optimizer,
            criterion=criterion,
            device=config.training.device,
            use_amp=config.training.use_amp,
            gradient_accumulation_steps=config.training.gradient_accumulation_steps,
            max_grad_norm=config.training.max_grad_norm,
            seed=config.training.seed
        )

        # 5. Fit Model
        trainer.fit(train_loader, num_epochs=config.training.epochs)
        
        # 6. Save model checkpoint
        checkpoint_dir = Path(config.training.checkpoint_dir)
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        checkpoint_path = checkpoint_dir / f"model_{config.dataset.name}.pt"
        
        torch.save({
            'model_state_dict': model.state_dict(),
            'config': adaptive_config
        }, checkpoint_path)

        logger.info("Training completed successfully!")
        logger.info(f"Model saved to: {checkpoint_path}")

    except Exception as e:
        logger.error(f"Training failed: {e}", exc_info=True)
        raise


def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Handle list datasets
    if args.list_datasets:
        list_datasets()
        return 0

    # Validate arguments
    if not args.config and not args.dataset:
        parser.print_help()
        print("\nError: Either --config or --dataset must be specified")
        return 1

    try:
        # Load configuration
        config = load_config(args)

        # Set logging level
        if config.training.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

        # Print configuration
        print_config(config)

        # Save configuration if requested
        if args.save_config:
            config.to_yaml(args.save_config)
            logger.info(f"Configuration saved to: {args.save_config}")

        # Execute training
        train_with_config(config)

        return 0

    except Exception as e:
        logger.error(f"Training failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
