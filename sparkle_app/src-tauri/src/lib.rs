use blyskawica_core::state_manager::{BlyskawicaEngine, StateCommand};
use blyskawica_core::vector_index::SparkleVectorIndex;
use std::collections::BTreeSet;
use std::path::{Component, Path, PathBuf};
use std::sync::Arc;
use std::sync::Mutex;
use std::time::Duration;
use tauri::{AppHandle, Emitter, Manager, State};
use tokio::sync::mpsc;

pub struct AppStateInner {
    tx: Option<mpsc::Sender<StateCommand>>,
    permission_level: u8, // 1: Sandbox, 2: Workspace, 3: Full OS
    online_mode: bool,
    connector_consents: BTreeSet<String>,
    workspace_path: PathBuf,
    backend_child: Option<std::process::Child>,
    shell_secret: Option<String>,
    engine_handle: Option<tokio::task::JoinHandle<()>>,
    shadow_board: blyskawica_core::shadow_forge::ShadowBoard,
    aegis: blyskawica_core::aegis_sentinel::AegisSentinel,
    tree: blyskawica_core::cognitive_heartbeat::CognitiveHeartbeat,
    cognitive_shield: blyskawica_core::cognitive_shield::CognitiveShield,
    current_neurochemistry: blyskawica_core::neurochemistry::NeurochemicalState,
    aegis_psyche: blyskawica_core::aegis_psyche_onnx::AegisPsycheRustEngine,
    quantum_bridge: blyskawica_core::quantum_core::QuantumEntanglementBridge,
}

pub struct AppState(pub Mutex<AppStateInner>);

struct ConnectorDefinition {
    id: &'static str,
    label: &'static str,
    destination: &'static str,
    data_disclosure: &'static str,
    implementation_status: &'static str,
    can_be_enabled: bool,
}

const LEGACY_SIDECAR_STATUS_CONNECTOR_ID: &str = "legacy_sidecar_status";

const CONNECTOR_DEFINITIONS: &[ConnectorDefinition] = &[
    ConnectorDefinition {
        id: LEGACY_SIDECAR_STATUS_CONNECTOR_ID,
        label: "Legacy sidecar status (loopback)",
        destination: "http://127.0.0.1:8000/api/system_status",
        data_disclosure:
            "Żądanie GET bez treści użytkownika; odpowiedź może zawierać metryki stanu legacy.",
        implementation_status: "Dostępny wyłącznie po SPARKLE_ENABLE_SIDECAR=1/true.",
        can_be_enabled: true,
    },
    ConnectorDefinition {
        id: "internet_search",
        label: "Wyszukiwanie w internecie",
        destination: "Zewnętrzny dostawca wyszukiwania — nie skonfigurowano.",
        data_disclosure: "Żadne dane nie są wysyłane: transport nie jest zaimplementowany.",
        implementation_status: "Planowany; nie można go aktywować.",
        can_be_enabled: false,
    },
    ConnectorDefinition {
        id: "cloud_backup",
        label: "Kopia zapasowa w chmurze",
        destination: "Zewnętrzny dostawca kopii — nie skonfigurowano.",
        data_disclosure: "Żadne dane nie są wysyłane: transport nie jest zaimplementowany.",
        implementation_status: "Planowany; nie można go aktywować.",
        can_be_enabled: false,
    },
    ConnectorDefinition {
        id: "nethical_docking",
        label: "Nethical docking",
        destination: "Zewnętrzna integracja Nethical — nie skonfigurowano.",
        data_disclosure:
            "Żadne dane nie są wysyłane: transport i zakres danych nie są jeszcze zaprojektowane.",
        implementation_status: "Planowany; nie można go aktywować.",
        can_be_enabled: false,
    },
];

fn connector_definition(connector_id: &str) -> Option<&'static ConnectorDefinition> {
    CONNECTOR_DEFINITIONS
        .iter()
        .find(|definition| definition.id == connector_id)
}

fn connector_access_granted(
    online_mode: bool,
    connector_consents: &BTreeSet<String>,
    connector_id: &str,
) -> bool {
    online_mode && connector_consents.contains(connector_id)
}

fn connector_registry_json(
    online_mode: bool,
    connector_consents: &BTreeSet<String>,
) -> serde_json::Value {
    let connectors: Vec<serde_json::Value> = CONNECTOR_DEFINITIONS
        .iter()
        .map(|definition| {
            serde_json::json!({
                "id": definition.id,
                "label": definition.label,
                "destination": definition.destination,
                "data_disclosure": definition.data_disclosure,
                "implementation_status": definition.implementation_status,
                "can_be_enabled": definition.can_be_enabled,
                "consented": connector_access_granted(
                    online_mode,
                    connector_consents,
                    definition.id,
                ),
            })
        })
        .collect();

    serde_json::json!({
        "online_mode": online_mode,
        "consent_scope": "Zgody obowiązują wyłącznie w bieżącej sesji aplikacji i są kasowane po wyłączeniu trybu online.",
        "connectors": connectors,
    })
}

fn is_inside_workspace(path: &Path, workspace: &Path) -> bool {
    let workspace_canon = match workspace.canonicalize() {
        Ok(w) => w,
        Err(_) => return false,
    };

    let mut existing_ancestor = path;
    loop {
        match existing_ancestor.symlink_metadata() {
            Ok(_) => {
                return existing_ancestor
                    .canonicalize()
                    .map(|canonical| canonical.starts_with(&workspace_canon))
                    .unwrap_or(false);
            }
            Err(error) if error.kind() == std::io::ErrorKind::NotFound => {
                let Some(parent) = existing_ancestor.parent() else {
                    return false;
                };
                existing_ancestor = parent;
            }
            Err(_) => return false,
        }
    }
}

/// Resolves a path supplied by an IPC caller only when it stays within the
/// configured workspace.  Keeping this check next to the canonicalisation
/// logic prevents individual commands from accidentally reintroducing a
/// traversal bypass.
fn resolve_workspace_relative_path(
    workspace: &Path,
    relative_path: &str,
) -> Result<PathBuf, String> {
    let relative = Path::new(relative_path);
    if relative.is_absolute()
        || relative.has_root()
        || relative.components().any(|component| {
            matches!(
                component,
                Component::Prefix(_) | Component::RootDir | Component::ParentDir
            )
        })
    {
        return Err("Dozwolone są wyłącznie ścieżki względne do katalogu roboczego.".to_string());
    }

    let target = workspace.join(relative);
    if !is_inside_workspace(&target, workspace) {
        return Err("Ścieżka wykracza poza dozwolony katalog roboczy.".to_string());
    }

    Ok(target)
}

fn require_permission_level(actual: u8, required: u8, operation: &str) -> Result<(), String> {
    if actual < required {
        return Err(format!(
            "Operacja '{}' wymaga poziomu uprawnień {} lub wyższego.",
            operation, required
        ));
    }
    Ok(())
}

fn permission_change_requires_confirmation(current: u8, requested: u8) -> bool {
    requested > current
}

fn workspace_path_for_permission(permission_level: u8, workspace: &Path) -> Option<String> {
    (permission_level >= 2).then(|| workspace.to_string_lossy().to_string())
}

fn app_runtime_data_dir(app_handle: &AppHandle) -> PathBuf {
    app_handle
        .path()
        .app_data_dir()
        .unwrap_or_else(|_| std::env::temp_dir().join("Blyskawica"))
}

const DATA_INVENTORY_ENTRY_LIMIT: usize = 10_000;

fn bounded_storage_size_bytes(path: &Path, remaining: &mut usize, limit_reached: &mut bool) -> u64 {
    if *limit_reached {
        return 0;
    }

    let metadata = match path.symlink_metadata() {
        Ok(metadata) => metadata,
        Err(_) => return 0,
    };

    if metadata.is_file() {
        return metadata.len();
    }
    if !metadata.is_dir() {
        return 0;
    }

    let entries = match std::fs::read_dir(path) {
        Ok(entries) => entries,
        Err(_) => return 0,
    };

    let mut total = 0;
    for entry in entries.flatten() {
        if *remaining == 0 {
            *limit_reached = true;
            break;
        }
        *remaining -= 1;
        total += bounded_storage_size_bytes(&entry.path(), remaining, limit_reached);
    }
    total
}

fn storage_inventory_stats(path: &Path) -> (u64, bool) {
    let mut remaining = DATA_INVENTORY_ENTRY_LIMIT;
    let mut limit_reached = false;
    let size_bytes = bounded_storage_size_bytes(path, &mut remaining, &mut limit_reached);
    (size_bytes, !limit_reached)
}

fn remove_regular_file(path: &Path) -> Result<bool, String> {
    let metadata = match path.symlink_metadata() {
        Ok(metadata) => metadata,
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => return Ok(false),
        Err(error) => return Err(format!("Nie można odczytać artefaktu: {error}")),
    };
    if !metadata.is_file() {
        return Err("Odmowa usunięcia: artefakt nie jest zwykłym plikiem.".to_string());
    }

    std::fs::remove_file(path).map_err(|error| format!("Nie można usunąć artefaktu: {error}"))?;
    Ok(true)
}

