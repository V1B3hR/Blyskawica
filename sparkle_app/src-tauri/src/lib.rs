use std::sync::Mutex;
use std::path::{Path, PathBuf};
use std::time::Duration;
use std::sync::Arc;
use tokio::sync::mpsc;
use tauri::{AppHandle, State, Emitter, Manager};
use blyskawica_core::state_manager::{BlyskawicaEngine, StateCommand};
use blyskawica_core::vector_index::SparkleVectorIndex;

pub struct AppStateInner {
    tx: Option<mpsc::Sender<StateCommand>>,
    permission_level: u8, // 1: Sandbox, 2: Workspace, 3: Full OS
    workspace_path: PathBuf,
    backend_child: Option<std::process::Child>,
}

pub struct AppState(pub Mutex<AppStateInner>);

fn is_inside_workspace(path: &Path, workspace: &Path) -> bool {
    let workspace_canon = match workspace.canonicalize() {
        Ok(w) => w,
        Err(_) => return false,
    };
    
    // Canonicalize path parent if the path itself does not exist yet (e.g. creating new file)
    let path_canon = if path.exists() {
        match path.canonicalize() {
            Ok(p) => p,
            Err(_) => return false,
        }
    } else {
        match path.parent() {
            Some(parent) if parent.exists() => {
                match parent.canonicalize() {
                    Ok(p_canon) => p_canon.join(path.file_name().unwrap_or_default()),
                    Err(_) => return false,
                }
            }
            _ => return false,
        }
    };
    
    path_canon.starts_with(workspace_canon)
}

