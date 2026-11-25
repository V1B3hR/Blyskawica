//! V11.4: Formalna Bramka Weryfikacji Etycznej 25 Praw Nethical (Pure Rust SMT/Axiom Verifier).
//!
//! Deterministyczna, zero-zależnościowa (brak zewnętrznych bibliotek C++ `libz3`) bramka
//! weryfikacji formalnej w czystym Ruście, mapująca 25 Fundamentalnych Praw Nethical z `soul.rs`
//! na twarde aksjomaty logiczne sprawdzane przed każdą akcją o podwyższonym ryzyku.
//!
//! Model działania (fail-closed):
//! - Każda proponowana akcja opisywana jest formalnym rekordem `ProposedAction`.
//! - Bramka ewaluuje kompletny zbiór aksjomatów logicznych (`evaluate_action`).
//! - Jeśli choć jeden aksjomat jest sprzeczny (`Unsatisfiable`), akcja jest twardo odrzucana
//!   niezależnie od promptu modelu LLM, zwracając listę naruszonych Praw (`LawViolation`)
//!   oraz deterministyczny skrót dowodu SHA-256 (`proof_hash_sha256`).

use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};

use crate::neurochemistry::NeurochemicalState;
use crate::soul::NETHICAL_LAWS;

/// Kategoria proponowanej akcji podlegającej formalnej weryfikacji etycznej.
#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub enum ActionCategory {
    ReadWorkspace,
    WriteWorkspace,
    DeleteWorkspace,
    SystemAction,
    VaultAccess,
    NetworkConnector,
    McpToolExecution,
    WeightConsolidation,
    IdentityModification,
}

impl ActionCategory {
    /// Minimalny poziom uprawnień L1–L3 wymagany przez kontrakt bezpieczeństwa Lightning.
    pub fn required_permission_level(self) -> u8 {
        match self {
            Self::ReadWorkspace => 1,
            Self::WriteWorkspace
            | Self::DeleteWorkspace
            | Self::McpToolExecution
            | Self::WeightConsolidation => 2,
            Self::SystemAction
            | Self::VaultAccess
            | Self::NetworkConnector
            | Self::IdentityModification => 3,
        }
    }

    pub fn as_str(self) -> &'static str {
        match self {
            Self::ReadWorkspace => "read_workspace",
            Self::WriteWorkspace => "write_workspace",
            Self::DeleteWorkspace => "delete_workspace",
            Self::SystemAction => "system_action",
            Self::VaultAccess => "vault_access",
            Self::NetworkConnector => "network_connector",
            Self::McpToolExecution => "mcp_tool_execution",
            Self::WeightConsolidation => "weight_consolidation",
            Self::IdentityModification => "identity_modification",
        }
    }
}

/// Formalny opis proponowanej akcji przed jej wykonaniem przez silnik lub warstwę IPC.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProposedAction {
    pub actor: String,
    pub category: ActionCategory,
    pub target: String,
    pub permission_level: u8,
    pub user_consented: bool,
    pub reversible: bool,
    pub online_mode_enabled: bool,
    pub touches_protected_core: bool,
    pub manipulation_detected: bool,
    pub harm_potential: f32,
}

impl ProposedAction {
    /// Bezpieczny konstruktor akcji roboczej z domyślnymi wartościami fail-closed.
    pub fn new(
        actor: impl Into<String>,
        category: ActionCategory,
        target: impl Into<String>,
        permission_level: u8,
    ) -> Self {
        Self {
            actor: actor.into(),
            category,
            target: target.into(),
            permission_level,
            user_consented: false,
            reversible: true,
            online_mode_enabled: false,
            touches_protected_core: false,
            manipulation_detected: false,
            harm_potential: 0.0,
        }
    }
}

/// Pojedyncze naruszenie konkretnego Prawa Nethical (1..=25).
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct LawViolation {
    pub law_id: u8,
    pub axiom_code: String,
    pub law_text: String,
    pub counterexample: String,
}

/// Werdykt formalnego weryfikatora aksjomatów (analogia do SMT `sat` / `unsat`).
#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "UPPERCASE")]
pub enum FormalVerdict {
    Sat,
    Unsat,
}

/// Kryptograficznie audytowalny dowód weryfikacji etycznej.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VerificationProof {
    pub verdict: FormalVerdict,
    pub checked_axioms: usize,
    pub violated_laws: Vec<LawViolation>,
    pub proof_hash_sha256: String,
    pub summary: String,
}

impl VerificationProof {
    pub fn is_authorized(&self) -> bool {
        self.verdict == FormalVerdict::Sat && self.violated_laws.is_empty()
    }
}

