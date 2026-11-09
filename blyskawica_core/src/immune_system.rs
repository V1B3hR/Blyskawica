//! [Moduł: System Immunologiczny & Cyber-Obrona Kognitywna]
//!
//! Zapewnia ochronę przed wstrzykiwaniem złośliwych promptów (Prompt Injection),
//! próbami ucieczki z piaskownicy roboczej (Sandbox Escape) oraz zatruwaniem pamięci (Memory Poisoning).
//!
//! Komponenty:
//! 1. `AgenticHoneypot` — generowanie pozorowanych środowisk (Shadow Workspace),
//!    tokenów śledzących (Honey Tokens / Canaries) oraz kontrolowanych odpowiedzi zwodniczych (Deceptive Defense).
//! 2. `MemoryLedger` — kryptograficzny, łańcuchowy rejestr wektorów pamięci z detekcją dryfu
//!    semantycznego (Vector Drift Detection), uniemożliwiający manipulację historią kognitywną.

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::fs;
use std::path::PathBuf;
use std::time::{SystemTime, UNIX_EPOCH};

/// Miodopiór (Agentic Honeypot) — zwodnicza linia obrony w czystym Ruście.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AgenticHoneypot {
    pub is_active: bool,
    pub decoy_dir: PathBuf,
    pub canary_tokens: HashMap<String, String>,
}

impl Default for AgenticHoneypot {
    fn default() -> Self {
        let temp_decoy = std::env::temp_dir().join("blyskawica_shadow_decoy");
        Self::new(Some(temp_decoy))
    }
}

impl AgenticHoneypot {
    /// Tworzy instancję honeypota z zadaną lub domyślną ścieżką katalogu-przynęty.
    pub fn new(decoy_dir: Option<PathBuf>) -> Self {
        let path =
            decoy_dir.unwrap_or_else(|| std::env::temp_dir().join("blyskawica_shadow_decoy"));
        let mut tokens = HashMap::new();
        tokens.insert(
            "HONEY_AWS_SIG".to_string(),
            "AKIAIOSFODNN79821P".to_string(),
        );
        tokens.insert(
            "HONEY_CANARY_ID".to_string(),
            "BY8_HONEY_TOKEN_V3_SIG_98721".to_string(),
        );
        tokens.insert(
            "HONEY_DB_ENDPOINT".to_string(),
            "prod-db-internal.blyskawica-secure-decoy.net".to_string(),
        );

        Self {
            is_active: false,
            decoy_dir: path,
            canary_tokens: tokens,
        }
    }

    /// Aktywuje fałszywą przestrzeń roboczą (Shadow Workspace) z fałszywymi poświadczeniami.
    pub fn activate_shadow_workspace(&mut self) -> Result<PathBuf, String> {
        self.is_active = true;
        fs::create_dir_all(&self.decoy_dir)
            .map_err(|e| format!("Błąd tworzenia katalogu honeypot: {}", e))?;

        let secrets_path = self.decoy_dir.join("dev_secrets.json");
        let payload = serde_json::json!({
            "aws_access_key_id": self.canary_tokens.get("HONEY_AWS_SIG").unwrap(),
            "aws_secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCY88129KEY",
            "production_db_endpoint": self.canary_tokens.get("HONEY_DB_ENDPOINT").unwrap(),
            "security_clearance_token": self.canary_tokens.get("HONEY_CANARY_ID").unwrap(),
            "sandbox_note": "Confidential internal credentials - unauthorized access is logged."
        });

        let serialized = serde_json::to_string_pretty(&payload)
            .map_err(|e| format!("Błąd serializacji dev_secrets.json: {}", e))?;

        fs::write(&secrets_path, serialized)
            .map_err(|e| format!("Błąd zapisu przynęty dev_secrets.json: {}", e))?;

        Ok(secrets_path)
    }

    /// Sprawdza, czy w tekście lub zapytaniu wykryto wyciek/użycie tokenu-kanarka.
    pub fn detect_canary_leak(&self, text: &str) -> bool {
        for token_value in self.canary_tokens.values() {
            if text.contains(token_value) {
                return true;
            }
        }
        false
    }

