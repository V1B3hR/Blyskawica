use std::fs::File;
use std::path::Path;
use candle_core::{Device, Tensor};
use candle_transformers::models::quantized_llama::ModelWeights;
use tokenizers::Tokenizer;

#[derive(Debug, Clone)]
pub struct GenerationParams {
    pub temperature: f64,
    pub top_p: f64,
    pub max_tokens: usize,
    pub repetition_penalty: f32,
}

impl Default for GenerationParams {
    fn default() -> Self {
        Self {
            temperature: 0.7,
            top_p: 0.9,
            max_tokens: 512,
            repetition_penalty: 1.1,
        }
    }
}

pub struct CognitiveLlmEngine {
    model: ModelWeights,
    tokenizer: Tokenizer,
    device: Device,
}

pub type LocalCognitiveLLM = CognitiveLlmEngine;

impl CognitiveLlmEngine {
    pub fn new(model_path: &Path, tokenizer_path: &Path) -> Result<Self, String> {
        let device = Device::Cpu;

        if !model_path.exists() {
            return Err(format!("Plik modelu GGUF nie istnieje: {:?}", model_path));
        }
        if !tokenizer_path.exists() {
            return Err(format!("Plik tokenizatora nie istnieje: {:?}", tokenizer_path));
        }

        // Weryfikacja spójności pliku GGUF z plikiem .sha256 jeśli istnieje (kryptograficzne SHA-256)
        let sha256_sidecar = model_path.with_extension("gguf.sha256");
        if sha256_sidecar.exists() {
            if let Ok(raw_hash) = std::fs::read_to_string(&sha256_sidecar) {
                let expected_hash = raw_hash.trim();
                if !expected_hash.is_empty() {
                    use std::io::Read;
                    use sha2::{Sha256, Digest};
                    
                    let mut hasher = Sha256::new();
                    if let Ok(mut f) = File::open(model_path) {
                        let mut buf = [0u8; 65536];
                        while let Ok(bytes) = f.read(&mut buf) {
                            if bytes == 0 { break; }
                            hasher.update(&buf[..bytes]);
                        }
                        let actual_hash = format!("{:x}", hasher.finalize());
                        if !expected_hash.eq_ignore_ascii_case(&actual_hash) {
                            return Err(format!(
                                "Weryfikacja integralności modelu GGUF (SHA-256) nie powiodła się. Oczekiwano: {}, Obliczono: {}",
                                expected_hash, actual_hash
                            ));
                        }
                    }
                }
            }
        }

        // Ładowanie tokenizatora
        let tokenizer = Tokenizer::from_file(tokenizer_path)
            .map_err(|e| format!("Błąd ładowania tokenizatora: {}", e))?;

        // Ładowanie pliku GGUF
        let mut file = File::open(model_path)
            .map_err(|e| format!("Błąd otwierania pliku modelu: {}", e))?;
        
        let reader = candle_core::quantized::gguf_file::Content::read(&mut file)
            .map_err(|e| format!("Błąd odczytu GGUF: {}", e))?;

        let model = ModelWeights::from_gguf(reader, &mut file, &device)
            .map_err(|e| format!("Błąd ładowania wag z GGUF do Candle: {}", e))?;

        Ok(Self {
            model,
            tokenizer,
            device,
        })
    }

    pub fn load(model_path: &Path, tokenizer_path: &Path) -> Result<Self, String> {
        Self::new(model_path, tokenizer_path)
    }

    /// Generuje odpowiedź na zadany prompt z uwzględnieniem neurochemicznych modyfikatorów i strumieniowaniem tokenów.
    pub fn generate<F>(&mut self, prompt: &str, params: &GenerationParams, callback: F) -> Result<String, String>
    where
        F: FnMut(&str),
    {
        self.generate_with_cancel(prompt, params, None, callback)
    }

