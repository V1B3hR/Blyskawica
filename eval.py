#!/usr/bin/env python3
"""
Evaluate Blyskawica Model

Consolidated entry point that delegates execution to the internal evaluation runner.
"""

import sys
import argparse
from pathlib import Path

# Add core path to Python path
sys.path.insert(0, str(Path(__file__).parent))

from train import WorkflowConfig


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for evaluation."""
    parser = argparse.ArgumentParser(description="Evaluate Blyskawica model")
    parser.add_argument("--checkpoint", "--model", type=str, required=True, help="Path to model checkpoint")
    parser.add_argument("--config", type=str, help="Path to config file")
    parser.add_argument("--dataset", type=str, default="mnist", help="Dataset name")
    parser.add_argument("--data-path", type=str, help="Dataset data path")
    parser.add_argument("--batch-size", type=int, default=64, help="Batch size")
    parser.add_argument("--device", type=str, default="cpu", help="Device to use")
    parser.add_argument("--output-dir", type=str, default="benchmarks/history", help="Output directory")
    parser.add_argument("--save-predictions", action="store_true", help="Save predictions")
    parser.add_argument("--metrics", nargs="+", help="List of metrics to evaluate")
    parser.add_argument("--full", action="store_true", help="Run full evaluation suite")
    return parser


def load_eval_config(args: Any) -> WorkflowConfig:
    """Load and merge evaluation configuration."""
    if hasattr(args, "config") and args.config:
        config = WorkflowConfig.from_yaml(args.config)
    else:
        config = WorkflowConfig()

    if hasattr(args, "dataset") and args.dataset is not None:
        config.dataset.name = args.dataset
    if hasattr(args, "data_path") and args.data_path is not None:
        config.dataset.data_path = args.data_path
    if hasattr(args, "batch_size") and args.batch_size is not None:
        config.evaluation.batch_size = args.batch_size
    if hasattr(args, "device") and args.device is not None:
        config.training.device = args.device
    if hasattr(args, "output_dir") and args.output_dir is not None:
        config.evaluation.output_dir = args.output_dir
    if hasattr(args, "save_predictions"):
        config.evaluation.save_predictions = args.save_predictions
    if hasattr(args, "metrics") and args.metrics is not None:
        config.evaluation.metrics = args.metrics

    return config


def main() -> int:
    """Main entry point delegating to internal run_eval module."""
    # Map command line arguments to match inner runner expected names
    mapped_args = []
    i = 0
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--checkpoint":
            mapped_args.append("--model")
        elif arg == "--checkpoint-dir":
            mapped_args.append("--output-dir")
        else:
            mapped_args.append(arg)
        i += 1
    sys.argv = mapped_args

    from adaptiveneuralnetwork.eval.run_eval import main as run_eval_main
    return run_eval_main()


if __name__ == "__main__":
    sys.exit(main())
