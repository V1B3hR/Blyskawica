import os
import sys
import argparse
import numpy as np
import logging
try:
    import tensorflow as tf
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    logging.warning("TensorFlow not available, some functionality will be limited")

from .data_pipeline import DataPipeline
try:
    from .model import GCSModelFactory
    from .affective_state_classifier import AffectiveModelBuilder
    MODEL_AVAILABLE = True
except ImportError:
    MODEL_AVAILABLE = False
    logging.warning("Model modules not available, using fallback implementations")

class Trainer:
    def __init__(self, config):
        self.config = config
        self.pipeline = DataPipeline(config)
        graph_data = np.load(self.config["graph_scaffold_path"])
        self.adj_matrix = graph_data['adjacency_matrix']

    def extract_features_labels(self, train_data):
        """Extract features and labels from training data for LOSO cross-validation."""
        X_list = []
        y_list = []
        
        for subject_data in train_data:
            X_list.append(subject_data['data'])
            y_list.append(subject_data['labels'])
        
        # Concatenate all subjects' data
        X_train = np.concatenate(X_list, axis=0)
        y_train = np.concatenate(y_list, axis=0)
        
        return X_train, y_train

    def run_loso_cross_validation(self):
        logging.info("Starting Leave-One-Subject-Out Cross-Validation...")
        
        if not TF_AVAILABLE or not MODEL_AVAILABLE:
            logging.error("TensorFlow or model modules not available. Cannot run training.")
            return
        
        try:
            all_data = self.pipeline.load_real_data_for_loso()
            model = GCSModelFactory.build_affective_model(self.config)
            
            fold_results = []
            
            for fold, held_out_subject in enumerate(all_data):
                logging.info(f"Processing fold {fold + 1}/{len(all_data)}")
                train_data = [subj for i, subj in enumerate(all_data) if i != fold]
                if not train_data:
                    logging.warning(f"No training data for fold {fold + 1}")
                    continue
                
                # Extract features/labels from train_data
                X_train, y_train = self.extract_features_labels(train_data)
                logging.info(f"Training data shape: {X_train.shape}, Labels shape: {y_train.shape}")
                
                # Prepare validation data from held-out subject
                X_val = held_out_subject['data']
                y_val = held_out_subject['labels']
                logging.info(f"Validation data shape: {X_val.shape}, Labels shape: {y_val.shape}")
                
                # Compile model for this fold
                model.compile(
                    optimizer='adam', 
                    loss='sparse_categorical_crossentropy', 
                    metrics=['accuracy']
                )
                
                # Train the model
                history = model.fit(
                    X_train, y_train,
                    validation_data=(X_val, y_val),
                    batch_size=self.config.get('batch_size', 32),
                    epochs=self.config.get('epochs', 10),
                    verbose=1
                )
                
                # Evaluate on validation set
                val_loss, val_acc = model.evaluate(X_val, y_val, verbose=0)
                fold_results.append({
                    'fold': fold + 1,
                    'val_loss': val_loss,
                    'val_accuracy': val_acc,
                    'subject_id': held_out_subject['subject_id'],
                    'source_file': held_out_subject.get('source_file', 'unknown')
                })
                
                logging.info(f"Fold {fold + 1} - Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}")
                
                # Save model for this fold
                model_path = os.path.join(self.config.get('output_model_dir', 'models'), f"gcs_fold_{fold + 1}.h5")
                os.makedirs(os.path.dirname(model_path), exist_ok=True)
                try:
                    model.save(model_path)
                    logging.info(f"Model for fold {fold + 1} saved to {model_path}")
                except Exception as e:
                    logging.error(f"Failed to save model for fold {fold + 1}: {e}", exc_info=True)
            
            # Log summary results
            if fold_results:
                avg_acc = np.mean([r['val_accuracy'] for r in fold_results])
                avg_loss = np.mean([r['val_loss'] for r in fold_results])
                logging.info(f"LOSO Cross-Validation Summary:")
                logging.info(f"Average Validation Accuracy: {avg_acc:.4f}")
                logging.info(f"Average Validation Loss: {avg_loss:.4f}")
                
                for result in fold_results:
                    logging.info(f"Fold {result['fold']} (Subject {result['subject_id']}, {result['source_file']}): "
                                f"Acc={result['val_accuracy']:.4f}, Loss={result['val_loss']:.4f}")
                model_path = os.path.join(self.config.get('output_model_dir', 'models'), f"gcs_fold_{fold + 1}.h5")
                os.makedirs(os.path.dirname(model_path), exist_ok=True)
                try:
                    model.save(model_path)
                    logging.info(f"Model for fold {fold + 1} saved to {model_path}")
                except Exception as e:
                    logging.error(f"Failed to save model for fold {fold + 1}: {e}", exc_info=True)
        except Exception as e:
            logging.error(f"LOSO Cross-Validation failed: {e}", exc_info=True)

        logging.info("LOSO Cross-Validation Complete.")

    def train_affective_model(self):
        logging.info("--- Starting Training for Affective State Classifier ---")
        
        if not TF_AVAILABLE or not MODEL_AVAILABLE:
            logging.error("TensorFlow or model modules not available. Cannot run training.")
            return
        
        try:
            foundational_model = GCSModelFactory.build_affective_model(self.config)
            model = AffectiveModelBuilder.build_fused_classifier(self.config, foundational_model)
            dataset_paths = [self.config['affective_model']['deap_dataset_path']]
            X, y = self.pipeline.load_affective_data(dataset_paths)
            model.compile(optimizer='adam', loss={'valence_output': 'mae', 'arousal_output': 'mae'})

            logging.info(f"Model expects {len(model.inputs)} inputs: {[inp.name for inp in model.inputs]}")
            logging.info(f"Data shapes: EEG {X.get('eeg', 'missing')}, Physio {X.get('physio', 'missing')}, Voice {X.get('voice', 'missing')}")
            inputs = [X['eeg'], X['physio'], X['voice']]
            targets = [y['valence'], y['arousal']]
            model.fit(inputs, targets,
                      batch_size=self.config['batch_size'], epochs=self.config['epochs'], validation_split=0.2)
            model_path = self.config['affective_model']['output_model_path']
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            try:
                model.save(model_path)
                logging.info(f"Affective model saved to {model_path}")
            except Exception as e:
                logging.error(f"Failed to save affective model: {e}", exc_info=True)
        except Exception as e:
            logging.error(f"Affective model training failed: {e}", exc_info=True)