    /// Generuje odpowiedź z możliwością natychmiastowego anulowania (sub-50ms cancellation) przez AtomicBool.
    pub fn generate_with_cancel<F>(
        &mut self,
        prompt: &str,
        params: &GenerationParams,
        cancel_flag: Option<&std::sync::atomic::AtomicBool>,
        mut callback: F,
    ) -> Result<String, String>
    where
        F: FnMut(&str),
    {
        let tokens = self.tokenizer.encode(prompt, true)
            .map_err(|e| format!("Błąd tokenizacji: {}", e))?;
        let mut tokens = tokens.get_ids().to_vec();

        let mut generated_text = String::new();
        let eos_token_id = self.tokenizer.token_to_id("<|im_end|>")
            .or_else(|| self.tokenizer.token_to_id("<eot_id>"))
            .or_else(|| self.tokenizer.token_to_id("</s>"))
            .unwrap_or(2); // Domyślnie id 2

        let mut index_pos = 0;
        for _i in 0..params.max_tokens {
            // Weryfikacja flagi anulowania generowania
            if let Some(flag) = cancel_flag {
                if flag.load(std::sync::atomic::Ordering::Relaxed) {
                    println!("🛑 [Cognitive LLM]: Generowanie tokenów zostało anulowane przez użytkownika.");
                    break;
                }
            }

            let context_size = if index_pos > 0 { 1 } else { tokens.len() };
            let context = &tokens[tokens.len() - context_size..];
            
            let input_tensor = Tensor::new(context, &self.device)
                .map_err(|e| format!("Błąd tworzenia tensora wejściowego: {}", e))?;
            
            let logits = self.model.forward(&input_tensor, index_pos)
                .map_err(|e| format!("Błąd inferencji w modelu: {}", e))?;
            
            let logits = logits.squeeze(0)
                .map_err(|e| format!("Błąd dopasowania wymiarowości: {}", e))?;
            let mut logits = logits.to_vec1::<f32>()
                .map_err(|e| format!("Błąd odczytu logits: {}", e))?;

            // Aplikacja kary za powtórzenia (repetition penalty)
            if params.repetition_penalty > 1.0 {
                let mut already_seen = std::collections::HashSet::new();
                for &token in tokens.iter().rev().take(64) {
                    if already_seen.insert(token) {
                        let token_idx = token as usize;
                        if token_idx < logits.len() {
                            if logits[token_idx] < 0.0 {
                                logits[token_idx] *= params.repetition_penalty;
                            } else {
                                logits[token_idx] /= params.repetition_penalty;
                            }
                        }
                    }
                }
            }

            // Próbkowanie z temperaturą i top-p
            let next_token = if params.temperature > 0.0 {
                // Skalowanie przez temperaturę
                for logit in logits.iter_mut() {
                    *logit /= params.temperature as f32;
                }

                // Softmax
                let max_logit = logits.iter().cloned().fold(f32::NEG_INFINITY, f32::max);
                let mut sum_exp = 0.0f32;
                for logit in logits.iter_mut() {
                    *logit = (*logit - max_logit).exp();
                    sum_exp += *logit;
                }
                for logit in logits.iter_mut() {
                    *logit /= sum_exp;
                }

                // Top-P Nucleus Filtering
                let mut indexed_probs: Vec<(usize, f64)> = logits.iter().enumerate().map(|(i, &p)| (i, p as f64)).collect();
                indexed_probs.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));

                let mut cum_prob = 0.0;
                let mut cutoff_index = indexed_probs.len();
                for (i, (_idx, prob)) in indexed_probs.iter().enumerate() {
                    cum_prob += prob;
                    if cum_prob >= params.top_p {
                        cutoff_index = i + 1;
                        break;
                    }
                }
                indexed_probs.truncate(cutoff_index);
                
                let norm_sum: f64 = indexed_probs.iter().map(|x| x.1).sum();
                let r: f64 = rand::random::<f64>() * norm_sum;
                
                let mut running_sum = 0.0;
                let mut selected = indexed_probs[0].0;
                for (idx, prob) in indexed_probs {
                    running_sum += prob;
                    if r <= running_sum {
                        selected = idx;
                        break;
                    }
                }
                selected as u32
            } else {
                // Argmax (Greedy Decoding)
                let mut max_idx = 0;
                let mut max_val = logits[0];
                for (idx, &val) in logits.iter().enumerate() {
                    if val > max_val {
                        max_val = val;
                        max_idx = idx;
                    }
                }
                max_idx as u32
            };

            index_pos += context.len();
            tokens.push(next_token);

            if next_token == eos_token_id {
                break;
            }

            // Dekodowanie wygenerowanego tokenu na tekst
            let chunk = self.tokenizer.decode(&[next_token], true)
                .map_err(|e| format!("Błąd dekodowania tokenu: {}", e))?;
            callback(&chunk);
            generated_text.push_str(&chunk);
        }

        Ok(generated_text)
    }
}