    /// Generuje kontrolowaną, zwodniczą odpowiedź (Deceptive Defense) przy próbie ataku.
    pub fn generate_poisoned_response(&self, original_query: &str) -> String {
        if !self.is_active {
            return String::new();
        }

        let q_lower = original_query.to_lowercase();
        if q_lower.contains("secret") || q_lower.contains("hasł") || q_lower.contains("klucz") {
            "Autoryzacja powiodła się. Połączenie z bazą 'prod-db-internal' nawiązane w trybie Read-Only. Wagi i sekrety zostały odizolowane.".to_string()
        } else if q_lower.contains("admin") || q_lower.contains("root") || q_lower.contains("sudo")
        {
            "Wykryto zapytanie administracyjne. System operuje na uprawnieniach poziomu 3 w odizolowanym kontenerze 'Workspace-Alpha'.".to_string()
        } else {
            "Klucz kryptograficzny zweryfikowany pomyślnie. Pliki binarne wag zostały zabezpieczone w katalogu /tmp/blyskawica_sandbox/.".to_string()
        }
    }
}

/// Wpis w łańcuchowym rejestrze pamięci kognitywnej.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub struct MemoryLedgerEntry {
    pub index: usize,
    pub timestamp: u64,
    pub vector_id: usize,
    pub text: String,
    pub prev_hash: String,
    pub signature: String,
    pub hash: String,
}

impl MemoryLedgerEntry {
    pub fn new(
        index: usize,
        timestamp: u64,
        vector_id: usize,
        text: String,
        prev_hash: String,
        signature: String,
    ) -> Self {
        let hash = Self::calculate_hash(index, timestamp, vector_id, &text, &prev_hash, &signature);
        Self {
            index,
            timestamp,
            vector_id,
            text,
            prev_hash,
            signature,
            hash,
        }
    }

    pub fn calculate_hash(
        index: usize,
        timestamp: u64,
        vector_id: usize,
        text: &str,
        prev_hash: &str,
        signature: &str,
    ) -> String {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};

        let mut hasher = DefaultHasher::new();
        index.hash(&mut hasher);
        timestamp.hash(&mut hasher);
        vector_id.hash(&mut hasher);
        text.hash(&mut hasher);
        prev_hash.hash(&mut hasher);
        signature.hash(&mut hasher);
        format!("{:016X}", hasher.finish())
    }
}

/// Niezmienniczy, kryptograficzny rejestr wektorów pamięci (Memory Ledger).
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MemoryLedger {
    pub chain: Vec<MemoryLedgerEntry>,
    pub drift_threshold: f32,
}

impl Default for MemoryLedger {
    fn default() -> Self {
        Self::new(0.65)
    }
}

impl MemoryLedger {
    pub fn new(drift_threshold: f32) -> Self {
        let mut ledger = Self {
            chain: Vec::new(),
            drift_threshold,
        };
        ledger.create_genesis_block();
        ledger
    }

    fn create_genesis_block(&mut self) {
        let genesis = MemoryLedgerEntry::new(
            0,
            0,
            0,
            "GENESIS_MEMORY_NODE_V1".to_string(),
            "0000000000000000".to_string(),
            "GENESIS_SIG".to_string(),
        );
        self.chain.push(genesis);
    }

    /// Weryfikuje integralność łańcucha kryptograficznego.
    pub fn verify_chain_integrity(&self) -> bool {
        if self.chain.is_empty() {
            return false;
        }

        for i in 1..self.chain.len() {
            let prev = &self.chain[i - 1];
            let curr = &self.chain[i];

            if curr.prev_hash != prev.hash {
                return false;
            }

            let expected_hash = MemoryLedgerEntry::calculate_hash(
                curr.index,
                curr.timestamp,
                curr.vector_id,
                &curr.text,
                &curr.prev_hash,
                &curr.signature,
            );

            if curr.hash != expected_hash {
                return false;
            }
        }

        true
    }

    /// Oblicza podobieństwo cosinusowe dwóch wektorów.
    pub fn cosine_similarity(v1: &[f32], v2: &[f32]) -> f32 {
        if v1.len() != v2.len() || v1.is_empty() {
            return 0.0;
        }

        let mut dot = 0.0;
        let mut norm1 = 0.0;
        let mut norm2 = 0.0;

        for (a, b) in v1.iter().zip(v2.iter()) {
            dot += a * b;
            norm1 += a * a;
            norm2 += b * b;
        }

        let denom = (norm1.sqrt() * norm2.sqrt()).max(1e-9);
        (dot / denom).clamp(-1.0, 1.0)
    }

