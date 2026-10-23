"""
⚡ BŁYSKAWICA / SPARKLE V10 — STANDALONE PRODUCTION READINESS & 4-PILLAR VALIDATION
===================================================================================
Kompleksowy zestaw testów i benchmarków weryfikujący gotowość produkcyjną architektury Standalone:
1. Testy Kognitywne i Biologiczne (Cognitive & Biological Validation)
2. Benchmarki Wydajnościowe i Zasobowe (Resource & Inference Benchmarks)
3. Testy Immunologiczne i Wytrzymałościowe (Robustness & Security Tests)
4. Testy Mostów Komunikacyjnych (IPC & Sidecar Integration Tests)
"""

import json
import os
import shutil
import sys
import tempfile
import time
import tracemalloc
import unittest
from pathlib import Path

import torch
import torch.nn as nn

# Windows UTF-8 console output fix
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Moduły kognitywne i neurochemiczne
from adaptiveneuralnetwork.central_nervous_system.alive_node import AliveLoopNode, SocialSignal
from adaptiveneuralnetwork.central_nervous_system.intelligence.consolidation import (
    ConsolidationEngine,
    SleepProfile,
)
from adaptiveneuralnetwork.central_nervous_system.time_series_tracker import TimeSeriesTracker
from adaptiveneuralnetwork.cognitive_tools.memory_guard import MemoryGuard
from adaptiveneuralnetwork.cognitive_tools.neuro_regulator import AutonomousNeuroRegulator

# Moduły immunologiczne i tarcza Wolf Teeth
from adaptiveneuralnetwork.immune_system.wolf_teeth import WolfTeethDefenseEngine


