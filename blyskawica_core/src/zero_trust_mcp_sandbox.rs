use crate::neurochemistry::NeurochemicalState;

pub struct ZeroTrustMcpSandbox {
    _base_reality_anchor: f32,
}

impl Default for ZeroTrustMcpSandbox {
    fn default() -> Self {
        Self::new()
    }
}

impl ZeroTrustMcpSandbox {
    pub fn new() -> Self {
        Self {
            _base_reality_anchor: 1.0,
        }
    }

    /// Oblicza współczynnik bezpieczeństwa na podstawie neurochemii i aktualnego Reality Anchor
    pub fn evaluate_security_index(&self, reality_anchor: f32, neuro_state: &NeurochemicalState) -> f32 {
        let cortisol = neuro_state.cortisol;
        let anxiety = (0.5 - neuro_state.gaba).max(0.0);
        let security_index = reality_anchor - anxiety - cortisol;
        security_index.clamp(0.0, 1.0)
    }

    /// Weryfikuje, czy dane narzędzie/akcja systemu może być uruchomione.
    /// Zwraca true jeśli dozwolone, false jeśli zablokowane (VETO).
    pub fn audit_tool_execution(&self, tool_name: &str, reality_anchor: f32, neuro_state: &NeurochemicalState) -> bool {
        let sec_index = self.evaluate_security_index(reality_anchor, neuro_state);
        
        // Narzędzia niebezpieczne (Execute / Write)
        let is_dangerous = tool_name.contains("execute") 
            || tool_name.contains("write") 
            || tool_name.contains("delete") 
            || tool_name.contains("wallpaper") 
            || tool_name.contains("system");

        if is_dangerous && sec_index < 0.40 {
            println!(
                "🛡️ [ZERO-TRUST MCP]: ZABLOKOWANO operację zapisu/wykonania: '{}'. Wskaźnik bezpieczeństwa: {:.4} (wymagane: >= 0.40)",
                tool_name, sec_index
            );
            // Natychmiastowe obniżenie uprawnień wątku do poziomu Read-Only
            if let Err(e) = crate::native_security::drop_thread_privileges() {
                println!("⚠️ [ZERO-TRUST MCP ERROR]: Nie udało się zrzucić uprawnień wątku: {}", e);
            } else {
                println!("🔒 [ZERO-TRUST MCP]: Pomyślnie zrzucono uprawnienia wątku roboczego.");
            }
            return false;
        }
        
        true
    }
}