fn is_restricted_system_path(path: &Path) -> bool {
    let path_str = match path.canonicalize() {
        Ok(p) => p.to_string_lossy().to_lowercase().replace("\\", "/"),
        Err(_) => path.to_string_lossy().to_lowercase().replace("\\", "/"),
    };
    
    let restricted_directories = [
        "c:/windows",
        "c:/program files",
        "c:/program files (x86)",
        "c:/users/default",
        "c:/users/all users",
    ];
    
    restricted_directories.iter().any(|rdir| path_str.starts_with(rdir))
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

#[cfg(not(target_os = "windows"))]
fn show_confirm_dialog(_message: &str, _title: &str) -> bool {
    true
}

#[tauri::command]
async fn start_engine(app_handle: AppHandle, state: State<'_, AppState>) -> Result<String, String> {
    let mut inner = state.0.lock().unwrap();
    if inner.tx.is_some() {
        return Ok("Silnik jest już uruchomiony.".to_string());
    }

    let workspace_path = inner.workspace_path.clone();
    let weights_path = workspace_path.join("mock_weights.bin");

    // 1. Generowanie mock_weights.bin jeśli nie istnieje
    if !weights_path.exists() {
        use std::fs::File;
        use std::io::Write;
        let mut file = File::create(&weights_path).map_err(|e| format!("Błąd tworzenia mock_weights.bin: {}", e))?;
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
        file.write_all(&byte_data).map_err(|e| format!("Błąd zapisu mock_weights.bin: {}", e))?;
    }

    // 2. Inicjalizacja HNSW z wczytywaniem i zapisem na dysku
    let dimension = 128;
    let app_data_dir = app_handle.path().app_data_dir().unwrap_or_else(|_| {
        std::env::temp_dir().join("Blyskawica")
    });
    let db_dir = app_data_dir.join("db");
    let file_basename = "sparkle_vectors";

    let index = match SparkleVectorIndex::load_hnsw(&db_dir, file_basename, dimension) {
        Ok(idx) => {
            println!("💾 [Tauri]: Pomyślnie wczytano indeks wektorowy Sparkle HNSW z dysku.");
            Arc::new(idx)
        }
        Err(err) => {
            println!("📊 [Tauri]: Brak zapisanego indeksu lub błąd ({}). Tworzenie nowego...", err);
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
    ).with_db(db_dir, file_basename.to_string());

    let (event_tx, mut event_rx) = mpsc::channel(100);
    engine.set_event_sender(event_tx);
    let tx = engine.get_sender();

    // Spawnowanie silnika
    tokio::spawn(async move {
        engine.run().await;
    });

    // Spawnowanie forwardera zdarzeń z Core do Tauri frontend
    let app_handle_clone = app_handle.clone();
    tokio::spawn(async move {
        while let Some(event) = event_rx.recv().await {
            let _ = app_handle_clone.emit("engine-event", event);
        }
    });

    inner.tx = Some(tx);
    Ok("Silnik Błyskawicy został pomyślnie uruchomiony.".to_string())
}

#[tauri::command]
async fn send_user_message(message: String, state: State<'_, AppState>) -> Result<String, String> {
    let tx = {
        let inner = state.0.lock().unwrap();
        inner.tx.clone().ok_or_else(|| "Silnik nie jest uruchomiony.".to_string())?
    };
    
    tx.send(StateCommand::Prompt(message))
        .await
        .map_err(|e| format!("Błąd wysyłania wiadomości do silnika: {}", e))?;
    
    Ok("Wiadomość wysłana".to_string())
}

#[tauri::command]
async fn send_human_feedback(feedback: f32, state: State<'_, AppState>) -> Result<String, String> {
    let tx = {
        let inner = state.0.lock().unwrap();
        inner.tx.clone().ok_or_else(|| "Silnik nie jest uruchomiony.".to_string())?
    };
    
    tx.send(StateCommand::Prompt(format!("[R_HUMAN_FEEDBACK]: {}", feedback)))
        .await
        .map_err(|e| format!("Błąd wysyłania feedbacku: {}", e))?;
    
    Ok("Feedback wysłany".to_string())
}

#[tauri::command]
async fn trigger_neurogenesis(state: State<'_, AppState>) -> Result<String, String> {
    let tx = {
        let inner = state.0.lock().unwrap();
        inner.tx.clone().ok_or_else(|| "Silnik nie jest uruchomiony.".to_string())?
    };
    
    tx.send(StateCommand::Neurogenesis)
        .await
        .map_err(|e| format!("Błąd wysyłania komendy neurogenezy: {}", e))?;
    
    Ok("Neurogeneza zainicjowana".to_string())
}

#[tauri::command]
fn set_permission_level(level: u8, state: State<'_, AppState>) -> Result<String, String> {
    if level < 1 || level > 3 {
        return Err("Nieprawidłowy poziom uprawnień (dozwolone 1, 2, 3)".to_string());
    }
    if level == 3 {
        let msg = "Błyskawica wymaga pełnego dostępu do systemu operacyjnego (Poziom 3). Czy chcesz zezwolić na tę operację?";
        let title = "Ostrzeżenie bezpieczeństwa Błyskawica";
        if !show_confirm_dialog(msg, title) {
            return Err("Operacja anulowana przez użytkownika.".to_string());
        }
    }
    let mut inner = state.0.lock().unwrap();
    inner.permission_level = level;
    Ok(format!("Poziom uprawnień ustawiony na: Poziom {}", level))
}

fn fetch_fastapi_status() -> Option<serde_json::Value> {
    use std::net::TcpStream;
    use std::io::{Write, Read};
    use std::time::Duration;
    
    let ip_addr = "127.0.0.1:8000".parse().ok()?;
    let mut stream = TcpStream::connect_timeout(
        &ip_addr,
        Duration::from_millis(500)
    ).ok()?;
    
    stream.set_read_timeout(Some(Duration::from_millis(500))).ok()?;
    
    let request = "GET /api/system_status HTTP/1.1\r\nHost: 127.0.0.1:8000\r\nConnection: close\r\n\r\n";
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
    let (is_running, permission_level, workspace_path_str, backend_alive) = {
        let mut inner = state.0.lock().unwrap();
        let is_running = inner.tx.is_some();
        let backend_alive = inner.backend_child.as_mut()
            .map(|c| c.try_wait().ok().flatten().is_none())
            .unwrap_or(false);
        (is_running, inner.permission_level, inner.workspace_path.to_string_lossy().to_string(), backend_alive)
    };

    let mut response = serde_json::json!({
        "running": is_running,
        "permission_level": permission_level,
        "workspace_path": workspace_path_str,
        "neurochemistry": serde_json::Value::Null,
        "backend_connected": backend_alive,
    });
    
    // Non-blocking fetch of sidecar status via spawn_blocking
    if backend_alive {
        if let Ok(Some(fastapi_status)) = tokio::task::spawn_blocking(fetch_fastapi_status).await {
            if let Some(metrics) = fastapi_status.get("cra_metrics") {
                response["neurochemistry"] = metrics.clone();
            }
        }
    }
    
    Ok(response)
}

#[tauri::command]
fn execute_system_action(action: String, args: serde_json::Value, state: State<'_, AppState>) -> Result<String, String> {
    let inner = state.0.lock().unwrap();
    if inner.permission_level < 3 {
        return Err("Brak uprawnień. Ta operacja wymaga Poziomu 3 (Pełna Suwerenność).".to_string());
    }

    let msg = format!("Błyskawica żąda wykonania akcji systemowej: '{}' z parametrami: {}.\nCzy wyrażasz zgodę?", action, args);
    let title = "Potwierdzenie Akcji Systemowej - Błyskawica";
    if !show_confirm_dialog(&msg, title) {
        return Err("Operacja anulowana przez użytkownika.".to_string());
    }

    match action.as_str() {
        "set_wallpaper" => {
            let path_str = args.get("path")
                .and_then(|v| v.as_str())
                .ok_or_else(|| "Brak ścieżki do obrazu".to_string())?;
            let path = PathBuf::from(path_str);
            if !path.exists() {
                return Err(format!("Plik obrazu nie istnieje: {:?}", path));
            }
            
            #[cfg(target_os = "windows")]
            {
                use std::os::windows::ffi::OsStrExt;
                
                let path_wide: Vec<u16> = path.as_os_str()
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
                        3,  // SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
                    );
                    if success != 0 {
                        Ok("Tapeta systemowa została pomyślnie zmieniona.".to_string())
                    } else {
                        Err("SystemParametersInfoW zwrócił status błędu.".to_string())
                    }
                }
            }
            #[cfg(not(target_os = "windows"))]
            {
                Err("Ta operacja jest obsługiwana wyłącznie na systemie Windows.".to_string())
            }
        }
        "create_folder" => {
            let path_str = args.get("path")
                .and_then(|v| v.as_str())
                .ok_or_else(|| "Brak ścieżki do folderu".to_string())?;
            let path = PathBuf::from(path_str);
            std::fs::create_dir_all(&path)
                .map_err(|e| format!("Błąd tworzenia folderu: {}", e))?;
            Ok(format!("Folder {:?} został pomyślnie utworzony.", path))
        }
        _ => Err(format!("Nieznana akcja systemowa: {}", action))
    }
}

