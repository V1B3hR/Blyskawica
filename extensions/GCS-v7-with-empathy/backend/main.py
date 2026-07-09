import argparse
import logging
import os
import sys
import time
import numpy as np

# --- GCS Core Modules ---
from gcs.config_loader import load_config
from gcs.training import Trainer
from gcs.closed_loop_agent import ClosedLoopAgent
# Optional: from gcs.security import SecurityManager
# Optional: from gcs.online_learning_module import OnlineLearningModule

def configure_logging():
    """Sets up a clean, standardized logging format."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

def run_live_simulation(config: dict, interval: int = 2):
    """
    Initiates and runs the main operational loop for the Closed-Loop Agent.
    Simulates a live data stream from hardware.
    """
    try:
        agent = ClosedLoopAgent(config)
        graph_path = config.get("graph_scaffold_path")
        if not graph_path or not os.path.exists(graph_path):
            logging.error(f"Graph scaffold path '{graph_path}' not found.")
            return

        graph_data = np.load(graph_path)
        adj_matrix = np.expand_dims(graph_data['adjacency_matrix'], 0)

        logging.info("--- GCS v7.0 Active Interface: ENGAGED ---")
        logging.info("Starting closed-loop SENSE -> DECIDE -> ACT -> LEARN cycle.")
        logging.info("Simulating live data stream. Press Ctrl+C to terminate.")

        while True:
            live_data = {
                "source_eeg": np.random.randn(1, config["cortical_nodes"], config["timesteps"]),
                "adj_matrix": adj_matrix,
                "physio": np.random.randn(1, config["physio_features"]),
                "voice": np.random.randn(1, 128)
            }
            agent.run_cycle(live_data)
            time.sleep(interval)
    except KeyboardInterrupt:
        logging.info("\n--- Closed-loop session terminated by user. ---")
    except Exception as e:
        logging.error(f"A critical error occurred in the main loop: {e}", exc_info=True)

def main():
    """
    Main entry point for the GCS backend.
    Parses command-line arguments to determine operational mode.
    """
    configure_logging()

    parser = argparse.ArgumentParser(
        description="Grand Council Sentient - The central orchestrator for the BCI system.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        'mode',
        choices=[
            'train-foundational', 
            'train-affective', 
            'run-closed-loop'
            # Optional: 'security', 'online-learning'
        ],
        help="""The operational mode:
  - train-foundational: Run LOSO cross-validation to train core GNN models.
  - train-affective:    Train the multi-modal classifier for empathetic understanding.
  - run-closed-loop:    Run the live, interactive agent with simulated data."""
    )
    parser.add_argument(
        '--config', 
        type=str, 
        default=os.path.join(os.path.dirname(__file__), '..', 'config.yaml'),
        help='Path to config file. Default: ../config.yaml'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=2,
        help='Live simulation interval in seconds (run-closed-loop mode)'
    )
    args = parser.parse_args()

    # --- Load the master configuration ---
    config_path = args.config
    if not os.path.exists(config_path):
        logging.error(f"Config file '{config_path}' not found. Exiting.")
        sys.exit(1)

    try:
        config = load_config(config_path)
    except Exception as e:
        logging.error(f"Failed to load configuration from {config_path}: {e}", exc_info=True)
        sys.exit(1)

    # --- Execute the selected mode ---
    if args.mode == 'train-foundational':
        logging.info("MODE: Training Foundational Model Initiated")
        trainer = Trainer(config)
        trainer.run_loso_cross_validation()
        logging.info("Foundational model training complete.")
    elif args.mode == 'train-affective':
        logging.info("MODE: Training Affective Model Initiated")
        trainer = Trainer(config)
        trainer.train_affective_model()
        logging.info("Affective model training complete.")
    elif args.mode == 'run-closed-loop':
        logging.info("MODE: Live Closed-Loop Simulation Initiated")
        run_live_simulation(config, interval=args.interval)
    # Optional: Add other modes here

if __name__ == "__main__":
    main()
