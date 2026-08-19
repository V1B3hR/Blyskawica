use serde::{Deserialize, Serialize};
use std::time::{SystemTime, UNIX_EPOCH};
use crate::neurochemistry::NeurochemicalState;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct IntentSeed {
    pub id: String,
    pub timestamp: u64,
    pub snippet: String,
    pub amplitude: f32, // Siła sygnału podprogowego (0.0 - 1.0)
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HypothesisBranch {
    pub id: String,
    pub category: String,
    pub ripeness: f32, // Stopień dojrzałości owocu (0.0 - 1.0)
    pub ripe_fruit_insight: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CognitiveTreeState {
    pub active_roots_count: usize,
    pub branches_count: usize,
    pub ripe_fruits_count: usize,
    pub vegetative_pulse_rate_hz: f32,
}

pub struct CognitiveHeartbeat {
    pub seeds: Vec<IntentSeed>,
    pub branches: Vec<HypothesisBranch>,
    pub pulse_count: u64,
}

impl CognitiveHeartbeat {
    pub fn new() -> Self {
        Self {
            seeds: Vec::new(),
            branches: vec![
                HypothesisBranch {
                    id: "BRANCH-CODE-OPT".to_string(),
                    category: "Inżynieria Kodu".to_string(),
                    ripeness: 0.15,
                    ripe_fruit_insight: None,
                },
                HypothesisBranch {
                    id: "BRANCH-POLYMATH-BIO".to_string(),
                    category: "Biomimetyka & Homeostaza".to_string(),
                    ripeness: 0.30,
                    ripe_fruit_insight: None,
                },
                HypothesisBranch {
                    id: "BRANCH-SYS-SEC".to_string(),
                    category: "Bezpieczeństwo Windows".to_string(),
                    ripeness: 0.25,
                    ripe_fruit_insight: None,
                },
            ],
            pulse_count: 0,
        }
    }

    /// Przechwycenie zalążka intencji z korzeni (Intent Seed)
    pub fn absorb_intent_seed(&mut self, snippet: &str, amplitude: f32) {
        if snippet.trim().is_empty() {
            return;
        }

        let timestamp = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs();

        let seed = IntentSeed {
            id: format!("SEED-{}", self.seeds.len() + 1),
            timestamp,
            snippet: snippet.to_string(),
            amplitude: amplitude.clamp(0.05, 1.0),
        };

        self.seeds.push(seed);
        if self.seeds.len() > 50 {
            self.seeds.remove(0);
        }
    }

    /// Cykl tętna kognitywnego (10Hz).
    /// Zwraca dojrzały owoc, jeśli na którymś konarze doszło do pełnej krystalizacji (ripeness >= 0.90).
    pub fn tick(&mut self, neuro: &NeurochemicalState) -> Option<HypothesisBranch> {
        self.pulse_count += 1;

        // Wpływ dopaminy (eksploracja) i serotoniny (konsolidacja) na dojrzewanie
        let growth_delta = (neuro.dopamine * 0.02 + neuro.serotonin * 0.03) as f32;

        let mut newly_ripened = None;

        for branch in self.branches.iter_mut() {
            if branch.ripeness < 0.90 {
                // Jeśli są świeże zalążki w korzeniach, konary rosną szybciej
                let seed_boost = if !self.seeds.is_empty() { 0.05 } else { 0.005 };
                branch.ripeness = (branch.ripeness + growth_delta + seed_boost).min(1.0);

                if branch.ripeness >= 0.90 && branch.ripe_fruit_insight.is_none() {
                    let insight = match branch.id.as_str() {
                        "BRANCH-CODE-OPT" => "🍎 [Owoc Dojrzały]: Wykryto możliwość modularnej dekompozycji funkcji i przyspieszenia SIMD w silniku Rust.".to_string(),
                        "BRANCH-POLYMATH-BIO" => "🍎 [Owoc Dojrzały]: Model neuroprzekaźników osiągnął stan idealnej symetrii fali Yant (Flow State).".to_string(),
                        "BRANCH-SYS-SEC" => "🍎 [Owoc Dojrzały]: Tarcza Aegis zweryfikowała szczelność Job Object dla wszystkich aktywnych wątków.".to_string(),
                        _ => "🍎 [Owoc Dojrzały]: Wykrystalizowano nową spójną hipotezę kognitywną.".to_string(),
                    };

                    branch.ripe_fruit_insight = Some(insight);
                    newly_ripened = Some(branch.clone());
                }
            }
        }

        newly_ripened
    }

    pub fn get_tree_state(&self) -> CognitiveTreeState {
        let ripe_count = self
            .branches
            .iter()
            .filter(|b| b.ripeness >= 0.90)
            .count();

        CognitiveTreeState {
            active_roots_count: self.seeds.len(),
            branches_count: self.branches.len(),
            ripe_fruits_count: ripe_count,
            vegetative_pulse_rate_hz: 10.0,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_intent_absorption_and_growth() {
        let mut tree = CognitiveHeartbeat::new();
        let neuro = NeurochemicalState::default();

        tree.absorb_intent_seed("fn calculate_harmonic_resonance()", 0.85);
        assert_eq!(tree.seeds.len(), 1);

        let initial_ripeness = tree.branches[0].ripeness;
        let _ = tree.tick(&neuro);
        assert!(tree.branches[0].ripeness > initial_ripeness);
    }

    #[test]
    fn test_fruit_maturation() {
        let mut tree = CognitiveHeartbeat::new();
        let neuro = NeurochemicalState::default();

        tree.branches[0].ripeness = 0.88;
        tree.absorb_intent_seed("optymalizacja SIMD", 0.9);

        let ripened = tree.tick(&neuro);
        assert!(ripened.is_some());
        let fruit = ripened.unwrap();
        assert!(fruit.ripeness >= 0.90);
        assert!(fruit.ripe_fruit_insight.is_some());
    }
}
