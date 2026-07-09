"""
Harmonic Engine: Musical Cognition Module.
Maps Frequencies, Intervals, and Rhythms to Neural Oscillations.
"""

import torch
import torch.nn as nn
import numpy as np

class HarmonicEngine(nn.Module):
    """
    Simulates musical perception as optimal neural state.
    """

    def __init__(self, sampling_rate=1000):
        super().__init__()
        self.fs = sampling_rate # 1ms resolution spikes

    def calculate_spectral_richness(self, fundamental, harmonics_count=8):
        """
        Analyzes the harmonic series and its contribution to neural 'Texture'.
        Rich spectra (more harmonics) correlate with higher cognitive engagement.
        """
        harmonics = [fundamental * (i + 1) for i in range(harmonics_count)]
        energy_distribution = [1.0 / (i + 1) for i in range(harmonics_count)]
        return sum(energy_distribution)

    def generate_polyrhythmic_pattern(self, base_bpm, ratios=[3, 4]):
        """
        Creates a multidimensional temporal lattice.
        Simulates the ability to track multiple time-scales simultaneously.
        """
        t = np.linspace(0, 1.0, self.fs)
        signals = []
        for r in ratios:
            freq = (base_bpm / 60.0) * r
            signals.append(np.sin(2 * np.pi * freq * t))
        
        return torch.tensor(np.column_stack(signals), dtype=torch.float32)

    def apply_relativistic_tempo(self, duration_ms, cognitive_velocity=0.0):
        """
        Time dilation applied to musical perception.
        High cognitive effort 'stretches' the musical moment.
        """
        gamma = 1.0 / np.sqrt(max(0.01, 1.0 - (cognitive_velocity**2)))
        return duration_ms * gamma

    def generate_tone_oscillation(self, frequency, duration_ms=100):
        """
        Converts a frequency into a rhythmic neural pulse.
        """
        t = np.linspace(0, duration_ms / 1000, int(duration_ms * (self.fs / 1000)))
        osc = np.sin(2 * np.pi * frequency * t)
        return torch.tensor(osc, dtype=torch.float32)

    def calculate_consonance(self, freq1, freq2):
        """
        Determines the 'Aesthetic Torque' of an interval.
        Consonant intervals (Perfect 5th, Octave) = Higher stability (Lower Torque).
        Dissonant intervals (Minor 2nd) = Higher tension.
        """
        ratio = max(freq1, freq2) / min(freq1, freq2)
        
        # Theoretical consonance peaks (integers/simple fractions)
        consonance_peaks = [1.0, 1.5, 2.0, 1.33, 1.2, 1.25]
        closest_peak_dist = min([abs(ratio - p) for p in consonance_peaks])
        
        aesthetic_stability = 1.0 / (1.0 + 10 * closest_peak_dist)
        return aesthetic_stability

if __name__ == "__main__":
    harmony = HarmonicEngine()
    
    # Octave (440Hz and 880Hz)
    octave_stability = harmony.calculate_consonance(440, 880)
    # Tritone (440Hz and 622.25Hz)
    tritone_stability = harmony.calculate_consonance(440, 622.25)
    
    print(f"[MUSIC] Consonance Stability (Octave): {octave_stability:.4f}")
    print(f"[MUSIC] Consonance Stability (Tritone): {tritone_stability:.4f}")
    print(f"[MUSIC] Harmonic Resonance Engine online. 🎶⚡️")
