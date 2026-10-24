//! [Phase XXVIII: Microtubule Quantum Coherence & Phonon Dispersion Engine]
//!
//! Models quantum dipole-dipole coupling within tubulin dimer lattices,
//! simulating quantum-optical coherence survival times under phonon noise.
//! Aligned with Orch OR theory and eNeuro 2024 experimental discoveries in quantum biology.
//!
//! In Błyskawica's cognitive architecture:
//! - Acetylcholine acts as a physical stabilizer for tubulin dimer lattices (+coherence)
//! - GABA suppresses thermal phonon noise (-decoherence)
//! - Coherence survival time (in picoseconds) modulates cognitive plasticity and sampling determinism.

use crate::neurochemistry::NeurochemicalState;
use serde::{Deserialize, Serialize};

/// Geometry and physical parameters of the tubulin dimer ring.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct TubulinLattice {
    pub dimer_count: usize,
    pub inter_dimer_distance_nanometers: f32,
    pub dipole_coupling_constant_ev: f32,
    pub ambient_temperature_kelvin: f32,
}

impl Default for TubulinLattice {
    fn default() -> Self {
        Self {
            dimer_count: 8,
            inter_dimer_distance_nanometers: 8.0,
            dipole_coupling_constant_ev: 0.012,
            ambient_temperature_kelvin: 310.15, // 37.0°C warm mammalian brain
        }
    }
}

/// Thresholds defining objective quantum state reduction (Orch OR).
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct QuantumCoherenceThresholds {
    pub coherence_time_limit_picoseconds: f32,
    pub critical_damping_factor: f32,
}

impl Default for QuantumCoherenceThresholds {
    fn default() -> Self {
        Self {
            coherence_time_limit_picoseconds: 500.0,
            critical_damping_factor: 0.18,
        }
    }
}

/// Real-time metrics output by the microtubule phonon engine.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct MicrotubuleMetrics {
    pub coherence_time_ps: f32,
    pub is_orch_or_capable: bool,
    pub phonon_noise_damping: f32,
    pub stabilization_factor: f32,
    pub decoherence_rate: f32,
    pub quantum_entropy: f32,
}

/// Native Microtubule Phonon Engine.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MicrotubulePhononEngine {
    pub lattice: TubulinLattice,
    pub thresholds: QuantumCoherenceThresholds,
}

impl Default for MicrotubulePhononEngine {
    fn default() -> Self {
        Self::new()
    }
}

impl MicrotubulePhononEngine {
    /// Constructs engine with canonical biological defaults.
    pub fn new() -> Self {
        Self {
            lattice: TubulinLattice::default(),
            thresholds: QuantumCoherenceThresholds::default(),
        }
    }

    /// Constructs engine from custom lattice configuration.
    pub fn with_lattice(lattice: TubulinLattice, thresholds: QuantumCoherenceThresholds) -> Self {
        Self {
            lattice,
            thresholds,
        }
    }

    /// Simulates coherence survival time and phonon dispersion given neurotransmitter levels.
    ///
    /// # Arguments
    /// * `acetylcholine`: Normalized level [0.0 .. 1.0] acting as lattice stabilizer.
    /// * `gaba`: Normalized level [0.0 .. 1.0] acting as acoustic phonon damper.
    /// * `ambient_temp_k`: Optional override for body temperature in Kelvin.
    pub fn simulate_coherence(
        &self,
        acetylcholine: f32,
        gaba: f32,
        ambient_temp_k: Option<f32>,
    ) -> MicrotubuleMetrics {
        let ach = if acetylcholine.is_nan() || acetylcholine.is_infinite() {
            0.5
        } else {
            acetylcholine.clamp(0.0, 1.0)
        };
        let g = if gaba.is_nan() || gaba.is_infinite() {
            0.5
        } else {
            gaba.clamp(0.0, 1.0)
        };

        let base_temp = match ambient_temp_k {
            Some(t) if !t.is_nan() && !t.is_infinite() => t.clamp(273.15, 373.15),
            _ => self.lattice.ambient_temperature_kelvin,
        };
        let coupling = self.lattice.dipole_coupling_constant_ev.max(0.0001);
        let dimers = (self.lattice.dimer_count as f32).max(1.0);

        // Acetylcholine-mediated stabilization factor (eNeuro 2024 inspired)
        let stabilization_factor = 1.0 + (ach * 0.4);

        // Phonon damping factor controlled by active GABA noise suppression
        let phonon_noise_damping = (1.0 - (g * 0.55)).clamp(0.01, 1.0);

        // Decoherence rate equation for warm biological dipole lattice
        let denominator = (coupling * dimers * stabilization_factor).max(1e-6);
        let raw_rate = (base_temp * 0.005) * phonon_noise_damping / denominator;
        let decoherence_rate = if raw_rate.is_nan() || raw_rate.is_infinite() {
            10.0
        } else {
            raw_rate.max(1e-6)
        };

        // Coherence survival time in picoseconds (capped at safe biological upper bound 2000 ps)
        let raw_time = (1.0 / (decoherence_rate + 0.0001)) * 100.0;
        let coherence_time_ps = if raw_time.is_nan() || raw_time.is_infinite() {
            100.0
        } else {
            raw_time.clamp(0.1, 2000.0)
        };

        let is_orch_or_capable =
            coherence_time_ps >= self.thresholds.coherence_time_limit_picoseconds;

        // Quantum entropy: normalized measure of phase uncertainty [0.0 .. 1.0]
        let raw_entropy = 1.0 - (coherence_time_ps / 2000.0);
        let quantum_entropy = if raw_entropy.is_nan() || raw_entropy.is_infinite() {
            0.5
        } else {
            raw_entropy.clamp(0.0, 1.0)
        };

        MicrotubuleMetrics {
            coherence_time_ps,
            is_orch_or_capable,
            phonon_noise_damping,
            stabilization_factor,
            decoherence_rate,
            quantum_entropy,
        }
    }