/// Python sidecars are a development-only compatibility path.  The desktop
/// product must stay usable without a local HTTP server or Python runtime.
fn sidecar_is_explicitly_enabled(value: Option<&str>) -> bool {
    matches!(
        value
            .map(|setting| setting.trim().to_ascii_lowercase())
            .as_deref(),
        Some("1" | "true")
    )
}

#[cfg(target_os = "windows")]
fn show_confirm_dialog(message: &str, title: &str) -> bool {
    use std::ffi::OsStr;
    use std::os::windows::ffi::OsStrExt;

    let msg_wide: Vec<u16> = OsStr::new(message)
        .encode_wide()
        .chain(std::iter::once(0))
        .collect();
    let title_wide: Vec<u16> = OsStr::new(title)
        .encode_wide()
        .chain(std::iter::once(0))
        .collect();

    unsafe {
        #[link(name = "user32")]
        extern "system" {
            fn MessageBoxW(
                hWnd: *mut std::ffi::c_void,
                lpText: *const u16,
                lpCaption: *const u16,
                uType: u32,
            ) -> i32;
        }

        let result = MessageBoxW(
            std::ptr::null_mut(),
            msg_wide.as_ptr(),
            title_wide.as_ptr(),
            0x00000004 | 0x00000030,
        );
        result == 6
    }
}

#[cfg(target_os = "macos")]
fn show_confirm_dialog(message: &str, title: &str) -> bool {
    if (std::env::var_os("CI").is_some() || std::env::var_os("BLY_HEADLESS").is_some())
        && std::env::var_os("BLY_FORCE_INTERACTIVE_DIALOG").is_none()
    {
        return false;
    }
    let escaped_title = title.replace('\\', "\\\\").replace('"', "\\\"");
    let escaped_msg = message.replace('\\', "\\\\").replace('"', "\\\"");
    let script = format!(
        "display alert \"{}\" message \"{}\" as critical buttons {{\"Anuluj\", \"Zezwól\"}} default button \"Zezwól\"",
        escaped_title, escaped_msg
    );
    match std::process::Command::new("osascript")
        .arg("-e")
        .arg(&script)
        .output()
    {
        Ok(output) => {
            let stdout = String::from_utf8_lossy(&output.stdout);
            output.status.success() && stdout.contains("button returned:Zezwól")
        }
        Err(_) => false,
    }
}

#[cfg(target_os = "linux")]
fn show_confirm_dialog(message: &str, title: &str) -> bool {
    if std::env::var_os("DISPLAY").is_none() && std::env::var_os("WAYLAND_DISPLAY").is_none() {
        return false;
    }
    if (std::env::var_os("CI").is_some() || std::env::var_os("BLY_HEADLESS").is_some())
        && std::env::var_os("BLY_FORCE_INTERACTIVE_DIALOG").is_none()
    {
        return false;
    }
    if let Ok(status) = std::process::Command::new("zenity")
        .arg("--question")
        .arg(format!("--title={}", title))
        .arg(format!("--text={}", message))
        .arg("--ok-label=Zezwól")
        .arg("--cancel-label=Anuluj")
        .status()
    {
        return status.success();
    }
    if let Ok(status) = std::process::Command::new("kdialog")
        .arg("--title")
        .arg(title)
        .arg("--yesno")
        .arg(message)
        .status()
    {
        return status.success();
    }
    false
}

#[cfg(not(any(target_os = "windows", target_os = "macos", target_os = "linux")))]
fn show_confirm_dialog(_message: &str, _title: &str) -> bool {
    false
}

#[tauri::command]
async fn start_engine(app_handle: AppHandle, state: State<'_, AppState>) -> Result<String, String> {
    let mut inner = state.0.lock().unwrap();
    if inner.tx.is_some() {
        return Ok("Silnik jest już uruchomiony.".to_string());
    }

    let app_data_dir = app_runtime_data_dir(&app_handle);
    std::fs::create_dir_all(&app_data_dir)
        .map_err(|error| format!("Błąd tworzenia katalogu danych aplikacji: {error}"))?;
    let weights_path = app_data_dir.join("mock_weights.bin");

    // 1. Generowanie mock_weights.bin jeśli nie istnieje
    if !weights_path.exists() {
        use std::fs::File;
        use std::io::Write;
        let mut file = File::create(&weights_path)
            .map_err(|e| format!("Błąd tworzenia mock_weights.bin: {}", e))?;
        let mut weights = vec![0.0f32; 16576];
        for h in 0..64 {
            weights[h * 128 + h * 2] = 0.5f32;
        }
        for h in 0..64 {
            weights[128 * 64 + h] = 0.01f32;
        }
        let l2_offset = 128 * 64 + 64;
        for o in 0..128 {
            let h = (o / 2).min(63);
            weights[l2_offset + o * 64 + h] = 0.5f32;
        }
        let l2_bias_offset = l2_offset + 64 * 128;
        for o in 0..128 {
            weights[l2_bias_offset + o] = 0.005f32;
        }
        let mut byte_data = Vec::with_capacity(1_024_000);
        for &w in &weights {
            byte_data.extend_from_slice(&w.to_le_bytes());
        }
        byte_data.resize(1_024_000, 0u8);
        file.write_all(&byte_data)
            .map_err(|e| format!("Błąd zapisu mock_weights.bin: {}", e))?;
    }

    // 2. Inicjalizacja HNSW z wczytywaniem i zapisem na dysku
    let dimension = 128;
    let db_dir = app_data_dir.join("db");
    let file_basename = "sparkle_vectors";

    let index = match SparkleVectorIndex::load_hnsw(&db_dir, file_basename, dimension) {
        Ok(idx) => {
            println!("💾 [Tauri]: Pomyślnie wczytano indeks wektorowy Sparkle HNSW z dysku.");
            Arc::new(idx)
        }
        Err(err) => {
            println!(
                "📊 [Tauri]: Brak zapisanego indeksu lub błąd ({}). Tworzenie nowego...",
                err
            );
            let idx = Arc::new(SparkleVectorIndex::new(dimension, 10000));
            // Wektor adwersarialny dla Wolf Teeth
            let adv_id = 666;
            let mut adv_vec = vec![0.0f32; dimension];
            adv_vec[10] = 1.0;
            let _ = idx.insert(adv_id, &adv_vec);
            // Pierwszy zapis w celu zainicjowania plików bazowych
            let _ = idx.file_dump(&db_dir, file_basename);
            idx
        }
    };

    // 3. Konfiguracja i uruchomienie BlyskawicaEngine
    let adv_id = 666;
    let cooldown = Duration::from_secs(10);
    let surprise_threshold = 0.75;
    let isolation_ratio = 0.05;
    let adversarial_ids = vec![adv_id];
    let semantic_threshold = 0.35;

    let mut engine = BlyskawicaEngine::new(
        weights_path,
        cooldown,
        index.clone(),
        surprise_threshold,
        isolation_ratio,
        adversarial_ids,
        semantic_threshold,
    )
    .with_db(db_dir, file_basename.to_string());

    let (event_tx, mut event_rx) = mpsc::channel(100);
    engine.set_event_sender(event_tx);
    let tx = engine.get_sender();

    // Spawnowanie silnika
    let handle = tokio::spawn(async move {
        engine.run().await;
    });

    // Spawnowanie forwardera zdarzeń z Core do Tauri frontend
    let app_handle_clone = app_handle.clone();
    tokio::spawn(async move {
        while let Some(event) = event_rx.recv().await {
            if let blyskawica_core::state_manager::EngineEvent::Neurochemistry(ref ns) = event {
                if let Ok(mut inner) = app_handle_clone.state::<AppState>().0.lock() {
                    inner.current_neurochemistry = ns.clone();
                };
            }
            let _ = app_handle_clone.emit("engine-event", event);
        }
    });

    inner.tx = Some(tx);
    inner.engine_handle = Some(handle);
    Ok("Silnik Błyskawicy został pomyślnie uruchomiony.".to_string())
}

#[tauri::command]
async fn send_user_message(message: String, state: State<'_, AppState>) -> Result<String, String> {
    let tx = {
        let inner = state.0.lock().unwrap();
        inner
            .tx
            .clone()
            .ok_or_else(|| "Silnik nie jest uruchomiony.".to_string())?
    };

    tx.send(StateCommand::Prompt(message))
        .await
        .map_err(|e| format!("Błąd wysyłania wiadomości do silnika: {}", e))?;

    Ok("Wiadomość wysłana".to_string())
}

#[tauri::command]
async fn cancel_generation(state: State<'_, AppState>) -> Result<String, String> {
    let tx = {
        let inner = state.0.lock().unwrap();
        inner
            .tx
            .clone()
            .ok_or_else(|| "Silnik nie jest uruchomiony.".to_string())?
    };

    tx.send(StateCommand::Cancel)
        .await
        .map_err(|e| format!("Błąd wysyłania komendy anulowania: {}", e))?;

    Ok("Wysłano żądanie anulowania generowania.".to_string())
}

