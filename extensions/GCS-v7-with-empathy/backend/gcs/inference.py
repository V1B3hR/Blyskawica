import numpy as np
import tensorflow as tf
import logging
import yaml
import os
import time
from prometheus_client import Counter, Histogram
from .model import GradReverse

# Monitoring metrics
PREDICTION_COUNT = Counter("gcs_predictions_total", "Total predictions made")
PREDICTION_ERRORS = Counter("gcs_prediction_errors_total", "Total prediction errors")
PREDICTION_LATENCY = Histogram("gcs_prediction_latency_seconds", "Prediction latency")

class GCSInference:
    def __init__(self, config_path="backend/gcs/config.yaml"):
        # Robust config path handling
        config_path = os.environ.get("GCS_CONFIG_PATH", config_path)
        try:
            with open(config_path) as f:
                self.config = yaml.safe_load(f)
        except Exception as e:
            logging.critical("Failed to load config file", exc_info=True)
            raise

        # Centralized config
        model_path = self.config["model_path"]
        graph_path = self.config["graph_path"]
        safe_mode = self.config.get("safe_mode", True)
        self.labels = self.config.get("labels", {0:"LEFT_HAND",1:"RIGHT_HAND"})
        self.batch_size = self.config.get("batch_size", 32)
        self.output_layers = self.config.get("output_layers")
        self.attention_extractor = self.config.get("attention_extractor")

        logging.info(f"Loading foundational model from {model_path}...")
        try:
            self.model = tf.keras.models.load_model(
                model_path,
                custom_objects={"GradReverse": GradReverse},
                safe_mode=safe_mode
            )
        except Exception as e:
            logging.critical("Model load failed", exc_info=True)
            raise

        try:
            graph_data = np.load(graph_path)
            adj = graph_data.get("adjacency_matrix")
            if adj is None or adj.shape[0] != adj.shape[1]:
                raise ValueError("Adjacency matrix invalid or not square.")
            if not np.allclose(adj, adj.T):
                logging.warning("Adjacency matrix is not symmetric.")
            self.adj = np.expand_dims(adj, 0)
        except Exception as e:
            logging.critical("Graph load failed", exc_info=True)
            raise

        # Output layer handling (robust selection)
        layer_names = [layer.name for layer in self.model.layers]
        if self.output_layers:
            missing = [name for name in self.output_layers if name not in layer_names]
            if missing:
                logging.error(f"Output layers not found in model: {missing}")
                raise ValueError(f"Output layers not found in model: {missing}")
            outputs = [self.model.get_layer(name).output for name in self.output_layers]
            self.inference_model = tf.keras.Model(inputs=self.model.inputs, outputs=outputs)
            self.output_names = self.output_layers
        else:
            if len(self.model.outputs) > 1:
                self.inference_model = tf.keras.Model(inputs=self.model.inputs, outputs=self.model.outputs)
                self.output_names = [out.name for out in self.model.outputs]
            else:
                if "mi_output" in layer_names:
                    self.inference_model = tf.keras.Model(inputs=self.model.inputs, outputs=self.model.get_layer("mi_output").output)
                    self.output_names = ["mi_output"]
                else:
                    logging.critical("Fallback layer 'mi_output' not found in model.")
                    raise ValueError("Fallback layer 'mi_output' not found in model.")

        # Attention plugin
        self.attention_fn = None
        if self.attention_extractor:
            module_path, func_name = self.attention_extractor.split(":")
            import importlib
            module = importlib.import_module(module_path.replace("/", "."))
            self.attention_fn = getattr(module, func_name)

        logging.info("Foundational Inference Engine ready.")

    @PREDICTION_LATENCY.time()
    def predict(self, source_localized_chunks):
        PREDICTION_COUNT.inc()
        expected_shape = tuple(self.model.inputs[0].shape[1:])
        if source_localized_chunks.shape[1:] != expected_shape:
            logging.error(f"Input shape mismatch. Expected {expected_shape}, got {source_localized_chunks.shape[1:]}")
            PREDICTION_ERRORS.inc()
            raise ValueError(f"Input shape mismatch. Expected {expected_shape}, got {source_localized_chunks.shape[1:]}")

        try:
            predictions = self.inference_model.predict(
                source_localized_chunks,
                verbose=0,
                batch_size=self.batch_size
            )
            results = []
            # Multi-output handling
            if isinstance(predictions, list):
                for i in range(len(source_localized_chunks)):
                    result = {}
                    for idx, output in enumerate(predictions):
                        pred = output[i]
                        try:
                            if pred.size == 0:
                                raise ValueError(f"Prediction output {self.output_names[idx]} is empty for sample {i}.")
                            intent_id = np.argmax(pred)
                            confidence = pred[intent_id]
                            label = self.labels.get(intent_id, intent_id)
                            attention = self.attention_fn(pred) if self.attention_fn else None
                            result[self.output_names[idx]] = {
                                "label": label,
                                "confidence": float(confidence),
                                "raw": pred.tolist(),
                                "attention": attention
                            }
                        except Exception as e:
                            PREDICTION_ERRORS.inc()
                            logging.error(f"Sample {i}, output {self.output_names[idx]} prediction error", exc_info=True)
                            result[self.output_names[idx]] = {"error": str(e)}
                    results.append(result)
            else:
                for i, pred in enumerate(predictions):
                    try:
                        if pred.size == 0:
                            raise ValueError("Prediction array is empty.")
                        intent_id = np.argmax(pred)
                        confidence = pred[intent_id]
                        label = self.labels.get(intent_id, intent_id)
                        attention = self.attention_fn(pred) if self.attention_fn else None
                        result = {
                            "label": label,
                            "confidence": float(confidence),
                            "raw": pred.tolist(),
                            "attention": attention
                        }
                    except Exception as e:
                        PREDICTION_ERRORS.inc()
                        logging.error(f"Sample {i} prediction error", exc_info=True)
                        result = {"error": str(e)}
                    results.append(result)
            return results
        except Exception as e:
            PREDICTION_ERRORS.inc()
            logging.error("Prediction failed", exc_info=True)
            raise

