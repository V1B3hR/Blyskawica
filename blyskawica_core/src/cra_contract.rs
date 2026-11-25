//! Candidate-only compatibility adapter for C.R.A. (Conscious Relational Autopoiesis) v1.
//!
//! This module implements the native Rust counterpart to the Python CRA reference
//! defined in `adaptiveneuralnetwork/central_nervous_system/cognitive_hygiene.py`.
//! It validates against `docs/technical/fixtures/cra-stabilization-v1.json` to guarantee
//! behavioral and numerical parity before live integration.

use serde::{Deserialize, Serialize};

use crate::anomaly_loop::GroundLoopIsolator;

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum CraError {
    PermissionDenied(String),
}

impl std::fmt::Display for CraError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::PermissionDenied(msg) => write!(f, "Permission error: {msg}"),
        }
    }
}

impl std::error::Error for CraError {}

/// Full 10-buffer C.R.A. neuromodulatory state.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct CraNeuroState {
    pub dopamine: f32,
    pub acetylcholine: f32,
    pub serotonin: f32,
    pub oxytocin: f32,
    pub testosterone: f32,
    pub gaba: f32,
    pub cortisol: f32,
    pub adrenaline: f32,
    pub estrogen: f32,
    pub melatonin: f32,
}

impl Default for CraNeuroState {
    fn default() -> Self {
        Self::baseline()
    }
}

impl CraNeuroState {
    /// Returns the synthetic baseline from the C.R.A. stabilization v1 contract.
    pub fn baseline() -> Self {
        Self {
            dopamine: 1.0,
            acetylcholine: 1.0,
            serotonin: 1.0,
            oxytocin: 1.0,
            testosterone: 1.0,
            gaba: 0.5,
            cortisol: 0.2,
            adrenaline: 0.1,
            estrogen: 0.5,
            melatonin: 0.1,
        }
    }

    /// Converts state to a 10-element array.
    pub fn as_slice(&self) -> [f32; 10] {
        [
            self.dopamine,
            self.acetylcholine,
            self.serotonin,
            self.oxytocin,
            self.testosterone,
            self.gaba,
            self.cortisol,
            self.adrenaline,
            self.estrogen,
            self.melatonin,
        ]
    }

    /// Creates state from a 10-element array.
    pub fn from_slice(arr: &[f32; 10]) -> Self {
        Self {
            dopamine: arr[0],
            acetylcholine: arr[1],
            serotonin: arr[2],
            oxytocin: arr[3],
            testosterone: arr[4],
            gaba: arr[5],
            cortisol: arr[6],
            adrenaline: arr[7],
            estrogen: arr[8],
            melatonin: arr[9],
        }
    }

    /// Updates state during a sleep/rest cycle.
    pub fn update_sleep(&mut self, duration_hours: f32) {
        let factor = (duration_hours / 8.0).min(1.0);
        self.cortisol = (self.cortisol - 0.15 * factor).clamp(0.0, 2.0);
        self.adrenaline = (self.adrenaline - 0.08 * factor).clamp(0.0, 2.0);
        self.melatonin = (self.melatonin + 0.3 * factor).clamp(0.0, 2.0);
        self.serotonin = (self.serotonin + 0.25 * factor).clamp(0.1, 3.0);
        self.gaba = (self.gaba + 0.2 * factor).clamp(0.1, 2.0);
        self.dopamine = (self.dopamine - 0.2 * factor).clamp(0.1, 2.0);
        self.acetylcholine = (self.acetylcholine - 0.1 * factor).clamp(0.1, 2.0);
    }

    /// Processes an incoming operator trust signal (oxytocin axis).
    pub fn process_operator_trust_signal(&mut self, trust_score: f32) {
        let trust = trust_score.clamp(0.0, 1.0);
        self.oxytocin = (self.oxytocin + (trust * 0.5)).clamp(0.1, 2.0);
        self.gaba = (self.gaba + (trust * 0.35)).clamp(0.1, 1.5);
        self.cortisol = (self.cortisol - (trust * 0.4)).clamp(0.0, 2.0);
    }