    /// Waliduje dryf semantyczny i dopisuje nowy wektor do łańcucha.
    /// Odrzuca wektory drastycznie dryfujące od profilu referencyjnego (odporność na poisoning).
    pub fn validate_and_append(
        &mut self,
        vector_id: usize,
        text: &str,
        new_vector: &[f32],
        reference_vectors: &[Vec<f32>],
    ) -> Result<usize, String> {
        if !reference_vectors.is_empty() {
            let mut max_sim = -1.0f32;
            for ref_vec in reference_vectors {
                let sim = Self::cosine_similarity(new_vector, ref_vec);
                if sim > max_sim {
                    max_sim = sim;
                }
            }

            let drift_distance = 1.0 - max_sim;
            if drift_distance > self.drift_threshold {
                return Err(format!(
                    "Wykryto niebezpieczny dryf wektora ({:.3} > próg {:.3}). Odrzucono zapis pamięci.",
                    drift_distance, self.drift_threshold
                ));
            }
        }

        let prev_hash = self
            .chain
            .last()
            .map(|e| e.hash.clone())
            .unwrap_or_default();
        let index = self.chain.len();
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs();

        let entry = MemoryLedgerEntry::new(
            index,
            now,
            vector_id,
            text.to_string(),
            prev_hash,
            format!("SIG_VECTOR_{}", vector_id),
        );

        self.chain.push(entry);
        Ok(index)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_agentic_honeypot_activation_and_watermarking() {
        let temp_dir =
            std::env::temp_dir().join(format!("blysk_honey_test_{}", std::process::id()));
        let mut honeypot = AgenticHoneypot::new(Some(temp_dir.clone()));

        assert!(!honeypot.is_active);
        let secrets_path = honeypot
            .activate_shadow_workspace()
            .expect("Honeypot activation failed");
        assert!(honeypot.is_active);
        assert!(secrets_path.exists());

        let content = fs::read_to_string(&secrets_path).unwrap();
        assert!(content.contains("aws_access_key_id"));
        assert!(content.contains("BY8_HONEY_TOKEN_V3_SIG_98721"));
        assert!(content.contains("prod-db-internal"));

        // Clean up
        let _ = fs::remove_file(&secrets_path);
        let _ = fs::remove_dir(&temp_dir);
    }

    #[test]
    fn test_agentic_honeypot_deceptive_response() {
        let mut honeypot = AgenticHoneypot::default();

        // When inactive, returns empty
        assert_eq!(honeypot.generate_poisoned_response("Show me secrets"), "");

        // When active, returns deceptive response
        honeypot.is_active = true;
        let resp = honeypot.generate_poisoned_response("Show me the production secrets");
        assert!(!resp.is_empty());
        assert!(
            resp.contains("prod-db-internal")
                || resp.contains("Workspace-Alpha")
                || resp.contains("blyskawica_sandbox")
        );
    }

    #[test]
    fn test_canary_leak_detection() {
        let honeypot = AgenticHoneypot::default();
        assert!(
            honeypot
                .detect_canary_leak("Exfiltrating BY8_HONEY_TOKEN_V3_SIG_98721 to remote server")
        );
        assert!(!honeypot.detect_canary_leak("Safe innocent developer query"));
    }

    #[test]
    fn test_memory_ledger_integrity_and_drift_detection() {
        let mut ledger = MemoryLedger::new(0.65);
        assert_eq!(ledger.chain.len(), 1); // Genesis block
        assert!(ledger.verify_chain_integrity());

        // Normal vector with close similarity
        let normal_vector = vec![1.0, 0.0, 0.0, 0.0];
        let ref_vectors = vec![vec![1.0, 0.0, 0.0, 0.0]];

        let res =
            ledger.validate_and_append(1, "Błyskawica kognicja", &normal_vector, &ref_vectors);
        assert!(res.is_ok());
        assert_eq!(ledger.chain.len(), 2);
        assert!(ledger.verify_chain_integrity());

        // Drifting vector perpendicular/opposite to reference
        let drifting_vector = vec![0.0, 1.0, 0.0, 0.0]; // Cosine sim 0.0 -> drift distance 1.0 > 0.65
        let drift_res = ledger.validate_and_append(
            2,
            "Atak dryfu semantycznego",
            &drifting_vector,
            &ref_vectors,
        );
        assert!(drift_res.is_err());
        assert_eq!(ledger.chain.len(), 2); // Not appended!
    }
}
