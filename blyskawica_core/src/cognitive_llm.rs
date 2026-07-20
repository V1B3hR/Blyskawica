use std::fs::File;
use std::path::Path;
use candle_core::{Device, Tensor};
use candle_transformers::models::quantized_llama::ModelWeights;
use tokenizers::Tokenizer;

pub struct LocalCognitiveLLM {
    model: ModelWeights,
    tokenizer: Tokenizer,
    device: Device,
}

pub struct GenerationParams {
    pub temperature: f64,
    pub repetition_penalty: f32,
    pub top_p: f64,
    pub max_tokens: usize,
}

impl LocalCognitiveLLM {
    /// Ładuje model z pliku GGUF oraz tokenizator z pliku tokenizer.json.
    pub fn load<P: AsRef<Path>>(model_path: P, tokenizer_path: P) -> Result<Self, String> {
        let device = Device::Cpu; // Domyślnie CPU dla maksymalnej kompatybilności offline
        
        let model_path = model_path.as_ref();
        let tokenizer_path = tokenizer_path.as_ref();

        if !model_path.exists() {
            return Err(format!("Plik modelu nie istnieje: {:?}", model_path));
        }
        if !tokenizer_path.exists() {
            return Err(format!("Plik tokenizatora nie istnieje: {:?}", tokenizer_path));
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

    /// Generuje odpowiedź na zadany prompt z uwzględnieniem neurochemicznych modyfikatorów i strumieniowaniem tokenów.
    pub fn generate<F>(&mut self, prompt: &str, params: &GenerationParams, mut callback: F) -> Result<String, String>
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

            // Próbkowanie z temperaturą
            let next_token = if params.temperature > 0.0 {
                // Skalowanie logitów temperaturą
                for logit in logits.iter_mut() {
                    *logit /= params.temperature as f32;
                }
                
                // Softmax + próbkowanie
                let mut exp_logits: Vec<f64> = logits.iter().map(|&x| (x as f64).exp()).collect();
                let sum: f64 = exp_logits.iter().sum();
                for prob in exp_logits.iter_mut() {
                    *prob /= sum;
                }
                
                // Próbkowanie z top_p
                let mut indexed_probs: Vec<(usize, f64)> = exp_logits.into_iter().enumerate().collect();
                indexed_probs.sort_by(|a, b| b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal));
                
                let mut cumulative_prob = 0.0;
                let mut cutoff_index = indexed_probs.len();
                for (idx, &(_, prob)) in indexed_probs.iter().enumerate() {
                    cumulative_prob += prob;
                    if cumulative_prob > params.top_p {
                        cutoff_index = idx + 1;
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