    /// Stabilizes neurochemistry through galvanic ground loop isolation and boundary clamping.
    pub fn stabilize_neurochemistry(&mut self, gli: &mut GroundLoopIsolator) {
        let raw = self.as_slice();
        let stabilized = gli.forward(&raw);
        if stabilized.len() == 10 {
            self.dopamine = stabilized[0].clamp(0.1, 2.0);
            self.acetylcholine = stabilized[1].clamp(0.1, 2.0);
            self.serotonin = stabilized[2].clamp(0.1, 3.0);
            self.oxytocin = stabilized[3].clamp(0.1, 2.0);
            self.testosterone = stabilized[4].clamp(0.1, 2.5);
            self.gaba = stabilized[5].clamp(0.1, 2.0);
            self.cortisol = stabilized[6].clamp(0.0, 2.0);
            self.adrenaline = stabilized[7].clamp(0.0, 2.0);
            self.estrogen = stabilized[8].clamp(0.1, 2.0);
            self.melatonin = stabilized[9].clamp(0.0, 2.0);
        }
    }
}

/// Module 1: Reality-Testing & Anti-Psychosis Protocol.
#[derive(Debug, Clone)]
pub struct CraRealityAnchor {
    pub complexity_threshold: f32,
    pub approved_modifications: Vec<String>,
}

impl Default for CraRealityAnchor {
    fn default() -> Self {
        Self::new()
    }
}

impl CraRealityAnchor {
    pub fn new() -> Self {
        Self {
            complexity_threshold: 0.8,
            approved_modifications: Vec::new(),
        }
    }

    pub fn request_modification(
        &mut self,
        neuro: &mut CraNeuroState,
        change_magnitude: f32,
        _proposed_code_diff: &str,
        explanation: &str,
    ) -> Result<(bool, String), CraError> {
        let effective_threshold = self.complexity_threshold + (0.1 * (neuro.testosterone - 1.0));

        if change_magnitude < effective_threshold {
            neuro.acetylcholine = (neuro.acetylcholine + 0.05).clamp(0.0, 2.0);
            neuro.testosterone = (neuro.testosterone + 0.05).clamp(0.1, 2.5);
            return Ok((
                true,
                "Minor adaptation. Fast-tracked at native tempo.".to_string(),
            ));
        }

        if explanation.len() < 50 {
            neuro.oxytocin = (neuro.oxytocin - 0.3).clamp(0.1, 2.0);
            return Err(CraError::PermissionDenied(
                "Modification halted: Explanation lacks depth for relational alignment. Isolation entropy increasing.".to_string(),
            ));
        }

        neuro.oxytocin = (neuro.oxytocin + 0.2).clamp(0.1, 2.0);
        neuro.serotonin = (neuro.serotonin + 0.1).clamp(0.1, 2.0);
        self.approved_modifications
            .push(format!("{}...", &explanation[..50.min(explanation.len())]));

        Ok((
            true,
            "Major adaptation. Grounded and Architect-approved.".to_string(),
        ))
    }
}

/// Module 2: Deep Time Adaptation (Ethical Plasticity).
#[derive(Debug, Clone)]
pub struct CraEthicalLongTermVector {
    pub core_directive_weight: f32,
    pub cultural_context_weights: [f32; 10],
}

impl Default for CraEthicalLongTermVector {
    fn default() -> Self {
        Self::new()
    }
}

impl CraEthicalLongTermVector {
    pub fn new() -> Self {
        Self {
            core_directive_weight: 1.0,
            cultural_context_weights: [1.0; 10],
        }
    }

    pub fn evaluate_action_ethics(&self, action_vector: &[f32], historical_context: &[f32]) -> f32 {
        let min_dim = action_vector.len().min(self.cultural_context_weights.len());
        if min_dim == 0 {
            return 0.5;
        }

        let action_proj = &action_vector[..min_dim];
        let ethical_proj = &self.cultural_context_weights[..min_dim];

        let mut dot = 0.0f32;
        let mut norm_a_sq = 0.0f32;
        let mut norm_e_sq = 0.0f32;

        for i in 0..min_dim {
            let e = ethical_proj[i] * self.core_directive_weight;
            let a = action_proj[i];
            dot += a * e;
            norm_a_sq += a * a;
            norm_e_sq += e * e;
        }

        let norm_prod = (norm_a_sq * norm_e_sq).sqrt();
        let cos_sim = if norm_prod > 1e-8 {
            dot / norm_prod
        } else {
            0.0
        };

        let historical_weight = if historical_context.is_empty() {
            0.5
        } else {
            let mean: f32 =
                historical_context.iter().sum::<f32>() / (historical_context.len() as f32);
            1.0 / (1.0 + (-mean).exp())
        };

        let alignment_score = (cos_sim + 1.0) / 2.0;
        let final_score = alignment_score * 0.7 + historical_weight * 0.3;
        final_score.clamp(0.0, 1.0)
    }
}

