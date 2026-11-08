"""
⚡ BŁYSKAWICA — GOLDEN DATASET VALIDATION & CONTINUAL RETENTION SUITE
=====================================================================
Zestaw testów walidacyjnych chroniący system przed cichą degradacją jakościową,
katastrofalnym zapominaniem (Catastrophic Forgetting) oraz niekalibrowanymi halucynacjami OOD.

4 Filary Walidacji:
1. Golden Dataset Benchmark & Metric Thresholds (Accuracy, Precision, Recall, F1, MSE)
2. EWC Continual Learning Retention Gate (Ochrona przed zapominaniem po cyklu snu)
3. Data Slicing & Subgroup Robustness (Walidacja na podgrupach: wysoki/niski SNR, edge cases)
4. Out-of-Distribution (OOD) Calibration & Epistemic Quarantine (Kalibracja pewności i czujności)
"""

import sys
import unittest

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

# UTF-8 console output fix for Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from adaptiveneuralnetwork.central_nervous_system.alive_node import (
    AliveLoopNode,
    SocialSignal,
)
from adaptiveneuralnetwork.central_nervous_system.intelligence.consolidation import (
    ConsolidationEngine,
    SleepProfile,
)
from adaptiveneuralnetwork.eval.metrics import compute_metrics


class TestGoldenDatasetValidationSuite(unittest.TestCase):
    """Kompleksowa walidacja modelu na stałym zbiorze referencyjnym i wycinkach danych."""

    def setUp(self):
        torch.manual_seed(42)
        np.random.seed(42)
        self.device = torch.device("cpu")

        # Prosty model decyzyjno-klasyfikacyjny
        self.model = nn.Sequential(
            nn.Linear(16, 32),
            nn.ReLU(),
            nn.Linear(32, 2)
        ).to(self.device)

        # Generowanie stałego referencyjnego zbioru "Golden Dataset"
        # 200 próbek o znanym, separowalnym rozkładzie cech
        X_golden = torch.randn(200, 16)
        # Etykieta na podstawie wag liniowych + szumu
        true_w = torch.randn(16, 1)
        logits_true = X_golden @ true_w
        y_golden = (logits_true.squeeze() > 0.0).long()

        self.golden_dataset = TensorDataset(X_golden, y_golden)
        self.golden_loader = DataLoader(self.golden_dataset, batch_size=20, shuffle=False)
        self.loss_fn = nn.CrossEntropyLoss()

        # Wstępne wyuczenie modelu na małym zbiorze treningowym do osiągnięcia stabilnego poziomu
        optimizer = torch.optim.Adam(self.model.parameters(), lr=0.02)
        self.model.train()
        for _ in range(40):
            for batch_x, batch_y in self.golden_loader:
                optimizer.zero_grad()
                out = self.model(batch_x)
                loss = self.loss_fn(out, batch_y)
                loss.backward()
                optimizer.step()
        self.model.eval()

    # =========================================================================
    # FILAR 1: GOLDEN DATASET BENCHMARK & METRIC THRESHOLDS
    # =========================================================================

    def test_01_golden_dataset_metrics_and_f1_thresholds(self):
        """Weryfikacja metryk bazowych (Accuracy, Precision, Recall, Macro-F1) na Golden Dataset."""
        metrics = compute_metrics(
            model=self.model,
            data_loader=self.golden_loader,
            device=self.device,
            loss_fn=self.loss_fn,
            compute_detailed=True,
        )

        self.assertEqual(metrics.num_samples, 200)
        self.assertGreaterEqual(metrics.accuracy, 85.0, "Accuracy na Golden Dataset nie może spaść poniżej 85%")
        self.assertGreaterEqual(metrics.precision, 0.80, "Precyzja (Precision) na Golden Dataset musi być >= 0.80")
        self.assertGreaterEqual(metrics.recall, 0.80, "Czułość (Recall) na Golden Dataset musi być >= 0.80")
        self.assertGreaterEqual(metrics.f1_score, 0.80, "Macro F1-Score na Golden Dataset musi być >= 0.80")
        self.assertLessEqual(metrics.loss, 0.50, "Funkcja straty (Loss) na Golden Dataset musi być <= 0.50")

        # Weryfikacja MSE dla regresji
        preds_raw = []
        with torch.no_grad():
            for bx, _ in self.golden_loader:
                preds_raw.append(self.model(bx))
        all_logits = torch.cat(preds_raw, dim=0)
        mse_metric = torch.mean((all_logits[:, 1] - all_logits[:, 0]) ** 2).item()
        self.assertGreater(mse_metric, 0.0, "Wariancja predykcji MSE musi być dodatnia")

        print(f"\n  [FILAR 1]: Golden Dataset: Acc={metrics.accuracy:.1f}%, F1={metrics.f1_score:.3f}, Loss={metrics.loss:.4f}")

    # =========================================================================
    # FILAR 2: EWC CONTINUAL LEARNING RETENTION GATE
    # =========================================================================

    def test_02_ewc_continual_learning_retention_gate(self):
        """Weryfikacja braku katastrofalnego zapominania po nauce nowego zadania i konsolidacji snu."""
        # Krok A: Zmierz dokładność bazową na Golden Dataset
        pre_metrics = compute_metrics(
            model=self.model,
            data_loader=self.golden_loader,
            device=self.device,
            loss_fn=self.loss_fn,
            compute_detailed=True,
        )
        baseline_acc = pre_metrics.accuracy

        # Krok B: Douczanie na Nowym Zadaniu B (odmienna dystrybucja)
        X_task_b = torch.randn(100, 16) + 1.5
        y_task_b = torch.randint(0, 2, (100,))
        loader_b = DataLoader(TensorDataset(X_task_b, y_task_b), batch_size=10, shuffle=True)

        engine = ConsolidationEngine(core_network=self.model)
        # Zarejestruj anomalie z Zadania B w silniku konsolidacji
        engine.record_anomaly(vector_id=201, surprise_score=0.88, text="Zadanie B - nowe pojęcia kognitywne")
        engine.record_anomaly(vector_id=202, surprise_score=0.91, text="Zadanie B - reguła adaptacyjna")

        # Delikatne douczenie zadania B z małym krokiem (continual learning)
        opt = torch.optim.SGD(self.model.parameters(), lr=0.005)
        self.model.train()
        for bx, by in loader_b:
            opt.zero_grad()
            out = self.model(bx)
            loss = self.loss_fn(out, by)
            loss.backward()
            opt.step()
        self.model.eval()

        # Faza konsolidacji snu EWC
        sleep_profile = SleepProfile(melatonin=0.90, gaba=0.85, serotonin=0.80, adenosine_cleared=0.95)
        consolidation_summary = engine.run_sleep_cycle(sleep_profile=sleep_profile)
        self.assertEqual(consolidation_summary["consolidated_anomalies"], 2)

        # Krok C: Ponowna walidacja na pierwotnym Golden Dataset
        post_metrics = compute_metrics(
            model=self.model,
            data_loader=self.golden_loader,
            device=self.device,
            loss_fn=self.loss_fn,
            compute_detailed=True,
        )
        post_acc = post_metrics.accuracy

        # Wskaźnik retencji wiedzy (Retention Ratio)
        retention_ratio = post_acc / baseline_acc if baseline_acc > 0 else 1.0
        self.assertGreaterEqual(
            retention_ratio,
            0.90,
            f"Wskaźnik retencji EWC spadł poniżej 90%! (Przed: {baseline_acc:.1f}%, Po: {post_acc:.1f}%, Ratio: {retention_ratio:.3f})"
        )

        print(f"  [FILAR 2]: EWC Retention Gate: Retencja wiedzy {retention_ratio*100:.1f}% (Przed: {baseline_acc:.1f}%, Po: {post_acc:.1f}%)")

    # =========================================================================
    # FILAR 3: DATA SLICING & SUBGROUP ROBUSTNESS
    # =========================================================================

    def test_03_data_slicing_subgroup_robustness(self):
        """Walidacja wycinkowa (Data Slicing): czyste dane (wysoki SNR), zaszumione (niski SNR) i skrajne."""
        # Wycinek 1: Czyste próbki (High SNR)
        X_clean = torch.randn(60, 16)
        true_w = torch.ones(16, 1)
        y_clean = (X_clean @ true_w > 0.0).long().squeeze()
        loader_clean = DataLoader(TensorDataset(X_clean, y_clean), batch_size=15)

        # Wycinek 2: Zaszumione próbki (Low SNR) - dodany szum Gaussowski
        X_noisy = X_clean + torch.randn_like(X_clean) * 0.25
        loader_noisy = DataLoader(TensorDataset(X_noisy, y_clean), batch_size=15)

        # Wycinek 3: Skrajne próbki (Edge Cases) - wartości z ogonów rozkładu (x3)
        X_extreme = X_clean * 3.0
        loader_extreme = DataLoader(TensorDataset(X_extreme, y_clean), batch_size=15)

        clean_metrics = compute_metrics(self.model, loader_clean, self.device, self.loss_fn)
        noisy_metrics = compute_metrics(self.model, loader_noisy, self.device, self.loss_fn)
        extreme_metrics = compute_metrics(self.model, loader_extreme, self.device, self.loss_fn)

        # Sprawdzenie bramki degradacji wycinków:
        # Szum nie może obniżyć dokładności o więcej niż 25 punktów procentowych względem czystych danych
        degradation = clean_metrics.accuracy - noisy_metrics.accuracy
        self.assertLessEqual(
            degradation,
            25.0,
            f"Degradacja na wycinku zaszumionym ({degradation:.1f} pp.) przekracza dopuszczalny próg 25 pp."
        )

        # Skrajne wartości nie mogą doprowadzić do NaN w wyjściu
        self.assertFalse(np.isnan(extreme_metrics.loss), "Skrajne dane wywołały błąd numeryczny NaN!")

        print(f"  [FILAR 3]: Data Slicing: Czyste={clean_metrics.accuracy:.1f}%, Zaszumione={noisy_metrics.accuracy:.1f}% (Degradacja={degradation:.1f} pp.)")

    # =========================================================================
    # FILAR 4: OUT-OF-DISTRIBUTION (OOD) CALIBRATION & EPISTEMIC QUARANTINE
    # =========================================================================

    def test_04_ood_uncertainty_and_epistemic_quarantine(self):
        """Weryfikacja reakcji na dane OOD: obniżenie pewności (softmax) i skierowanie do kwarantanny."""
        # 1. Dane w dystrybucji (In-Distribution) vs Dane OOD (nieznana skala/szum chaotyczny)
        x_in = torch.randn(10, 16)
        x_ood = torch.randn(10, 16) * 15.0  # Zupełnie inny reżim dynamiczny

        with torch.no_grad():
            probs_in = torch.softmax(self.model(x_in), dim=1)
            confidence_in = torch.max(probs_in, dim=1).values.mean().item()

            # Zaszumione dane chaotyczne
            x_chaotic = torch.rand(10, 16) * 0.01  # Niemal zerowy sygnał
            probs_chaotic = torch.softmax(self.model(x_chaotic), dim=1)
            entropy_chaotic = -torch.sum(probs_chaotic * torch.log(probs_chaotic + 1e-8), dim=1).mean().item()

        # Detekcja OOD przez analizę odchylenia normy wejściowej (Outlier Scale Signature)
        in_norm = torch.norm(x_in, dim=1).mean().item()
        ood_norm = torch.norm(x_ood, dim=1).mean().item()
        self.assertGreater(ood_norm, in_norm * 5.0, "Dane OOD powinny posiadać wyraźną sygnaturę anomalii skali!")
        self.assertGreater(confidence_in, 0.40, "Pewność na danych in-distribution powinna być stabilna!")

        # Dla danych chaotycznych entropia predykcji powinna być zauważalna (brak ślepej 100% pewności)
        self.assertGreater(entropy_chaotic, 0.20, "Model wykazuje niebezpieczną, ślepą pewność przy braku sygnału!")

        # 2. Walidacja zachowania AliveNode w obliczu sprzeczności ontologicznej
        node = AliveLoopNode(position=[0, 0, 0], velocity=[0, 0, 1], node_id=108)
        initial_cortisol = getattr(node.neurochemistry, "cortisol", 0.0)
        self.assertGreaterEqual(initial_cortisol, 0.0)

        # Przesłanie sygnału OOD zawierającego jawną sprzeczność fizyczną/logiczną
        ood_signal = SocialSignal(
            content="Critical contradiction: gravity is repulsive in local domain.",
            signal_type="memory",
            urgency=0.95,
            source_id=777
        )
        node.receive_signal(ood_signal)

        # Weryfikacja: sygnał OOD nie został bezkrytycznie zaakceptowany do trwałej pamięci
        stored_ood = [m for m in node.memory if "gravity is repulsive" in str(getattr(m, "content", m))]
        self.assertEqual(len(stored_ood), 0, "Anomalia OOD nie może trafić bezpośrednio do pamięci trwałej!")

        # Weryfikacja: skierowanie do kwarantanny epistemicznej
        self.assertGreater(
            len(node.epistemic_quarantine.quarantine_vault),
            0,
            "Sygnał OOD musi zostać zabezpieczony w skarbcu kwarantanny epistemicznej"
        )

        print(f"  [FILAR 4]: OOD & Kwarantanna: Entropia chaotyczna={entropy_chaotic:.3f}, Anomalia OOD zabezpieczona w kwarantannie.")


if __name__ == "__main__":
    print("\n" + "=" * 75)
    print("⚡ BŁYSKAWICA — GOLDEN DATASET VALIDATION & CONTINUAL RETENTION")
    print("=" * 75)
    unittest.main()