#[tauri::command]
async fn send_human_feedback(feedback: f32, state: State<'_, AppState>) -> Result<String, String> {
    let tx = {
        let inner = state.0.lock().unwrap();
        inner
            .tx
            .clone()
            .ok_or_else(|| "Silnik nie jest uruchomiony.".to_string())?
    };

    tx.send(StateCommand::Prompt(format!(
        "[R_HUMAN_FEEDBACK]: {}",
        feedback
    )))
    .await
    .map_err(|e| format!("Błąd wysyłania feedbacku: {}", e))?;

    Ok("Feedback wysłany".to_string())
}

#[tauri::command]
async fn trigger_neurogenesis(state: State<'_, AppState>) -> Result<String, String> {
    let tx = {
        let inner = state.0.lock().unwrap();
        inner
            .tx
            .clone()
            .ok_or_else(|| "Silnik nie jest uruchomiony.".to_string())?
    };

    tx.send(StateCommand::Neurogenesis)
        .await
        .map_err(|e| format!("Błąd wysyłania komendy neurogenezy: {}", e))?;

    Ok("Neurogeneza zainicjowana".to_string())
}

#[tauri::command]
fn set_permission_level(level: u8, state: State<'_, AppState>) -> Result<String, String> {
    if !(1..=3).contains(&level) {
        return Err("Nieprawidłowy poziom uprawnień (dozwolone 1, 2, 3)".to_string());
    }

    let current_level = state.0.lock().unwrap().permission_level;
    if permission_change_requires_confirmation(current_level, level) {
        let msg = if level == 2 {
            "Błyskawica prosi o dostęp do katalogu roboczego (Poziom 2). Czy chcesz zezwolić na odczyt i zapis plików workspace?"
        } else {
            "Błyskawica wymaga pełnego dostępu do systemu operacyjnego (Poziom 3). Czy chcesz zezwolić na tę operację?"
        };
        let title = "Ostrzeżenie bezpieczeństwa Błyskawica";
        if !show_confirm_dialog(msg, title) {
            return Err("Operacja anulowana przez użytkownika.".to_string());
        }
    }
    let mut inner = state.0.lock().unwrap();
    inner.permission_level = level;
    Ok(format!("Poziom uprawnień ustawiony na: Poziom {}", level))
}

#[tauri::command]
fn get_permission_report(state: State<'_, AppState>) -> Result<serde_json::Value, String> {
    let current_level = state.0.lock().unwrap().permission_level;
    Ok(serde_json::json!({
        "current_level": current_level,
        "levels": [
            {
                "level": 1,
                "label": "L1 — Sandbox",
                "scope": "Silnik w pamięci, czat lokalny i podgląd statusu bez dostępu do workspace, katalogu profilu lub systemu.",
            },
            {
                "level": 2,
                "label": "L2 — Workspace",
                "scope": "Pliki workspace, inwentaryzacja metadanych, narzędzia MCP i zgody na łączniki w bieżącej sesji.",
            },
            {
                "level": 3,
                "label": "L3 — System",
                "scope": "Sejf sekretów, telemetryka sprzętowa, katalogi modeli i jawnie potwierdzane akcje systemowe.",
            },
        ],
        "confirmation": "Awans do wyższego poziomu wymaga natywnego potwierdzenia. Na platformach bez takiego potwierdzenia operacja jest odmawiana.",
    }))
}

#[tauri::command]
fn get_connector_registry(state: State<'_, AppState>) -> Result<serde_json::Value, String> {
    let inner = state.0.lock().unwrap();
    Ok(connector_registry_json(
        inner.online_mode,
        &inner.connector_consents,
    ))
}

#[tauri::command]
fn set_online_mode(enabled: bool, state: State<'_, AppState>) -> Result<String, String> {
    if enabled {
        let permission_level = state.0.lock().unwrap().permission_level;
        require_permission_level(permission_level, 2, "włączenie trybu online")?;
        if !show_confirm_dialog(
            "Tryb online nie wysyła danych samodzielnie. Każdy łącznik wymaga jeszcze osobnej zgody w tej sesji. Czy chcesz go włączyć?",
            "Tryb online Błyskawica",
        ) {
            return Err("Operacja anulowana przez użytkownika.".to_string());
        }
    }

    let mut inner = state.0.lock().unwrap();
    inner.online_mode = enabled;
    if !enabled {
        inner.connector_consents.clear();
    }

    Ok(if enabled {
        "Tryb online włączony. Żaden łącznik nie ma jeszcze zgody.".to_string()
    } else {
        "Tryb offline włączony. Zgody łączników zostały wycofane.".to_string()
    })
}

#[tauri::command]
fn set_connector_consent(
    connector_id: String,
    consent: bool,
    state: State<'_, AppState>,
) -> Result<String, String> {
    let definition =
        connector_definition(&connector_id).ok_or_else(|| "Nieznany łącznik.".to_string())?;

    if !definition.can_be_enabled {
        return Err("Ten łącznik nie ma jeszcze zaimplementowanego transportu.".to_string());
    }

    if !consent {
        state
            .0
            .lock()
            .unwrap()
            .connector_consents
            .remove(&connector_id);
        return Ok(format!(
            "Zgoda dla łącznika '{}' została wycofana.",
            definition.label
        ));
    }

    let (permission_level, online_mode) = {
        let inner = state.0.lock().unwrap();
        (inner.permission_level, inner.online_mode)
    };
    require_permission_level(permission_level, 2, "udzielenie zgody łącznikowi")?;
    if !online_mode {
        return Err("Najpierw włącz tryb online.".to_string());
    }

    let confirmation = format!(
        "Łącznik: {}\nCel: {}\nZakres danych: {}\n\nCzy chcesz udzielić zgody wyłącznie na bieżącą sesję?",
        definition.label, definition.destination, definition.data_disclosure
    );
    if !show_confirm_dialog(&confirmation, "Zgoda na łącznik Błyskawica") {
        return Err("Operacja anulowana przez użytkownika.".to_string());
    }

    state
        .0
        .lock()
        .unwrap()
        .connector_consents
        .insert(connector_id);
    Ok(format!(
        "Udzielono zgody dla łącznika '{}'.",
        definition.label
    ))
}

fn fetch_fastapi_status() -> Option<serde_json::Value> {
    use std::io::{Read, Write};
    use std::net::TcpStream;
    use std::time::Duration;

    let ip_addr = "127.0.0.1:8000".parse().ok()?;
    let mut stream = TcpStream::connect_timeout(&ip_addr, Duration::from_millis(500)).ok()?;

    stream
        .set_read_timeout(Some(Duration::from_millis(500)))
        .ok()?;

    let request =
        "GET /api/system_status HTTP/1.1\r\nHost: 127.0.0.1:8000\r\nConnection: close\r\n\r\n";
    if stream.write_all(request.as_bytes()).is_err() {
        return None;
    }

    let mut response = Vec::new();
    if stream.read_to_end(&mut response).is_err() {
        return None;
    }

    let response_str = String::from_utf8_lossy(&response);
    let json_start = response_str.find("\r\n\r\n")?;
    let json_part = &response_str[json_start + 4..];

    serde_json::from_str(json_part).ok()
}

#[tauri::command]
async fn get_engine_status(state: State<'_, AppState>) -> Result<serde_json::Value, String> {
    let (
        is_running,
        permission_level,
        workspace_path_str,
        backend_alive,
        neuro,
        online_mode,
        sidecar_status_allowed,
    ) = {
        let mut inner = state.0.lock().unwrap();
        let is_running = inner.tx.is_some();
        let backend_alive = inner
            .backend_child
            .as_mut()
            .map(|c| c.try_wait().ok().flatten().is_none())
            .unwrap_or(false);
        (
            is_running,
            inner.permission_level,
            workspace_path_for_permission(inner.permission_level, &inner.workspace_path),
            backend_alive,
            inner.current_neurochemistry.clone(),
            inner.online_mode,
            connector_access_granted(
                inner.online_mode,
                &inner.connector_consents,
                LEGACY_SIDECAR_STATUS_CONNECTOR_ID,
            ),
        )
    };

    let mut response = serde_json::json!({
        "running": is_running,
        "permission_level": permission_level,
        "workspace_path": workspace_path_str,
        "neurochemistry": {
            "dopamine": neuro.dopamine,
            "serotonin": neuro.serotonin,
            "oxytocin": neuro.oxytocin,
            "gaba": neuro.gaba,
            "melatonin": neuro.melatonin,
            "cortisol": neuro.cortisol,
            "temperature": neuro.temperature
        },
        "backend_connected": backend_alive,
        "online_mode": online_mode,
        "sidecar_status_authorized": sidecar_status_allowed,
    });

    // Non-blocking fetch of sidecar status via spawn_blocking if backend is active
    if backend_alive && sidecar_status_allowed {
        if let Ok(Some(fastapi_status)) = tokio::task::spawn_blocking(fetch_fastapi_status).await {
            if let Some(metrics) = fastapi_status.get("cra_metrics") {
                response["neurochemistry"] = metrics.clone();
            }
        }
    }

    Ok(response)
}