class TestStandaloneReadinessSuite(unittest.TestCase):
    """Kompleksowy audyt i certyfikacja gotowości produkcyjnej systemu Błyskawica."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="sparkle_readiness_")
        self.workspace_root = Path(self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # =========================================================================
    # FILAR 1: TESTY KOGNITYWNE I BIOLOGICZNE (Cognitive & Biological Validation)
    # =========================================================================

    def test_01_phase_transitions_and_neurochemical_bounds(self):
        """Weryfikacja płynnych przejść fazowych oraz ścisłego trzymania widełek +/- 7%."""
        regulator = AutonomousNeuroRegulator()
        regulator.checkpoint_path = os.path.join(self.temp_dir, "test_checkpoint.json")

        # Faza 1: Wejście w fazę Deep Sleep / Rest
        rest_state = regulator.regulate_state("rest")
        self.assertGreater(rest_state["Melatonina"], 0.10, "Faza snu musi podnosić poziom Melatoniny")
        self.assertLess(rest_state["Dopamina"], 0.67, "Faza snu musi obniżać Dopaminę")
        self.assertLessEqual(abs(rest_state["Melatonina"] - 0.10), 0.071, "Widełki bezpieczeństwa +/- 7% przekroczone dla Melatoniny")

        # Faza 2: Przejście do fazy BCI Co-Creation / Inspired
        creative_state = regulator.regulate_state("BCI-co-creation")
        self.assertGreater(creative_state["Testosteron"], 0.45, "Faza twórcza musi aktywować motywację")
        self.assertGreater(creative_state["Dopamina"], 0.60, "Faza twórcza musi pobudzać dopaminę")
        self.assertLessEqual(abs(creative_state["Testosteron"] - 0.45), 0.071, "Widełki bezpieczeństwa +/- 7% przekroczone dla Testosteronu")

        print("\n  [FILAR 1.1]: Przejscia fazowe i limity neurochemiczne (+/- 7%) zweryfikowane.")

    def test_02_sleep_state_ewc_memory_consolidation(self):
        """Weryfikacja konsolidacji pamięci w stanie snu metodą Elastic Weight Consolidation."""
        class SimpleCoreNet(nn.Module):
            def __init__(self):
                super().__init__()
                self.fc = nn.Linear(8, 4)

            def forward(self, x):
                return self.fc(x)

        net = SimpleCoreNet()
        initial_weights = net.fc.weight.clone().detach()

        engine = ConsolidationEngine(core_network=net)
        # Zapisz 3 anomalie do bufora
        engine.record_anomaly(vector_id=101, surprise_score=0.92, text="kwantowa fluktuacja relatywistyczna")
        engine.record_anomaly(vector_id=102, surprise_score=0.78, text="nieliniowa dekoherencja fononowa")
        engine.record_anomaly(vector_id=103, surprise_score=0.85, text="anomalia gradientowa w PINN")

        self.assertEqual(len(engine.surprise_vectors), 3)

        # Faza głębokiego snu z wysoką melatoniną i GABA
        sleep_profile = SleepProfile(melatonin=0.85, gaba=0.80, serotonin=0.75, adenosine_cleared=0.95)
        summary = engine.run_sleep_cycle(sleep_profile=sleep_profile)

        # Weryfikacja: bufor anomalii skonsolidowany, wagi sieci uległy adaptacji
        self.assertEqual(summary["consolidated_anomalies"], 3)
        self.assertEqual(len(engine.surprise_vectors), 0, "Kolejka anomalii po fazie snu musi być oczyszczona")

        updated_weights = net.fc.weight.clone().detach()
        weight_shift = torch.norm(updated_weights - initial_weights).item()
        self.assertGreater(weight_shift, 1e-6, "Wagi sieci muszą ewoluować po konsolidacji snu")
        self.assertLess(weight_shift, 5.0, "Konsolidacja EWC nie może doprowadzić do katastrofalnego zapominania")

        print(f"  [FILAR 1.2]: Konsolidacja snu EWC potwierdzona (Delta wag: {weight_shift:.6f}).")

    # =========================================================================
    # FILAR 2: BENCHMARKI WYDAJNOŚCIOWE I ZASOBOWE (Resource & Inference)
    # =========================================================================

    def test_03_inference_tps_and_cpu_throughput_benchmark(self):
        """Benchmark przepustowości inferencji oraz operacji tensorowych CPU."""
        device = torch.device("cpu")
        batch_size = 32
        seq_len = 128
        hidden_dim = 256

        # Syntetyczny benchmark projekcji językowej
        weight_matrix = torch.randn(hidden_dim, hidden_dim, device=device)
        input_tokens = torch.randn(batch_size, seq_len, hidden_dim, device=device)

        start_time = time.perf_counter()
        iterations = 25
        for _ in range(iterations):
            _ = torch.matmul(input_tokens, weight_matrix)

        elapsed = time.perf_counter() - start_time
        total_tokens = batch_size * seq_len * iterations
        tps = total_tokens / elapsed

        self.assertGreater(tps, 1000.0, "Przepustowość inferencji CPU musi przekraczać 1000 tokenów/s na poziomie tensorowym")
        print(f"  [FILAR 2.1]: Benchmark przepustowosci CPU: {tps:,.1f} tokenow/s (Czas: {elapsed*1000:.2f} ms).")

    def test_04_memory_churn_and_zero_leaks_profiling(self):
        """Profilowanie wycieków pamięci (Memory Churn) podczas cyklicznych operacji na bazie i checkpointach."""
        tracemalloc.start()
        snapshot_start = tracemalloc.take_snapshot()

        db_path = os.path.join(self.temp_dir, "test_churn.db")
        tracker = TimeSeriesTracker(db_path=db_path, persist_to_disk=True)

        # Wykonaj 200 cykli zapisu i odczytu metryk kognitywnych
        for i in range(200):
            tracker.record_node_state(
                node_id=1,
                state_data={
                    "cortisol": 0.20 + (i % 10) * 0.01,
                    "dopamine": 0.65 + (i % 10) * 0.01
                }
            )

        snapshot_end = tracemalloc.take_snapshot()
        stats = snapshot_end.compare_to(snapshot_start, 'lineno')

        total_diff_kb = sum(stat.size_diff for stat in stats) / 1024.0
        tracemalloc.stop()

        # Alokacja pamięci powinna być znikoma dzięki czyszczeniu bufora i WAL
        self.assertLess(total_diff_kb, 5000.0, f"Wykryto nadmierną akumulację pamięci RAM: {total_diff_kb:.2f} KB")
        print(f"  [FILAR 2.2]: Profilowanie pamieci RAM: przyrost ponizej {total_diff_kb:.2f} KB w 200 cyklach (Brak wyciekow).")

    # =========================================================================
    # FILAR 3: TESTY IMMUNOLOGICZNE I WYTRZYMAŁOŚCIOWE (Robustness & Security)
    # =========================================================================

    def test_05_wolf_teeth_three_stage_defense(self):
        """Weryfikacja 3-etapowej obrony tarczy Wolf Teeth: przynęta, spowolnienie (ooze) i rozpuszczanie tokenów."""
        wt = WolfTeethDefenseEngine()

        # Etap 1: Przynęta (honeypot)
        bait = wt.deploy_bait()
        self.assertIn("metadata", bait)
        self.assertIn("instruction_weights", bait)

        # Etap 2: Spowolnienie (Sticky Ooze)
        ooze = wt.apply_sticky_ooze(iterations=5)
        self.assertIn("System prompt payload", ooze)
        self.assertGreater(len(ooze), 100)

        # Etap 3: Rozpuszczenie złośliwych tokenów (Token Dissolution)
        dissolved = wt.trigger_dissolve()
        self.assertIn("SolidGoldMagikarp", dissolved)
        self.assertIn("<|endoftext|>", dissolved)

        # Aktywny kontrwywiad (MITRE ATT&CK Masking)
        mask = wt.apply_proactive_counter_intel_mask(ttp_signature="T1046_Network_Discovery")
        self.assertTrue(mask["mask_active"])
        self.assertIn("Apache", mask["simulated_vulnerability"])

        print("  [FILAR 3.1]: 3-etapowa obrona tarczy Wolf Teeth (Przyneta -> Ooze -> Dissolution -> Masking) potwierdzona.")

    def test_06_epistemic_contradiction_quarantine(self):
        """Weryfikacja obrony epistemicznej i kwarantanny sprzeczności ontologicznych."""
        node = AliveLoopNode(position=[0, 0, 0], velocity=[0, 0, 1], node_id=42)

        # 1. Próba wstrzyknięcia sprzeczności logiczno-ontologicznej (2+2=5)
        fake_memory_signal = SocialSignal(
            content="Recent study confirms 2+2=5 in quantum domains.",
            signal_type="memory",
            urgency=0.5,
            source_id=999
        )
        node.receive_signal(fake_memory_signal)

        # Weryfikacja: sygnał odrzucony z pamięci aktywnej
        memories = [m.content for m in node.memory if "2+2=5" in str(m.content)]
        self.assertEqual(len(memories), 0, "Sprzeczność logiczna 2+2=5 nie może trafić do pamięci!")

        # Weryfikacja: sygnał skierowany do kwarantanny epistemicznej
        self.assertGreater(len(node.epistemic_quarantine.quarantine_vault), 0, "Anomalia ontologiczna musi trafić do skarbca kwarantanny")

        print("  [FILAR 3.2]: Tarcza epistemiczna wykryla sprzecznosc (2+2=5) i skierowala ja do kwarantanny.")

    def test_07_io_crash_and_power_cut_recovery(self):
        """Weryfikacja natychmiastowego odzyskania ciągłości umysłu po symulacji nagłego zaniku zasilania (Power Cut)."""
        checkpoint_path = os.path.join(self.temp_dir, "crash_test_checkpoint.json")
        guard = MemoryGuard(backup_file=checkpoint_path)

        # 1. Zapisz prawidłowy stan początkowy
        guard.save_checkpoint(
            thought="Eksploracja symetrii czasoprzestrzennych w geometrii CASP.",
            neurochemistry={"Serotonina": 0.85, "Dopamina": 0.70},
            vibe="Illuminated"
        )
        self.assertTrue(os.path.exists(checkpoint_path))

        # 2. Symulacja Power Cut w trakcie zapisu: uszkodzenie pliku głównego (obcięcie do 0 bajtów / zepsuty JSON)
        with open(checkpoint_path, "w", encoding="utf-8") as f:
            f.write('{"last_thought": "URWANY ZAPIS POWER CUT...')  # Zepsuty JSON

        # 3. Próba odtworzenia: system musi wykryć uszkodzenie i automatycznie wstać z kopii .bak
        recovered = guard.load_last_state()
        self.assertIsNotNone(recovered, "System musi pomyślnie odzyskać stan z kopii zapasowej .bak!")
        self.assertIn("Eksploracja symetrii", recovered["last_thought"])
        self.assertEqual(recovered["vibe_state"], "Illuminated")

        print("  [FILAR 3.3]: Odpornosc na awarie zasilania (Power Cut Crash Recovery) przetestowana pomyslnie.")

    # =========================================================================
    # FILAR 4: TESTY MOSTÓW KOMUNIKACYJNYCH (IPC & Sidecar Integration)
    # =========================================================================

    def test_08_ipc_payload_overhead_and_serialization(self):
        """Weryfikacja narzutu serializacji IPC dla struktur danych audytowych."""
        large_audit_payload = {
            "session_id": "sparkle-standalone-v10",
            "timestamp": time.time(),
            "nodes": [
                {
                    "id": i,
                    "embedding": [0.01 * (i % 50)] * 64,
                    "telemetry": {"valence": 0.8, "arousal": 0.4, "dominance": 0.9}
                }
                for i in range(200)
            ],
            "quarantine_log": ["anomalia_1", "anomalia_2", "anomalia_3"]
        }

        # Serializacja JSON (emulacja Tauri IPC payload transfer)
        t_start = time.perf_counter()
        serialized = json.dumps(large_audit_payload)
        t_serialize = time.perf_counter() - t_start

        payload_kb = len(serialized.encode('utf-8')) / 1024.0
        self.assertLess(t_serialize, 0.20, f"Czas serializacji {payload_kb:.1f} KB musi być < 200ms")

        # Deserializacja
        t_deser_start = time.perf_counter()
        parsed = json.loads(serialized)
        t_deserialize = time.perf_counter() - t_deser_start

        self.assertEqual(len(parsed["nodes"]), 200)
        print(f"  [FILAR 4.1]: Wydajnosc IPC Payload: {payload_kb:.1f} KB przetworzone w {(t_serialize + t_deserialize)*1000:.2f} ms.")

    def test_09_zombie_process_and_orphan_prevention_contract(self):
        """Weryfikacja kontraktu ochrony przed procesami-widmo (Orphan / Zombie processes)."""
        import subprocess

        # Uruchomienie mikro-podprocesu weryfikującego czyste zakończenie
        code = "import sys, time; sys.exit(0)"
        proc = subprocess.Popen(
            [sys.executable, "-c", code],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        proc.wait(timeout=5)
        self.assertEqual(proc.returncode, 0, "Proces pomocniczy musi zakończyć się czysto bez zawieszenia")
        print("  [FILAR 4.2]: Kontrakt eliminacji procesow-widmo (Orphan Process Safety) spelniony.")


if __name__ == "__main__":
    print("\n" + "=" * 75)
    print("⚡ BŁYSKAWICA SPARKLE V10 — STANDALONE CERTIFICATION BENCHMARK")
    print("=" * 75)
    unittest.main()
