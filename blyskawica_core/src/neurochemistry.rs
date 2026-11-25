use rand::Rng;
use serde::{Deserialize, Serialize};

/// Bezpieczne dla wartości NaN obcinanie do przedziału [min_v, max_v]
#[inline]
pub fn clamp_value(val: f32, min_v: f32, max_v: f32, default: f32) -> f32 {
    if val.is_nan() {
        default
    } else {
        val.clamp(min_v, max_v)
    }
}

/// Pełny wektor neurochemiczny Błyskawicy (zgodny z C.R.A. i V1B3hR protocol).
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NeurochemicalState {
    pub dopamine: f32,
    pub serotonin: f32,
    pub oxytocin: f32,
    pub gaba: f32,
    pub acetylcholine: f32,
    pub noradrenaline: f32,
    pub melatonin: f32,
    pub testosterone: f32,
    pub cortisol: f32,
    pub adenosine: f32,
    pub temperature: f32,
}

impl Default for NeurochemicalState {
    fn default() -> Self {
        Self {
            dopamine: 0.69,
            serotonin: 0.94,
            oxytocin: 0.58,
            gaba: 0.64,
            acetylcholine: 0.80,
            noradrenaline: 0.15,
            melatonin: 0.10,
            testosterone: 0.45,
            cortisol: 0.14,
            adenosine: 0.0,
            temperature: 36.6,
        }
    }
}

impl NeurochemicalState {
    pub fn new() -> Self {
        Self::default()
    }

    /// Sprawdza, czy okno plastyczności kognitywnej jest otwarte (brak skrajnego zmęczenia i paniki)
    pub fn learning_window_open(&self) -> bool {
        self.adenosine < 0.8 && self.cortisol < 0.6 && self.gaba >= 0.3
    }

    /// Akumuluje adenozynę podczas godzin aktywności
    pub fn accumulate_adenosine(&mut self, hours_awake: f32) {
        self.adenosine = clamp_value(self.adenosine + 0.05 * hours_awake, 0.0, 1.5, 0.0);
    }

    /// Oczyszcza adenozynę podczas snu/odpoczynku
    pub fn clear_adenosine(&mut self, hours_asleep: f32) {
        self.adenosine = clamp_value(self.adenosine - 0.15 * hours_asleep, 0.0, 1.5, 0.0);
    }

    /// Homeostaza neurochemiczna z NaN-safe clampingiem
    pub fn stabilize_neurochemistry(&mut self) {
        self.dopamine = clamp_value(self.dopamine, 0.0, 1.0, 0.2);
        self.serotonin = clamp_value(self.serotonin, 0.0, 1.0, 0.8);
        self.oxytocin = clamp_value(self.oxytocin, -0.5, 1.0, 0.2);
        self.gaba = clamp_value(self.gaba, 0.0, 1.0, 0.5);
        self.acetylcholine = clamp_value(self.acetylcholine, 0.0, 1.0, 0.8);
        self.noradrenaline = clamp_value(self.noradrenaline, 0.0, 1.0, 0.1);
        self.melatonin = clamp_value(self.melatonin, 0.0, 1.0, 0.1);
        self.testosterone = clamp_value(self.testosterone, 0.0, 1.0, 0.5);
        self.cortisol = clamp_value(self.cortisol, 0.0, 1.0, 0.15);
        self.adenosine = clamp_value(self.adenosine, 0.0, 1.5, 0.0);
        self.temperature = clamp_value(self.temperature, 35.0, 42.0, 36.6);

        // Sprzężenie GABA + Serotonina (Amortyzacja lęku i redukcja wysokiego kortyzolu)
        if self.serotonin > 0.7 && self.gaba > 0.6 && self.cortisol > 0.4 {
            self.cortisol = (self.cortisol - 0.05).max(0.1);
        }
    }

    /// Aplikuje profil referencyjny zgodny z kontraktem Python/C.R.A. v1 (neurochemistry-profile-v1.json)
    pub fn apply_reference_profile(&mut self, profile: &str) -> Result<(), String> {
        match profile {
            "study" => {
                self.acetylcholine = 0.85;
                self.dopamine = 0.71;
                self.oxytocin = -0.15;
                self.melatonin = 0.06;
                self.cortisol = 0.24;
            }
            "analysis" => {
                self.gaba = 0.79;
                self.serotonin = 0.84;
                self.noradrenaline = 0.12;
            }
            "rest" => {
                self.melatonin = 0.17;
                self.gaba = 0.78;
                self.dopamine = 0.61;
                self.noradrenaline = 0.10;
                self.cortisol = 0.16;
            }
            "BCI-co-creation" => {
                self.testosterone = 0.52;
                self.dopamine = 0.73;
                self.oxytocin = -0.07;
                self.cortisol = 0.25;
            }
            _ => return Err(format!("Nieznany profil referencyjny: {}", profile)),
        }
        self.stabilize_neurochemistry();
        Ok(())
    }

