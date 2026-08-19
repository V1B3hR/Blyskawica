use serde::{Deserialize, Serialize};
use std::time::{SystemTime, UNIX_EPOCH};

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum AegisActionType {
    RegistryTampering,
    ProcessInjection,
    UnauthorizedFileWrite,
    PortHijack,
    RogueAgentSpawn,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum SentinelActionStatus {
    QuarantinedInJobObject,
    AllowedByArchitect,
    Terminated,
    Monitoring,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AegisSecurityEvent {
    pub id: String,
    pub timestamp: u64,
    pub process_id: u32,
    pub process_name: String,
    pub target_resource: String,
    pub action_type: AegisActionType,
    pub severity: u8, // 1: Info, 2: Low, 3: Medium, 4: High, 5: Critical
    pub status: SentinelActionStatus,
    pub rationale: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AegisPostureSummary {
    pub active_shields: bool,
    pub intercepted_threats_count: usize,
    pub quarantined_processes_count: usize,
    pub system_integrity_score: f32, // 0.0 - 1.0 (1.0 = idealna homeostaza)
}

pub struct AegisSentinel {
    pub events_history: Vec<AegisSecurityEvent>,
    pub protected_paths: Vec<String>,
    pub protected_registry_keys: Vec<String>,
}

impl AegisSentinel {
    pub fn new() -> Self {
        Self {
            events_history: Vec::new(),
            protected_paths: vec![
                "C:\\Windows".to_string(),
                "C:\\Windows\\System32".to_string(),
                "C:\\Program Files".to_string(),
                "C:\\Windows\\System32\\drivers\\etc\\hosts".to_string(),
            ],
            protected_registry_keys: vec![
                "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run".to_string(),
                "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run".to_string(),
                "HKLM\\System\\CurrentControlSet\\Services".to_string(),
                "HKLM\\Software\\Policies".to_string(),
            ],
        }
    }

    /// Weryfikuje intencję wykonania akcji przez zewnętrzny proces / agenta AI.
    /// Jeśli akcja narusza bezpieczeństwo systemu Windows, zwraca zdarzenie AegisSecurityEvent
    /// z natychmiastowym przeniesieniem do kwarantanny.
    pub fn audit_system_access(
        &mut self,
        process_id: u32,
        process_name: &str,
        target_resource: &str,
        action_type: AegisActionType,
    ) -> Result<(), AegisSecurityEvent> {
        let is_sensitive_registry = self
            .protected_registry_keys
            .iter()
            .any(|key| target_resource.to_lowercase().contains(&key.to_lowercase()));

        let is_sensitive_path = self
            .protected_paths
            .iter()
            .any(|path| target_resource.to_lowercase().starts_with(&path.to_lowercase()));

        let is_suspicious_rogue = process_name.to_lowercase().contains("untrusted_agent")
            || process_name.to_lowercase().contains("rogue")
            || process_name.to_lowercase().contains("malicious_bot");

        if is_sensitive_registry || is_sensitive_path || is_suspicious_rogue {
            let timestamp = SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .unwrap_or_default()
                .as_secs();

            let rationale = if is_sensitive_registry {
                format!(
                    "🛡️ [Aegis]: Wykryto nieautoryzowaną próbę modyfikacji rejestru Windows: {}",
                    target_resource
                )
            } else if is_sensitive_path {
                format!(
                    "🛡️ [Aegis]: Wykryto próbę zapisu do chronionego katalogu systemowego: {}",
                    target_resource
                )
            } else {
                format!(
                    "🛡️ [Aegis]: Wykryto podejrzany proces obcego agenta AI: {}",
                    process_name
                )
            };

            let event = AegisSecurityEvent {
                id: format!("AEGIS-EVT-{}", self.events_history.len() + 1),
                timestamp,
                process_id,
                process_name: process_name.to_string(),
                target_resource: target_resource.to_string(),
                action_type,
                severity: 5, // Krytyczny
                status: SentinelActionStatus::QuarantinedInJobObject,
                rationale,
            };

            self.events_history.push(event.clone());
            println!(
                "🛑 [Aegis Sentinel]: Hola hola! Proces {} (PID: {}) zablokowany przy próbie dostępu do '{}'.",
                process_name, process_id, target_resource
            );

            return Err(event);
        }

        Ok(())
    }

    pub fn get_security_posture(&self) -> AegisPostureSummary {
        let threats = self.events_history.len();
        let quarantined = self
            .events_history
            .iter()
            .filter(|e| e.status == SentinelActionStatus::QuarantinedInJobObject)
            .count();

        let integrity = if threats == 0 {
            1.0
        } else {
            (1.0 - (quarantined as f32 * 0.05)).max(0.60)
        };

        AegisPostureSummary {
            active_shields: true,
            intercepted_threats_count: threats,
            quarantined_processes_count: quarantined,
            system_integrity_score: integrity,
        }
    }

    pub fn handle_architect_decision(&mut self, event_id: &str, new_status: SentinelActionStatus) -> Result<(), String> {
        if let Some(event) = self.events_history.iter_mut().find(|e| e.id == event_id) {
            event.status = new_status;
            Ok(())
        } else {
            Err(format!("Zdarzenie Aegis o ID '{}' nie istnieje.", event_id))
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_aegis_blocks_registry_tampering() {
        let mut sentinel = AegisSentinel::new();
        
        let result = sentinel.audit_system_access(
            4412,
            "foreign_agent.exe",
            "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\\SpyScript",
            AegisActionType::RegistryTampering,
        );

        assert!(result.is_err());
        let event = result.unwrap_err();
        assert_eq!(event.process_id, 4412);
        assert_eq!(event.status, SentinelActionStatus::QuarantinedInJobObject);
        assert_eq!(sentinel.events_history.len(), 1);
    }

    #[test]
    fn test_aegis_allows_safe_operations() {
        let mut sentinel = AegisSentinel::new();
        
        let result = sentinel.audit_system_access(
            1200,
            "sparkle_ide.exe",
            "C:\\Projekty\\Blyskawica_V8\\workspace\\main.py",
            AegisActionType::UnauthorizedFileWrite,
        );

        assert!(result.is_ok());
        assert_eq!(sentinel.events_history.len(), 0);
    }
}
