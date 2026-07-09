import logging
import yaml
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)

def load_config(path: str) -> Dict[str, Any]:
    """
    Loads the YAML configuration file with robust error handling, validation, and optional schema enforcement.
    """
    config_path = Path(path)
    logger.debug(f"Attempting to load configuration from: {config_path.resolve()}")

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        if config is None:
            logger.warning(f"Configuration file '{path}' is empty. Returning an empty dictionary.")
            return {}

        if not isinstance(config, dict):
            logger.error(f"Configuration file '{path}' does not contain a dictionary. Found: {type(config)}")
            raise ValueError("Configuration must be a dictionary.")

        # Basic schema validation (example: add your required keys)
        required_keys = ['output_model_dir', 'affective_model', 'graph_scaffold_path']
        missing_keys = [k for k in required_keys if k not in config]
        if missing_keys:
            logger.error(f"Missing required keys in config: {missing_keys}")
            raise KeyError(f"Missing required keys: {missing_keys}")

        logger.info(f"Configuration file loaded successfully. Keys: {list(config.keys())}")
        return config

    except FileNotFoundError:
        logger.error(f"FATAL: Configuration file not found at '{path}'. Please ensure it exists.")
        raise
    except yaml.YAMLError as e:
        logger.error(f"FATAL: Error parsing YAML configuration file '{path}': {e}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred while loading config '{path}': {e}", exc_info=True)
        raise