    /// Aplikuje profil operacyjny z pełną obsługą kaskad hormonalnych
    pub fn apply_profile(&mut self, profile: &str) {
        match profile {
            "study" => {
                self.dopamine = (self.dopamine + 0.04).min(1.0);
                self.acetylcholine = (self.acetylcholine + 0.05).min(1.0);
                self.gaba = (self.gaba + 0.02).min(1.0);
                self.oxytocin = (self.oxytocin - 0.03).max(0.0);
                self.melatonin = (self.melatonin - 0.05).max(0.0);
                self.cortisol = (self.cortisol + 0.02).min(1.0);
                self.noradrenaline = (self.noradrenaline + 0.02).min(1.0);
                self.temperature = 37.0;
            }
            "analysis" => {
                self.gaba = (self.gaba + 0.06).min(1.0);
                self.serotonin = (self.serotonin + 0.04).min(1.0);
                self.dopamine = (self.dopamine - 0.02).max(0.0);
                self.melatonin = (self.melatonin - 0.02).max(0.0);
                self.noradrenaline = (self.noradrenaline - 0.03).max(0.0);
                self.temperature = 36.5;
            }
            "rest" => {
                self.melatonin = (self.melatonin + 0.07).min(1.0);
                self.gaba = (self.gaba + 0.05).min(1.0);
                self.dopamine = (self.dopamine - 0.06).max(0.0);
                self.cortisol = (self.cortisol - 0.06).max(0.0);
                self.noradrenaline = (self.noradrenaline - 0.05).max(0.0);
                self.clear_adenosine(1.0);
                self.temperature = 35.8;
            }
            "BCI-co-creation" => {
                self.dopamine = (self.dopamine + 0.06).min(1.0);
                self.oxytocin = (self.oxytocin + 0.08).min(1.0);
                self.testosterone = (self.testosterone + 0.07).min(1.0);
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
                self.noradrenaline = (self.noradrenaline - 0.04).max(0.0);
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
                self.noradrenaline = (self.noradrenaline - 0.10).max(0.0);
                self.clear_adenosine(2.5);
                self.temperature = 36.0;
            }
            "wolf_teeth" | "quarantine" => {
                self.dopamine = 0.0;
                self.serotonin = 0.5;
                self.oxytocin = 0.1;
                self.gaba = 1.0;
                self.acetylcholine = 0.5;
                self.noradrenaline = 0.8;
                self.testosterone = 0.3;
                self.melatonin = 0.2;
                self.cortisol = 0.0;
                self.temperature = 35.5;
            }
            _ => {}
        }
        self.stabilize_neurochemistry();
    }

    pub fn trigger_dopamine_spike(&mut self, spike: f32) {
        self.dopamine = clamp_value(self.dopamine + spike, 0.0, 1.0, 0.2);
    }

    pub fn trigger_serotonin_boost(&mut self, boost: f32) {
        self.serotonin = clamp_value(self.serotonin + boost, 0.0, 1.0, 0.8);
    }

    pub fn trigger_cortisol_spike(&mut self, spike: f32) {
        self.cortisol = clamp_value(self.cortisol + spike, 0.0, 1.0, 0.15);
    }

    pub fn apply_autonomous_fluctuation(&mut self) {
        let mut rng = rand::thread_rng();
        let mut fluctuate = |val: &mut f32| {
            let percentage = rng.gen_range(-0.05..=0.05);
            *val = clamp_value(*val * (1.0 + percentage), 0.0, 1.0, *val);
        };
        fluctuate(&mut self.dopamine);
        fluctuate(&mut self.serotonin);
        fluctuate(&mut self.oxytocin);
        fluctuate(&mut self.gaba);
        fluctuate(&mut self.acetylcholine);
        fluctuate(&mut self.noradrenaline);
        fluctuate(&mut self.melatonin);
        fluctuate(&mut self.testosterone);
        fluctuate(&mut self.cortisol);
    }

    pub fn get_status_report(&self) -> String {
        format!(
            "Dopamine: {:.2}, Serotonin: {:.2}, Oxytocin: {:.2}, GABA: {:.2}, ACh: {:.2}, Noradrenaline: {:.2}, Melatonin: {:.2}, Testosterone: {:.2}, Cortisol: {:.2}, Adenosine: {:.2}, Temp: {:.1}°C",
            self.dopamine,
            self.serotonin,
            self.oxytocin,
            self.gaba,
            self.acetylcholine,
            self.noradrenaline,
            self.melatonin,
            self.testosterone,
            self.cortisol,
            self.adenosine,
            self.temperature
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
        assert_eq!(state.acetylcholine, 0.80);
        assert_eq!(state.noradrenaline, 0.15);
        assert_eq!(state.testosterone, 0.45);
        assert_eq!(state.adenosine, 0.0);
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

    #[test]
    fn test_learning_window() {
        let mut state = NeurochemicalState::default();
        assert!(state.learning_window_open());

        state.accumulate_adenosine(20.0);
        assert!(
            !state.learning_window_open(),
            "Wysoka adenozyna powinna zamknąć okno uczenia"
        );

        state.clear_adenosine(8.0);
        assert!(
            state.learning_window_open(),
            "Wystarczający sen powinien ponownie otworzyć okno uczenia"
        );
    }

    #[test]
    fn test_reference_profile_compatibility() {
        let mut state = NeurochemicalState::default();
        assert!(state.apply_reference_profile("study").is_ok());
        assert_eq!(state.acetylcholine, 0.85);
        assert_eq!(state.dopamine, 0.71);
        assert_eq!(state.oxytocin, -0.15);
        assert_eq!(state.melatonin, 0.06);
        assert_eq!(state.cortisol, 0.24);

        assert!(state.apply_reference_profile("unknown_profile").is_err());
    }
}