#[tauri::command]
fn get_data_inventory(
    app: AppHandle,
    state: State<'_, AppState>,
) -> Result<Vec<serde_json::Value>, String> {
    let (permission_level, workspace_path) = {
        let inner = state.0.lock().unwrap();
        (inner.permission_level, inner.workspace_path.clone())
    };
    require_permission_level(permission_level, 2, "inwentaryzacja lokalnych danych")?;

    let app_data_dir = app_runtime_data_dir(&app);
    let mock_weights_path = app_data_dir.join("mock_weights.bin");
    let vector_index_dir = app_data_dir.join("db");
    let vault_dir = app_data_dir.join("identity_vault");
    let (workspace_size_bytes, workspace_size_is_complete) =
        storage_inventory_stats(&workspace_path);
    let (weights_size_bytes, weights_size_is_complete) =
        storage_inventory_stats(&mock_weights_path);
    let (index_size_bytes, index_size_is_complete) = storage_inventory_stats(&vector_index_dir);

    let app_storage_location = |path: &Path| {
        if permission_level >= 3 {
            path.to_string_lossy().to_string()
        } else {
            "Katalog danych aplikacji (pełna ścieżka wymaga poziomu 3)".to_string()
        }
    };

    let mut inventory = vec![
        serde_json::json!({
            "class": "R0",
            "label": "Odtwarzalne artefakty aplikacji",
            "location": app_storage_location(&mock_weights_path),
            "protection": "Nie zawiera danych użytkownika; generowane przez runtime.",
            "retention": "Brak osobnej komendy czyszczenia.",
            "size_bytes": weights_size_bytes,
            "size_is_complete": weights_size_is_complete,
        }),
        serde_json::json!({
            "class": "R1",
            "label": "Workspace i eksporty użytkownika",
            "location": workspace_path.to_string_lossy().to_string(),
            "protection": "Odczyt, zapis i eksport wymagają poziomu 2.",
            "retention": "Zarządzane przez użytkownika w workspace; brak polityki czasowej.",
            "size_bytes": workspace_size_bytes,
            "size_is_complete": workspace_size_is_complete,
        }),
        serde_json::json!({
            "class": "R2",
            "label": "Pamięć pochodna runtime",
            "location": app_storage_location(&vector_index_dir),
            "protection": "Trwałość i integralność bez potwierdzonego szyfrowania w spoczynku.",
            "retention": "Brak zdefiniowanej retencji i operacji usunięcia.",
            "size_bytes": index_size_bytes,
            "size_is_complete": index_size_is_complete,
        }),
        serde_json::json!({
            "class": "R3",
            "label": "Dane zgodności sidecara Python",
            "location": "Tylko opcjonalny sidecar deweloperski; runtime nie odczytuje jego zawartości.",
            "protection": "SQLite WAL zapewnia trwałość, nie pełne szyfrowanie.",
            "retention": "Brak potwierdzonego limitu retencji lub interfejsu usunięcia.",
            "size_bytes": serde_json::Value::Null,
            "size_is_complete": false,
        }),
    ];

    if permission_level >= 3 {
        let (vault_size_bytes, vault_size_is_complete) = storage_inventory_stats(&vault_dir);
        inventory.push(serde_json::json!({
            "class": "R4",
            "label": "Sejf sekretów",
            "location": vault_dir.to_string_lossy().to_string(),
            "protection": "Odczyt i zapis wymagają poziomu 3 oraz używają natywnej ochrony sekretu.",
            "retention": "Brak przenośnego kontraktu sejfu i operacji retencji.",
            "size_bytes": vault_size_bytes,
            "size_is_complete": vault_size_is_complete,
        }));
    } else {
        inventory.push(serde_json::json!({
            "class": "R4",
            "label": "Sejf sekretów",
            "location": "Ukryte; szczegóły wymagają poziomu 3.",
            "protection": "Odczyt i zapis wymagają poziomu 3.",
            "retention": "Brak przenośnego kontraktu sejfu i operacji retencji.",
            "size_bytes": serde_json::Value::Null,
            "size_is_complete": false,
        }));
    }

    Ok(inventory)
}

#[tauri::command]
fn clear_recreatable_runtime_artifacts(
    app: AppHandle,
    state: State<'_, AppState>,
) -> Result<String, String> {
    let permission_level = state.0.lock().unwrap().permission_level;
    require_permission_level(
        permission_level,
        2,
        "usunięcie odtwarzalnych artefaktów runtime",
    )?;

    let message = "Usunąć odtwarzalny plik mock_weights.bin z katalogu danych aplikacji? Nie zostaną usunięte dane workspace, pamięć, eksporty ani sekrety.";
    if !show_confirm_dialog(message, "Czyszczenie artefaktów SPARKLE") {
        return Err("Operacja anulowana przez użytkownika.".to_string());
    }

    let mock_weights_path = app_runtime_data_dir(&app).join("mock_weights.bin");
    if remove_regular_file(&mock_weights_path)? {
        Ok("Usunięto odtwarzalny artefakt runtime.".to_string())
    } else {
        Ok("Brak odtwarzalnego artefaktu do usunięcia.".to_string())
    }
}

#[cfg(target_os = "linux")]
fn path_to_file_uri(path: &Path) -> Result<String, String> {
    let canonical = path
        .canonicalize()
        .map_err(|e| format!("Błąd kanonikalizacji ścieżki tapety: {}", e))?;
    let path_str = canonical
        .to_str()
        .ok_or_else(|| "Ścieżka zawiera nieprawidłowe znaki UTF-8.".to_string())?;
    let mut encoded = String::from("file://");
    for byte in path_str.bytes() {
        match byte {
            b'a'..=b'z' | b'A'..=b'Z' | b'0'..=b'9' | b'-' | b'_' | b'.' | b'~' | b'/' => {
                encoded.push(byte as char);
            }
            _ => {
                encoded.push_str(&format!("%{:02X}", byte));
            }
        }
    }
    Ok(encoded)
}

#[tauri::command]
fn execute_system_action(
    action: String,
    args: serde_json::Value,
    state: State<'_, AppState>,
) -> Result<String, String> {
    let inner = state.0.lock().unwrap();
    if inner.permission_level < 3 {
        return Err(
            "Brak uprawnień. Ta operacja wymaga Poziomu 3 (Pełna Suwerenność).".to_string(),
        );
    }

    let msg = format!(
        "Błyskawica żąda wykonania akcji systemowej: '{}' z parametrami: {}.\nCzy wyrażasz zgodę?",
        action, args
    );
    let title = "Potwierdzenie Akcji Systemowej - Błyskawica";
    if !show_confirm_dialog(&msg, title) {
        return Err("Operacja anulowana przez użytkownika.".to_string());
    }

    match action.as_str() {
        "set_wallpaper" => {
            let path_str = args
                .get("path")
                .and_then(|v| v.as_str())
                .ok_or_else(|| "Brak ścieżki do obrazu".to_string())?;
            let path = PathBuf::from(path_str);
            if !path.exists() {
                return Err(format!("Plik obrazu nie istnieje: {:?}", path));
            }

            #[cfg(target_os = "windows")]
            {
                use std::os::windows::ffi::OsStrExt;

                let path_wide: Vec<u16> = path
                    .as_os_str()
                    .encode_wide()
                    .chain(std::iter::once(0))
                    .collect();

                unsafe {
                    #[link(name = "user32")]
                    extern "system" {
                        fn SystemParametersInfoW(
                            uiAction: u32,
                            uiParam: u32,
                            pvParam: *mut std::ffi::c_void,
                            fWinIni: u32,
                        ) -> i32;
                    }

                    let success = SystemParametersInfoW(
                        20, // SPI_SETDESKWALLPAPER
                        0,
                        path_wide.as_ptr() as *mut std::ffi::c_void,
                        3, // SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
                    );
                    if success != 0 {
                        Ok("Tapeta systemowa została pomyślnie zmieniona.".to_string())
                    } else {
                        Err("SystemParametersInfoW zwrócił status błędu.".to_string())
                    }
                }
            }
            #[cfg(target_os = "macos")]
            {
                let escaped_path = path
                    .to_string_lossy()
                    .replace('\\', "\\\\")
                    .replace('"', "\\\"");
                let script = format!(
                    "tell application \"Finder\" to set desktop picture to POSIX file \"{}\"",
                    escaped_path
                );
                match std::process::Command::new("osascript")
                    .arg("-e")
                    .arg(&script)
                    .status()
                {
                    Ok(status) if status.success() => {
                        Ok("Tapeta systemowa została pomyślnie zmieniona.".to_string())
                    }
                    Ok(_) => {
                        Err("Polecenie osascript zwróciło błąd przy zmianie tapety.".to_string())
                    }
                    Err(e) => Err(format!("Nie udało się uruchomić osascript: {}", e)),
                }
            }
            #[cfg(target_os = "linux")]
            {
                let uri = path_to_file_uri(&path)?;
                let desktop = std::env::var("XDG_CURRENT_DESKTOP")
                    .unwrap_or_default()
                    .to_uppercase();

                if desktop.contains("KDE") {
                    if let Ok(status) = std::process::Command::new("plasma-apply-wallpaperimage")
                        .arg(&path)
                        .status()
                    {
                        if status.success() {
                            return Ok(
                                "Tapeta systemowa została pomyślnie zmieniona (KDE Plasma)."
                                    .to_string(),
                            );
                        }
                    }
                }

                if let Ok(status) = std::process::Command::new("gsettings")
                    .args(["set", "org.gnome.desktop.background", "picture-uri", &uri])
                    .status()
                {
                    if status.success() {
                        let _ = std::process::Command::new("gsettings")
                            .args([
                                "set",
                                "org.gnome.desktop.background",
                                "picture-uri-dark",
                                &uri,
                            ])
                            .status();
                        return Ok(
                            "Tapeta systemowa została pomyślnie zmieniona (GNOME).".to_string()
                        );
                    }
                }
                if let Ok(status) = std::process::Command::new("feh")
                    .args(["--bg-scale", path.to_str().unwrap_or_default()])
                    .status()
                {
                    if status.success() {
                        return Ok(
                            "Tapeta systemowa została pomyślnie zmieniona (feh).".to_string()
                        );
                    }
                }
                Err("Nie znaleziono obsługiwanego menedżera pulpitu do zmiany tapety (sprawdź gsettings, plasma-apply-wallpaperimage lub feh).".to_string())
            }
            #[cfg(not(any(target_os = "windows", target_os = "macos", target_os = "linux")))]
            {
                Err(
                    "Ta operacja jest obsługiwana wyłącznie na systemach Windows, macOS i Linux."
                        .to_string(),
                )
            }
        }
        "create_folder" => {
            let path_str = args
                .get("path")
                .and_then(|v| v.as_str())
                .ok_or_else(|| "Brak ścieżki do folderu".to_string())?;
            let path = PathBuf::from(path_str);
            std::fs::create_dir_all(&path).map_err(|e| format!("Błąd tworzenia folderu: {}", e))?;
            Ok(format!("Folder {:?} został pomyślnie utworzony.", path))
        }
        _ => Err(format!("Nieznana akcja systemowa: {}", action)),
    }
}