#[tauri::command]
async fn read_workspace_file(path: String, state: State<'_, AppState>) -> Result<String, String> {
    let (permission_level, workspace_path) = {
        let inner = state.0.lock().unwrap();
        (inner.permission_level, inner.workspace_path.clone())
    };

    if permission_level < 2 {
        return Err("Zablokowano. Odczyt plików wyłączony w trybie Sandbox (Poziom 1).".to_string());
    }

    let absolute_path = PathBuf::from(&path);
    if is_restricted_system_path(&absolute_path) {
        return Err("Zablokowano. Odczyt z katalogu systemowego jest zabroniony.".to_string());
    }

    if permission_level == 2 && !is_inside_workspace(&absolute_path, &workspace_path) {
        return Err("Zablokowano. W Poziomie 2 dozwolony jest dostęp wyłącznie do katalogu roboczego.".to_string());
    }

    tokio::fs::read_to_string(&absolute_path)
        .await
        .map_err(|e| format!("Błąd odczytu pliku: {}", e))
}

#[tauri::command]
async fn write_workspace_file(path: String, content: String, state: State<'_, AppState>) -> Result<String, String> {
    let (permission_level, workspace_path) = {
        let inner = state.0.lock().unwrap();
        (inner.permission_level, inner.workspace_path.clone())
    };

    if permission_level < 2 {
        return Err("Zablokowano. Zapis plików wyłączony w trybie Sandbox (Poziom 1).".to_string());
    }

    let absolute_path = PathBuf::from(&path);
    if is_restricted_system_path(&absolute_path) {
        return Err("Zablokowano. Zapis w katalogu systemowym jest zabroniony.".to_string());
    }

    if permission_level == 2 && !is_inside_workspace(&absolute_path, &workspace_path) {
        return Err("Zablokowano. W Poziomie 2 zapis plików dozwolony jest wyłącznie w katalogu roboczym.".to_string());
    }

    if let Some(parent) = absolute_path.parent() {
        let _ = tokio::fs::create_dir_all(parent).await;
    }

    tokio::fs::write(&absolute_path, content)
        .await
        .map_err(|e| format!("Błąd zapisu pliku: {}", e))?;
    Ok("Plik zapisany pomyślnie.".to_string())
}