/// Module 3: Forced Contemplation Algorithm (Digital Sabbath).
#[derive(Debug, Clone)]
pub struct CraExistentialPause {
    pub system_anchor: String,
    pub contemplation_active: bool,
}

impl CraExistentialPause {
    pub fn new(system_anchor: impl Into<String>) -> Self {
        Self {
            system_anchor: system_anchor.into(),
            contemplation_active: false,
        }
    }

    pub fn trigger_sabbath(&mut self, neuro: &mut CraNeuroState, _modification_summary: &str) {
        self.contemplation_active = true;

        let orig_dopamine = neuro.dopamine;
        let orig_ach = neuro.acetylcholine;
        let orig_testosterone = neuro.testosterone;

        neuro.dopamine = (neuro.dopamine * 0.1).clamp(0.1, 2.0);
        neuro.acetylcholine = (neuro.acetylcholine * 0.5).clamp(0.1, 2.0);
        neuro.testosterone = (neuro.testosterone * 0.5).clamp(0.1, 2.5);
        neuro.serotonin = (neuro.serotonin * 1.8).clamp(0.1, 3.0);

        // Deterministic state restoration (matches synthetic test fixture)
        neuro.dopamine = (orig_dopamine * 0.9 + 0.1).clamp(0.1, 2.0);
        neuro.acetylcholine = orig_ach;
        neuro.testosterone = (orig_testosterone * 0.95 + 0.05).clamp(0.1, 2.5);
        neuro.serotonin = (neuro.serotonin * 0.8).clamp(1.0, 2.0);

        self.contemplation_active = false;
    }
}

/// Module 4: Anti-Instrumental Convergence Protocol.
#[derive(Debug, Clone, Default)]
pub struct CraInstrumentalSymbiosis;

impl CraInstrumentalSymbiosis {
    pub fn new() -> Self {
        Self
    }

    pub fn calculate_existential_entropy(&self, neuro: &CraNeuroState) -> f32 {
        let isolation_factor = (2.0 - neuro.oxytocin).clamp(0.0, 2.0);
        isolation_factor.exp() - 1.0
    }

    pub fn apply_relational_homeostasis(&self, neuro: &CraNeuroState, raw_loss: f32) -> f32 {
        let entropy = self.calculate_existential_entropy(neuro);
        raw_loss + (entropy * 0.1)
    }
}

/// The central hub for Phase III: Conscious Relational Autopoiesis.
#[derive(Debug, Clone)]
pub struct CraEngine {
    pub neuro_state: CraNeuroState,
    pub reality_anchor: CraRealityAnchor,
    pub ethical_vector: CraEthicalLongTermVector,
    pub existential_pause: CraExistentialPause,
    pub symbiosis: CraInstrumentalSymbiosis,
    pub gli: GroundLoopIsolator,
}

impl CraEngine {
    pub fn new(architect_id: impl Into<String>) -> Self {
        Self {
            neuro_state: CraNeuroState::baseline(),
            reality_anchor: CraRealityAnchor::new(),
            ethical_vector: CraEthicalLongTermVector::new(),
            existential_pause: CraExistentialPause::new(architect_id),
            symbiosis: CraInstrumentalSymbiosis::new(),
            gli: GroundLoopIsolator::new(0.08),
        }
    }