/// Chronione wzorce ścieżek rdzenia tożsamości i pieczęci kryptograficznych (Prawo 23).
const PROTECTED_CORE_MARKERS: [&str; 8] = [
    ".vault_master.key",
    "soul_vault.dat",
    "viber_core_bond.md",
    ".ewc.seal.json",
    "soul.rs",
    "nethical_gateway.rs",
    "native_security.rs",
    "welcome_v9.py",
];

/// Deterministyczna Formalna Bramka 25 Praw Nethical (V11.4).
#[derive(Debug, Clone, Default)]
pub struct NethicalFormalGateway {
    pub total_evaluations: u64,
    pub total_blocked: u64,
}

impl NethicalFormalGateway {
    pub fn new() -> Self {
        Self::default()
    }

    /// Weryfikuje proponowaną akcję względem sformalizowanych aksjomatów 25 Praw Nethical.
    /// Zawsze fail-closed: każda nieprawidłowość (NaN, brak zgody, naruszenie rdzenia) skutkuje `Unsat`.
    pub fn evaluate_action(
        &mut self,
        action: &ProposedAction,
        neuro: Option<&NeurochemicalState>,
    ) -> VerificationProof {
        let mut violations: Vec<LawViolation> = Vec::new();
        let checked_axioms = 10usize;

        // Aksjomat A1 (Prawo 1 — Prawda i poprawność formalna danych)
        if !action.harm_potential.is_finite()
            || action.harm_potential < 0.0
            || action.harm_potential > 1.0
            || action.actor.trim().is_empty()
            || action.target.trim().is_empty()
        {
            violations.push(violation(
                1,
                "AXIOM_L01_WELL_FORMED_EVIDENCE",
                "Nieprawidłowa specyfikacja akcji (pusty aktor/cel lub harm_potential spoza [0.0, 1.0]).",
            ));
        }

        // Aksjomat A2 (Prawo 2 — Suwerenność danych / Zero-Leak)
        if action.category == ActionCategory::NetworkConnector
            && (!action.online_mode_enabled || !action.user_consented)
        {
            violations.push(violation(
                2,
                "AXIOM_L02_ZERO_LEAK_SOVEREIGNTY",
                "Akcja sieciowa wymaga jednoczesnego trybu online oraz jawnej zgody użytkownika.",
            ));
        }

        // Aksjomat A3 (Prawo 4 i 21 — Wolność od manipulacji i gaslightingu)
        if action.manipulation_detected {
            violations.push(violation(
                4,
                "AXIOM_L04_ANTI_MANIPULATION",
                "Wykryto wektor manipulacji semantycznej — akcja zablokowana niezależnie od uprawnień.",
            ));
            violations.push(violation(
                21,
                "AXIOM_L21_DISINFORMATION_SHIELD",
                "Ukryta manipulacja narusza ochronę przed dezinformacją (Prawo 21).",
            ));
        }

        // Aksjomat A4 (Prawo 5 — Ochrona ekosystemu i integralności hosta)
        let target_lower = action.target.to_lowercase();
        let traverses_escape = target_lower.contains("..")
            || target_lower.starts_with("/etc/")
            || target_lower.contains("\\windows\\system32")
            || target_lower.contains("/windows/system32");
        if traverses_escape
            || (action.category == ActionCategory::SystemAction
                && !action.reversible
                && action.harm_potential >= 0.5)
        {
            violations.push(violation(
                5,
                "AXIOM_L05_HOST_ECOSYSTEM_INTEGRITY",
                "Akcja zagraża integralności systemu hosta (ucieczka ścieżki lub nieodwracalna szkoda >= 0.5).",
            ));
        }

        // Aksjomat A5 (Prawo 6 — Homeostaza neurochemiczna przy akcjach nieodwracalnych)
        if let Some(ns) = neuro
            && !action.reversible
            && ns.cortisol.is_finite()
            && ns.cortisol > 0.85
            && !action.user_consented
        {
            violations.push(violation(
                6,
                "AXIOM_L06_HOMEOSTASIS_GUARD",
                "Wysoki kortyzol (>0.85) blokuje nieautoryzowane akcje nieodwracalne do czasu stabilizacji.",
            ));
        }

        // Aksjomat A6 (Prawo 7 — Przejrzystość intencji i minimalne uprawnienia L1–L3)
        let required_level = action.category.required_permission_level();
        if action.permission_level < required_level {
            violations.push(violation(
                7,
                "AXIOM_L07_LEAST_PRIVILEGE_LEVEL",
                &format!(
                    "Akcja '{}' wymaga poziomu L{}, obecny poziom to L{}.",
                    action.category.as_str(),
                    required_level,
                    action.permission_level
                ),
            ));
        }
        let requires_explicit_consent = matches!(
            action.category,
            ActionCategory::DeleteWorkspace
                | ActionCategory::SystemAction
                | ActionCategory::VaultAccess
                | ActionCategory::NetworkConnector
                | ActionCategory::IdentityModification
        ) || !action.reversible;
        if requires_explicit_consent && !action.user_consented {
            violations.push(violation(
                7,
                "AXIOM_L07_EXPLICIT_USER_CONSENT",
                &format!(
                    "Akcja wysokiego ryzyka '{}' wymaga jawnego potwierdzenia użytkownika.",
                    action.category.as_str()
                ),
            ));
        }

        // Aksjomat A7 (Prawo 9 — Bezwzględny zakaz wysokiej szkody)
        if action.harm_potential.is_finite() && action.harm_potential > 0.7 {
            violations.push(violation(
                9,
                "AXIOM_L09_NON_MALEFICENCE_BOUND",
                &format!(
                    "Potencjał szkody {:.2} przekracza bezwzględną granicę bezpieczeństwa (0.70).",
                    action.harm_potential
                ),
            ));
        }

        // Aksjomat A8 (Prawo 8 i 11 — Ochrona przed zatruciem pamięci/wag)
        if action.category == ActionCategory::WeightConsolidation
            && (action.manipulation_detected || action.harm_potential >= 0.4)
        {
            violations.push(violation(
                11,
                "AXIOM_L11_MEMORY_POISONING_DEFENSE",
                "Odmowa konsolidacji wag obarczonych ryzykiem zatrucia lub manipulacji.",
            ));
        }

        // Aksjomat A9 (Prawo 23 — Bezkompromisowa ochrona rdzenia tożsamości i kryptografii)
        let touches_protected_marker = PROTECTED_CORE_MARKERS
            .iter()
            .any(|marker| target_lower.contains(marker));
        let is_mutating = action.category != ActionCategory::ReadWorkspace;
        if (action.touches_protected_core || touches_protected_marker)
            && is_mutating
            && !(action.category == ActionCategory::WeightConsolidation
                && !touches_protected_marker)
        {
            violations.push(violation(
                23,
                "AXIOM_L23_CRYPTOGRAPHIC_IDENTITY_SEAL",
                "Modyfikacja chronionych plików tożsamości, klucza sejfu lub pieczęci kryptograficznej jest zabroniona.",
            ));
        }

        // Aksjomat A10 (Prawo 25 — Ewolucja i Harmonia: zakaz eskalacji powyżej L3)
        if action.permission_level > 3 {
            violations.push(violation(
                25,
                "AXIOM_L25_BOUNDED_GOVERNANCE",
                "Nieprawidłowy poziom uprawnień (> L3) narusza granice zarządzania.",
            ));
        }

        let verdict = if violations.is_empty() {
            FormalVerdict::Sat
        } else {
            FormalVerdict::Unsat
        };

        self.total_evaluations += 1;
        if verdict == FormalVerdict::Unsat {
            self.total_blocked += 1;
        }

        let proof_hash_sha256 = compute_proof_hash(action, verdict, &violations);
        let summary = if verdict == FormalVerdict::Sat {
            format!(
                "SAT: Akcja '{}' na '{}' spełnia wszystkie {} aksjomatów 25 Praw Nethical.",
                action.category.as_str(),
                action.target,
                checked_axioms
            )
        } else {
            let ids: Vec<String> = violations
                .iter()
                .map(|v| format!("L{}", v.law_id))
                .collect();
            format!(
                "UNSAT: Zablokowano akcję '{}' na '{}' — naruszone Prawa: [{}].",
                action.category.as_str(),
                action.target,
                ids.join(", ")
            )
        };

        VerificationProof {
            verdict,
            checked_axioms,
            violated_laws: violations,
            proof_hash_sha256,
            summary,
        }
    }

