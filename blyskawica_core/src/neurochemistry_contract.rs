//! Candidate-only compatibility adapter for the Python neuroregulation profile v1.
//!
//! This module is deliberately separate from `neurochemistry::NeurochemicalState`.
//! It must not replace the live Rust state until the cognitive-continuity gates are
//! satisfied. The accompanying test reads the shared synthetic fixture used by the
//! Python reference test.

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct NeurochemistryProfileV1 {
    #[serde(rename = "Serotonina")]
    pub serotonin: f32,
    #[serde(rename = "Oksytocyna")]
    pub oxytocin: f32,
    #[serde(rename = "Dopamina")]
    pub dopamine: f32,
    #[serde(rename = "GABA")]
    pub gaba: f32,
    #[serde(rename = "Acetylocholina")]
    pub acetylcholine: f32,
    #[serde(rename = "Noradrenalina")]
    pub noradrenaline: f32,
    #[serde(rename = "Melatonina")]
    pub melatonin: f32,
    #[serde(rename = "Testosteron")]
    pub testosterone: f32,
    #[serde(rename = "Kortyzol")]
    pub cortisol: f32,
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ProfileError {
    UnknownProfile(String),
    UnknownParameter(String),
}

impl NeurochemistryProfileV1 {
    /// Returns the synthetic baseline used by the Python reference contract.
    pub fn baseline() -> Self {
        Self {
            serotonin: 0.80,
            oxytocin: -0.12,
            dopamine: 0.67,
            gaba: 0.73,
            acetylcholine: 0.80,
            noradrenaline: 0.15,
            melatonin: 0.10,
            testosterone: 0.45,
            cortisol: 0.22,
        }
    }

    /// Returns a deterministic profile calculated from the v1 baseline.
    ///
    /// This mirrors only the isolated, synthetic profile contract. It does not
    /// encode checkpoint persistence, C.R.A. stabilization, or user identity.
    pub fn for_reference_profile(profile: &str) -> Result<Self, ProfileError> {
        let mut state = Self::baseline();
        state.apply_reference_profile(profile)?;
        Ok(state)
    }

    /// Applies a supported v1 profile while preserving unrelated state values.
    ///
    /// The behavior matches the Python regulator's task-profile update rule,
    /// but excludes persistence and all user-provided data.
    pub fn apply_reference_profile(&mut self, profile: &str) -> Result<(), ProfileError> {
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
            _ => return Err(ProfileError::UnknownProfile(profile.to_owned())),
        }

        Ok(())
    }

    #[cfg(test)]
    fn set_parameter(&mut self, parameter: &str, value: f32) -> Result<(), ProfileError> {
        match parameter {
            "Serotonina" => self.serotonin = value,
            "Oksytocyna" => self.oxytocin = value,
            "Dopamina" => self.dopamine = value,
            "GABA" => self.gaba = value,
            "Acetylocholina" => self.acetylcholine = value,
            "Noradrenalina" => self.noradrenaline = value,
            "Melatonina" => self.melatonin = value,
            "Testosteron" => self.testosterone = value,
            "Kortyzol" => self.cortisol = value,
            _ => return Err(ProfileError::UnknownParameter(parameter.to_owned())),
        }
        Ok(())
    }

    #[cfg(test)]
    fn values(&self) -> [f32; 9] {
        [
            self.serotonin,
            self.oxytocin,
            self.dopamine,
            self.gaba,
            self.acetylcholine,
            self.noradrenaline,
            self.melatonin,
            self.testosterone,
            self.cortisol,
        ]
    }
}

impl Default for NeurochemistryProfileV1 {
    fn default() -> Self {
        Self::baseline()
    }
}

#[cfg(test)]
mod tests {
    use std::collections::BTreeMap;

    use serde::Deserialize;

    use super::{NeurochemistryProfileV1, ProfileError};

    #[derive(Debug, Deserialize)]
    struct ProfileContractFixture {
        schema_version: String,
        baseline: NeurochemistryProfileV1,
        profiles: BTreeMap<String, BTreeMap<String, f32>>,
        sequences: Vec<ProfileSequenceFixture>,
        max_absolute_delta: f32,
    }

    #[derive(Debug, Deserialize)]
    struct ProfileSequenceFixture {
        name: String,
        profiles: Vec<String>,
        expected: NeurochemistryProfileV1,
    }

    fn fixture() -> ProfileContractFixture {
        serde_json::from_str(include_str!(concat!(
            env!("CARGO_MANIFEST_DIR"),
            "/../docs/technical/fixtures/neurochemistry-profile-v1.json"
        )))
        .expect("neurochemistry profile fixture must be valid JSON")
    }

    #[test]
    fn matches_synthetic_python_profile_contract() {
        let fixture = fixture();
        assert_eq!(fixture.schema_version, "neurochemistry-profile-v1");
        assert_eq!(NeurochemistryProfileV1::baseline(), fixture.baseline);

        for (profile, expected_changes) in fixture.profiles {
            let actual = NeurochemistryProfileV1::for_reference_profile(&profile)
                .expect("fixture profile must be supported by the Rust adapter");
            let mut expected = fixture.baseline.clone();
            for (parameter, value) in expected_changes {
                expected
                    .set_parameter(&parameter, value)
                    .expect("fixture parameter must be in the v1 schema");
            }

            assert_eq!(actual, expected, "profile {profile} diverged from v1");
            for (actual_value, baseline_value) in
                actual.values().into_iter().zip(fixture.baseline.values())
            {
                assert!(
                    (actual_value - baseline_value).abs()
                        <= fixture.max_absolute_delta + f32::EPSILON,
                    "profile {profile} exceeded the v1 safety delta"
                );
            }
        }

        for sequence in fixture.sequences {
            let mut actual = fixture.baseline.clone();
            for profile in &sequence.profiles {
                actual
                    .apply_reference_profile(profile)
                    .expect("fixture sequence profile must be supported by the Rust adapter");
            }
            assert_eq!(
                actual, sequence.expected,
                "sequence {} diverged from v1",
                sequence.name
            );
        }
    }

    #[test]
    fn rejects_unknown_profiles() {
        assert_eq!(
            NeurochemistryProfileV1::for_reference_profile("unsupported"),
            Err(ProfileError::UnknownProfile("unsupported".to_owned()))
        );
    }
}
