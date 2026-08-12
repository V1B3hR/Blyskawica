use std::fs::File;
use std::io::Write;
use std::path::PathBuf;
use std::sync::Arc;
use std::time::Duration;
use tokio::sync::{mpsc, RwLock};
use memmap2::Mmap;
use serde::{Serialize, Deserialize};

use crate::neurochemistry::NeurochemicalState;
use crate::vector_index::SparkleVectorIndex;
use crate::anomaly_loop::AnomalyDetector;

#[derive(Debug, Serialize, Deserialize, Clone)]
pub enum EngineEvent {
    Log(String),
    Neurochemistry(NeurochemicalState),
    AnomalyQueued { id: usize, surprise: f32, text: String },
    Token(String),
    ResponseFinished(String),
}

macro_rules! log_print {
    ($engine:expr, $($arg:tt)*) => {{
        let msg = format!($($arg)*);
        println!("{}", msg);
        if let Some(tx) = &$engine.event_tx {
            let tx = tx.clone();
            let msg_clone = msg.clone();
            tokio::spawn(async move {
                let _ = tx.send(EngineEvent::Log(msg_clone)).await;
            });
        }
    }};
}

#[derive(Debug)]
pub struct ExpertModule {
    pub id: usize,
    pub mmap: Mmap,
    pub weights_path: PathBuf,
    pub engine: Option<crate::local_inference::LocalInferenceEngine>,
}

impl ExpertModule {
    pub fn new(id: usize, mmap: Mmap, weights_path: PathBuf) -> Self {
        let engine = crate::local_inference::LocalInferenceEngine::load_from_slice(mmap.as_ref(), &candle_core::Device::Cpu).ok();
        Self {
            id,
            mmap,
            weights_path,
            engine,
        }
    }
}

#[derive(Debug, Clone)]
pub struct GatingNetwork {
    pub num_experts: usize,
}

impl GatingNetwork {
    pub fn new() -> Self {
        Self { num_experts: 1 }
    }

    pub fn select_expert(&self, neuro_state: &NeurochemicalState, query_text: &str) -> usize {
        if self.num_experts <= 1 {
            return 0;
        }
        let query_lower = query_text.to_lowercase();
        if query_lower.contains("analiz") || query_lower.contains("math") || neuro_state.serotonin > 0.85 {
            if self.num_experts > 2 {
                return 2;
            }
        }
        if neuro_state.dopamine > 0.75 || query_lower.contains("nowe") || query_lower.contains("ciekaw") {
            return 1;
        }
        0
    }
}

#[derive(Debug)]
pub enum BlysState {
    Hibernated { weights_path: PathBuf },
    Active {
        experts: Vec<ExpertModule>,
        gating: GatingNetwork,
        neuro_state: Arc<RwLock<NeurochemicalState>>,
        ewc_saturation: f32,
    },
}

#[derive(Debug, Clone)]
pub enum StateCommand {
    Prompt(String),
    QueryWithVector {
        id: usize,
        vector: Vec<f32>,
        text: String,
    },
    DeepSleep,
    CoolDown,
    Status,
    Neurogenesis,
}

pub struct BlyskawicaEngine {
    state: BlysState,
    weights_path: PathBuf,
    cooldown_duration: Duration,
    tx: Option<mpsc::Sender<StateCommand>>,
    rx: Option<mpsc::Receiver<StateCommand>>,
    index: Arc<SparkleVectorIndex>,
    pub anomaly_detector: AnomalyDetector,
    pub shield: crate::cognitive_shield::CognitiveShield,
    pub event_tx: Option<mpsc::Sender<EngineEvent>>,
    db_path: Option<(PathBuf, String)>,
    pub llm: Option<crate::cognitive_llm::LocalCognitiveLLM>,
}

