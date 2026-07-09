import os
import tempfile
import pytest
import numpy as np

from gcs.config_loader import load_config
from gcs.training import Trainer
from gcs.security import SecurityManager
from gcs.closed_loop_agent import ClosedLoopAgent

@pytest.fixture
def config():
    # Minimal valid config for integration testing
    return {
        "graph_scaffold_path": "tests/test_graph.npz",
        "cortical_nodes": 4,
        "timesteps": 10,
        "physio_features": 3,
        "affective_model": {
            "deap_dataset_path": "tests/test_deap.npz",
            "output_model_path": "tests/model_affective.h5"
        },
        "output_model_dir": "tests/models",
        "batch_size": 2,
        "epochs": 1
    }

def test_config_loading(config):
    assert isinstance(config, dict)
    # Optionally test loading from YAML if desired

def test_trainer_foundational(config):
    trainer = Trainer(config)
    trainer.run_loso_cross_validation()
    # Check that model files are created
    files = os.listdir(config["output_model_dir"])
    assert any(fn.endswith(".h5") for fn in files)

def test_trainer_affective(config):
    trainer = Trainer(config)
    trainer.train_affective_model()
    assert os.path.exists(config["affective_model"]["output_model_path"])

def test_security_manager():
    with tempfile.TemporaryDirectory() as td:
        key_path = os.path.join(td, "test.key")
        file_path = os.path.join(td, "data.txt")
        with open(file_path, "wb") as f:
            f.write(b"hello world")
        SecurityManager.generate_key(key_path)
        assert os.path.exists(key_path)
        assert SecurityManager.encrypt_file(file_path, key_path)
        assert SecurityManager.decrypt_file_safely(file_path, key_path)
        with open(file_path, "rb") as f:
            assert f.read() == b"hello world"

def test_closed_loop_agent(config):
    agent = ClosedLoopAgent(config)
    graph_data = np.load(config["graph_scaffold_path"])
    adj_matrix = np.expand_dims(graph_data['adjacency_matrix'], 0)
    live_data = {
        "source_eeg": np.random.randn(1, config["cortical_nodes"], config["timesteps"]),
        "adj_matrix": adj_matrix,
        "physio": np.random.randn(1, config["physio_features"]),
        "voice": np.random.randn(1, 128)
    }
    agent.run_cycle(live_data)
    # No assertion needed; test is for integration/no crash
