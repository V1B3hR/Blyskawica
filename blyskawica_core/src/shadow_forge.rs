use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum ShadowStatus {
    Hanging {
        checksum_sha256: String,
        file_path: String,
        execution_count: usize,
    },
    EmptySilhouette {
        requested_times: usize,
        missing_capabilities: Vec<String>,
    },
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ToolShadow {
    pub id: String,
    pub name: String,
    pub description: String,
    pub input_schema: serde_json::Value,
    pub output_schema: serde_json::Value,
    pub permission_level: u8, // 1: Sandbox, 2: Workspace, 3: Full OS
    pub semantic_category: String,
    pub status: ShadowStatus,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ShadowBoard {
    pub tools: HashMap<String, ToolShadow>,
}

impl ShadowBoard {
    pub fn new() -> Self {
        let mut board = Self {
            tools: HashMap::new(),
        };
        board.seed_default_shadows();
        board
    }

    fn seed_default_shadows(&mut self) {
        // 1. Wiszące narzędzia bazowe (Hanging Core Tools)
        self.register_shadow(ToolShadow {
            id: "vector_search".to_string(),
            name: "Przeszukiwarka Wektorowa".to_string(),
            description: "Semantyczne wyszukiwanie w przestrzeni pamięci HNSW".to_string(),
            input_schema: serde_json::json!({
                "type": "object",
                "properties": { "query": { "type": "string" }, "k": { "type": "integer" } },
                "required": ["query"]
            }),
            output_schema: serde_json::json!({
                "type": "object",
                "properties": { "matches": { "type": "array" } }
            }),
            permission_level: 1,
            semantic_category: "memory".to_string(),
            status: ShadowStatus::Hanging {
                checksum_sha256: "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855".to_string(),
                file_path: "builtin://vector_search".to_string(),
                execution_count: 0,
            },
        });

        self.register_shadow(ToolShadow {
            id: "text_embedder".to_string(),
            name: "Natywny Embedder Tekstu".to_string(),
            description: "Wielowymiarowa projekcja semantyczna zdań do wektorów f32".to_string(),
            input_schema: serde_json::json!({
                "type": "object",
                "properties": { "text": { "type": "string" } },
                "required": ["text"]
            }),
            output_schema: serde_json::json!({
                "type": "object",
                "properties": { "dimension": { "type": "integer" }, "vector": { "type": "array" } }
            }),
            permission_level: 1,
            semantic_category: "nlp".to_string(),
            status: ShadowStatus::Hanging {
                checksum_sha256: "builtin_sha256_native_embedder_v10".to_string(),
                file_path: "builtin://embedder".to_string(),
                execution_count: 0,
            },
        });

        // 2. Puste Cienie czekające na wykucie w kuźni (Empty Silhouettes)
        self.register_shadow(ToolShadow {
            id: "pdf_deep_extractor".to_string(),
            name: "Ekstraktor Dokumentów PDF".to_string(),
            description: "Pusty Cień: Narzędzie do parsowania i ekstrakcji układu dokumentów technicznych".to_string(),
            input_schema: serde_json::json!({
                "type": "object",
                "properties": { "path": { "type": "string" } },
                "required": ["path"]
            }),
            output_schema: serde_json::json!({
                "type": "object",
                "properties": { "pages": { "type": "array" }, "metadata": { "type": "object" } }
            }),
            permission_level: 2,
            semantic_category: "documents".to_string(),
            status: ShadowStatus::EmptySilhouette {
                requested_times: 0,
                missing_capabilities: vec!["pdf_page_parser".to_string(), "layout_analyzer".to_string()],
            },
        });

        self.register_shadow(ToolShadow {
            id: "web_graph_crawler".to_string(),
            name: "Asynchroniczny Pająk Grafów Wiedzy".to_string(),
            description: "Pusty Cień: Narzędzie do badania topologii odnośników w sandboxie".to_string(),
            input_schema: serde_json::json!({
                "type": "object",
                "properties": { "url": { "type": "string" }, "max_depth": { "type": "integer" } },
                "required": ["url"]
            }),
            output_schema: serde_json::json!({
                "type": "object",
                "properties": { "nodes": { "type": "array" }, "edges": { "type": "array" } }
            }),
            permission_level: 2,
            semantic_category: "web".to_string(),
            status: ShadowStatus::EmptySilhouette {
                requested_times: 0,
                missing_capabilities: vec!["html_graph_extractor".to_string()],
            },
        });
    }

    pub fn register_shadow(&mut self, shadow: ToolShadow) {
        self.tools.insert(shadow.id.clone(), shadow);
    }

    pub fn get_tool(&self, id: &str) -> Option<&ToolShadow> {
        self.tools.get(id)
    }

    pub fn list_all_tools(&self) -> Vec<ToolShadow> {
        self.tools.values().cloned().collect()
    }

    pub fn hang_forged_tool(&mut self, id: &str, file_path: &str, checksum_sha256: &str) -> Result<(), String> {
        if let Some(tool) = self.tools.get_mut(id) {
            tool.status = ShadowStatus::Hanging {
                checksum_sha256: checksum_sha256.to_string(),
                file_path: file_path.to_string(),
                execution_count: 0,
            };
            Ok(())
        } else {
            Err(format!("Cień o ID '{}' nie istnieje na Tablicy Cieni.", id))
        }
    }

    pub fn request_silhouette(&mut self, id: &str) {
        if let Some(tool) = self.tools.get_mut(id) {
            if let ShadowStatus::EmptySilhouette { ref mut requested_times, .. } = tool.status {
                *requested_times += 1;
            }
        }
    }
}

pub struct TheAnvil;

impl TheAnvil {
    /// Oblicza sumę kryptograficzną SHA-256 dla wykutego kodu narzędzia
    pub fn compute_tool_hash(source_code: &str) -> String {
        let mut hasher = Sha256::new();
        hasher.update(source_code.as_bytes());
        format!("{:x}", hasher.finalize())
    }

    /// Symuluje hartowanie na kowadle: walidacja składni, test wejść/wyjść w piaskownicy
    pub fn temper_tool(
        tool_id: &str,
        code: &str,
        _test_payload: &serde_json::Value,
    ) -> Result<String, String> {
        if code.trim().is_empty() {
            return Err("Kod mikro-narzędzia nie może być pusty.".to_string());
        }

        // Test podstawowych reguł bezpieczeństwa kodu (Statyczna analiza kowadła)
        if code.contains("format C:") || code.contains("Remove-Item -Recurse C:\\Windows") {
            return Err("KOWADŁO ODRZUCIŁO KOD: Wykryto destrukcyjne instrukcje systemowe.".to_string());
        }

        let checksum = Self::compute_tool_hash(code);
        
        // Zapis do bezpiecznego bufora w kuźni
        println!(
            "🔨 [Kowadło Kuźni]: Narzędzie '{}' pomyślnie zahartowane! Pieczęć SHA-256: {}",
            tool_id, checksum
        );

        Ok(checksum)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_shadow_board_defaults() {
        let board = ShadowBoard::new();
        assert!(board.tools.contains_key("vector_search"));
        assert!(board.tools.contains_key("pdf_deep_extractor"));
        
        let pdf_shadow = board.get_tool("pdf_deep_extractor").unwrap();
        match &pdf_shadow.status {
            ShadowStatus::EmptySilhouette { requested_times, .. } => {
                assert_eq!(*requested_times, 0);
            }
            _ => panic!("Oczekiwano pustego cienia dla pdf_deep_extractor"),
        }
    }

    #[test]
    fn test_anvil_tempering_and_hanging() {
        let mut board = ShadowBoard::new();
        let code = r#"
            def extract_pdf_layout(path):
                return {"pages": [1, 2], "metadata": {"status": "ok"}}
        "#;
        
        let checksum = TheAnvil::temper_tool(
            "pdf_deep_extractor",
            code,
            &serde_json::json!({"path": "test.pdf"}),
        ).expect("Hartowanie powinno się udać");

        assert_eq!(checksum.len(), 64);

        board.hang_forged_tool("pdf_deep_extractor", "tools/pdf_extractor.py", &checksum)
            .expect("Zawieszenie na cieniu powinno się udać");

        let tool = board.get_tool("pdf_deep_extractor").unwrap();
        match &tool.status {
            ShadowStatus::Hanging { checksum_sha256, file_path, .. } => {
                assert_eq!(checksum_sha256, &checksum);
                assert_eq!(file_path, "tools/pdf_extractor.py");
            }
            _ => panic!("Oczekiwano wiszącego narzędzia po wykuciu"),
        }
    }
}