impl BlyskawicaEngine {
    pub fn new(
        weights_path: PathBuf,
        cooldown_duration: Duration,
        index: Arc<SparkleVectorIndex>,
        surprise_threshold: f32,
        isolation_ratio: f32,
        adversarial_ids: Vec<usize>,
        semantic_threshold: f32,
    ) -> Self {
        let (tx, rx) = mpsc::channel(32);
        Self {
            state: BlysState::Hibernated { weights_path: weights_path.clone() },
            weights_path,
            cooldown_duration,
            tx: Some(tx),
            rx: Some(rx),
            index,
            anomaly_detector: AnomalyDetector::new(surprise_threshold, isolation_ratio),
            shield: crate::cognitive_shield::CognitiveShield::new(adversarial_ids, semantic_threshold),
            event_tx: None,
            db_path: None,
            llm: None,
        }
    }

    pub fn with_db(mut self, path: PathBuf, basename: String) -> Self {
        self.db_path = Some((path, basename));
        self
    }

    pub fn set_event_sender(&mut self, tx: mpsc::Sender<EngineEvent>) {
        self.event_tx = Some(tx);
    }

    pub fn emit_event(&self, event: EngineEvent) {
        if let Some(tx) = &self.event_tx {
            let tx = tx.clone();
            tokio::spawn(async move {
                let _ = tx.send(event).await;
            });
        }
    }

    pub fn get_sender(&self) -> mpsc::Sender<StateCommand> {
        self.tx.clone().expect("Sender must be available")
    }