def configure_logging():
    """Sets up a clean, standardized logging format."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )


if __name__ == "__main__":
    """
    Direct execution entry point for training.
    Allows running training directly with: python -m backend.gcs.training [mode]
    """
    configure_logging()
    
    parser = argparse.ArgumentParser(
        description="GCS Training Module - Train foundational or affective models",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        'mode',
        choices=['foundational', 'affective', 'both'],
        help="""Training mode:
  - foundational: Run LOSO cross-validation to train core GNN models
  - affective:    Train the multi-modal classifier for empathetic understanding
  - both:         Run both foundational and affective training sequentially"""
    )
    parser.add_argument(
        '--config',
        type=str,
        default=os.path.join(os.path.dirname(__file__), '..', '..', 'config.yaml'),
        help='Path to config file. Default: ../../config.yaml'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config_path = args.config
    if not os.path.exists(config_path):
        logging.error(f"Config file '{config_path}' not found. Exiting.")
        sys.exit(1)
    
    try:
        # Import config_loader here to avoid circular imports
        from .config_loader import load_config
        config = load_config(config_path)
    except Exception as e:
        logging.error(f"Failed to load configuration from {config_path}: {e}", exc_info=True)
        sys.exit(1)
    
    # Initialize trainer
    try:
        trainer = Trainer(config)
    except Exception as e:
        logging.error(f"Failed to initialize Trainer: {e}", exc_info=True)
        sys.exit(1)
    
    # Execute training based on mode
    try:
        if args.mode == 'foundational':
            logging.info("=== Starting Foundational Model Training ===")
            trainer.run_loso_cross_validation()
            logging.info("=== Foundational model training complete ===")
        elif args.mode == 'affective':
            logging.info("=== Starting Affective Model Training ===")
            trainer.train_affective_model()
            logging.info("=== Affective model training complete ===")
        elif args.mode == 'both':
            logging.info("=== Starting Complete Training Pipeline ===")
            logging.info("Step 1/2: Foundational Model Training")
            trainer.run_loso_cross_validation()
            logging.info("Step 2/2: Affective Model Training")
            trainer.train_affective_model()
            logging.info("=== Complete training pipeline finished ===")
    except Exception as e:
        logging.error(f"Training failed: {e}", exc_info=True)
        sys.exit(1)
    
    logging.info("Training completed successfully.")
    sys.exit(0)

