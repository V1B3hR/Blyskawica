import logging
import torch
import numpy as np
import matplotlib.pyplot as plt

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EEGBCISimulator:
    """BCI Telemetry Simulator (Phase 6)."""
    def generate_stress_wave(self):
        # Stress = Beta waves (13-30 Hz) + high noise
        t = np.linspace(0, 1, 1000)
        signal = np.sin(2 * np.pi * 25 * t) + 0.5 * np.random.normal(size=1000)
        return signal

    def generate_relax_wave(self):
        # Relax = Alpha waves (8-13 Hz) + smooth sine
        t = np.linspace(0, 1, 1000)
        signal = np.sin(2 * np.pi * 10 * t) 
        return signal

def run_experiment_2():
    """
    Experiment 2: Cymatics & BCI (Carbon-Silicon Bridge Test)
    Logic: Translate Bio-Signals (Phase 6) to Harmonics (Phase 3).
    """
    logger.info("\n" + "="*60)
    logger.info("🧪 EXPERIMENT 2: CYMATICS & BCI SYNC (Visual/Audio Bio-Translation)")
    logger.info("="*60)
    
    sim = EEGBCISimulator()
    stress_signal = sim.generate_stress_wave()
    
    # Błyskawica's Harmonic Translation Engine
    logger.info("🧬 [SYMBIOSTIC_BRIDGE] Receiving biological telemetry...")
    
    n = len(stress_signal)
    freqs = np.fft.fftfreq(n, d=1/1000) # 1000Hz sampling
    fft_values = np.abs(np.fft.fft(stress_signal))
    
    # We only care about positive frequencies
    positive_mask = freqs > 0
    dominant_freq = freqs[positive_mask][fft_values[positive_mask].argmax()]
    logger.info(f"🌊 Detected Dominant Frequency: {dominant_freq} Hz")
    
    # Translate to Cymatic Geometry / Tone
    if 13 <= dominant_freq <= 30:
        logger.info("🔔 [HARMONIC_OUTPUT] State: STRESS. Playing: Dissonant Tritone / Sharp Geometric Patterns.")
        tonal_profile = "C - F#"
    elif 8 <= dominant_freq <= 12:
        logger.info("🍃 [HARMONIC_OUTPUT] State: RELAX. Playing: Major Pentatonic / Circular Kymatic Symmetry.")
        tonal_profile = "G - B - D"
    else:
        tonal_profile = "No Match"

    if tonal_profile != "No Match":
        logger.info(f"✅ [PASSED] Experiment 2: Biological impulses successfully mapped to {tonal_profile}.")
        return True
    return False

if __name__ == "__main__":
    run_experiment_2()