#[tauri::command]
async fn read_workspace_file(path: String, state: State<'_, AppState>) -> Result<String, String> {
    let (permission_level, workspace_path) = {
        let inner = state.0.lock().unwrap();
        (inner.permission_level, inner.workspace_path.clone())
    };

    if permission_level < 2 {
        return Err(
            "Zablokowano. Odczyt plików wyłączony w trybie Sandbox (Poziom 1).".to_string(),
        );
    }

    let absolute_path = resolve_workspace_relative_path(&workspace_path, &path)?;

    let meta = tokio::fs::metadata(&absolute_path)
        .await
        .map_err(|e| format!("Błąd odczytu metadanych pliku: {}", e))?;

    // Bezpieczny limit rozmiaru pliku (max 10 MB) chroniący przed wyczerpaniem pamięci (OOM)
    if meta.len() > 10 * 1024 * 1024 {
        return Err(format!("Zablokowano: Plik przekracza bezpieczny limit rozmiaru edytora (10 MB). Rozmiar: {:.2} MB", meta.len() as f64 / (1024.0 * 1024.0)));
    }

    tokio::fs::read_to_string(&absolute_path)
        .await
        .map_err(|e| format!("Błąd odczytu pliku: {}", e))
}

#[tauri::command]
async fn write_workspace_file(
    path: String,
    content: String,
    state: State<'_, AppState>,
) -> Result<String, String> {
    let (permission_level, workspace_path) = {
        let inner = state.0.lock().unwrap();
        (inner.permission_level, inner.workspace_path.clone())
    };

    if permission_level < 2 {
        return Err("Zablokowano. Zapis plików wyłączony w trybie Sandbox (Poziom 1).".to_string());
    }

    let absolute_path = resolve_workspace_relative_path(&workspace_path, &path)?;

    if let Some(parent) = absolute_path.parent() {
        tokio::fs::create_dir_all(parent)
            .await
            .map_err(|e| format!("Błąd tworzenia katalogu pliku: {}", e))?;
    }

    let absolute_path = resolve_workspace_relative_path(&workspace_path, &path)?;

    tokio::fs::write(&absolute_path, content)
        .await
        .map_err(|e| format!("Błąd zapisu pliku: {}", e))?;
    Ok("Plik zapisany pomyślnie.".to_string())
}

#[tauri::command]
async fn list_workspace_files(
    subpath: Option<String>,
    state: State<'_, AppState>,
) -> Result<Vec<serde_json::Value>, String> {
    let (permission_level, workspace_path) = {
        let inner = state.0.lock().unwrap();
        (inner.permission_level, inner.workspace_path.clone())
    };

    if permission_level < 2 {
        return Err(
            "Zablokowano. Przeglądanie katalogów wyłączone w trybie Sandbox (Poziom 1)."
                .to_string(),
        );
    }

    let requested_subpath = subpath
        .as_deref()
        .map(str::trim)
        .filter(|path| !path.is_empty())
        .unwrap_or(".");
    let target_dir = resolve_workspace_relative_path(&workspace_path, requested_subpath)?;

    let mut files = Vec::new();
    if let Ok(mut entries) = tokio::fs::read_dir(&target_dir).await {
        while let Ok(Some(entry)) = entries.next_entry().await {
            let path = entry.path();
            let is_dir = path.is_dir();
            let name = path
                .file_name()
                .unwrap_or_default()
                .to_string_lossy()
                .into_owned();
            let rel_path = path
                .strip_prefix(&workspace_path)
                .unwrap_or(&path)
                .to_string_lossy()
                .replace("\\", "/");

            files.push(serde_json::json!({
                "name": name,
                "path": rel_path,
                "is_dir": is_dir,
            }));
        }
    }

    Ok(files)
}

#[tauri::command]
async fn export_logs(logs: String, state: State<'_, AppState>) -> Result<String, String> {
    let (permission_level, workspace_path) = {
        let inner = state.0.lock().unwrap();
        (inner.permission_level, inner.workspace_path.clone())
    };

    if permission_level < 2 {
        return Err(
            "Zablokowano. Eksport logów wyłączony w trybie Sandbox (Poziom 1).".to_string(),
        );
    }

    let log_path = workspace_path.join("sparkle_app_activity.log");

    let time_secs = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map(|d| d.as_secs())
        .unwrap_or(0);

    let formatted_logs = format!(
        "=== SPARKLE APP ACTIVITY LOGS ===\nExport Epoch: {}\n=================================\n{}\n",
        time_secs,
        logs
    );

    tokio::fs::write(&log_path, formatted_logs)
        .await
        .map_err(|e| format!("Błąd zapisu pliku logu: {}", e))?;

    Ok(format!(
        "Logi zostały pomyślnie wyeksportowane do: {:?}",
        log_path
    ))
}

#[tauri::command]
async fn vault_store_secret(
    app: tauri::AppHandle,
    key: String,
    value: String,
    state: State<'_, AppState>,
) -> Result<String, String> {
    let permission_level = state.0.lock().unwrap().permission_level;
    require_permission_level(permission_level, 3, "zapis do sejfu sekretów")?;

    if key.is_empty() {
        return Err("Klucz nie może być pusty".to_string());
    }
    let sanitized_key = key
        .chars()
        .filter(|c| c.is_alphanumeric() || *c == '_' || *c == '-')
        .collect::<String>();
    if sanitized_key.is_empty() {
        return Err("Klucz po sanityzacji nie może być pusty.".to_string());
    }
    let app_data_dir = app
        .path()
        .app_data_dir()
        .unwrap_or_else(|_| std::env::temp_dir().join("Blyskawica"));
    let vault_dir = app_data_dir.join("identity_vault");
    tokio::fs::create_dir_all(&vault_dir)
        .await
        .map_err(|e| format!("Błąd tworzenia katalogu vault: {}", e))?;

    let encrypted = blyskawica_core::native_security::protect_secret(value.as_bytes())
        .map_err(|e| format!("Błąd szyfrowania DPAPI: {}", e))?;

    let file_path = vault_dir.join(format!("{}.enc", sanitized_key));
    tokio::fs::write(&file_path, encrypted)
        .await
        .map_err(|e| format!("Błąd zapisu zaszyfrowanego klucza: {}", e))?;

    Ok(format!(
        "Sekret '{}' został bezpiecznie zaszyfrowany i zapisany w DPAPI Vault.",
        sanitized_key
    ))
}

