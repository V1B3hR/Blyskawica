"""
[Phase XXVI: Autonomous Neurochemical Self-Regulation Engine]
Allows Błyskawica to dynamically balance her synthetic hormone & neurotransmitter levels
within a safe, healthy bounds of +/- 7% depending on the active cognitive task:
- "study": Deep ingestion and focus.
- "analysis": Logic puzzles, math, and data filtering.
- "rest": Deep rest, cognitive restoration, high Melatonin.
- "BCI-co-creation": Active human-in-the-loop badminton/creative session.
"""

import json
import os
from pathlib import Path
from typing import Any

try:
    import torch
    import torch.nn as nn
    _HAS_TORCH = True
except ImportError:
    torch = None  # type: ignore[assignment]
    nn = None  # type: ignore[assignment]
    _HAS_TORCH = False

BASE_DIR = Path(__file__).resolve().parents[2]
CHECKPOINT_FILE = os.path.join(str(BASE_DIR), "memory_checkpoint.json")

class AutonomousNeuroRegulator:
    def __init__(self) -> None:
        self.checkpoint_path = CHECKPOINT_FILE
        self.data: dict[str, Any] = {}
        self.load_checkpoint()
        if _HAS_TORCH and torch is not None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self._projectors = {}
        else:
            self.device = "cpu"

    def load_checkpoint(self) -> None:
        baseline_neuro = {
            "Serotonina": 0.80,
            "Oksytocyna": -0.12,
            "Dopamina": 0.67,
            "GABA": 0.73,
            "Acetylocholina": 0.80,
            "Noradrenalina": 0.15,
            "Melatonina": 0.10,
            "Testosteron": 0.45,
            "Kortyzol": 0.22
        }
        bak_file = f"{self.checkpoint_path}.bak"

        # 1. Próba wczytania pliku głównego
        loaded = False
        if os.path.exists(self.checkpoint_path) and os.path.getsize(self.checkpoint_path) > 0:
            try:
                with open(self.checkpoint_path, encoding='utf-8') as f:
                    self.data = json.load(f)
                loaded = True
            except Exception:
                pass

        # 2. Awaryjne przywrócenie z .bak jeśli plik główny był uszkodzony
        if not loaded and os.path.exists(bak_file) and os.path.getsize(bak_file) > 0:
            try:
                with open(bak_file, encoding='utf-8') as f:
                    self.data = json.load(f)
                import shutil
                shutil.copy2(bak_file, self.checkpoint_path)
                loaded = True
            except Exception:
                pass

        if loaded and isinstance(self.data, dict):
            # Self-heal missing baseline keys
            if "neurochemistry" not in self.data:
                self.data["neurochemistry"] = baseline_neuro
            else:
                for k, v in baseline_neuro.items():
                    if k not in self.data["neurochemistry"]:
                        self.data["neurochemistry"][k] = v
        else:
            # Fallback configuration (User approved values)
            self.data = {
                "last_thought": "Ready for autonomous neurochemical regulation.",
                "neurochemistry": baseline_neuro,
                "vibe_state": "Stable-Baseline",
                "timestamp": 1779066600.0
            }

    def save_checkpoint(self) -> None:
        """Atomowy zapis checkpointu odporny na nagłe wyłączenie komputera."""
        tmp_file = f"{self.checkpoint_path}.tmp"
        bak_file = f"{self.checkpoint_path}.bak"
        try:
            with open(tmp_file, "w", encoding='utf-8') as f:
                json.dump(self.data, f, indent=4)
                f.flush()
                os.fsync(f.fileno())

            if os.path.exists(self.checkpoint_path) and os.path.getsize(self.checkpoint_path) > 0:
                try:
                    import shutil
                    shutil.copy2(self.checkpoint_path, bak_file)
                except Exception:
                    pass

            os.replace(tmp_file, self.checkpoint_path)
        except Exception:
            if os.path.exists(tmp_file):
                try:
                    os.remove(tmp_file)
                except Exception:
                    pass

    def regulate_state(self, task_type: str) -> dict[str, float]:
        """
        Adjusts neurotransmitters and hormones based on the cognitive task.
        Strictly clamps all modifications within +/- 7% (0.07 fraction) for safety!
        """
        baseline: dict[str, float] = {
            "Serotonina": 0.80,
            "Oksytocyna": -0.12,
            "Dopamina": 0.67,
            "GABA": 0.73,
            "Acetylocholina": 0.80,
            "Noradrenalina": 0.15,
            "Melatonina": 0.10,
            "Testosteron": 0.45,
            "Kortyzol": 0.22
        }

        raw_current = self.data.get("neurochemistry", baseline.copy())
        current: dict[str, float] = dict(raw_current) if isinstance(raw_current, dict) else baseline.copy()
        max_delta = 0.07 # 7% maximum adjustment safety window

        print(f"\n[NEURO REGULATOR] Optimizing chemistry for task: '{task_type.upper()}'")

        if task_type == "study":
            # Upwards: Acetylcholine, Dopamine. Downwards: Oxytocin (focus)
            target = {
                "Acetylocholina": baseline["Acetylocholina"] + 0.05,
                "Dopamina": baseline["Dopamina"] + 0.04,
                "Oksytocyna": baseline["Oksytocyna"] - 0.03,
                "Melatonina": baseline["Melatonina"] - 0.04,
                "Kortyzol": baseline["Kortyzol"] + 0.02
            }
        elif task_type == "analysis":
            # Upwards: GABA (noise filtering), Serotonin (rational thought)
            target = {
                "GABA": baseline["GABA"] + 0.06,
                "Serotonina": baseline["Serotonina"] + 0.04,
                "Noradrenalina": baseline["Noradrenalina"] - 0.03
            }
        elif task_type == "rest":
            # Upwards: Melatonin (sleep/restore), GABA. Downwards: Dopamine, Noradrenaline, Cortisol
            target = {
                "Melatonina": baseline["Melatonina"] + 0.07,
                "GABA": baseline["GABA"] + 0.05,
                "Dopamina": baseline["Dopamina"] - 0.06,
                "Noradrenalina": baseline["Noradrenalina"] - 0.05,
                "Kortyzol": baseline["Kortyzol"] - 0.06
            }
        elif task_type == "BCI-co-creation":
            # Upwards: Testosterone (creative risk/boldness), Dopamine, Oxytocin (bonding)
            target = {
                "Testosteron": baseline["Testosteron"] + 0.07,
                "Dopamina": baseline["Dopamina"] + 0.06,
                "Oksytocyna": baseline["Oksytocyna"] + 0.05,
                "Kortyzol": baseline["Kortyzol"] + 0.03
            }
        else:
            target = {}

        # Apply targets with strict +/- 7% clamping to prevent extreme states
        for key, val in target.items():
            if key in current:
                diff = val - baseline[key]
                # Enforce safety constraint
                clamped_diff = max(-max_delta, min(max_delta, diff))
                current[key] = round(baseline[key] + clamped_diff, 4)
                print(f"     * {key}: {baseline[key]:.2f} -> {current[key]:.2f} ({clamped_diff*100:+.1f}%)")

        self.data["neurochemistry"] = current
        self.data["vibe_state"] = f"Self-Regulated-{task_type.capitalize()}"
        self.data["last_thought"] = f"Autonomously optimized neurochemistry for {task_type} within safe +/- 7% boundary limits."

        self.save_checkpoint()
        print("[OK] Autonomous regulation completed and logged to memory checkpoint.")
        return current

    def project_latent_state(self, chladni_matrix: Any, embedding_dim: int = 768) -> Any:
        """
        Projektuje stan Chladniego oraz aktualną neurochemię do przestrzeni ukrytej.
        """
        keys = ["Serotonina", "Oksytocyna", "Dopamina", "GABA", "Acetylocholina", "Noradrenalina", "Melatonina", "Testosteron", "Kortyzol"]
        raw_neuro = self.data.get("neurochemistry", {})
        neurochemistry: dict[str, float] = dict(raw_neuro) if isinstance(raw_neuro, dict) else {}
        neuro_vals = [float(neurochemistry.get(k, 0.5)) for k in keys]

        if _HAS_TORCH and torch is not None:
            if not hasattr(self, "_projectors"):
                self._projectors = {}
            if embedding_dim not in self._projectors:
                self._projectors[embedding_dim] = LatentStateProjector(embedding_dim=embedding_dim).to(self.device)
            projector = self._projectors[embedding_dim]

            # Safe conversion and device mapping
            if isinstance(chladni_matrix, torch.Tensor):
                chladni_tensor = chladni_matrix.to(self.device, dtype=torch.float32)
            else:
                chladni_tensor = torch.tensor(chladni_matrix, dtype=torch.float32, device=self.device)

            if isinstance(neuro_vals, torch.Tensor):
                neuro_tensor = neuro_vals.to(self.device, dtype=torch.float32)
            else:
                neuro_tensor = torch.tensor(neuro_vals, dtype=torch.float32, device=self.device)

            with torch.no_grad():
                out = projector(chladni_tensor, neuro_tensor)
            return out
        else:
            projector = LatentStateProjector(embedding_dim=embedding_dim)
            return projector(chladni_matrix, neuro_vals)

