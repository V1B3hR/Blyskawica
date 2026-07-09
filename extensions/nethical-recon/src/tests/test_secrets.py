"""Tests for secrets management module."""

import os
import tempfile
from pathlib import Path

import pytest

from nethical_recon.secrets import (
    SecretsSanitizer,
    SecretsManager,
    get_secrets_manager,
    sanitize_dict,
    sanitize_string,
)
from nethical_recon.secrets.backends import DotEnvBackend, EnvBackend
from nethical_recon.secrets.manager import init_secrets_manager


class TestEnvBackend:
    """Tests for environment variables backend."""

    def test_get_existing_env_var(self):
        """Test getting an existing environment variable."""
        os.environ["TEST_SECRET"] = "test_value"
        backend = EnvBackend()
        assert backend.get("TEST_SECRET") == "test_value"
        del os.environ["TEST_SECRET"]

    def test_get_nonexistent_env_var(self):
        """Test getting a non-existent environment variable."""
        backend = EnvBackend()
        assert backend.get("NONEXISTENT_VAR") is None
        assert backend.get("NONEXISTENT_VAR", "default") == "default"

    def test_set_env_var(self):
        """Test setting an environment variable."""
        backend = EnvBackend()
        backend.set("TEST_SET_VAR", "set_value")
        assert os.environ["TEST_SET_VAR"] == "set_value"
        del os.environ["TEST_SET_VAR"]

    def test_exists(self):
        """Test checking if environment variable exists."""
        os.environ["TEST_EXISTS"] = "value"
        backend = EnvBackend()
        assert backend.exists("TEST_EXISTS")
        assert not backend.exists("DOES_NOT_EXIST")
        del os.environ["TEST_EXISTS"]

    def test_list_keys(self):
        """Test listing environment variable keys."""
        backend = EnvBackend()
        keys = backend.list_keys()
        assert isinstance(keys, list)
        assert "PATH" in keys


class TestDotEnvBackend:
    """Tests for .env file backend."""

    def test_load_env_file(self, tmp_path):
        """Test loading secrets from .env file."""
        env_file = tmp_path / ".env"
        env_file.write_text("""
# Comment line
API_KEY=test_api_key_123
SECRET=test_secret

# Another comment
DATABASE_URL="postgresql://user:pass@localhost/db"
QUOTED_VALUE='single_quoted'
""")

        backend = DotEnvBackend(env_file)
        assert backend.get("API_KEY") == "test_api_key_123"
        assert backend.get("SECRET") == "test_secret"
        assert backend.get("DATABASE_URL") == "postgresql://user:pass@localhost/db"
        assert backend.get("QUOTED_VALUE") == "single_quoted"

    def test_empty_env_file(self, tmp_path):
        """Test loading from empty .env file."""
        env_file = tmp_path / ".env"
        env_file.write_text("")

        backend = DotEnvBackend(env_file)
        assert backend.get("ANYTHING") is None

    def test_nonexistent_env_file(self, tmp_path):
        """Test handling non-existent .env file."""
        backend = DotEnvBackend(tmp_path / "nonexistent.env")
        assert backend.get("ANYTHING") is None

    def test_fallback_to_env_var(self, tmp_path):
        """Test fallback to environment variable."""
        os.environ["TEST_FALLBACK"] = "env_value"
        env_file = tmp_path / ".env"
        env_file.write_text("OTHER_KEY=other_value")

        backend = DotEnvBackend(env_file)
        assert backend.get("TEST_FALLBACK") == "env_value"
        del os.environ["TEST_FALLBACK"]

    def test_env_file_overrides_env_var(self, tmp_path):
        """Test that .env file overrides environment variable."""
        os.environ["TEST_OVERRIDE"] = "env_value"
        env_file = tmp_path / ".env"
        env_file.write_text("TEST_OVERRIDE=file_value")

        backend = DotEnvBackend(env_file)
        assert backend.get("TEST_OVERRIDE") == "file_value"
        del os.environ["TEST_OVERRIDE"]


class TestSecretsManager:
    """Tests for SecretsManager."""

    def test_default_backend(self):
        """Test that default backend is used."""
        manager = SecretsManager()
        assert manager._backend is not None

    def test_custom_backend(self):
        """Test using custom backend."""
        backend = EnvBackend()
        manager = SecretsManager(backend)
        assert manager._backend is backend

    def test_get_secret(self):
        """Test getting a secret."""
        os.environ["TEST_SECRET"] = "secret_value"
        manager = SecretsManager(EnvBackend())
        assert manager.get("TEST_SECRET") == "secret_value"
        del os.environ["TEST_SECRET"]

    def test_get_required_existing(self):
        """Test getting a required secret that exists."""
        os.environ["REQUIRED_SECRET"] = "required_value"
        manager = SecretsManager(EnvBackend())
        assert manager.get_required("REQUIRED_SECRET") == "required_value"
        del os.environ["REQUIRED_SECRET"]

    def test_get_required_missing(self):
        """Test getting a required secret that doesn't exist."""
        manager = SecretsManager(EnvBackend())
        with pytest.raises(ValueError, match="Required secret.*not found"):
            manager.get_required("MISSING_REQUIRED_SECRET")

    def test_get_api_config(self):
        """Test getting API configuration."""
        manager = SecretsManager(EnvBackend())
        config = manager.get_api_config()
        assert "secret_key" in config
        assert "database_url" in config
        assert "broker_url" in config
        assert "result_backend" in config

    def test_get_external_api_keys(self):
        """Test getting external API keys."""
        os.environ["SHODAN_API_KEY"] = "test_shodan_key"
        manager = SecretsManager(EnvBackend())
        keys = manager.get_external_api_keys()
        assert keys["shodan_api_key"] == "test_shodan_key"
        assert "censys_api_id" in keys
        assert "openai_api_key" in keys
        del os.environ["SHODAN_API_KEY"]

    def test_get_database_config(self):
        """Test getting database configuration."""
        manager = SecretsManager(EnvBackend())
        config = manager.get_database_config()
        assert "database_url" in config
        assert "db_user" in config
        assert "db_password" in config
        assert "db_host" in config
        assert "db_port" in config
        assert "db_name" in config


