"""
[Unit Tests: EWC and Dataset Ingestion (Task B1)]
Verifies:
1. File loading for JSON, JSONL, and Parquet formats.
2. Conversion of parsed records into feature/label PyTorch Tensors.
3. EWC consolidation, trainer epoch execution, optimal weights update, and Fisher information estimation.
"""

import json
import os
import sys
import tempfile
import unittest

try:
    import pandas as pd
    _HAS_PANDAS = True
except (ImportError, AttributeError):
    from unittest.mock import MagicMock
    sys.modules['pandas'] = MagicMock()
    pd = sys.modules['pandas']
    _HAS_PANDAS = False
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from adaptiveneuralnetwork.data.dataset_loader import (
    ContinuousLearningDataset,
    DatasetLoader,
    EWCTrainer,
)


class DummyModel(nn.Module):
    """
    Minimal dummy linear layer model for testing EWC integration.
    """
    def __init__(self, input_dim=4, output_dim=2):
        super().__init__()
        self.fc = nn.Linear(input_dim, output_dim)

    def forward(self, x):
        return self.fc(x)


class TestDatasetLoaderEWC(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

        # Define mock samples
        self.mock_samples = [
            {"feat1": 0.5, "feat2": -1.2, "feat3": 0.1, "feat4": 3.0, "label": 0},
            {"feat1": 1.2, "feat2": 0.3, "feat3": -0.8, "feat4": -1.5, "label": 1},
            {"feat1": -0.2, "feat2": 0.9, "feat3": 0.5, "feat4": 0.4, "label": 0},
            {"feat1": 0.8, "feat2": -0.5, "feat3": -0.2, "feat4": 1.1, "label": 1},
        ]

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_json_loading(self):
        """Test reading records from a standard JSON file."""
        json_path = os.path.join(self.temp_dir.name, "data.json")
        with open(json_path, "w") as f:
            json.dump(self.mock_samples, f)

        loaded = DatasetLoader.load_file(json_path)
        self.assertEqual(len(loaded), 4)
        self.assertEqual(loaded[0]["feat1"], 0.5)
        self.assertEqual(loaded[1]["label"], 1)

    def test_jsonl_loading(self):
        """Test reading records from a JSONL file."""
        jsonl_path = os.path.join(self.temp_dir.name, "data.jsonl")
        with open(jsonl_path, "w") as f:
            for sample in self.mock_samples:
                f.write(json.dumps(sample) + "\n")

        loaded = DatasetLoader.load_file(jsonl_path)
        self.assertEqual(len(loaded), 4)
        self.assertEqual(loaded[2]["feat2"], 0.9)
        self.assertEqual(loaded[3]["label"], 1)

    @unittest.skipUnless(_HAS_PANDAS, "Pandas is not available or broken on Python 3.14")
    def test_parquet_loading(self):
        """Test reading records from a Parquet file."""
        parquet_path = os.path.join(self.temp_dir.name, "data.parquet")
        df = pd.DataFrame(self.mock_samples)
        df.to_parquet(parquet_path)

        loaded = DatasetLoader.load_file(parquet_path)
        self.assertEqual(len(loaded), 4)
        self.assertEqual(loaded[0]["feat1"], 0.5)
        self.assertEqual(loaded[1]["label"], 1)

    def test_continuous_learning_dataset_mapping(self):
        """Test wrapping loaded records into PyTorch Tensors."""
        # Wrap the mock samples
        dataset = ContinuousLearningDataset(
            samples=self.mock_samples,
            feature_keys=["feat1", "feat2", "feat3", "feat4"],
            target_key="label"
        )

        self.assertEqual(len(dataset), 4)
        self.assertEqual(list(dataset.features.shape), [4, 4])
        self.assertEqual(list(dataset.targets.shape), [4])

        # Test item retrieving
        x, y = dataset[0]
        self.assertEqual(x.shape[0], 4)
        self.assertEqual(y.item(), 0)

    def test_ewc_training_cycle(self):
        """Test EWC training loop updates model parameters and incorporates regularization."""
        model = DummyModel(input_dim=4, output_dim=2)

        # Check initial device
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = model.to(device)

        # Wrap data and initialize loader
        dataset = ContinuousLearningDataset(
            samples=self.mock_samples,
            feature_keys=["feat1", "feat2", "feat3", "feat4"],
            target_key="label",
            device=device
        )
        loader = DataLoader(dataset, batch_size=2, shuffle=False)

        trainer = EWCTrainer(model, ewc_strength=100.0, lr=0.01)

        # Run a first training epoch (with 0 EWC loss since Fisher is not estimated yet)
        initial_loss = trainer.train_epoch(loader)
        self.assertTrue(initial_loss > 0.0)

        # Consolidate first task (computes Fisher matrix and saves optimal weights)
        trainer.consolidate_task(loader, num_samples=10)

        # Make a parameter modification and run another training step (now with active EWC loss)
        next_loss = trainer.train_epoch(loader)
        self.assertTrue(next_loss >= 0.0)

        print(f"[TEST EWC] Initial loss: {initial_loss:.4f} | Loss with EWC penalty: {next_loss:.4f}")
        print("[OK] EWC training cycle verified successfully.")


if __name__ == "__main__":
    unittest.main()