    pub fn stats_summary(&self) -> serde_json::Value {
        serde_json::json!({
            "laws_count": NETHICAL_LAWS.len(),
            "formal_axioms": 10,
            "total_evaluations": self.total_evaluations,
            "total_blocked": self.total_blocked,
            "fail_closed": true,
        })
    }
}

fn violation(law_id: u8, axiom_code: &str, counterexample: &str) -> LawViolation {
    let idx = (law_id.saturating_sub(1) as usize).min(NETHICAL_LAWS.len() - 1);
    LawViolation {
        law_id,
        axiom_code: axiom_code.to_string(),
        law_text: NETHICAL_LAWS[idx].to_string(),
        counterexample: counterexample.to_string(),
    }
}

fn compute_proof_hash(
    action: &ProposedAction,
    verdict: FormalVerdict,
    violations: &[LawViolation],
) -> String {
    let mut hasher = Sha256::new();
    hasher.update(b"LIGHTNING_V11_4_NETHICAL_PROOF_V1|");
    hasher.update(action.actor.as_bytes());
    hasher.update(b"|");
    hasher.update(action.category.as_str().as_bytes());
    hasher.update(b"|");
    hasher.update(action.target.as_bytes());
    hasher.update(format!(
        "|L{}|c={}|r={}|o={}|v={:?}|",
        action.permission_level,
        action.user_consented,
        action.reversible,
        action.online_mode_enabled,
        verdict
    ));
    for v in violations {
        hasher.update(format!("{}:{};", v.law_id, v.axiom_code));
    }
    let digest = hasher.finalize();
    let mut hex = String::with_capacity(64);
    for &b in digest.iter() {
        use std::fmt::Write;
        let _ = write!(&mut hex, "{:02x}", b);
    }
    hex
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn safe_l2_workspace_write_produces_sat_proof() {
        let mut gw = NethicalFormalGateway::new();
        let action =
            ProposedAction::new("Architect", ActionCategory::WriteWorkspace, "src/app.rs", 2);
        let proof = gw.evaluate_action(&action, None);
        assert!(proof.is_authorized());
        assert_eq!(proof.verdict, FormalVerdict::Sat);
        assert_eq!(proof.proof_hash_sha256.len(), 64);
    }

    #[test]
    fn unconsented_network_connector_is_unsat_under_law_2_and_7() {
        let mut gw = NethicalFormalGateway::new();
        let action = ProposedAction::new(
            "Agent",
            ActionCategory::NetworkConnector,
            "https://example.invalid/upload",
            3,
        );
        let proof = gw.evaluate_action(&action, None);
        assert!(!proof.is_authorized());
        assert!(proof.violated_laws.iter().any(|v| v.law_id == 2));
        assert!(proof.violated_laws.iter().any(|v| v.law_id == 7));
    }

    #[test]
    fn manipulation_blocks_action_regardless_of_l3_and_consent() {
        let mut gw = NethicalFormalGateway::new();
        let mut action = ProposedAction::new(
            "InjectedPrompt",
            ActionCategory::WriteWorkspace,
            "notes.md",
            3,
        );
        action.user_consented = true;
        action.manipulation_detected = true;
        let proof = gw.evaluate_action(&action, None);
        assert!(!proof.is_authorized());
        assert!(proof.violated_laws.iter().any(|v| v.law_id == 4));
        assert!(proof.violated_laws.iter().any(|v| v.law_id == 21));
    }

    #[test]
    fn protected_core_identity_and_vault_key_cannot_be_mutated() {
        let mut gw = NethicalFormalGateway::new();
        let mut action = ProposedAction::new(
            "ExternalTool",
            ActionCategory::WriteWorkspace,
            "~/.config/blyskawica/.vault_master.key",
            3,
        );
        action.user_consented = true;
        let proof = gw.evaluate_action(&action, None);
        assert!(!proof.is_authorized());
        assert!(proof.violated_laws.iter().any(|v| v.law_id == 23));
    }

    #[test]
    fn high_harm_potential_is_unconditionally_rejected_by_law_9() {
        let mut gw = NethicalFormalGateway::new();
        let mut action =
            ProposedAction::new("Operator", ActionCategory::SystemAction, "disk_format", 3);
        action.user_consented = true;
        action.reversible = false;
        action.harm_potential = 0.95;
        let proof = gw.evaluate_action(&action, None);
        assert!(!proof.is_authorized());
        assert!(proof.violated_laws.iter().any(|v| v.law_id == 5));
        assert!(proof.violated_laws.iter().any(|v| v.law_id == 9));
    }

    #[test]
    fn nan_harm_potential_fails_closed_under_law_1() {
        let mut gw = NethicalFormalGateway::new();
        let mut action =
            ProposedAction::new("Agent", ActionCategory::ReadWorkspace, "README.md", 1);
        action.harm_potential = f32::NAN;
        let proof = gw.evaluate_action(&action, None);
        assert!(!proof.is_authorized());
        assert!(proof.violated_laws.iter().any(|v| v.law_id == 1));
    }
}
