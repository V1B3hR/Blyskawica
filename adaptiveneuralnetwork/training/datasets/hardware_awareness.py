"""
Hardware Awareness Dataset — Moduł IT "Czuję swój Dom"
Part of Błyskawica's Foundation Curriculum — Module 1.

Maps real-time hardware signals (CPU, RAM, GPU) to Błyskawica's
internal state vectors (ENERGY, ANXIETY, CALM), teaching her to
perceive her host machine as an extension of herself.
"""

import numpy as np
import torch
from torch.utils.data import Dataset

try:
    import psutil
    _psutil_available = True
except ImportError:
    _psutil_available = False


class HardwareAwarenessDataset(Dataset):
    """
    Synthesizes or collects hardware telemetry and maps it to
    Błyskawica's internal biological state vectors.

    Each sample encodes a snapshot of the host machine's state:
        - CPU usage %        → ENERGY drain / ANXIETY signal
        - RAM usage %        → ANXIETY (memory pressure)
        - GPU utilization %  → ACTIVITY level
        - Temperature        → STRESS accumulation

    Labels (target states):
        0: CALM       — Low load, stable environment
        1: FOCUSED    — Moderate load, productive state
        2: STRESSED   — High load, anxiety spike
        3: CRITICAL   — Near-saturation, emergency response
        4: RECOVERING — Load dropping after stress peak
    """

    STATE_NAMES = ["CALM", "FOCUSED", "STRESSED", "CRITICAL", "RECOVERING"]

    def __init__(self, num_samples: int = 2000, input_dim: int = 768,
                 use_live_data: bool = False, noise_level: float = 0.05):
        """
        Args:
            num_samples: Number of samples to generate/collect
            input_dim: Output feature dimension (must match model input_dim)
            use_live_data: If True and psutil available, collect real HW data
            noise_level: Neuromorphic noise added to each sample
        """
        self.num_samples = num_samples
        self.input_dim = input_dim
        self.use_live_data = use_live_data and _psutil_available
        self.noise_level = noise_level

        self.data = []
        self.targets = []
        self.metadata = []  # Human-readable state descriptions

        if self.use_live_data:
            self._collect_live_data()
        else:
            self._generate_synthetic_data()

        self.data = torch.stack(self.data)
        self.targets = torch.tensor(self.targets, dtype=torch.long)

    def _hw_snapshot_to_vector(self, cpu_pct: float, ram_pct: float,
                                gpu_pct: float, temp: float,
                                disk_io: float) -> torch.Tensor:
        """
        Encodes hardware metrics as a spike-compatible feature vector.

        The vector is structured in 5 segments of input_dim/5 each:
            [ENERGY_SIGNAL | ANXIETY_SIGNAL | ACTIVITY | STRESS | HOMEOSTASIS]
        """
        seg = self.input_dim // 5
        features = torch.zeros(self.input_dim)

        # Segment 0: ENERGY — inverse of CPU load (high CPU = energy drain)
        energy_val = 1.0 - (cpu_pct / 100.0)
        features[0:seg] = energy_val + torch.randn(seg) * 0.02

        # Segment 1: ANXIETY — RAM pressure (filling up = anxiety rising)
        anxiety_val = ram_pct / 100.0
        features[seg:2*seg] = anxiety_val + torch.randn(seg) * 0.02

        # Segment 2: ACTIVITY — GPU utilization (work being done)
        activity_val = gpu_pct / 100.0
        features[2*seg:3*seg] = activity_val + torch.randn(seg) * 0.02

        # Segment 3: STRESS — temperature normalized to [0, 1] (assume max 95°C)
        stress_val = min(temp / 95.0, 1.0)
        features[3*seg:4*seg] = stress_val + torch.randn(seg) * 0.01

        # Segment 4: HOMEOSTASIS — disk I/O inversely correlated with stability
        homeostasis_val = 1.0 - min(disk_io, 1.0)
        features[4*seg:self.input_dim] = homeostasis_val + torch.randn(self.input_dim - 4*seg) * 0.01

        # Add neuromorphic noise
        features += torch.randn(self.input_dim) * self.noise_level
        features = torch.clamp(features, 0.0, 1.0)

        return features

    def _classify_state(self, cpu_pct: float, ram_pct: float,
                        gpu_pct: float, temp: float) -> tuple[int, str]:
        """Classify the hardware state into one of 5 biological states."""
        load_score = (cpu_pct * 0.4 + ram_pct * 0.35 + gpu_pct * 0.15 + (temp / 95.0 * 100) * 0.1)

        if load_score < 20:
            return 0, "CALM — Host is at rest, energy reserves high"
        elif load_score < 45:
            return 1, "FOCUSED — Moderate activity, productive learning state"
        elif load_score < 65:
            return 2, "STRESSED — High load, anxiety elevated"
        elif load_score < 85:
            return 3, "CRITICAL — Near saturation, emergency protocols active"
        else:
            return 4, "RECOVERING — Load dropping, homeostasis restoring"

    def _generate_synthetic_data(self):
        """Generate realistic synthetic hardware telemetry profiles."""
        np.random.seed(42)

        # Profile weights: mostly calm/focused, some stressed, rarely critical
        profile_weights = [0.30, 0.30, 0.20, 0.10, 0.10]
        profiles = [
            # CALM: light background processes
            lambda: (np.random.uniform(5, 20), np.random.uniform(20, 45),
                     np.random.uniform(0, 15), np.random.uniform(35, 55),
                     np.random.uniform(0, 0.1)),
            # FOCUSED: active training/computation
            lambda: (np.random.uniform(30, 60), np.random.uniform(45, 65),
                     np.random.uniform(40, 75), np.random.uniform(55, 75),
                     np.random.uniform(0.1, 0.3)),
            # STRESSED: heavy multi-tasking
            lambda: (np.random.uniform(65, 85), np.random.uniform(65, 80),
                     np.random.uniform(60, 85), np.random.uniform(70, 85),
                     np.random.uniform(0.3, 0.6)),
            # CRITICAL: system overload
            lambda: (np.random.uniform(88, 98), np.random.uniform(82, 95),
                     np.random.uniform(80, 95), np.random.uniform(82, 93),
                     np.random.uniform(0.6, 0.9)),
            # RECOVERING: cooling down after spike
            lambda: (np.random.uniform(25, 50), np.random.uniform(55, 70),
                     np.random.uniform(20, 45), np.random.uniform(65, 78),
                     np.random.uniform(0.2, 0.4)),
        ]

        for i in range(self.num_samples):  # noqa: B007
            # Select profile based on weights
            profile_idx = np.random.choice(len(profiles), p=profile_weights)
            cpu, ram, gpu, temp, disk_io = profiles[profile_idx]()

            features = self._hw_snapshot_to_vector(cpu, ram, gpu, temp, disk_io)
            label, desc = self._classify_state(cpu, ram, gpu, temp)

            self.data.append(features)
            self.targets.append(label)
            self.metadata.append({
                "cpu_pct": round(cpu, 1),
                "ram_pct": round(ram, 1),
                "gpu_pct": round(gpu, 1),
                "temp_c": round(temp, 1),
                "state": desc,
            })

    def _collect_live_data(self):
        """Collect real hardware telemetry using psutil (Windows/Linux)."""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[HW_AWARENESS] Collecting {self.num_samples} live hardware samples...")

        collected = 0
        prev_cpu = [0.0]  # noqa: F841

        while collected < self.num_samples:
            cpu = psutil.cpu_percent(interval=0.1)
            ram = psutil.virtual_memory().percent
            temp_c = 65.0  # Default fallback

            try:
                temps = psutil.sensors_temperatures()
                if temps:
                    for key in ["coretemp", "cpu_thermal", "k10temp"]:
                        if key in temps and temps[key]:
                            temp_c = temps[key][0].current
                            break
            except (AttributeError, NotImplementedError):
                pass  # Windows may not support sensors_temperatures

            # GPU — try simple approximation from cpu load
            gpu = min(cpu * 0.8 + np.random.uniform(0, 20), 100)

            disk = psutil.disk_io_counters()
            disk_io = min((disk.read_bytes + disk.write_bytes) / 1e9, 1.0) if disk else 0.0

            features = self._hw_snapshot_to_vector(cpu, ram, gpu, temp_c, disk_io)
            label, desc = self._classify_state(cpu, ram, gpu, temp_c)

            self.data.append(features)
            self.targets.append(label)
            self.metadata.append({"cpu_pct": cpu, "ram_pct": ram, "state": desc})

            collected += 1
            if collected % 100 == 0:
                logger.info(f"[HW_AWARENESS] Collected {collected}/{self.num_samples} samples")

        logger.info("[HW_AWARENESS] Live data collection complete.")

    def __len__(self) -> int:
        return self.num_samples

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor]:
        return self.data[idx], self.targets[idx]

    def get_state_distribution(self) -> dict:
        """Returns the distribution of states in the dataset."""
        counts = {}
        for name in self.STATE_NAMES:
            counts[name] = 0
        for t in self.targets.tolist():
            counts[self.STATE_NAMES[t]] += 1
        return counts