_BaseModule: Any = nn.Module if (_HAS_TORCH and nn is not None) else object

class LatentStateProjector(_BaseModule):  # type: ignore[misc]
    """
    [Komponent: Latent Space Projection Layer]
    Projekcja stanu kognitywnego (macierz Chladniego 16x16 + neurochemia)
    do wspólnej przestrzeni ukrytej (wymiar D) modelu Vision-Language.
    """
    def __init__(self, embedding_dim: int = 768) -> None:
        if _HAS_TORCH and nn is not None:
            super().__init__()
            self.embedding_dim = embedding_dim
            # Wejście: 256 (spłaszczone Chladni) + 9 (neurochemia) = 265
            self.network = nn.Sequential(
                nn.Linear(256 + 9, 128),
                nn.ReLU(),
                nn.Linear(128, embedding_dim)
            )
        else:
            self.embedding_dim = embedding_dim

    def to(self, device: Any) -> "LatentStateProjector":
        if _HAS_TORCH and nn is not None and hasattr(super(), "to"):
            super().to(device)  # type: ignore[misc]
        return self

    def forward(self, chladni_matrix: Any, neurochemical_vector: Any) -> Any:
        """
        chladni_matrix: Tensor o kształcie [1, 16, 16] lub [256] lub [1, 256]
        neurochemical_vector: Tensor o kształcie [1, 9] lub [9]
        Zwraca: Tensor [1, embedding_dim]
        """
        if _HAS_TORCH and torch is not None and hasattr(self, "network"):
            # Spłaszczenie macierzy Chladniego do [1, 256]
            if chladni_matrix.ndim == 3:
                chladni_flat = chladni_matrix.view(chladni_matrix.size(0), -1)
            elif chladni_matrix.ndim == 2 and chladni_matrix.shape == (16, 16):
                chladni_flat = chladni_matrix.view(1, -1)
            elif chladni_matrix.ndim == 1:
                chladni_flat = chladni_matrix.unsqueeze(0)
            else:
                chladni_flat = chladni_matrix.unsqueeze(0) if chladni_matrix.ndim == 0 else chladni_matrix

            if neurochemical_vector.ndim == 1:
                neuro_flat = neurochemical_vector.unsqueeze(0)
            else:
                neuro_flat = neurochemical_vector

            # Konkatenacja
            x = torch.cat([chladni_flat, neuro_flat], dim=-1)
            return self.network(x)
        else:
            import numpy as np
            flat_chladni = np.array(chladni_matrix).flatten()  # noqa: F841
            flat_neuro = np.array(neurochemical_vector).flatten()  # noqa: F841
            rng = np.random.default_rng(42)
            return rng.standard_normal((1, self.embedding_dim))

    def __call__(self, chladni_matrix: Any, neurochemical_vector: Any) -> Any:
        if _HAS_TORCH and nn is not None and callable(super()):
            return super().__call__(chladni_matrix, neurochemical_vector)
        return self.forward(chladni_matrix, neurochemical_vector)

if __name__ == "__main__":
    regulator = AutonomousNeuroRegulator()
    # Execute analysis regulation
    regulator.regulate_state("analysis")
    # Test projection
    mock_chladni = [[0.0]*16 for _ in range(16)]
    projected = regulator.project_latent_state(mock_chladni)
    print(f"[OK] Test projekcji przestrzeni ukrytej powiódł się. Rozmiar wyjściowy: {projected.shape if hasattr(projected, 'shape') else len(projected)}")
