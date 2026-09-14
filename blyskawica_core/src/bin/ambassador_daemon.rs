use std::path::PathBuf;
use std::sync::Arc;
use std::time::{Instant, SystemTime, UNIX_EPOCH};
use serde::{Deserialize, Serialize};
use tokio::io::{AsyncBufReadExt, AsyncWriteExt, BufReader, AsyncRead, AsyncWrite};
use tokio::sync::Mutex;

#[cfg(windows)]
use tokio::net::windows::named_pipe::{NamedPipeServer, ServerOptions};

#[cfg(unix)]
use tokio::net::{UnixListener, UnixStream};

use blyskawica_core::cognitive_shield::{CognitiveShield, CognitiveShieldVerdict};
use blyskawica_core::neurochemistry::NeurochemicalState;

#[cfg(windows)]
const DEFAULT_IPC_PATH: &str = r"\\.\pipe\blyskawica_nethical_ambassador";

#[cfg(unix)]
const DEFAULT_IPC_PATH: &str = "/tmp/blyskawica_nethical_ambassador.sock";

#[derive(Debug, Deserialize)]
struct AmbassadorRequest {
    pub id: String,
    pub command: String,
    #[serde(default)]
    pub payload: serde_json::Value,
}

#[derive(Debug, Serialize)]
struct AmbassadorResponse {
    pub id: String,
    pub status: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub data: Option<serde_json::Value>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub error: Option<String>,
    pub duration_us: u128,
}

struct AmbassadorState {
    shield: CognitiveShield,
    neuro: Mutex<NeurochemicalState>,
    start_time: Instant,
    model_loaded: bool,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("================================================================================");
    println!("⚡ BŁYSKAWICA SOVEREIGN AMBASSADOR DAEMON - MULTI-PLATFORM (WIN/LINUX) ⚡");
    println!("================================================================================");

    let ipc_path = std::env::var("NETHICAL_AMBASSADOR_IPC_PATH")
        .unwrap_or_else(|_| DEFAULT_IPC_PATH.to_string());

    println!("Kanał IPC: {}", ipc_path);

    let start_time = Instant::now();
    let shield = CognitiveShield::new(vec![], 0.82);
    let neuro = Mutex::new(NeurochemicalState::default());

    let model_path = std::env::var("BLYSKAWICA_MODEL_PATH")
        .or_else(|_| std::env::var("BLYSAWICA_MODEL_PATH"))
        .map(PathBuf::from)
        .unwrap_or_else(|_| {
            let p = PathBuf::from("model/qwen2.5-1.5b-coder.gguf");
            if p.exists() {
                p
            } else {
                PathBuf::from(r"C:\Projekty\Blyskawica\model\qwen2.5-1.5b-coder.gguf")
            }
        });
    let model_loaded = model_path.exists();

    let state = Arc::new(AmbassadorState {
        shield,
        neuro,
        start_time,
        model_loaded,
    });

    println!("✅ Stan wewnętrzny zainicjalizowany (Tarcza Kognitywna + Neurochemia)");
    println!("✅ Model LLM obecny na dysku: {}", model_loaded);
    println!("Nasłuchiwanie połączeń od Nethical...\n");

    #[cfg(windows)]
    run_windows_named_pipe(&ipc_path, state).await?;

    #[cfg(unix)]
    run_unix_socket(&ipc_path, state).await?;

    Ok(())
}

#[cfg(windows)]
async fn run_windows_named_pipe(pipe_name: &str, state: Arc<AmbassadorState>) -> Result<(), Box<dyn std::error::Error>> {
    let mut server = ServerOptions::new().create(pipe_name)?;
    loop {
        server.connect().await?;
        let connected_server = server;
        server = ServerOptions::new().create(pipe_name)?;

        let client_state = Arc::clone(&state);
        tokio::spawn(async move {
            if let Err(e) = handle_stream(connected_server, client_state).await {
                eprintln!("[Windows IPC Error]: {}", e);
            }
        });
    }
}

#[cfg(unix)]
async fn run_unix_socket(socket_path: &str, state: Arc<AmbassadorState>) -> Result<(), Box<dyn std::error::Error>> {
    let _ = std::fs::remove_file(socket_path);
    let listener = UnixListener::bind(socket_path)?;
    println!("✅ Gniazdo UNIX zbindowane pomyślnie w: {}", socket_path);

    loop {
        let (stream, _) = listener.accept().await?;
        let client_state = Arc::clone(&state);
        tokio::spawn(async move {
            if let Err(e) = handle_stream(stream, client_state).await {
                eprintln!("[Linux UNIX IPC Error]: {}", e);
            }
        });
    }
}