    /// Evaluates coherence dynamics directly against the system's full 10-buffer `NeurochemicalState`.
    pub fn simulate_from_neurochemistry(&self, neuro: &NeurochemicalState) -> MicrotubuleMetrics {
        // Temperature buffer in NeurochemicalState is normalized [0.0 .. 1.0], mapping to [295.15K .. 320.15K]
        let kelvin = 295.15 + (neuro.temperature.clamp(0.0, 1.0) * 25.0);
        self.simulate_coherence(neuro.acetylcholine, neuro.gaba, Some(kelvin))
    }

    /// Modulates sampling temperature / cognitive search radius based on microtubule quantum coherence.
    ///
    /// - High coherence (Orch OR active): opens subtle quantum exploration window (+plasticity).
    /// - Low coherence (decoherence dominant): tightens bounds toward strict analytical determinism.
    pub fn modulate_cognitive_temperature(
        &self,
        base_temp: f32,
        metrics: &MicrotubuleMetrics,
    ) -> f32 {
        let base = base_temp.clamp(0.1, 2.0);
        if metrics.is_orch_or_capable {
            // Sustained coherence allows creative superposition exploration (+15% max)
            (base * (1.0 + (1.0 - metrics.quantum_entropy) * 0.15)).clamp(0.1, 2.0)
        } else {
            // High phonon noise forces deterministic collapse
            (base * (0.85 + (metrics.coherence_time_ps / 1000.0) * 0.15)).clamp(0.1, 2.0)
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_lattice_default_dimensions() {
        let engine = MicrotubulePhononEngine::new();
        assert_eq!(engine.lattice.dimer_count, 8);
        assert!((engine.lattice.ambient_temperature_kelvin - 310.15).abs() < 1e-4);
        assert!((engine.lattice.dipole_coupling_constant_ev - 0.012).abs() < 1e-4);
    }

    #[test]
    fn test_chemistry_coherence_sensitivity() {
        let engine = MicrotubulePhononEngine::new();

        // Standard state (moderate focus)
        let metrics_std = engine.simulate_coherence(0.50, 0.50, None);

        // Highly focused and calm state (high Acetylcholine + high GABA)
        let metrics_focused = engine.simulate_coherence(0.95, 0.95, None);

        // Focused state must produce longer quantum coherence survival time
        assert!(
            metrics_focused.coherence_time_ps > metrics_std.coherence_time_ps,
            "Focused coherence ({}) must exceed standard coherence ({})",
            metrics_focused.coherence_time_ps,
            metrics_std.coherence_time_ps
        );

        // Damping must be lower (less noise) in focused state
        assert!(metrics_focused.phonon_noise_damping < metrics_std.phonon_noise_damping);

        // Stabilization factor must be higher in focused state
        assert!(metrics_focused.stabilization_factor > metrics_std.stabilization_factor);
    }

    #[test]
    fn test_neurochemistry_integration() {
        let engine = MicrotubulePhononEngine::new();
        let mut neuro = NeurochemicalState::default();
        neuro.acetylcholine = 0.90;
        neuro.gaba = 0.85;
        neuro.temperature = 0.60;

        let metrics = engine.simulate_from_neurochemistry(&neuro);
        assert!(metrics.coherence_time_ps > 10.0);
        assert!(metrics.quantum_entropy >= 0.0 && metrics.quantum_entropy <= 1.0);
    }

    #[test]
    fn test_cognitive_temperature_modulation() {
        let engine = MicrotubulePhononEngine::new();
        let mut metrics = engine.simulate_coherence(0.99, 0.99, None);
        metrics.is_orch_or_capable = true;

        let modulated_creative = engine.modulate_cognitive_temperature(0.7, &metrics);
        assert!(modulated_creative >= 0.7);

        metrics.is_orch_or_capable = false;
        metrics.coherence_time_ps = 50.0;
        let modulated_strict = engine.modulate_cognitive_temperature(0.7, &metrics);
        assert!(modulated_strict < 0.7);
    }

    #[test]
    fn test_nan_and_infinity_resilience() {
        let engine = MicrotubulePhononEngine::new();
        let metrics = engine.simulate_coherence(f32::NAN, f32::INFINITY, Some(f32::NAN));
        assert!(!metrics.coherence_time_ps.is_nan());
        assert!(!metrics.decoherence_rate.is_nan());
        assert!(!metrics.quantum_entropy.is_nan());
    }
}