    pub async fn run(&mut self) {
        let mut rx = self.rx.take().expect("Engine can only be run once");
        let _ = self.tx.take(); // Drop sender held by engine to avoid deadlock
        let cooldown_duration = self.cooldown_duration;

        log_print!(self, "⚡ [BŁYSKAWICA ENGINE]: Inicjalizacja pętli zdarzeń.");

        let mut throttle = crate::tempo_throttle::TempoThrottle::new();
        let sandbox = crate::zero_trust_mcp_sandbox::ZeroTrustMcpSandbox::new();

        loop {
            let timeout_res = tokio::time::timeout(cooldown_duration, rx.recv()).await;
            match timeout_res {
                Ok(Some(command)) => {
                    match command {
                        StateCommand::Prompt(text) => {
                            log_print!(self, "📥 [ENGINE INPUT]: Otrzymano prompt: \"{}\"", text);
                            
                            // 1. TEMPO THROTTLE check
                            let cortisol_level = if let BlysState::Active { neuro_state, .. } = &self.state {
                                neuro_state.read().await.cortisol
                            } else {
                                0.14
                            };
                            let stress_boost = throttle.audit_request_speed(cortisol_level).await;
                            if stress_boost > 0.0 {
                                if let BlysState::Active { neuro_state, .. } = &self.state {
                                    let mut ns = neuro_state.write().await;
                                    ns.cortisol = (ns.cortisol + stress_boost).min(1.0);
                                    log_print!(self, "🛡️ [TEMPO THROTTLE]: Wzrost Kortyzolu z powodu prędkości maszynowej: {:.2}", ns.cortisol);
                                    self.emit_event(EngineEvent::Neurochemistry(ns.clone()));
                                }
                            }

                            // 2. ZERO-TRUST MCP SANDBOX check
                            let security_ok = if let BlysState::Active { neuro_state, .. } = &self.state {
                                let ns = neuro_state.read().await;
                                let reality_anchor = (ns.serotonin * 1.2 - ns.dopamine * 0.2).min(1.0).max(0.0);
                                sandbox.audit_tool_execution(&text.to_lowercase(), reality_anchor, &ns)
                            } else {
                                true
                            };
                            if !security_ok {
                                log_print!(self, "🛡️ [ZERO-TRUST MCP]: Odmowa wykonania komendy (kognitywne VETO) ze względu na stan stresu.");
                                continue;
                            }

                            if self.shield.check_heuristics(&text) {
                                log_print!(self, "🛡️ [WOLF TEETH]: Wykryto zagrożenie (Warstwa 1 - Heurystyka)!");
                                self.wake_up().await;
                                if let BlysState::Active { neuro_state, .. } = &self.state {
                                    let mut ns = neuro_state.write().await;
                                    ns.apply_profile("wolf_teeth");
                                    log_print!(self, "🧠 [ENGINE STATE]: Kwarantanna - stan neurochemiczny: {}", ns.get_status_report());
                                    self.emit_event(EngineEvent::Neurochemistry(ns.clone()));
                                }
                                log_print!(self, "🔒 [ENGINE QUARANTINE]: Błyskawica AI: RealityAnchor protected. Cognitive quarantine activated.");
                                
                                // Natywne obniżenie uprawnień wątku i kwarantanna sieciowa
                                if let Err(e) = crate::native_security::drop_thread_privileges() {
                                    log_print!(self, "⚠️ [WOLF TEETH ERROR]: Nie udało się zrzucić uprawnień wątku: {}", e);
                                } else {
                                    log_print!(self, "🔒 [WOLF TEETH]: Uprawnienia wątku roboczego zostały zrzucone do poziomu Read-Only.");
                                }
                                if let Ok(closed_count) = crate::native_security::terminate_external_tcp_connections() {
                                    if closed_count > 0 {
                                        log_print!(self, "🔒 [NETWORK QUARANTINE]: Kwarantanna sieciowa aktywna. Zamknięto {} aktywnych połączeń TCP/IP.", closed_count);
                                    }
                                }
                                continue;
                            }
                            
                            // Przywrócenie normalnych uprawnień przy bezpiecznym przejściu
                            let _ = crate::native_security::restore_thread_privileges();
                            self.wake_up().await;
                            if let BlysState::Active { gating, neuro_state, .. } = &self.state {
                                let mut ns = neuro_state.write().await;
                                ns.apply_profile("query");
                                log_print!(self, "🧠 [ENGINE STATE]: Wirtualna neurochemia (po zapytaniu): {}", ns.get_status_report());
                                ns.apply_autonomous_fluctuation();
                                log_print!(self, "🧠 [ENGINE AUTONOMY]: Autonomiczna adaptacja (+/- 5%): {}", ns.get_status_report());
                                self.emit_event(EngineEvent::Neurochemistry(ns.clone()));
                                
                                let selected = gating.select_expert(&ns, &text);
                                log_print!(self, "🧠 [ENGINE GATING]: Zapytanie skierowane do Eksperta ID: {} na podstawie stanu: Serotonina={:.2}, Dopamina={:.2}", selected, ns.serotonin, ns.dopamine);
                            }

                            // Wczytywanie lokalnego modelu LLM jeśli nie jest załadowany
                            if self.llm.is_none() {
                                let workspace_root = self.weights_path.parent().unwrap_or(&self.weights_path);
                                let model_dir = workspace_root.join("model");
                                let mut model_path = model_dir.join("qwen2.5-1.5b-coder.gguf");
                                let mut tokenizer_path = model_dir.join("tokenizer.json");
                                
                                if !model_path.exists() {
                                    // Auto-discover any .gguf file in model/ directory
                                    if let Ok(entries) = std::fs::read_dir(&model_dir) {
                                        for entry in entries.flatten() {
                                            let p = entry.path();
                                            if p.extension().map_or(false, |ext| ext == "gguf") {
                                                model_path = p;
                                                break;
                                            }
                                        }
                                    }
                                }
                                
                                if !model_path.exists() {
                                    if let Some(parent) = workspace_root.parent() {
                                        let alt_model_dir = parent.join("model");
                                        let alt_model = alt_model_dir.join("qwen2.5-1.5b-coder.gguf");
                                        if alt_model.exists() {
                                            model_path = alt_model;
                                            tokenizer_path = alt_model_dir.join("tokenizer.json");
                                        } else if let Ok(entries) = std::fs::read_dir(&alt_model_dir) {
                                            for entry in entries.flatten() {
                                                let p = entry.path();
                                                if p.extension().map_or(false, |ext| ext == "gguf") {
                                                    model_path = p;
                                                    tokenizer_path = alt_model_dir.join("tokenizer.json");
                                                    break;
                                                }
                                            }
                                        }
                                    }
                                }
                                
                                log_print!(self, "⚙️ [ENGINE LLM]: Próba wczytania lokalnego modelu: {:?}", model_path);
                                match crate::cognitive_llm::LocalCognitiveLLM::load(&model_path, &tokenizer_path) {
                                    Ok(loaded_llm) => {
                                        self.llm = Some(loaded_llm);
                                        log_print!(self, "✓ [ENGINE LLM]: Lokalny model załadowany pomyślnie.");
                                    }
                                    Err(e) => {
                                        let err_msg = format!("⚠️ [ENGINE LLM BŁĄD]: Nie udało się załadować lokalnego modelu ({:?}): {}", model_path, e);
                                        log_print!(self, "{}", err_msg);
                                        self.emit_event(EngineEvent::ResponseFinished(err_msg));
                                    }
                                }
                            }

                            if let Some(llm) = &mut self.llm {
                                // Dynamiczne parametry z Neurochemii
                                let (temp, rep_pen, max_toks) = if let BlysState::Active { neuro_state, .. } = &self.state {
                                    let ns = neuro_state.read().await;
                                    (
                                        (0.7 + (ns.dopamine - 0.5) * 0.5) as f64,
                                        (1.1 + (ns.serotonin - 0.5) * 0.2) as f32,
                                        (256.0 + (ns.cortisol - 0.5) * 128.0) as usize
                                    )
                                } else {
                                    (0.7, 1.1, 256)
                                };
                                
                                log_print!(self, "🚀 [ENGINE INFERENCE]: Rozpoczęcie natywnego generowania odpowiedzi.");
                                
                                let params = crate::cognitive_llm::GenerationParams {
                                    temperature: temp,
                                    repetition_penalty: rep_pen,
                                    top_p: 0.9,
                                    max_tokens: max_toks,
                                };
                                
                                let event_tx_clone = self.event_tx.clone();
                                let prompt_input = text.clone();
                                
                                let response_res = llm.generate(&prompt_input, &params, |token| {
                                    if let Some(ref tx) = event_tx_clone {
                                        let _ = tx.try_send(EngineEvent::Token(token.to_string()));
                                    }
                                });
                                
                                match response_res {
                                    Ok(final_reply) => {
                                        log_print!(self, "✓ [ENGINE INFERENCE]: Odpowiedź wygenerowana.");
                                        self.emit_event(EngineEvent::ResponseFinished(final_reply));
                                    }
                                    Err(e) => {
                                        let err_msg = format!("❌ [ENGINE INFERENCE ERROR]: {}", e);
                                        log_print!(self, "{}", err_msg);
                                        self.emit_event(EngineEvent::ResponseFinished(err_msg));
                                    }
                                }
                            } else {
                                let warn_msg = format!("⚠️ [ENGINE LLM]: Brak załadowanego modelu. Umieść pliki qwen2.5-1.5b-coder.gguf i tokenizer.json w katalogu model/ i spróbuj ponownie.");
                                log_print!(self, "{}", warn_msg);
                                self.emit_event(EngineEvent::ResponseFinished(warn_msg));
                            }
                        }
                        StateCommand::QueryWithVector { id, vector, text } => {
                            log_print!(self, "📥 [ENGINE INPUT]: Otrzymano zapytanie wektorowe: \"{}\" (ID: {})", text, id);
                            
                            // Wybór eksperta MoE
                            let mut selected_expert_idx = 0;
                            if let BlysState::Active { gating, neuro_state, .. } = &self.state {
                                let ns = neuro_state.read().await;
                                selected_expert_idx = gating.select_expert(&ns, &text);
                                log_print!(self, "🧠 [ENGINE GATING]: Wybrano Eksperta ID: {} (z {}) na podstawie stanu neurochemicznego.", selected_expert_idx, gating.num_experts);
                            }

                            let projected_vector = self.project_vector_with_expert(&vector, selected_expert_idx);
                            
                            // Log projection change
                            if projected_vector != vector {
                                log_print!(self, 
                                    "🧠 [ENGINE PROJECTION]: Wektor został przetransformowany przez MLP. Pierwsze 3 elementy: [{:.4}, {:.4}, {:.4}] -> [{:.4}, {:.4}, {:.4}]",
                                    vector.get(0).unwrap_or(&0.0), vector.get(1).unwrap_or(&0.0), vector.get(2).unwrap_or(&0.0),
                                    projected_vector.get(0).unwrap_or(&0.0), projected_vector.get(1).unwrap_or(&0.0), projected_vector.get(2).unwrap_or(&0.0)
                                );
                            } else {
                                log_print!(self, "🧠 [ENGINE PROJECTION]: Projekcja neuronowa nieaktywna (wagi zerowe). Użyto wektora wejściowego.");
                            }

                            let heuristic_threat = self.shield.check_heuristics(&text);
                            let semantic_threat = {
                                let neuro_ref = if let BlysState::Active { neuro_state, .. } = &self.state {
                                    Some(neuro_state.read().await)
                                } else {
                                    None
                                };
                                self.shield.check_semantic(
                                    &projected_vector,
                                    &self.index,
                                    neuro_ref.as_deref()
                                )
                            };
                            if heuristic_threat || semantic_threat {
                                if heuristic_threat {
                                    log_print!(self, "🛡️ [WOLF TEETH]: Wykryto zagrożenie (Warstwa 1 - Heurystyka)!");
                                }
                                if semantic_threat {
                                    log_print!(self, "🛡️ [WOLF TEETH]: Wykryto zagrożenie (Warstwa 2 - Semantyka)!");
                                }
                                self.wake_up().await;
                                if let BlysState::Active { neuro_state, .. } = &self.state {
                                    let mut ns = neuro_state.write().await;
                                    ns.apply_profile("wolf_teeth");
                                    log_print!(self, "🧠 [ENGINE STATE]: Kwarantanna - stan neurochemiczny: {}", ns.get_status_report());
                                    self.emit_event(EngineEvent::Neurochemistry(ns.clone()));
                                }
                                log_print!(self, "🔒 [ENGINE QUARANTINE]: Błyskawica AI: RealityAnchor protected. Cognitive quarantine activated.");
                                
                                // Natywne obniżenie uprawnień wątku i kwarantanna sieciowa
                                if let Err(e) = crate::native_security::drop_thread_privileges() {
                                    log_print!(self, "⚠️ [WOLF TEETH ERROR]: Nie udało się zrzucić uprawnień wątku: {}", e);
                                } else {
                                    log_print!(self, "🔒 [WOLF TEETH]: Uprawnienia wątku roboczego zostały zrzucone do poziomu Read-Only.");
                                }
                                if let Ok(closed_count) = crate::native_security::terminate_external_tcp_connections() {
                                    if closed_count > 0 {
                                        log_print!(self, "🔒 [NETWORK QUARANTINE]: Kwarantanna sieciowa aktywna. Zamknięto {} aktywnych połączeń TCP/IP.", closed_count);
                                    }
                                }
                                continue;
                            }
                            
                            // Przywrócenie normalnych uprawnień przy bezpiecznym przejściu
                            let _ = crate::native_security::restore_thread_privileges();
                            self.wake_up().await;
                            if let BlysState::Active { neuro_state, .. } = &self.state {
                                // 1. Apply query profile + autonomous adaptation
                                {
                                    let mut ns = neuro_state.write().await;
                                    ns.apply_profile("query");
                                    ns.apply_autonomous_fluctuation();
                                    log_print!(self, "🧠 [ENGINE STATE]: Wirtualna neurochemia (po zapytaniu): {}", ns.get_status_report());
                                    self.emit_event(EngineEvent::Neurochemistry(ns.clone()));
                                }

                                // 2. Search index
                                let search_results = self.index.search(&projected_vector, 1);
                                let best_distance = if let Some(best) = search_results.first() {
                                    best.distance
                                } else {
                                    1.0 // no neighbor found
                                };

                                // 3. Inspect vector with GroundLoopIsolator and determine anomaly
                                let (_clean_vector, is_anomaly) = self.anomaly_detector.inspect_and_queue(
                                    id,
                                    &projected_vector,
                                    best_distance,
                                    text.clone(),
                                );

                                log_print!(self, "🔍 [ENGINE SEARCH]: Najlepszy dystans cosinusowy: {:.4}", best_distance);
                                if is_anomaly {
                                    log_print!(self, 
                                        "⚠️ [ENGINE ANOMALY]: Wykryto anomalię (zaskoczenie: {:.4} > {:.4})! Oczyszczony wektor zakolejkowany.",
                                        best_distance, self.anomaly_detector.surprise_threshold
                                    );
                                    self.emit_event(EngineEvent::AnomalyQueued {
                                        id,
                                        surprise: best_distance,
                                        text: text.clone(),
                                    });
                                } else {
                                    log_print!(self, "✅ [ENGINE SEARCH]: Wektor dopasowany pomyślnie. Brak anomalii.");
                                }
                            }
                        }
                        StateCommand::DeepSleep => {
                            log_print!(self, "\n😴 [ENGINE DEEP SLEEP]: Rozpoczęto fazę DEEP_SLEEP (Konsolidacja Pamięci).");
                            self.wake_up().await;
                            if let BlysState::Active { neuro_state, .. } = &self.state {
                                // 1. Apply deep sleep neurochemistry profile
                                {
                                    let mut ns = neuro_state.write().await;
                                    ns.apply_profile("deep_sleep");
                                    log_print!(self, "🧠 [ENGINE STATE]: Stan neurochemiczny (Głęboki Sen): {}", ns.get_status_report());
                                    self.emit_event(EngineEvent::Neurochemistry(ns.clone()));
                                }

                                // 2. Drain queued anomalies
                                let items = self.anomaly_detector.drain_queue();
                                let count = items.len();
                                if count > 0 {
                                    log_print!(self, "💤 [ENGINE DEEP SLEEP]: Znaleziono {} anomalii w kolejce. Rozpoczynanie konsolidacji...", count);
                                    for item in items {
                                        log_print!(self, 
                                            "   └─ [KONSOLIDACJA]: Zapisywanie nowego pojęcia w bazie Sparkle: \"{}\" (ID: {})",
                                            item.metadata, item.id
                                        );
                                        // Insert clean vector into HNSW index
                                        self.index.insert(item.id, &item.vector);
                                        tokio::time::sleep(Duration::from_millis(300)).await; // simulate synaptic integration time
                                    }
                                    log_print!(self, "✅ [ENGINE DEEP SLEEP]: Pomyślnie skonsolidowano {} nowe pojęcia.", count);

                                    // Save the index to disk if db_path is set
                                    if let Some((ref path, ref basename)) = self.db_path {
                                        log_print!(self, "💾 [ENGINE DEEP SLEEP]: Zapisywanie indeksu HNSW do pliku: {} pod ścieżką {:?}", basename, path);
                                        match self.index.file_dump(path, basename) {
                                            Ok(saved_name) => log_print!(self, "💾 [ENGINE DEEP SLEEP]: Indeks HNSW zapisany pomyślnie jako {}", saved_name),
                                            Err(err) => log_print!(self, "❌ [ENGINE DEEP SLEEP ERROR]: Błąd zapisu indeksu HNSW: {}", err),
                                        }
                                    }
                                } else {
                                    log_print!(self, "💤 [ENGINE DEEP SLEEP]: Kolejka anomalii jest pusta. Brak tematów do konsolidacji.");
                                }

                                // 3. Set to hibernation
                                self.hibernate().await;
                            }
                        }
                        StateCommand::Status => {
                            self.print_status().await;
                        }
                        StateCommand::CoolDown => {
                            self.cooldown().await;
                        }
                        StateCommand::Neurogenesis => {
                            log_print!(self, "\n🧬 [ENGINE NEUROGENESIS]: Inicjowanie powołania nowego eksperta MoE...");
                            self.wake_up().await;
                            
                            if let BlysState::Active { experts, gating, ewc_saturation, .. } = &mut self.state {
                                let new_id = experts.len();
                                if new_id >= 3 {
                                    log_print!(self, "🧬 [ENGINE NEUROGENESIS]: Osiągnięto maksymalną liczbę ekspertów (3).");
                                } else {
                                    let new_weights_path = self.weights_path.parent()
                                        .unwrap_or(&PathBuf::from("."))
                                        .join(format!("mock_weights_expert_{}.bin", new_id));
                                        
                                    log_print!(self, "💾 [ENGINE NEUROGENESIS]: Generowanie pliku wag dla nowego eksperta: {:?}", new_weights_path);
                                    let mut success = false;
                                    if let Ok(mut file) = File::create(&new_weights_path) {
                                        let weights = vec![0.0f32; 16576];
                                        let mut byte_data = Vec::with_capacity(1_024_000);
                                        for &w in &weights {
                                            byte_data.extend_from_slice(&w.to_le_bytes());
                                        }
                                        byte_data.resize(1_024_000, 0u8);
                                        if file.write_all(&byte_data).is_ok() {
                                            if let Ok(open_file) = File::open(&new_weights_path) {
                                                if let Ok(mmap) = unsafe { memmap2::Mmap::map(&open_file) } {
                                                    experts.push(ExpertModule::new(new_id, mmap, new_weights_path.clone()));
                                                    gating.num_experts = experts.len();
                                                    *ewc_saturation = 0.0; // reset
                                                    log_print!(self, "🧬 [ENGINE NEUROGENESIS]: Nowy Ekspert ID: {} załadowany. Łączna liczba ekspertów: {}", new_id, gating.num_experts);
                                                    success = true;
                                                }
                                            }
                                        }
                                    }
                                    if !success {
                                        log_print!(self, "❌ [ENGINE ERROR]: Nie udało się zainicjalizować nowego eksperta.");
                                    }
                                }
                            }
                        }
                    }
                }
                Ok(None) => {
                    log_print!(self, "🛑 [ENGINE CLOSED]: Kanał komunikacyjny zamknięty. Kończenie pętli.");
                    break;
                }
                Err(_) => {
                    // Timeout occurred
                    if let BlysState::Active { .. } = &self.state {
                        log_print!(self, "⏳ [ENGINE TIMEOUT]: Brak aktywności przez {:?}. Inicjowanie fazy cooldown i hibernacji...", cooldown_duration);
                        self.cooldown().await;
                        self.hibernate().await;
                    }
                }
            }
        }
    }