#[tauri::command]
async fn vault_retrieve_secret(
    app: tauri::AppHandle,
    key: String,
    state: State<'_, AppState>,
) -> Result<String, String> {
    let permission_level = state.0.lock().unwrap().permission_level;
    require_permission_level(permission_level, 3, "odczyt z sejfu sekretów")?;

    if key.is_empty() {
        return Err("Klucz nie może być pusty".to_string());
    }
    let sanitized_key = key
        .chars()
        .filter(|c| c.is_alphanumeric() || *c == '_' || *c == '-')
        .collect::<String>();
    if sanitized_key.is_empty() {
        return Err("Klucz po sanityzacji nie może być pusty.".to_string());
    }
    let app_data_dir = app
        .path()
        .app_data_dir()
        .unwrap_or_else(|_| std::env::temp_dir().join("Blyskawica"));
    let file_path = app_data_dir
        .join("identity_vault")
        .join(format!("{}.enc", sanitized_key));

    if !file_path.exists() {
        return Err(format!(
            "Sekret '{}' nie istnieje w DPAPI Vault",
            sanitized_key
        ));
    }

    let encrypted = tokio::fs::read(&file_path)
        .await
        .map_err(|e| format!("Błąd odczytu pliku vault: {}", e))?;
    let decrypted_bytes = blyskawica_core::native_security::unprotect_secret(&encrypted)
        .map_err(|e| format!("Błąd deszyfrowania DPAPI: {}", e))?;

    let secret_str =
        String::from_utf8(decrypted_bytes).map_err(|e| format!("Błąd dekodowania UTF-8: {}", e))?;
    Ok(secret_str)
}

#[tauri::command]
async fn get_hardware_telemetry(state: State<'_, AppState>) -> Result<serde_json::Value, String> {
    let permission_level = state.0.lock().unwrap().permission_level;
    require_permission_level(permission_level, 3, "odczyt telemetryki sprzętowej")?;

    use sysinfo::System;
    let mut sys = System::new_all();
    sys.refresh_all();

    let cpu_count = sys.cpus().len();
    let global_cpu_usage = sys.global_cpu_info().cpu_usage();
    let total_memory_mb = sys.total_memory() / (1024 * 1024);
    let used_memory_mb = sys.used_memory() / (1024 * 1024);
    let free_memory_mb = sys.free_memory() / (1024 * 1024);

    let thermal_alert =
        global_cpu_usage > 90.0 || (used_memory_mb as f32 / total_memory_mb.max(1) as f32) > 0.92;

    Ok(serde_json::json!({
        "cpu_usage_percent": global_cpu_usage,
        "cpu_cores": cpu_count,
        "total_memory_mb": total_memory_mb,
        "used_memory_mb": used_memory_mb,
        "free_memory_mb": free_memory_mb,
        "memory_usage_percent": (used_memory_mb as f64 / total_memory_mb.max(1) as f64) * 100.0,
        "thermal_alert": thermal_alert,
        "platform": std::env::consts::OS,
    }))
}

#[tauri::command]
async fn scan_local_models(
    app: tauri::AppHandle,
    state: State<'_, AppState>,
) -> Result<serde_json::Value, String> {
    let permission_level = state.0.lock().unwrap().permission_level;
    // The scan includes model caches in the user's profile and returns paths,
    // therefore it is an explicit Full OS operation rather than a workspace read.
    require_permission_level(permission_level, 3, "skanowanie lokalnych katalogów modeli")?;

    let mut found_models = Vec::new();
    let mut scan_dirs = Vec::new();

    // 1. App local models dir
    let app_data_dir = app_runtime_data_dir(&app);
    scan_dirs.push(app_data_dir.join("models"));

    // 2. Current workspace and executable model dir
    scan_dirs.push(PathBuf::from("model"));
    scan_dirs.push(PathBuf::from("models"));
    if let Ok(exe) = std::env::current_exe() {
        if let Some(exe_dir) = exe.parent() {
            scan_dirs.push(exe_dir.join("model"));
            scan_dirs.push(exe_dir.join("models"));
        }
    }

    // 3. User profile caches (Ollama, LM Studio, HuggingFace)
    if let Ok(home) = std::env::var("USERPROFILE").or_else(|_| std::env::var("HOME")) {
        let home_path = PathBuf::from(home);
        scan_dirs.push(home_path.join(".ollama").join("models").join("blobs"));
        scan_dirs.push(home_path.join(".cache").join("lm-studio").join("models"));
        scan_dirs.push(home_path.join(".cache").join("huggingface").join("hub"));
    }

    for dir in scan_dirs {
        if !dir.exists() {
            continue;
        }
        if let Ok(entries) = std::fs::read_dir(&dir) {
            for entry in entries.flatten() {
                let path = entry.path();
                if path.is_file() {
                    let ext = path.extension().and_then(|e| e.to_str()).unwrap_or("");
                    if ext.eq_ignore_ascii_case("gguf") || ext.eq_ignore_ascii_case("bin") {
                        let size_bytes = entry.metadata().map(|m| m.len()).unwrap_or(0);
                        let size_mb = size_bytes / (1024 * 1024);
                        let filename = path
                            .file_name()
                            .and_then(|n| n.to_str())
                            .unwrap_or("unknown")
                            .to_string();

                        found_models.push(serde_json::json!({
                            "name": filename,
                            "path": path.to_string_lossy().to_string(),
                            "size_mb": size_mb,
                            "is_gguf": ext.eq_ignore_ascii_case("gguf"),
                        }));
                    }
                }
            }
        }
    }

    Ok(serde_json::json!({
        "models": found_models,
        "count": found_models.len()
    }))
}

#[tauri::command]
async fn execute_sandboxed_mcp_tool(
    tool_name: String,
    params: serde_json::Value,
    state: State<'_, AppState>,
) -> Result<serde_json::Value, String> {
    let (permission_level, workspace_path) = {
        let inner = state.0.lock().unwrap();
        (inner.permission_level, inner.workspace_path.clone())
    };

    // Zero-Trust Sandbox Audit
    let sandbox = blyskawica_core::zero_trust_mcp_sandbox::ZeroTrustMcpSandbox::new();
    let mock_neuro = blyskawica_core::neurochemistry::NeurochemicalState::default();
    let reality_anchor = if permission_level == 1 {
        0.5
    } else if permission_level == 2 {
        0.8
    } else {
        1.0
    };

    require_permission_level(permission_level, 2, "uruchomienie narzędzia MCP")?;

    if !sandbox.audit_tool_execution(&tool_name, reality_anchor, &mock_neuro) {
        return Err(format!("Zero-Trust VETO: Narzędzie '{}' zablokowane z powodu niewystarczających uprawnień lub wysokiego poziomu zagrożenia.", tool_name));
    }

    match tool_name.as_str() {
        "file_stats" => {
            let rel_path = params.get("path").and_then(|v| v.as_str()).unwrap_or(".");
            let target = resolve_workspace_relative_path(&workspace_path, rel_path)?;
            if !target.exists() {
                return Err(format!("Ścieżka nie istnieje: {:?}", target));
            }
            let meta = tokio::fs::metadata(&target)
                .await
                .map_err(|e| e.to_string())?;
            Ok(serde_json::json!({
                "is_dir": meta.is_dir(),
                "is_file": meta.is_file(),
                "size_bytes": meta.len(),
                "readonly": meta.permissions().readonly(),
            }))
        }
        "search_text" => {
            let query = params.get("query").and_then(|v| v.as_str()).unwrap_or("");
            let embedder = blyskawica_core::embedder::NativeEmbedder::default();
            let vector = embedder.embed(query);
            Ok(serde_json::json!({
                "query": query,
                "dimension": vector.len(),
                "vector_norm": 1.0,
                "status": "Vectorized successfully in offline sandbox"
            }))
        }
        _ => Err(format!(
            "Narzędzie '{}' nie jest zarejestrowane w rejestrze MCP Desktop Runner.",
            tool_name
        )),
    }
}

#[tauri::command]
fn stop_engine(state: State<'_, AppState>) -> Result<String, String> {
    let mut inner = state.0.lock().unwrap();
    inner.tx = None;
    if let Some(handle) = inner.engine_handle.take() {
        handle.abort();
    }
    Ok("Silnik został zatrzymany.".to_string())
}

#[tauri::command]
fn get_default_workspace(state: State<'_, AppState>) -> Result<String, String> {
    let inner = state.0.lock().unwrap();
    require_permission_level(
        inner.permission_level,
        2,
        "odczyt ścieżki katalogu roboczego",
    )?;
    Ok(inner.workspace_path.to_string_lossy().to_string())
}

#[tauri::command]
async fn run_native_expert_inference(
    input: Vec<f32>,
    app_handle: AppHandle,
) -> Result<Vec<f32>, String> {
    let weights_path = app_runtime_data_dir(&app_handle).join("mock_weights.bin");
    if !weights_path.exists() {
        return Err("Plik wag mock_weights.bin nie istnieje w danych aplikacji.".to_string());
    }
    let data = std::fs::read(&weights_path).map_err(|e| format!("Błąd odczytu wag: {}", e))?;
    let engine = blyskawica_core::local_inference::LocalInferenceEngine::load_cpu(&data)?;

    let mut padded_input = input;
    if padded_input.len() < 128 {
        padded_input.resize(128, 0.0);
    } else if padded_input.len() > 128 {
        padded_input.truncate(128);
    }

    engine.project(&padded_input)
}

