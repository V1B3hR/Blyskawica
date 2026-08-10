"""
[Moduł: Dataset Ingestion and EWC Training Loop (Task B1)]
Provides facilities to:
1. Load dataset files in JSON, JSONL, and Parquet format.
2. Wrap records into PyTorch Dataset instances for sequential and continual learning.
3. Integrate PyTorch training with Elastic Weight Consolidation (EWC) to mitigate catastrophic forgetting.
"""

import json
import os

import numpy as np

try:
    import pandas as pd
    _HAS_PANDAS = True
except (ImportError, AttributeError):
    _HAS_PANDAS = False
from typing import Any

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset

# Import the SynapticConsolidation mechanism from continual learning
from adaptiveneuralnetwork.applications.continual_learning import SynapticConsolidation

# Detect Parquet reading capability via pyarrow
_HAS_PYARROW = False
try:
    import pyarrow  # noqa: F401
    _HAS_PYARROW = True
except ImportError:
    pass


class DatasetLoader:
    """
    Utility loader for reading datasets in JSON, JSONL, and Parquet formats.
    """
    @staticmethod
    def load_file(file_path: str) -> list[dict[str, Any]]:
        """
        Loads a file (JSON, JSONL, or Parquet) and returns it as a list of dictionaries (records).
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        ext = os.path.splitext(file_path)[1].lower()

        if ext == '.parquet':
            if not _HAS_PANDAS:
                raise ImportError("Pandas package is required to read Parquet files, but it is currently unavailable or incompatible on this system.")
            if not _HAS_PYARROW:
                raise ImportError("PyArrow package is required to read Parquet files. Please install pyarrow.")
            df = pd.read_parquet(file_path)
            return df.to_dict('records')

        elif ext == '.jsonl':
            samples = []
            with open(file_path, encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        samples.append(json.loads(line))
            return samples

        elif ext == '.json':
            with open(file_path, encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                return [data]
            else:
                raise ValueError("JSON file must contain either a list or a dictionary object.")
        else:
            raise ValueError(f"Unsupported file format: {ext}. Supported types: .json, .jsonl, .parquet")


class ContinuousLearningDataset(Dataset):
    """
    PyTorch Dataset wrapper for continuous learning datasets.
    Converts list of dictionaries containing features and targets into PyTorch tensors.
    """
    def __init__(
        self,
        samples: list[dict[str, Any]],
        feature_keys: list[str] = None,
        target_key: str = None,
        device: str = None
    ):
        self.samples = samples
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")

        if not samples:
            self.features = torch.empty((0, 1), device=self.device)
            self.targets = torch.empty(0, dtype=torch.long, device=self.device)
            self.feature_keys = []
            self.target_key = ""
            return

        first_sample = samples[0]

        # Determine target key if not provided
        if target_key is None:
            for k in ['label', 'target', 'class', 'Attrition', 'y']:
                if k in first_sample:
                    target_key = k
                    break
            if target_key is None:
                target_key = list(first_sample.keys())[-1]

        # Determine feature keys (exclude non-numeric and the target key)
        if feature_keys is None:
            feature_keys = [
                k for k, v in first_sample.items()
                if k != target_key and isinstance(v, (int, float, bool, np.number))
            ]

        self.feature_keys = feature_keys
        self.target_key = target_key

        features_list = []
        targets_list = []

        for sample in samples:
            # Vector of features
            feat_vec = [float(sample.get(k, 0.0)) for k in self.feature_keys]
            features_list.append(feat_vec)

            # Target labels mapping
            val = sample.get(self.target_key, 0)
            if isinstance(val, str):
                targets_list.append(abs(hash(val)) % 10)  # map categories dynamically
            else:
                targets_list.append(int(val))

        self.features = torch.tensor(features_list, dtype=torch.float32, device=self.device)
        self.targets = torch.tensor(targets_list, dtype=torch.long, device=self.device)

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor]:
        return self.features[idx], self.targets[idx]


class EWCTrainer:
    """
    Trainer integrating PyTorch model training with Elastic Weight Consolidation (EWC)
    to protect previously learned synapses/tasks from catastrophic forgetting.
    """
    def __init__(self, model: nn.Module, ewc_strength: float = 100.0, lr: float = 0.005):
        self.model = model
        self.ewc_strength = ewc_strength
        self.device = next(model.parameters()).device
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)

        # Instantiate SynapticConsolidation
        self.consolidation = SynapticConsolidation(self.model)

    def train_epoch(self, data_loader: DataLoader, criterion: Any = None) -> float:
        """
        Trains the model for one epoch on the current task using the EWC regularization penalty.
        """
        self.model.train()
        total_loss = 0.0

        if criterion is None:
            criterion = nn.CrossEntropyLoss()

        for batch_data, batch_targets in data_loader:
            self.optimizer.zero_grad()

            # Map batch to target device
            x = batch_data.to(self.device)
            y = batch_targets.to(self.device)

            outputs = self.model(x)
            task_loss = criterion(outputs, y)

            # Compute EWC consolidation loss
            ewc_loss = self.consolidation.consolidation_loss(self.ewc_strength)

            # Combined Loss
            loss = task_loss + ewc_loss

            loss.backward()
            self.optimizer.step()

            total_loss += loss.item()

        return total_loss / len(data_loader) if len(data_loader) > 0 else 0.0

    def consolidate_task(self, data_loader: DataLoader, num_samples: int = 1000):
        """
        Locks in learned weights for the current task by updating the optimal
        parameters and estimating the Fisher Information Matrix on the dataset.
        """
        # Save the current weights as optimal params
        self.consolidation.update_optimal_params()
        # Compute Fisher information on the task dataset
        self.consolidation.estimate_fisher_information(data_loader, num_samples=num_samples)