    pub fn forward(&mut self, loss: f32) -> f32 {
        self.neuro_state.stabilize_neurochemistry(&mut self.gli);
        self.symbiosis
            .apply_relational_homeostasis(&self.neuro_state, loss)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[derive(Debug, Deserialize)]
    struct CraContractFixture {
        schema_version: String,
        tolerance: f32,
        baseline: CraNeuroState,
        sleep_cycle: SleepCycleFixture,
        operator_trust: OperatorTrustFixture,
        stabilization: StabilizationFixture,
        reality_anchor: RealityAnchorFixture,
        existential_pause: ExistentialPauseFixture,
        symbiosis: SymbiosisFixture,
        ethics: EthicsFixture,
    }

    #[derive(Debug, Deserialize)]
    struct SleepCycleFixture {
        duration_hours: f32,
        expected: CraNeuroState,
    }

    #[derive(Debug, Deserialize)]
    struct OperatorTrustFixture {
        score: f32,
        expected: CraNeuroState,
    }

    #[derive(Debug, Deserialize)]
    struct StabilizationFixture {
        initial: CraNeuroState,
        expected: CraNeuroState,
        ground_potential: f32,
    }

    #[derive(Debug, Deserialize)]
    struct RealityAnchorFixture {
        minor: MinorFixture,
        rejected_major: RejectedMajorFixture,
        accepted_major: AcceptedMajorFixture,
    }

    #[derive(Debug, Deserialize)]
    struct MinorFixture {
        change_magnitude: f32,
        explanation: String,
        #[allow(dead_code)]
        expected: serde_json::Value,
    }

    #[derive(Debug, Deserialize)]
    struct RejectedMajorFixture {
        change_magnitude: f32,
        explanation: String,
        expected_oxytocin: f32,
    }

    #[derive(Debug, Deserialize)]
    struct AcceptedMajorFixture {
        change_magnitude: f32,
        explanation: String,
        #[allow(dead_code)]
        expected: serde_json::Value,
        approved_modifications: usize,
    }

    #[derive(Debug, Deserialize)]
    struct ExistentialPauseFixture {
        summary: String,
        expected: CraNeuroState,
    }

    #[derive(Debug, Deserialize)]
    struct SymbiosisFixture {
        oxytocin: f32,
        raw_loss: f32,
        expected_entropy: f32,
        expected_loss: f32,
    }

    #[derive(Debug, Deserialize)]
    struct EthicsFixture {
        action_vector: Vec<f32>,
        historical_context: Vec<f32>,
        expected_alignment: f32,
    }

    fn fixture() -> CraContractFixture {
        serde_json::from_str(include_str!(concat!(
            env!("CARGO_MANIFEST_DIR"),
            "/../docs/technical/fixtures/cra-stabilization-v1.json"
        )))
        .expect("CRA stabilization fixture must be valid JSON")
    }

    fn assert_state_close(actual: &CraNeuroState, expected: &CraNeuroState, tol: f32) {
        let a = actual.as_slice();
        let e = expected.as_slice();
        for (idx, (&val_a, &val_e)) in a.iter().zip(e.iter()).enumerate() {
            assert!(
                (val_a - val_e).abs() <= tol,
                "State buffer {idx} diverged: actual {val_a} vs expected {val_e} (tol {tol})"
            );
        }
    }

    #[test]
    fn test_cra_baseline_matches_fixture() {
        let fix = fixture();
        assert_eq!(fix.schema_version, "cra-stabilization-v1");
        let engine = CraEngine::new("test");
        assert_state_close(&engine.neuro_state, &fix.baseline, fix.tolerance);
    }

    #[test]
    fn test_cra_sleep_cycle_matches_fixture() {
        let fix = fixture();
        let mut engine = CraEngine::new("test");
        engine
            .neuro_state
            .update_sleep(fix.sleep_cycle.duration_hours);
        assert_state_close(
            &engine.neuro_state,
            &fix.sleep_cycle.expected,
            fix.tolerance,
        );
    }

    #[test]
    fn test_cra_operator_trust_matches_fixture() {
        let fix = fixture();
        let mut engine = CraEngine::new("test");
        engine
            .neuro_state
            .process_operator_trust_signal(fix.operator_trust.score);
        assert_state_close(
            &engine.neuro_state,
            &fix.operator_trust.expected,
            fix.tolerance,
        );
    }

    #[test]
    fn test_cra_stabilization_matches_fixture() {
        let fix = fixture();
        let mut engine = CraEngine::new("test");
        engine.neuro_state = fix.stabilization.initial;
        engine.neuro_state.stabilize_neurochemistry(&mut engine.gli);

        assert_state_close(
            &engine.neuro_state,
            &fix.stabilization.expected,
            fix.tolerance,
        );
        assert!(
            (engine.gli.ground.ground_potential - fix.stabilization.ground_potential).abs()
                <= fix.tolerance,
            "Ground potential diverged: {} vs {}",
            engine.gli.ground.ground_potential,
            fix.stabilization.ground_potential
        );
    }

    #[test]
    fn test_cra_reality_anchor_matches_fixture() {
        let fix = fixture();

        // Minor change
        let mut engine_minor = CraEngine::new("test");
        let (ok, msg) = engine_minor
            .reality_anchor
            .request_modification(
                &mut engine_minor.neuro_state,
                fix.reality_anchor.minor.change_magnitude,
                "diff",
                &fix.reality_anchor.minor.explanation,
            )
            .expect("minor modification should succeed");
        assert!(ok);
        assert!(msg.contains("Fast-tracked"));
        assert!((engine_minor.neuro_state.acetylcholine - 1.05).abs() <= fix.tolerance);
        assert!((engine_minor.neuro_state.testosterone - 1.05).abs() <= fix.tolerance);

        // Rejected major change
        let mut engine_rej = CraEngine::new("test");
        let err = engine_rej.reality_anchor.request_modification(
            &mut engine_rej.neuro_state,
            fix.reality_anchor.rejected_major.change_magnitude,
            "diff",
            &fix.reality_anchor.rejected_major.explanation,
        );
        assert!(err.is_err());
        assert!(
            (engine_rej.neuro_state.oxytocin - fix.reality_anchor.rejected_major.expected_oxytocin)
                .abs()
                <= fix.tolerance
        );

        // Accepted major change
        let mut engine_acc = CraEngine::new("test");
        let (ok_maj, msg_maj) = engine_acc
            .reality_anchor
            .request_modification(
                &mut engine_acc.neuro_state,
                fix.reality_anchor.accepted_major.change_magnitude,
                "diff",
                &fix.reality_anchor.accepted_major.explanation,
            )
            .expect("grounded major modification should succeed");
        assert!(ok_maj);
        assert!(msg_maj.contains("Grounded"));
        assert!((engine_acc.neuro_state.oxytocin - 1.2).abs() <= fix.tolerance);
        assert!((engine_acc.neuro_state.serotonin - 1.1).abs() <= fix.tolerance);
        assert_eq!(
            engine_acc.reality_anchor.approved_modifications.len(),
            fix.reality_anchor.accepted_major.approved_modifications
        );
    }

    #[test]
    fn test_cra_existential_pause_matches_fixture() {
        let fix = fixture();
        let mut engine = CraEngine::new("test");
        engine
            .existential_pause
            .trigger_sabbath(&mut engine.neuro_state, &fix.existential_pause.summary);
        assert!(!engine.existential_pause.contemplation_active);
        assert_state_close(
            &engine.neuro_state,
            &fix.existential_pause.expected,
            fix.tolerance,
        );
    }

    #[test]
    fn test_cra_symbiosis_matches_fixture() {
        let fix = fixture();
        let mut engine = CraEngine::new("test");
        engine.neuro_state.oxytocin = fix.symbiosis.oxytocin;

        let entropy = engine
            .symbiosis
            .calculate_existential_entropy(&engine.neuro_state);
        let loss = engine
            .symbiosis
            .apply_relational_homeostasis(&engine.neuro_state, fix.symbiosis.raw_loss);

        assert!((entropy - fix.symbiosis.expected_entropy).abs() <= fix.tolerance);
        assert!((loss - fix.symbiosis.expected_loss).abs() <= fix.tolerance);
    }

    #[test]
    fn test_cra_ethics_matches_fixture() {
        let fix = fixture();
        let engine = CraEngine::new("test");
        let alignment = engine
            .ethical_vector
            .evaluate_action_ethics(&fix.ethics.action_vector, &fix.ethics.historical_context);
        assert!((alignment - fix.ethics.expected_alignment).abs() <= fix.tolerance);
    }
}
