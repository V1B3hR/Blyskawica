"""Regression tests for coherent NVIDIA GPU-memory-mode reporting."""

from adaptiveneuralnetwork.utils import reproducibility
from adaptiveneuralnetwork.utils.reproducibility import get_coherent_gpu_memory_mode


def test_reads_driver_cdmm_mode_from_nvidia_params(tmp_path):
    params = tmp_path / "nvidia-params"
    params.write_text('OtherOption: 1\nCoherentGPUMemoryMode: "driver"\n', encoding="utf-8")

    assert get_coherent_gpu_memory_mode(params) == "driver"


def test_reads_numa_mode_from_nvidia_params(tmp_path):
    params = tmp_path / "nvidia-params"
    params.write_text("CoherentGPUMemoryMode: numa\n", encoding="utf-8")

    assert get_coherent_gpu_memory_mode(params) == "numa"


def test_returns_none_when_the_nvidia_params_file_is_unavailable(tmp_path):
    assert get_coherent_gpu_memory_mode(tmp_path / "missing") is None


def test_returns_none_for_an_unknown_mode(tmp_path):
    params = tmp_path / "nvidia-params"
    params.write_text("CoherentGPUMemoryMode: unsupported\n", encoding="utf-8")

    assert get_coherent_gpu_memory_mode(params) is None


def test_environment_snapshot_includes_the_observed_coherent_memory_mode(monkeypatch):
    monkeypatch.setattr(reproducibility, "get_coherent_gpu_memory_mode", lambda: "driver")

    snapshot = reproducibility.EnvironmentSnapshot.capture()

    assert snapshot.coherent_gpu_memory_mode == "driver"