#[tauri::command]
async fn list_workspace_files(state: State<'_, AppState>) -> Result<Vec<serde_json::Value>, String> {
    let (permission_level, workspace_path) = {
        let inner = state.0.lock().unwrap();
        (inner.permission_level, inner.workspace_path.clone())
    };

    if permission_level < 2 {
        return Err("Zablokowano. Przeglądanie katalogów wyłączone w trybie Sandbox (Poziom 1).".to_string());
    }

    let mut files = Vec::new();
    if let Ok(mut entries) = tokio::fs::read_dir(&workspace_path).await {
        while let Ok(Some(entry)) = entries.next_entry().await {
            let path = entry.path();
            let is_dir = path.is_dir();
            let name = path.file_name().unwrap_or_default().to_string_lossy().into_owned();
            let abs_path = path.to_string_lossy().into_owned();

            files.push(serde_json::json!({
                "name": name,
                "path": abs_path,
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
        return Err("Zablokowano. Eksport logów wyłączony w trybie Sandbox (Poziom 1).".to_string());
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

    Ok(format!("Logi zostały pomyślnie wyeksportowane do: {:?}", log_path))
}

#[tauri::command]
async fn vault_store_secret(app: tauri::AppHandle, key: String, value: String) -> Result<String, String> {
    if key.is_empty() {
        return Err("Klucz nie może być pusty".to_string());
    }
    let sanitized_key = key.chars().filter(|c| c.is_alphanumeric() || *c == '_' || *c == '-').collect::<String>();
    let app_data_dir = app.path().app_data_dir().unwrap_or_else(|_| std::env::temp_dir().join("Blyskawica"));
    let vault_dir = app_data_dir.join("identity_vault");
    tokio::fs::create_dir_all(&vault_dir).await.map_err(|e| format!("Błąd tworzenia katalogu vault: {}", e))?;

    let encrypted = blyskawica_core::native_security::protect_secret(value.as_bytes())
        .map_err(|e| format!("Błąd szyfrowania DPAPI: {}", e))?;

    let file_path = vault_dir.join(format!("{}.enc", sanitized_key));
    tokio::fs::write(&file_path, encrypted).await.map_err(|e| format!("Błąd zapisu zaszyfrowanego klucza: {}", e))?;

    Ok(format!("Sekret '{}' został bezpiecznie zaszyfrowany i zapisany w DPAPI Vault.", sanitized_key))
}

#[tauri::command]
async fn vault_retrieve_secret(app: tauri::AppHandle, key: String) -> Result<String, String> {
    if key.is_empty() {
        return Err("Klucz nie może być pusty".to_string());
    }
    let sanitized_key = key.chars().filter(|c| c.is_alphanumeric() || *c == '_' || *c == '-').collect::<String>();
    let app_data_dir = app.path().app_data_dir().unwrap_or_else(|_| std::env::temp_dir().join("Blyskawica"));
    let file_path = app_data_dir.join("identity_vault").join(format!("{}.enc", sanitized_key));

    if !file_path.exists() {
        return Err(format!("Sekret '{}' nie istnieje w DPAPI Vault", sanitized_key));
    }

    let encrypted = tokio::fs::read(&file_path).await.map_err(|e| format!("Błąd odczytu pliku vault: {}", e))?;
    let decrypted_bytes = blyskawica_core::native_security::unprotect_secret(&encrypted)
        .map_err(|e| format!("Błąd deszyfrowania DPAPI: {}", e))?;

    let secret_str = String::from_utf8(decrypted_bytes).map_err(|e| format!("Błąd dekodowania UTF-8: {}", e))?;
    Ok(secret_str)
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let builder = tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .manage(AppState(Mutex::new(AppStateInner {
            tx: None,
            permission_level: 2, // Standard Workspace by default
            workspace_path: PathBuf::from("."),
            backend_child: None,
        })))
        .invoke_handler(tauri::generate_handler![
            start_engine,
            send_user_message,
            set_permission_level,
            get_engine_status,
            execute_system_action,
            read_workspace_file,
            write_workspace_file,
            list_workspace_files,
            send_human_feedback,
            trigger_neurogenesis,
            export_logs,
            vault_store_secret,
            vault_retrieve_secret
        ])
        .setup(|app| {
            let state = app.state::<AppState>();
            let mut inner = state.0.lock().unwrap();
            
            // Dynamic workspace resolution: use local repo dir if valid, else fallback to app_data_dir
            let app_data_dir = app.path().app_data_dir().unwrap_or_else(|_| std::env::temp_dir().join("Blyskawica"));
            let current_dir = std::env::current_dir().unwrap_or_else(|_| PathBuf::from("."));
            
            if current_dir.join("adaptiveneuralnetwork").exists() || current_dir.join("blyskawica_core").exists() {
                inner.workspace_path = current_dir;
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
            
            if sidecar_path.exists() {
                println!("🚀 [Tauri Setup]: Wykryto Sidecar backend ({:?}). Uruchamianie w tle...", sidecar_path);
                
                let mut cmd = std::process::Command::new(&sidecar_path);
                cmd.env("SPARKLE_WORKSPACE", &workspace)
                   .stdout(std::process::Stdio::null())
                   .stderr(std::process::Stdio::null());
                
                #[cfg(target_os = "windows")]
                {
                    use std::os::windows::process::CommandExt;
                    cmd.creation_flags(0x08000000); // CREATE_NO_WINDOW
                }
                
                match cmd.spawn() {
                    Ok(child) => {
                        inner.backend_child = Some(child);
                        println!("✓ [Tauri Setup]: Sidecar backend uruchomiony pomyślnie.");
                    }
                    Err(err) => {
                        eprintln!("❌ [Tauri Setup Błąd]: Nie udało się uruchomić Sidecar: {}", err);
                    }
                }
            } else {
                println!("ℹ️ [Tauri Setup]: Brak pliku wykonywalnego Sidecar backend. Działanie w czystym trybie Wbudowanym (Native Offline Embedded Core).");
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
