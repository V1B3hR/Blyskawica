use candle_core::{Device, Tensor};
use candle_transformers::models::quantized_qwen2::ModelWeights;
use std::fs::File;
use std::path::Path;
use tokenizers::Tokenizer;

fn checksum_reader(mut reader: impl std::io::Read) -> Result<String, String> {
    use sha2::{Digest, Sha256};
    let mut hasher = Sha256::new();
    let mut buf = [0u8; 65536];
    loop {
        let bytes = reader
            .read(&mut buf)
            .map_err(|e| format!("Błąd odczytu modelu podczas kontroli SHA-256: {e}"))?;
        if bytes == 0 {
            break;
        }
        hasher.update(&buf[..bytes]);
    }
    Ok(format!("{:x}", hasher.finalize()))
}

fn verify_optional_model_checksum(model_path: &Path) -> Result<(), String> {
    use std::io::Read;
    let sidecar = model_path.with_extension("gguf.sha256");
    match std::fs::symlink_metadata(&sidecar) {
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => return Ok(()),
        Err(error) => return Err(format!("Nie można sprawdzić sumy modelu: {error}")),
        Ok(metadata) if !metadata.file_type().is_file() || metadata.file_type().is_symlink() => {
            return Err("Nieprawidłowy plik sumy kontrolnej modelu".into());
        }
        Ok(metadata) => {
            #[cfg(windows)]
            {
                use std::os::windows::fs::MetadataExt;
                if metadata.file_attributes() & 0x400 != 0 {
                    return Err("Suma modelu jest punktem przekierowania".into());
                }
            }
            #[cfg(not(windows))]
            let _ = metadata;
        }
    }
    let mut bytes = Vec::new();
    File::open(&sidecar)
        .map_err(|e| format!("Nie można otworzyć sumy modelu: {e}"))?
        .take(1025)
        .read_to_end(&mut bytes)
        .map_err(|e| format!("Nie można odczytać sumy modelu: {e}"))?;
    if bytes.len() > 1024 {
        return Err("Plik sumy kontrolnej modelu jest zbyt duży".into());
    }
    let expected = std::str::from_utf8(&bytes)
        .map_err(|_| "Suma modelu nie jest tekstem UTF-8")?
        .trim();
    if expected.len() != 64 || !expected.bytes().all(|b| b.is_ascii_hexdigit()) {
        return Err("Suma modelu musi zawierać dokładnie 64 cyfry szesnastkowe SHA-256".into());
    }
    let model = File::open(model_path)
        .map_err(|e| format!("Nie można otworzyć modelu do kontroli SHA-256: {e}"))?;
    let actual = checksum_reader(model)?;
    if !expected.eq_ignore_ascii_case(&actual) {
        return Err("Weryfikacja integralności modelu GGUF (SHA-256) nie powiodła się".into());
    }
    Ok(())
}

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
            return Err(format!(
                "Plik tokenizatora nie istnieje: {:?}",
                tokenizer_path
            ));
        }

        // Missing sidecar is accepted but does not establish integrity.
        // A present unreadable, malformed or mismatched sidecar fails closed.
        verify_optional_model_checksum(model_path)?;

        // Weryfikacja nagłówka GGUF (magic bytes: "GGUF" = [0x47, 0x47, 0x55, 0x46])
        {
            use std::io::Read;
            let mut magic = [0u8; 4];
            let mut test_f = File::open(model_path)
                .map_err(|e| format!("Błąd otwierania pliku modelu: {}", e))?;
            test_f
                .read_exact(&mut magic)
                .map_err(|e| format!("Błąd odczytu nagłówka pliku GGUF: {}", e))?;
            if &magic != b"GGUF" {
                return Err(format!(
                    "Nieprawidłowy format pliku modelu (oczekiwano nagłówka 'GGUF', odczytano: {:?}). Plik może być uszkodzony.",
                    magic
                ));
            }
        }

        // Ładowanie tokenizatora
        let tokenizer = Tokenizer::from_file(tokenizer_path)
            .map_err(|e| format!("Błąd ładowania tokenizatora: {}", e))?;

        // Ładowanie pliku GGUF
        let mut file =
            File::open(model_path).map_err(|e| format!("Błąd otwierania pliku modelu: {}", e))?;

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

    /// Szybki benchmark operacji tensorowych CPU do oceny przepustowości obliczeniowej
    pub fn benchmark_cpu_tensor_ops(iterations: usize) -> Result<f64, String> {
        let device = Device::Cpu;
        let start = std::time::Instant::now();
        for _ in 0..iterations {
            let a = Tensor::new(&[1.0f32, 2.0, 3.0, 4.0], &device).map_err(|e| e.to_string())?;
            let _ = (a.clone() * 2.0).map_err(|e| e.to_string())?;
        }
        let elapsed = start.elapsed().as_secs_f64();
        let ops_per_sec = (iterations as f64) / elapsed.max(1e-6);
        Ok(ops_per_sec)
    }

    /// Generuje odpowiedź na zadany prompt z uwzględnieniem neurochemicznych modyfikatorów i strumieniowaniem tokenów.
    pub fn generate<F>(
        &mut self,
        prompt: &str,
        params: &GenerationParams,
        callback: F,
    ) -> Result<String, String>
    where
        F: FnMut(&str),
    {
        self.generate_with_cancel(prompt, params, None, callback)
    }

    /// Sprawdza żądanie anulowania pomiędzy operacjami modelu; czas zależy od
    /// tokenizacji i aktualnie wykonywanego wywołania modelu.
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
        if cancel_flag.is_some_and(|flag| flag.load(std::sync::atomic::Ordering::Relaxed)) {
            return Ok(String::new());
        }
        let tokens = self
            .tokenizer
            .encode(prompt, true)
            .map_err(|e| format!("Błąd tokenizacji: {}", e))?;
        let mut tokens = tokens.get_ids().to_vec();

        let mut generated_text = String::new();
        let eos_token_id = self
            .tokenizer
            .token_to_id("<|im_end|>")
            .or_else(|| self.tokenizer.token_to_id("<eot_id>"))
            .or_else(|| self.tokenizer.token_to_id("</s>"))
            .unwrap_or(2); // Domyślnie id 2

        let mut index_pos = 0;
        for _i in 0..params.max_tokens {
            // Weryfikacja flagi anulowania generowania
            if let Some(flag) = cancel_flag
                && flag.load(std::sync::atomic::Ordering::Relaxed)
            {
                println!(
                    "🛑 [Cognitive LLM]: Generowanie tokenów zostało anulowane przez użytkownika."
                );
                break;
            }

            let context_size = if index_pos > 0 { 1 } else { tokens.len() };
            let context = &tokens[tokens.len() - context_size..];

            let input_tensor = Tensor::new(context, &self.device)
                .map_err(|e| format!("Błąd tensora wejściowego: {}", e))?
                .unsqueeze(0)
                .map_err(|e| format!("Błąd unsqueeze: {}", e))?;

            let logits = self
                .model
                .forward(&input_tensor, index_pos)
                .map_err(|e| format!("Błąd inferencji w modelu: {}", e))?;

            if cancel_flag.is_some_and(|flag| flag.load(std::sync::atomic::Ordering::Relaxed)) {
                break;
            }

            let logits = logits
                .squeeze(0)
                .map_err(|e| format!("Błąd dopasowania wymiarowości: {}", e))?;
            let logits = if logits.rank() == 2 {
                let seq_len = logits.dim(0).map_err(|e| format!("{}", e))?;
                logits.get(seq_len - 1).map_err(|e| format!("{}", e))?
            } else {
                logits
            };
            let mut logits = logits
                .to_vec1::<f32>()
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
            let next_token = if params.temperature > 0.05 {
                // Skalowanie przez temperaturę
                let temp = params.temperature as f32;

                // Optymalizacja CPU: Selekcja Top-K (K=50) zamiast pełnego sortowania 152 064 elementów
                const TOP_K: usize = 50;
                let mut top_k: Vec<(usize, f32)> = Vec::with_capacity(TOP_K + 1);

                for (idx, &val) in logits.iter().enumerate() {
                    let scaled_val = val / temp;
                    if top_k.len() < TOP_K {
                        top_k.push((idx, scaled_val));
                        if top_k.len() == TOP_K {
                            top_k.sort_unstable_by(|a, b| {
                                b.1.partial_cmp(&a.1).unwrap_or(std::cmp::Ordering::Equal)
                            });
                        }
                    } else if scaled_val > top_k[TOP_K - 1].1 {
                        top_k[TOP_K - 1] = (idx, scaled_val);
                        let mut j = TOP_K - 1;
                        while j > 0 && top_k[j].1 > top_k[j - 1].1 {
                            top_k.swap(j, j - 1);
                            j -= 1;
                        }
                    }
                }

                // Softmax wyłącznie na wybranych 50 najwyższych logitach
                let max_logit = top_k[0].1;
                let mut sum_exp = 0.0f32;
                for item in top_k.iter_mut() {
                    item.1 = (item.1 - max_logit).exp();
                    sum_exp += item.1;
                }
                for item in top_k.iter_mut() {
                    item.1 /= sum_exp;
                }

                // Top-P Nucleus Filtering na wybranych kandydatach
                let mut cum_prob = 0.0f32;
                let mut cutoff_index = top_k.len();
                let top_p_f32 = params.top_p as f32;
                for (i, item) in top_k.iter().enumerate() {
                    cum_prob += item.1;
                    if cum_prob >= top_p_f32 {
                        cutoff_index = i + 1;
                        break;
                    }
                }
                top_k.truncate(cutoff_index);

                let norm_sum: f32 = top_k.iter().map(|x| x.1).sum();
                let r: f32 = rand::random::<f32>() * norm_sum;

                let mut running_sum = 0.0f32;
                let mut selected = top_k[0].0;
                for item in top_k {
                    running_sum += item.1;
                    if r <= running_sum {
                        selected = item.0;
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
            let chunk = self
                .tokenizer
                .decode(&[next_token], true)
                .map_err(|e| format!("Błąd dekodowania tokenu: {}", e))?;
            callback(&chunk);
            generated_text.push_str(&chunk);
        }

        Ok(generated_text)
    }
}

#[cfg(test)]
mod cancellation_real_model_tests {
    use super::*;
    use std::sync::{
        Arc,
        atomic::{AtomicBool, Ordering},
        mpsc,
    };
    use std::time::{Duration, Instant};

    #[test]
    fn optional_checksum_fails_closed_when_present_but_invalid() {
        let root = std::env::temp_dir().join(format!(
            "sparkle-model-checksum-{:016x}",
            rand::random::<u64>()
        ));
        std::fs::create_dir_all(&root).unwrap();
        let model = root.join("synthetic.gguf");
        std::fs::write(&model, b"synthetic model").unwrap();
        let sidecar = model.with_extension("gguf.sha256");
        assert!(verify_optional_model_checksum(&model).is_ok());
        std::fs::write(&sidecar, b"").unwrap();
        assert!(verify_optional_model_checksum(&model).is_err());
        std::fs::write(&sidecar, "a".repeat(1025)).unwrap();
        assert!(verify_optional_model_checksum(&model).is_err());
        std::fs::write(&sidecar, "z".repeat(64)).unwrap();
        assert!(verify_optional_model_checksum(&model).is_err());
        std::fs::write(&sidecar, "0".repeat(64)).unwrap();
        assert!(verify_optional_model_checksum(&model).is_err());
        let expected = checksum_reader(&b"synthetic model"[..]).unwrap();
        std::fs::write(&sidecar, format!("{}\n", expected.to_uppercase())).unwrap();
        assert!(verify_optional_model_checksum(&model).is_ok());
        std::fs::remove_file(&model).unwrap();
        assert!(verify_optional_model_checksum(&model).is_err());
        std::fs::remove_dir_all(root).unwrap();
    }

    #[test]
    fn checksum_reader_propagates_read_errors() {
        struct FaultyReader(bool);
        impl std::io::Read for FaultyReader {
            fn read(&mut self, buf: &mut [u8]) -> std::io::Result<usize> {
                if !self.0 {
                    self.0 = true;
                    buf[0] = b'x';
                    Ok(1)
                } else {
                    Err(std::io::Error::other("synthetic read failure"))
                }
            }
        }
        assert!(checksum_reader(FaultyReader(false)).is_err());
    }

    // Explicitly run only with a locally selected model; ordinary tests never
    // load multi-gigabyte user assets or assert a universal latency.
    #[test]
    #[ignore = "wymaga lokalnego modelu GGUF i znacznej ilości pamięci"]
    fn real_model_stops_after_external_cancellation() {
        enum Event {
            Loaded,
            FirstToken,
            Finished(Result<usize, String>),
        }
        let model = std::env::var_os("SPARKLE_TEST_GGUF").expect("SPARKLE_TEST_GGUF");
        let tokenizer = std::env::var_os("SPARKLE_TEST_TOKENIZER").expect("SPARKLE_TEST_TOKENIZER");
        let cancellation = Arc::new(AtomicBool::new(false));
        let worker_cancellation = cancellation.clone();
        let (tx, rx) = mpsc::channel();
        let worker = std::thread::spawn(move || {
            let mut engine = match CognitiveLlmEngine::new(Path::new(&model), Path::new(&tokenizer))
            {
                Ok(engine) => engine,
                Err(error) => {
                    let _ = tx.send(Event::Finished(Err(error)));
                    return;
                }
            };
            let _ = tx.send(Event::Loaded);
            let mut chunks = 0;
            let params = GenerationParams {
                max_tokens: 128,
                temperature: 0.0,
                top_p: 1.0,
                repetition_penalty: 1.0,
            };
            let result = engine.generate_with_cancel(
                "<|im_start|>user\nPolicz od jeden do stu.\n<|im_end|>\n<|im_start|>assistant\n",
                &params,
                Some(&worker_cancellation),
                |_| {
                    chunks += 1;
                    if chunks == 1 {
                        let _ = tx.send(Event::FirstToken);
                    }
                },
            );
            let _ = tx.send(Event::Finished(result.map(|_| chunks)));
        });
        match rx
            .recv_timeout(Duration::from_secs(180))
            .expect("model nie został załadowany w czasie testu")
        {
            Event::Loaded => println!("Model i tokenizator załadowane na CPU."),
            Event::Finished(Err(error)) => panic!("Błąd ładowania modelu: {error}"),
            _ => panic!("Nieoczekiwane zdarzenie podczas ładowania"),
        }
        match rx
            .recv_timeout(Duration::from_secs(180))
            .expect("nie otrzymano pierwszego tokenu")
        {
            Event::FirstToken => {}
            Event::Finished(result) => {
                panic!("Generowanie zakończyło się przed pierwszym tokenem: {result:?}")
            }
            _ => panic!("Nieoczekiwane zdarzenie generowania"),
        }
        assert!(
            !worker.is_finished(),
            "generowanie zakończyło się przed sygnałem anulowania"
        );
        let start = Instant::now();
        cancellation.store(true, Ordering::SeqCst);
        match rx
            .recv_timeout(Duration::from_secs(180))
            .expect("model nie zakończył anulowania")
        {
            Event::Finished(Ok(chunks)) => {
                println!(
                    "Od sygnału anulowania do końca funkcji: {:?}; fragmentów: {chunks}",
                    start.elapsed()
                );
                assert!((1..128).contains(&chunks));
            }
            Event::Finished(Err(error)) => panic!("Błąd generowania: {error}"),
            _ => panic!("Nieoczekiwane zdarzenie po anulowaniu"),
        }
        worker.join().unwrap();
    }
}