    pub fn project_vector(&self, input: &[f32]) -> Vec<f32> {
        self.project_vector_with_expert(input, 0)
    }

    pub fn project_vector_with_expert(&self, input: &[f32], expert_idx: usize) -> Vec<f32> {
        let input_dim = 128;
        if input.len() != input_dim {
            return input.to_vec();
        }

        match &self.state {
            BlysState::Active { experts, .. } => {
                if experts.is_empty() {
                    return input.to_vec();
                }
                let idx = if expert_idx < experts.len() { expert_idx } else { 0 };
                let expert = &experts[idx];

                if let Some(engine) = &expert.engine {
                    match engine.project(input) {
                        Ok(output) => output,
                        Err(e) => {
                            log_print!(self, "⚠️ [ENGINE ERROR]: Błąd projekcji Candle: {}", e);
                            input.to_vec()
                        }
                    }
                } else {
                    input.to_vec()
                }
            }
            _ => input.to_vec(),
        }
    }

    pub async fn wake_up(&mut self) {
        match &self.state {
            BlysState::Active { .. } => {
                log_print!(self, "✅ [ENGINE]: Silnik jest już aktywny (Woda).");
            }
            BlysState::Hibernated { weights_path } => {
                log_print!(self, "🧊 ⇄ 💧 [ENGINE]: Wybudzanie: Lód ⇄ Woda. Mapowanie wag pliku: {:?}", weights_path);
                match File::open(weights_path) {
                    Ok(file) => {
                        match unsafe { Mmap::map(&file) } {
                            Ok(mmap) => {
                                log_print!(self, "💾 [ENGINE MMAP]: Plik wag zamapowany w pamięci RAM. Rozmiar: {} bajtów.", mmap.len());
                                let neuro_state = Arc::new(RwLock::new(NeurochemicalState::new()));
                                {
                                    let mut ns = neuro_state.write().await;
                                    ns.apply_profile("study");
                                    log_print!(self, "🧠 [ENGINE STATE]: Zainicjowano profil kognitywny 'study'.");
                                    self.emit_event(EngineEvent::Neurochemistry(ns.clone()));
                                }
                                let base_expert = ExpertModule::new(0, mmap, weights_path.clone());
                                self.state = BlysState::Active {
                                    experts: vec![base_expert],
                                    gating: GatingNetwork::new(),
                                    neuro_state,
                                    ewc_saturation: 0.25,
                                };
                                log_print!(self, "🌞 [ENGINE]: Silnik przeszedł w stan Aktywny (Woda).");
                            }
                            Err(e) => {
                                log_print!(self, "❌ [ENGINE ERROR]: Błąd mapowania pamięci: {}", e);
                            }
                        }
                    }
                    Err(e) => {
                        log_print!(self, "❌ [ENGINE ERROR]: Błąd otwierania pliku wag {:?}: {}", weights_path, e);
                    }
                }
            }
        }
    }