class TestSecretsSanitizer:
    """Tests for SecretsSanitizer."""

    def test_sanitize_api_key(self):
        """Test sanitizing API key."""
        sanitizer = SecretsSanitizer()
        text = 'api_key="abcdefghijklmnopqrstuvwxyz123456"'
        sanitized = sanitizer.sanitize_string(text)
        assert "abcdefghijklmnopqrstuvwxyz123456" not in sanitized
        assert "****" in sanitized

    def test_sanitize_token(self):
        """Test sanitizing token."""
        sanitizer = SecretsSanitizer()
        text = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
        sanitized = sanitizer.sanitize_string(text)
        assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in sanitized

    def test_sanitize_password(self):
        """Test sanitizing password."""
        sanitizer = SecretsSanitizer()
        text = "password=mySecretPassword123"
        sanitized = sanitizer.sanitize_string(text)
        assert "mySecretPassword123" not in sanitized

    def test_sanitize_database_url(self):
        """Test sanitizing database connection string."""
        sanitizer = SecretsSanitizer()
        text = "postgresql://user:secretpassword@localhost:5432/db"
        sanitized = sanitizer.sanitize_string(text)
        assert "secretpassword" not in sanitized

    def test_sanitize_dict_with_secret_keys(self):
        """Test sanitizing dictionary with secret keys."""
        sanitizer = SecretsSanitizer()
        data = {"api_key": "secret123456", "username": "user", "password": "pass123456", "data": "normal data"}
        sanitized = sanitizer.sanitize_dict(data)
        assert "secret123456" not in str(sanitized)
        assert "pass123456" not in str(sanitized)
        assert sanitized["username"] == "user"
        assert sanitized["data"] == "normal data"

    def test_sanitize_nested_dict(self):
        """Test sanitizing nested dictionary."""
        sanitizer = SecretsSanitizer()
        data = {"outer": {"api_key": "secret123", "value": "data"}, "token": "token456"}
        sanitized = sanitizer.sanitize_dict(data)
        assert "secret123" not in str(sanitized)
        assert "token456" not in str(sanitized)
        assert sanitized["outer"]["value"] == "data"

    def test_sanitize_list(self):
        """Test sanitizing list."""
        sanitizer = SecretsSanitizer()
        items = [{"api_key": "secret123"}, "normal text", {"password": "pass456"}]
        sanitized = sanitizer.sanitize_list(items)
        assert "secret123" not in str(sanitized)
        assert "pass456" not in str(sanitized)
        assert "normal text" in sanitized

    def test_empty_string(self):
        """Test sanitizing empty string."""
        sanitizer = SecretsSanitizer()
        assert sanitizer.sanitize_string("") == ""

    def test_none_value(self):
        """Test sanitizing None value."""
        sanitizer = SecretsSanitizer()
        assert sanitizer.sanitize_string(None) is None


class TestGlobalFunctions:
    """Tests for global convenience functions."""

    def test_sanitize_string_global(self):
        """Test global sanitize_string function."""
        text = "api_key=secret123456789012345678901234567890"
        sanitized = sanitize_string(text)
        assert "secret123456789012345678901234567890" not in sanitized

    def test_sanitize_dict_global(self):
        """Test global sanitize_dict function."""
        data = {"api_key": "secret123456", "value": "data"}
        sanitized = sanitize_dict(data)
        assert "secret123456" not in str(sanitized)
        assert sanitized["value"] == "data"

    def test_get_secrets_manager_singleton(self):
        """Test that get_secrets_manager returns singleton."""
        manager1 = get_secrets_manager()
        manager2 = get_secrets_manager()
        assert manager1 is manager2

    def test_init_secrets_manager(self):
        """Test initializing secrets manager with custom backend."""
        backend = EnvBackend()
        manager = init_secrets_manager(backend)
        assert manager._backend is backend


class TestSecretLeakagePrevention:
    """Tests to ensure secrets don't leak in various scenarios."""

    def test_no_secrets_in_repr(self):
        """Test that secrets are not in string representations."""
        os.environ["TEST_API_KEY"] = "secret_api_key_12345"
        manager = SecretsManager(EnvBackend())
        api_config = manager.get_api_config()

        # Sanitize before printing
        sanitized = sanitize_dict(api_config)
        repr_str = str(sanitized)

        assert "secret_api_key_12345" not in repr_str
        del os.environ["TEST_API_KEY"]

    def test_no_secrets_in_logs(self):
        """Test that secrets are masked in log-like strings."""
        log_message = "Connecting with api_key=sk_live_51234567890abcdefghijk to API"
        sanitized = sanitize_string(log_message)
        assert "sk_live_51234567890abcdefghijk" not in sanitized

    def test_aws_keys_detection(self):
        """Test detection of AWS keys."""
        sanitizer = SecretsSanitizer()
        text = "AWS Key: AKIAIOSFODNN7EXAMPLE"
        sanitized = sanitizer.sanitize_string(text)
        assert "AKIAIOSFODNN7EXAMPLE" not in sanitized

    def test_github_token_detection(self):
        """Test detection of GitHub tokens."""
        sanitizer = SecretsSanitizer()
        text = "Token: ghp_1234567890abcdefghijklmnopqrstuvwxyz"
        sanitized = sanitizer.sanitize_string(text)
        assert "ghp_1234567890abcdefghijklmnopqrstuvwxyz" not in sanitized
