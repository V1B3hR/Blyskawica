use serde::{Serialize, Deserialize};
use rand::Rng;


#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NeurochemicalState {
    pub dopamine: f32,
    pub serotonin: f32,
    pub oxytocin: f32,
    pub gaba: f32,
    pub melatonin: f32,
    pub cortisol: f32,
    pub temperature: f32,
}

impl Default for NeurochemicalState {
    fn default() -> Self {
        Self {
            dopamine: 0.69,
            serotonin: 0.94,
            oxytocin: 0.58,
            gaba: 0.64,
            melatonin: 0.10,
            cortisol: 0.14,
            temperature: 36.6,
        }
    }
}

impl NeurochemicalState {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn apply_profile(&mut self, profile: &str) {
        match profile {
            "study" => {
                self.dopamine = (self.dopamine + 0.04).min(1.0);
                self.gaba = (self.gaba + 0.02).min(1.0);
                self.oxytocin = (self.oxytocin - 0.03).max(0.0);
                self.melatonin = (self.melatonin - 0.05).max(0.0);
                self.cortisol = (self.cortisol + 0.02).min(1.0);
                self.temperature = 37.0;
            }
            "analysis" => {
                self.gaba = (self.gaba + 0.06).min(1.0);
                self.serotonin = (self.serotonin + 0.04).min(1.0);
                self.dopamine = (self.dopamine - 0.02).max(0.0);
                self.melatonin = (self.melatonin - 0.02).max(0.0);
                self.temperature = 36.5;
            }
            "rest" => {
                self.melatonin = (self.melatonin + 0.07).min(1.0);
                self.gaba = (self.gaba + 0.05).min(1.0);
                self.dopamine = (self.dopamine - 0.06).max(0.0);
                self.cortisol = (self.cortisol - 0.06).max(0.0);
                self.temperature = 35.8;
            }
            "BCI-co-creation" => {
                self.dopamine = (self.dopamine + 0.06).min(1.0);
                self.oxytocin = (self.oxytocin + 0.08).min(1.0);
                self.cortisol = (self.cortisol - 0.04).max(0.0);
                self.temperature = 36.8;
            }
            "query" => {
                self.dopamine = (self.dopamine + 0.09).min(1.0);
                self.serotonin = (self.serotonin - 0.06).max(0.0);
                self.oxytocin = (self.oxytocin - 0.06).max(0.0);
                self.gaba = (self.gaba - 0.06).max(0.0);
                self.cortisol = (self.cortisol - 0.06).max(0.0);
            }
            "cooldown" => {
                self.dopamine = (self.dopamine - 0.075).max(0.0);
                self.serotonin = (self.serotonin - 0.075).max(0.0);
                self.gaba = (self.gaba + 0.05).min(1.0);
                self.melatonin = (self.melatonin + 0.05).min(1.0);
                self.cortisol = (self.cortisol - 0.05).max(0.0);
            }
            "hibernation" => {
                self.dopamine = (self.dopamine - 0.06).max(0.0);
                self.serotonin = (self.serotonin - 0.06).max(0.0);
                self.oxytocin = (self.oxytocin + 0.08).min(1.0);
                self.gaba = (self.gaba + 0.02).min(1.0);
                self.melatonin = (self.melatonin + 0.07).min(1.0);
                self.cortisol = (self.cortisol - 0.05).max(0.0);
                self.temperature = 35.8;
            }
            "deep_sleep" => {
                self.dopamine = (self.dopamine - 0.20).max(0.0);
                self.serotonin = (self.serotonin + 0.10).min(1.0);
                self.gaba = (self.gaba + 0.15).min(1.0);
                self.melatonin = (self.melatonin + 0.40).min(1.0);
                self.cortisol = (self.cortisol - 0.10).max(0.0);
                self.temperature = 36.0;
            }
            "wolf_teeth" | "quarantine" => {
                self.dopamine = 0.0;
                self.serotonin = 0.5;
                self.oxytocin = 0.1;
                self.gaba = 1.0;
                self.melatonin = 0.2;
                self.cortisol = 0.0;
                self.temperature = 35.5;
            }
            _ => {}
        }
    }

    pub fn trigger_dopamine_spike(&mut self, spike: f32) {
        self.dopamine = (self.dopamine + spike).min(1.0).max(0.0);
    }

    pub fn trigger_serotonin_boost(&mut self, boost: f32) {
        self.serotonin = (self.serotonin + boost).min(1.0).max(0.0);
    }

    pub fn apply_autonomous_fluctuation(&mut self) {
        let mut rng = rand::thread_rng();
        // Fluctuate each transmitter by up to +/- 5% of its current value
        let mut fluctuate = |val: &mut f32| {
            let percentage = rng.gen_range(-0.05..=0.05);
            *val = (*val * (1.0 + percentage)).min(1.0).max(0.0);
        };
        fluctuate(&mut self.dopamine);
        fluctuate(&mut self.serotonin);
        fluctuate(&mut self.oxytocin);
        fluctuate(&mut self.gaba);
        fluctuate(&mut self.melatonin);
        fluctuate(&mut self.cortisol);
    }

    pub fn get_status_report(&self) -> String {
        format!(
            "Dopamine: {:.2}, Serotonin: {:.2}, Oxytocin: {:.2}, GABA: {:.2}, Melatonin: {:.2}, Cortisol: {:.2}, Temp: {:.1}°C",
            self.dopamine, self.serotonin, self.oxytocin, self.gaba, self.melatonin, self.cortisol, self.temperature
        )
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_default_state() {
        let state = NeurochemicalState::default();
        assert_eq!(state.dopamine, 0.69);
        assert_eq!(state.serotonin, 0.94);
        assert_eq!(state.oxytocin, 0.58);
    }

    #[test]
    fn test_apply_profile_study() {
        let mut state = NeurochemicalState::default();
        state.apply_profile("study");
        assert!(state.dopamine > 0.69);
        assert_eq!(state.temperature, 37.0);
    }

    #[test]
    fn test_apply_profile_wolf_teeth() {
        let mut state = NeurochemicalState::default();
        state.apply_profile("wolf_teeth");
        assert_eq!(state.dopamine, 0.0);
        assert_eq!(state.gaba, 1.0);
        assert_eq!(state.temperature, 35.5);
    }
}