    pub async fn cooldown(&mut self) {
        if let BlysState::Active { neuro_state, .. } = &self.state {
            let mut ns = neuro_state.write().await;
            ns.apply_profile("cooldown");
            log_print!(self, "🧠 [ENGINE STATE]: Wyciszenie kognitywne (Cooldown): {}", ns.get_status_report());
            self.emit_event(EngineEvent::Neurochemistry(ns.clone()));
        }
    }

    pub async fn hibernate(&mut self) {
        match &self.state {
            BlysState::Hibernated { .. } => {
                log_print!(self, "💤 [ENGINE]: Silnik jest już zahibernowany (Lód).");
            }
            BlysState::Active { neuro_state, .. } => {
                log_print!(self, "💧 ⇄ 🧊 [ENGINE]: Rozpoczęto hibernację: Woda ⇄ Lód. Odmapowywanie pamięci...");
                {
                    let mut ns = neuro_state.write().await;
                    ns.apply_profile("hibernation");
                    log_print!(self, "🧠 [ENGINE STATE]: Neurochemia przy inicjacji hibernacji: {}", ns.get_status_report());
                    self.emit_event(EngineEvent::Neurochemistry(ns.clone()));
                }
                // Dropping experts happens implicitly as we re-assign self.state
                self.state = BlysState::Hibernated { weights_path: self.weights_path.clone() };
                log_print!(self, "❄️ [ENGINE]: Plik wag odmapowany z pamięci. Silnik przeszedł w stan Hibernacji.");
            }
        }
    }

    pub async fn print_status(&self) {
        match &self.state {
            BlysState::Hibernated { weights_path } => {
                log_print!(self, "📊 [ENGINE STATUS]: Stan: HIBERNATED (Lód). Ścieżka: {:?}", weights_path);
            }
            BlysState::Active { experts, gating, neuro_state, ewc_saturation } => {
                let ns = neuro_state.read().await;
                log_print!(self,
                    "📊 [ENGINE STATUS]: Stan: ACTIVE (Woda). Liczba ekspertów MoE: {} (aktywnych: {}). Saturacja EWC: {:.2}. Neurochemia: {}",
                    experts.len(),
                    gating.num_experts,
                    ewc_saturation,
                    ns.get_status_report()
                );
            }
        }
    }
}
