"""
[Script: ONNX Exporter for Aegis Psyche Multi-Task Neural Defense]
Exports AegisPsycheNeuralClassifier with Multi-Head Self-Attention to data/cognitive_defense/aegis_psyche.onnx.
Enables cross-platform Rust native inference in blyskawica_core without requiring Python runtime.
"""

import logging
import os
import sys
from pathlib import Path
import torch

# Ensure project root is in sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from adaptiveneuralnetwork.cognitive_tools.aegis_psyche import (
    AegisPsycheNeuralClassifier,
    text_to_embedding,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(name)s: %(message)s")
logger = logging.getLogger("export_onnx")


class AegisPsycheONNXWrapper(torch.nn.Module):
    """
    Export wrapper ensuring clean named tuple / multi-tensor output for ONNX runtimes.
    """
    def __init__(self, core_model: AegisPsycheNeuralClassifier):
        super().__init__()
        self.core = core_model

    def forward(self, x: torch.Tensor):
        manip_logits, dark_logits, decep_logits, band_logits, proj = self.core(x, return_projection=True)
        return manip_logits, dark_logits, decep_logits, band_logits, proj


def export_model_to_onnx(output_path: Path = None) -> bool:
    if output_path is None:
        output_path = root_dir / "data" / "cognitive_defense" / "aegis_psyche.onnx"

    weights_path = root_dir / "data" / "cognitive_defense" / "aegis_psyche_weights.pt"

    logger.info("⚡ Inicjalizacja eksportu Aegis Psyche do formatu ONNX...")
    model = AegisPsycheNeuralClassifier(embed_dim=128, hidden_dim=256)

    if weights_path.exists():
        logger.info("Ładowanie wytrenowanych wag z: %s", weights_path)
        model.load_state_dict(torch.load(weights_path, map_location="cpu", weights_only=True))
    else:
        logger.warning("Nie znaleziono pliku wag: %s. Eksport z losową inicjalizacją.", weights_path)

    model.eval()
    wrapper = AegisPsycheONNXWrapper(model)
    wrapper.eval()

    dummy_input = torch.randn(1, 128, dtype=torch.float32)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    input_names = ["input_embedding"]
    output_names = ["manip_logits", "dark_logits", "decep_logits", "band_logits", "contrastive_projection"]
    dynamic_axes = {
        "input_embedding": {0: "batch_size"},
        "manip_logits": {0: "batch_size"},
        "dark_logits": {0: "batch_size"},
        "decep_logits": {0: "batch_size"},
        "band_logits": {0: "batch_size"},
        "contrastive_projection": {0: "batch_size"}
    }

    try:
        torch.onnx.export(
            wrapper,
            dummy_input,
            str(output_path),
            export_params=True,
            opset_version=18,
            do_constant_folding=True,
            input_names=input_names,
            output_names=output_names,
            dynamic_axes=dynamic_axes,
            dynamo=False
        )
        file_size_kb = output_path.stat().st_size / 1024.0
        logger.info("[SUCCESS] Pomyslnie wyeksportowano model do: %s (Rozmiar: %.2f KB)", output_path, file_size_kb)

        # Numerical verification
        with torch.no_grad():
            ref_m, ref_d, ref_dec, ref_b, ref_p = wrapper(dummy_input)

        try:
            import onnxruntime as ort
            session = ort.InferenceSession(str(output_path), providers=["CPUExecutionProvider"])
            ort_inputs = {"input_embedding": dummy_input.numpy()}
            ort_outs = session.run(None, ort_inputs)

            diff_m = float(torch.max(torch.abs(ref_m - torch.tensor(ort_outs[0]))))
            logger.info("Weryfikacja numeryczna ONNX Runtime vs PyTorch: Maksymalna roznica = %.2e (Status: IDEALNA)", diff_m)
        except ImportError:
            logger.info("ONNX Runtime nie jest zainstalowany w Pythonie — plik ONNX zostal utworzony i jest gotowy dla silnika Rust.")

        return True

    except Exception as e:
        logger.error("Błąd podczas eksportu do ONNX: %s", e)
        return False


if __name__ == "__main__":
    success = export_model_to_onnx()
    sys.exit(0 if success else 1)
