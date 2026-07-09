"""Secrets management for Nethical Recon."""

import logging
import os

from .backends import DotEnvBackend, K8sSecretsBackend, VaultBackend
from .manager import SecretsManager, get_secrets_manager
from .sanitizer import SecretsSanitizer, sanitize_dict, sanitize_string

logger = logging.getLogger(__name__)


def init_secrets_backend() -> SecretsManager:
    """
    Initialize secrets backend with graceful fallback.

    Tries backends in order: Vault -> K8s -> DotEnv
    Falls back to environment variables if all fail.

    Returns:
        SecretsManager instance
    """
    backend_type = os.getenv("SECRETS_BACKEND", "env").lower()

    try:
        if backend_type == "vault":
            logger.info("Attempting to initialize Vault secrets backend")
            backend = VaultBackend()
            return SecretsManager(backend)
        elif backend_type == "k8s" or backend_type == "kubernetes":
            logger.info("Attempting to initialize Kubernetes secrets backend")
            backend = K8sSecretsBackend()
            return SecretsManager(backend)
        elif backend_type == "dotenv" or backend_type == "env":
            logger.info("Using .env file secrets backend")
            backend = DotEnvBackend()
            return SecretsManager(backend)
        else:
            logger.warning(f"Unknown backend type '{backend_type}', using .env fallback")
            backend = DotEnvBackend()
            return SecretsManager(backend)
    except NotImplementedError:
        logger.warning(f"Backend '{backend_type}' not implemented, falling back to .env")
        backend = DotEnvBackend()
        return SecretsManager(backend)
    except Exception as e:
        logger.error(f"Failed to initialize '{backend_type}' backend: {e}, falling back to .env")
        backend = DotEnvBackend()
        return SecretsManager(backend)


__all__ = [
    "SecretsManager",
    "get_secrets_manager",
    "init_secrets_backend",
    "SecretsSanitizer",
    "sanitize_dict",
    "sanitize_string",
]