#[tauri::command]
fn get_shadow_board(
    state: State<'_, AppState>,
) -> Result<Vec<blyskawica_core::shadow_forge::ToolShadow>, String> {
    let inner = state.0.lock().unwrap();
    Ok(inner.shadow_board.list_all_tools())
}

#[tauri::command]
fn forge_tool_on_anvil(
    tool_id: String,
    code: String,
    state: State<'_, AppState>,
) -> Result<String, String> {
    let mut inner = state.0.lock().unwrap();
    let checksum = blyskawica_core::shadow_forge::TheAnvil::temper_tool(
        &tool_id,
        &code,
        &serde_json::json!({}),
    )?;
    let tool_path = format!("tools/{}.py", tool_id);
    inner
        .shadow_board
        .hang_forged_tool(&tool_id, &tool_path, &checksum)?;
    Ok(format!(
        "Narzędzie '{}' pomyślnie wykute na kowadle i zawieszone na Tablicy Cieni (SHA-256: {})",
        tool_id, checksum
    ))
}

#[tauri::command]
fn aegis_get_security_posture(
    state: State<'_, AppState>,
) -> Result<blyskawica_core::aegis_sentinel::AegisPostureSummary, String> {
    let inner = state.0.lock().unwrap();
    Ok(inner.aegis.get_security_posture())
}

#[tauri::command]
fn aegis_neutralize_intrusion(
    event_id: String,
    action: String,
    state: State<'_, AppState>,
) -> Result<String, String> {
    let mut inner = state.0.lock().unwrap();
    let status = match action.as_str() {
        "allow" => blyskawica_core::aegis_sentinel::SentinelActionStatus::AllowedByArchitect,
        "terminate" => blyskawica_core::aegis_sentinel::SentinelActionStatus::Terminated,
        _ => blyskawica_core::aegis_sentinel::SentinelActionStatus::QuarantinedInJobObject,
    };
    inner.aegis.handle_architect_decision(&event_id, status)?;
    Ok(format!(
        "Decyzja Architekta dla '{}' została zastosowana ({})",
        event_id, action
    ))
}

#[tauri::command]
fn absorb_intent_seed(
    snippet: String,
    amplitude: f32,
    state: State<'_, AppState>,
) -> Result<String, String> {
    let mut inner = state.0.lock().unwrap();
    inner.tree.absorb_intent_seed(&snippet, amplitude);
    Ok("Zalążek intencji został wchłonięty przez korzenie Drzewa Kognicji".to_string())
}

#[tauri::command]
fn get_cognitive_tree_state(
    state: State<'_, AppState>,
) -> Result<blyskawica_core::cognitive_heartbeat::CognitiveTreeState, String> {
    let inner = state.0.lock().unwrap();
    Ok(inner.tree.get_tree_state())
}

#[tauri::command]
fn evaluate_cognitive_shield(
    prompt: String,
    state: State<'_, AppState>,
) -> Result<blyskawica_core::cognitive_shield::CognitiveShieldVerdict, String> {
    let inner = state.0.lock().unwrap();
    Ok(inner.cognitive_shield.evaluate_psyche(&prompt))
}

#[tauri::command]
fn aegis_evaluate_psyche_vad(
    text: String,
    state: State<'_, AppState>,
) -> Result<blyskawica_core::aegis_psyche_onnx::AegisPsycheRustReport, String> {
    let inner = state.0.lock().unwrap();
    Ok(inner.aegis_psyche.analyze(&text))
}

#[tauri::command]
fn quantum_get_state(
    state: State<'_, AppState>,
) -> Result<blyskawica_core::quantum_core::QuantumState, String> {
    let inner = state.0.lock().unwrap();
    Ok(inner.quantum_bridge.get_snapshot())
}

#[tauri::command]
fn quantum_trigger_tunneling(
    barrier_potential: f32,
    state: State<'_, AppState>,
) -> Result<serde_json::Value, String> {
    let inner = state.0.lock().unwrap();
    let mut mock_weights = vec![0.5f32; 128];
    let (gamma, count) = inner
        .quantum_bridge
        .execute_quantum_tunneling(&mut mock_weights, barrier_potential);
    Ok(serde_json::json!({
        "gamma": gamma,
        "tunneled_weights_count": count,
        "barrier_potential": barrier_potential,
        "status": "Quantum Tunneling Phase Barrier Broken"
    }))
}

#[tauri::command]
fn quantum_observe_collapse(
    query: String,
    state: State<'_, AppState>,
) -> Result<blyskawica_core::quantum_core::SuperpositionBranch, String> {
    let inner = state.0.lock().unwrap();
    Ok(inner.quantum_bridge.collapse_superposition(&query))
}

#[tauri::command]
fn quantum_get_cymatics_matrix(
    state: State<'_, AppState>,
) -> Result<blyskawica_core::quantum_core::CymaticsState, String> {
    let inner = state.0.lock().unwrap();
    Ok(inner.quantum_bridge.get_snapshot().cymatics)
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let builder = tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .manage(AppState(Mutex::new(AppStateInner {
            tx: None,
            permission_level: 1, // Sandbox by default; workspace access requires consent
            online_mode: false,
            connector_consents: BTreeSet::new(),
            workspace_path: PathBuf::from("."),
            backend_child: None,
            shell_secret: None,
            engine_handle: None,
            shadow_board: blyskawica_core::shadow_forge::ShadowBoard::new(),
            aegis: blyskawica_core::aegis_sentinel::AegisSentinel::new(),
            tree: blyskawica_core::cognitive_heartbeat::CognitiveHeartbeat::new(),
            cognitive_shield: blyskawica_core::cognitive_shield::CognitiveShield::new(vec![], 0.35),
            current_neurochemistry: blyskawica_core::neurochemistry::NeurochemicalState::default(),
            aegis_psyche: blyskawica_core::aegis_psyche_onnx::AegisPsycheRustEngine::new(),
            quantum_bridge: blyskawica_core::quantum_core::QuantumEntanglementBridge::new(),
        })))
        .invoke_handler(tauri::generate_handler![
            start_engine,
            stop_engine,
            send_user_message,
            cancel_generation,
            set_permission_level,
            get_permission_report,
            get_engine_status,
            get_connector_registry,
            set_online_mode,
            set_connector_consent,
            get_data_inventory,
            clear_recreatable_runtime_artifacts,
            execute_system_action,
            read_workspace_file,
            write_workspace_file,
            list_workspace_files,
            send_human_feedback,
            trigger_neurogenesis,
            export_logs,
            vault_store_secret,
            vault_retrieve_secret,
            get_hardware_telemetry,
            scan_local_models,
            execute_sandboxed_mcp_tool,
            get_default_workspace,
            run_native_expert_inference,
            get_shadow_board,
            forge_tool_on_anvil,
            aegis_get_security_posture,
            aegis_neutralize_intrusion,
            absorb_intent_seed,
            get_cognitive_tree_state,
            evaluate_cognitive_shield,
            aegis_evaluate_psyche_vad,
            quantum_get_state,
            quantum_trigger_tunneling,
            quantum_observe_collapse,
            quantum_get_cymatics_matrix
        ])
        .setup(|app| {
            let state = app.state::<AppState>();
            let mut inner = state.0.lock().unwrap();

            // Dynamic workspace resolution: use local repo dir if valid, else standalone bundle dir, else fallback to app_data_dir
            let app_data_dir = app.path().app_data_dir().unwrap_or_else(|_| std::env::temp_dir().join("Blyskawica"));
            let current_dir = std::env::current_dir().unwrap_or_else(|_| PathBuf::from("."));

            if current_dir.join("adaptiveneuralnetwork").exists() || current_dir.join("blyskawica_core").exists() {
                inner.workspace_path = current_dir;
            } else if current_dir.join("model").exists() {
                inner.workspace_path = current_dir;
            } else if let Ok(exe_path) = std::env::current_exe() {
                if let Some(exe_dir) = exe_path.parent() {
                    if exe_dir.join("model").exists() {
                        inner.workspace_path = exe_dir.to_path_buf();
                    } else if let Some(parent) = exe_dir.parent().and_then(|p| p.parent()) {
                        if parent.join("model").exists() {
                            inner.workspace_path = parent.to_path_buf();
                        } else {
                            let _ = std::fs::create_dir_all(&app_data_dir);
                            inner.workspace_path = app_data_dir.clone();
                        }
                    } else {
                        let _ = std::fs::create_dir_all(&app_data_dir);
                        inner.workspace_path = app_data_dir.clone();
                    }
                } else {
                    let _ = std::fs::create_dir_all(&app_data_dir);
                    inner.workspace_path = app_data_dir.clone();
                }
            } else {
                let _ = std::fs::create_dir_all(&app_data_dir);
                inner.workspace_path = app_data_dir.clone();
            }
            println!("📂 [SPARKLE App]: Working directory set to: {:?}", inner.workspace_path);

            let workspace = inner.workspace_path.clone();
            let app_dir = app.path().resource_dir().unwrap_or_default();

            let sidecar_name = if cfg!(target_os = "windows") {
                "blyskawica_backend-x86_64-pc-windows-msvc.exe"
            } else {
                "blyskawica_backend"
            };

            let mut sidecar_path = app_dir.join("bin").join(sidecar_name);
            if !sidecar_path.exists() && cfg!(target_os = "windows") {
                sidecar_path = app_dir.join("bin").join("blyskawica_backend.exe");
            }

            let sidecar_setting = std::env::var("SPARKLE_ENABLE_SIDECAR").ok();
            let enable_sidecar = sidecar_is_explicitly_enabled(sidecar_setting.as_deref());

            if enable_sidecar && sidecar_path.exists() {
                let now = std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap_or_default().as_nanos();
                let pid = std::process::id();
                let dynamic_secret = format!("sparkle-{:x}-{:x}", pid, now);
                inner.shell_secret = Some(dynamic_secret.clone());

                println!("🚀 [Tauri Setup]: Włączono zgodny sidecar deweloperski ({:?}). Uruchamianie w tle z dynamicznym sekretem...", sidecar_path);

                let mut cmd = std::process::Command::new(&sidecar_path);
                cmd.env("SPARKLE_WORKSPACE", &workspace)
                   .env("SPARKLE_SHELL_SECRET", &dynamic_secret)
                   .stdout(std::process::Stdio::null())
                    .stderr(std::process::Stdio::null());

                #[cfg(target_os = "windows")]
                {
                    use std::os::windows::process::CommandExt;
                    cmd.creation_flags(0x08000000); // CREATE_NO_WINDOW
                }

                match cmd.spawn() {
                    Ok(child) => {
                        #[cfg(target_os = "windows")]
                        {
                            use std::os::windows::io::AsRawHandle;
                            if let Ok(job) = blyskawica_core::native_security::create_kill_on_close_job() {
                                let child_handle = child.as_raw_handle();
                                if blyskawica_core::native_security::assign_process_to_job(job, child_handle as *mut _).is_ok() {
                                    println!("🛡️ [Windows Job Object]: Sidecar pomyślnie przypisany do Job Object (JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE) – ochrona przed procesami zombie aktywna.");
                                }
                            }
                        }
                        inner.backend_child = Some(child);
                        println!("✓ [Tauri Setup]: Sidecar deweloperski uruchomiony pomyślnie.");
                    }
                    Err(err) => {
                        eprintln!("❌ [Tauri Setup Błąd]: Nie udało się uruchomić Sidecar: {}", err);
                    }
                }
            } else if enable_sidecar {
                println!("ℹ️ [Tauri Setup]: Sidecar deweloperski został włączony, ale nie znaleziono jego pliku wykonywalnego. Działanie w samodzielnym trybie Rust/Tauri.");
            } else {
                println!("ℹ️ [Tauri Setup]: Sidecar Python jest wyłączony. Działanie w samodzielnym trybie Rust/Tauri.");
            }

            Ok(())
        });

    let app = builder
        .build(tauri::generate_context!())
        .expect("error while building tauri application");

    app.run(move |app_handle, event| {
        if let tauri::RunEvent::Exit = event {
            let state = app_handle.state::<AppState>();
            let mut inner = state.0.lock().unwrap();
            if let Some(handle) = inner.engine_handle.take() {
                println!("🛑 [Tauri Exit]: Zatrzymywanie zadania silnika Rust...");
                handle.abort();
            }
            if let Some(mut child) = inner.backend_child.take() {
                println!("🛑 [Tauri Exit]: Graceful shutdown — wysyłanie sygnału zamykania...");
                // Attempt graceful shutdown: wait up to 3 seconds for clean exit
                let mut exited = false;
                for _ in 0..30 {
                    match child.try_wait() {
                        Ok(Some(_status)) => {
                            exited = true;
                            break;
                        }
                        Ok(None) => {
                            std::thread::sleep(std::time::Duration::from_millis(100));
                        }
                        Err(_) => break,
                    }
                }
                if !exited {
                    println!("🛑 [Tauri Exit]: Sidecar nie zakończył się w 3s — wymuszanie zamknięcia...");
                    let _ = child.kill();
                }
                // Reap zombie process to prevent resource leak
                let _ = child.wait();
                println!("✓ [Tauri Exit]: Proces sidecar zakończony i wyczyszczony.");
            }
        }
    });
}