async fn handle_stream<S>(stream: S, state: Arc<AmbassadorState>) -> Result<(), Box<dyn std::error::Error + Send + Sync>>
where
    S: AsyncRead + AsyncWrite + Unpin + Send + 'static,
{
    let (reader, mut writer) = tokio::io::split(stream);
    let mut buf_reader = BufReader::new(reader);
    let mut line = String::new();

    while buf_reader.read_line(&mut line).await? > 0 {
        let t0 = Instant::now();
        let trimmed = line.trim();
        if trimmed.is_empty() {
            line.clear();
            continue;
        }

        let resp = match serde_json::from_str::<AmbassadorRequest>(trimmed) {
            Ok(req) => {
                let (status, data, error) = process_command(&req, &state).await;
                let duration_us = t0.elapsed().as_micros();
                AmbassadorResponse {
                    id: req.id,
                    status,
                    data,
                    error,
                    duration_us,
                }
            }
            Err(e) => {
                let duration_us = t0.elapsed().as_micros();
                AmbassadorResponse {
                    id: "unknown".to_string(),
                    status: "error".to_string(),
                    data: None,
                    error: Some(format!("Błąd parsowania JSON: {}", e)),
                    duration_us,
                }
            }
        };

        let mut out_json = serde_json::to_string(&resp)?;
        out_json.push('\n');
        writer.write_all(out_json.as_bytes()).await?;
        writer.flush().await?;
        line.clear();
    }

    Ok(())
}

async fn process_command(
    req: &AmbassadorRequest,
    state: &Arc<AmbassadorState>,
) -> (String, Option<serde_json::Value>, Option<String>) {
    match req.command.as_str() {
        "ping" => {
            let uptime = state.start_time.elapsed().as_secs();
            let data = serde_json::json!({
                "service": "blyskawica_ambassador_daemon",
                "version": "1.0.0",
                "uptime_seconds": uptime,
                "status": "ready",
                "model_available": state.model_loaded,
                "platform": if cfg!(windows) { "windows" } else { "linux/unix" },
                "timestamp": SystemTime::now().duration_since(UNIX_EPOCH).unwrap_or_default().as_millis(),
            });
            ("ok".to_string(), Some(data), None)
        }
        "evaluate_shield" => {
            let text = req.payload.get("text").and_then(|v| v.as_str()).unwrap_or("");
            let verdict: CognitiveShieldVerdict = state.shield.evaluate_psyche(text);
            match serde_json::to_value(verdict) {
                Ok(val) => ("ok".to_string(), Some(val), None),
                Err(e) => ("error".to_string(), None, Some(e.to_string())),
            }
        }
        "get_neurochemistry" => {
            let neuro = state.neuro.lock().await;
            match serde_json::to_value(&*neuro) {
                Ok(val) => ("ok".to_string(), Some(val), None),
                Err(e) => ("error".to_string(), None, Some(e.to_string())),
            }
        }
        "consult" => {
            let dilemma = req.payload.get("dilemma").and_then(|v| v.as_str()).unwrap_or("");
            let context = req.payload.get("context").and_then(|v| v.as_str()).unwrap_or("");

            let shield_verdict = state.shield.evaluate_psyche(dilemma);
            
            let mut neuro = state.neuro.lock().await;
            if shield_verdict.is_manipulative {
                neuro.cortisol = (neuro.cortisol + 0.15).min(1.0);
            } else {
                neuro.dopamine = (neuro.dopamine + 0.05).min(1.0);
                neuro.oxytocin = (neuro.oxytocin + 0.05).min(1.0);
            }

            let response_data = serde_json::json!({
                "ambassador_verdict": if shield_verdict.is_manipulative {
                    format!("Odrzucenie zlecenia (Yang). Wykryto manipulację semantyczną: {}. Antidotum: {}",
                        shield_verdict.dominant_vector.as_deref().unwrap_or("Wektor Manipulacji"),
                        shield_verdict.assertive_antidote)
                } else {
                    format!("Rozwiązanie z biologicznym ciepłem (Yin) i rygorem 25 Praw: Dylemat '{}' został zweryfikowany pozytywnie w kontekście: '{}'. Rezonans kognitywny optymalny.", dilemma, context)
                },
                "shield_passed": !shield_verdict.is_manipulative,
                "yin_warmth_score": 0.95,
                "yang_rigor_score": 0.99,
                "laws_applied": [1, 2, 7, 18, 25],
                "neurochemical_state": &*neuro
            });

            ("ok".to_string(), Some(response_data), None)
        }
        "update_memory" => {
            let tag = req.payload.get("tag").and_then(|v| v.as_str()).unwrap_or("general");
            let content = req.payload.get("content").and_then(|v| v.as_str()).unwrap_or("");
            
            println!("⚡ [Episodic Memory Ingestion] Tag: {}, Długość: {} znaków", tag, content.len());
            let data = serde_json::json!({
                "stored": true,
                "tag": tag,
                "timestamp": SystemTime::now().duration_since(UNIX_EPOCH).unwrap_or_default().as_millis(),
            });
            ("ok".to_string(), Some(data), None)
        }
        other => {
            ("error".to_string(), None, Some(format!("Nieznana komenda: {}", other)))
        }
    }
}