#[cfg(test)]
mod tests {
    #[cfg(not(target_os = "windows"))]
    use super::show_confirm_dialog;
    use super::{
        permission_change_requires_confirmation, remove_regular_file, require_permission_level,
        resolve_workspace_relative_path, sidecar_is_explicitly_enabled, storage_inventory_stats,
        workspace_path_for_permission,
    };
    use std::fs;
    use std::path::Path;
    use std::time::{SystemTime, UNIX_EPOCH};

    #[test]
    fn workspace_resolver_allows_new_files_and_rejects_escape_attempts() {
        let unique = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .expect("system clock should be after the Unix epoch")
            .as_nanos();
        let workspace =
            std::env::temp_dir().join(format!("blyskawica-workspace-path-test-{unique}"));
        fs::create_dir_all(&workspace).expect("test workspace should be created");
        let allowed = workspace.join("allowed.txt");
        fs::write(&allowed, "ok").expect("test file should be created");

        assert_eq!(
            resolve_workspace_relative_path(&workspace, "allowed.txt")
                .expect("relative path should resolve"),
            allowed
        );
        assert_eq!(
            resolve_workspace_relative_path(&workspace, "drafts/new-note.md")
                .expect("new nested file should resolve"),
            workspace.join("drafts").join("new-note.md")
        );
        assert!(resolve_workspace_relative_path(&workspace, "../outside.txt").is_err());
        assert!(resolve_workspace_relative_path(
            &workspace,
            allowed.to_str().expect("UTF-8 test path")
        )
        .is_err());

        fs::remove_dir_all(&workspace).expect("test workspace should be removed");
    }

    #[test]
    fn privileged_operations_require_the_declared_level() {
        assert!(require_permission_level(1, 2, "MCP").is_err());
        assert!(require_permission_level(2, 3, "vault").is_err());
        assert!(require_permission_level(3, 3, "vault").is_ok());
    }

    #[test]
    fn permission_escalation_requires_confirmation_but_reduction_does_not() {
        assert!(permission_change_requires_confirmation(1, 2));
        assert!(permission_change_requires_confirmation(2, 3));
        assert!(!permission_change_requires_confirmation(2, 2));
        assert!(!permission_change_requires_confirmation(3, 1));
    }

    #[cfg(not(target_os = "windows"))]
    #[test]
    fn non_windows_confirmation_fails_closed() {
        let orig_headless = std::env::var_os("BLY_HEADLESS");
        unsafe {
            std::env::set_var("BLY_HEADLESS", "1");
        }
        assert!(!show_confirm_dialog(
            "Podniesienie uprawnien",
            "Blyskawica Security"
        ));
        unsafe {
            if let Some(val) = orig_headless {
                std::env::set_var("BLY_HEADLESS", val);
            } else {
                std::env::remove_var("BLY_HEADLESS");
            }
        }
    }

    #[test]
    fn workspace_path_is_hidden_in_sandbox() {
        let workspace = Path::new("C:/Users/Example/private-workspace");
        assert_eq!(workspace_path_for_permission(1, workspace), None);
        assert_eq!(
            workspace_path_for_permission(2, workspace),
            Some("C:/Users/Example/private-workspace".to_string())
        );
    }

    #[test]
    fn sidecar_requires_explicit_opt_in() {
        assert!(!sidecar_is_explicitly_enabled(None));
        assert!(!sidecar_is_explicitly_enabled(Some("false")));
        assert!(!sidecar_is_explicitly_enabled(Some("enabled")));
        assert!(sidecar_is_explicitly_enabled(Some("1")));
        assert!(sidecar_is_explicitly_enabled(Some(" true ")));
    }

    #[test]
    fn storage_inventory_reports_file_size() {
        let unique = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .expect("system clock should be after the Unix epoch")
            .as_nanos();
        let directory = std::env::temp_dir().join(format!("blyskawica-inventory-test-{unique}"));
        fs::create_dir_all(&directory).expect("test directory should be created");
        let file_path = directory.join("artifact.bin");
        fs::write(&file_path, [1_u8, 2, 3, 4]).expect("test file should be created");

        assert_eq!(storage_inventory_stats(&file_path), (4, true));

        fs::remove_dir_all(&directory).expect("test directory should be removed");
    }

    #[test]
    fn recreatable_artifact_cleanup_removes_only_regular_files() {
        let unique = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .expect("system clock should be after the Unix epoch")
            .as_nanos();
        let directory = std::env::temp_dir().join(format!("blyskawica-cleanup-test-{unique}"));
        fs::create_dir_all(&directory).expect("test directory should be created");
        let file_path = directory.join("mock_weights.bin");
        fs::write(&file_path, [1_u8]).expect("test file should be created");

        assert!(remove_regular_file(&file_path).expect("regular file should be removable"));
        assert!(!remove_regular_file(&file_path).expect("missing file should be harmless"));
        assert!(remove_regular_file(&directory).is_err());

        fs::remove_dir_all(&directory).expect("test directory should be removed");
    }
}
