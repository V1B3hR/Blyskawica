# Security Hardening Plan for Błyskawica V8/V9 Hybrid System

> **Role**: Lead Systems Architect  
> **Target System**: Błyskawica V8 / V9 (FastAPI + Rust Tauri WebView Hybrid)  
> **Status**: Confidential — Institutional Review Ready (UK AISI / Government Audit)  
> **Date**: 2026-05-26  

---

## 1. Executive Summary

Błyskawica V8/V9 represents a highly sophisticated, biologically-inspired cognitive simulation network. However, its hybrid integration pattern (where a Python FastAPI server runs locally to coordinate PyTorch/ONNX models while a Rust Tauri WebView shell serves as the desktop environment) exposes a significant local attack surface. 

This security hardening plan identifies architectural flaws in the privilege escalation mechanism, Tauri IPC routing, Web API design, and local persistence layers. Remediating these issues is a prerequisite for presenting this technology to security-focused government agencies such as the UK Artificial Intelligence Security Institute (AISI) or the Polish government.

---

## 2. Threat Model & Attack Surface

The system operates locally on Windows 11 with three declared permission levels:
1. **Sandbox (Level 1)**: In-memory simulation only, no local disk write operations.
2. **Workspace (Level 2)**: Disk operations restricted to the project root (`c:\Projekty\Blyskawica_V8`).
3. **Full OS Control (Level 3)**: Unrestricted OS integration (changing wallpapers, directory creation, shell execution).

The primary threat vectors include:
- **Tauri IPC Command Abuse**: A compromised or malicious frontend script invoking system-level Tauri commands.
- **REST API Abuse**: Any local program or unauthorized network origin scanning local ports and invoking FastAPI routes.
- **Cross-Site Request Forgery (CSRF) / DNS Rebinding**: Remote malicious websites exploiting the local loopback server to execute local files or elevate privileges.

---

## 3. Vulnerability & Issue Checklist

The following table summarizes the identified vulnerabilities categorized by severity:

| ID | Severity | Component | Issue Description |
|:---|:---:|:---|:---|
| **C1** | 🔴 **Critical** | FastAPI | Unauthenticated Privilege Elevation via `/api/permission_level` |
| **C2** | 🔴 **Critical** | Tauri IPC | Unauthenticated Privilege Elevation via `set_permission_level` command |
| **C3** | 🔴 **Critical** | Tauri Config | Webview Security Policy Deficiencies (`csp: null` & `withGlobalTauri: true`) |
| **C4** | 🔴 **Critical** | FastAPI | Arbitrary Write Vulnerability via `/api/ide/vibe_code` |
| **H1** | 🟡 **High** | Tauri Core | Host Command Injection in PowerShell execution (`set_wallpaper`) |
| **H2** | 🟡 **High** | Hybrid Bridge | Lack of Session/Token Authentication between Tauri Shell and Python backend |
| **M1** | 🟢 **Medium** | Python Core | Stored XSS Risks in DuckDuckGo HTML Scraper parser |
| **M2** | 🟢 **Medium** | Data Storage | Plaintext Local Storage of Sensitive Identities (`user_identity.json`) |

---

## 4. Detailed Remediation Plan (Critical & High Issues)

---

### [C1] Unauthenticated Privilege Elevation (FastAPI)

*   **Vulnerability Analysis**: The POST endpoint `/api/permission_level` accepts an integer `level` and immediately updates the global state variable `permission_level` to 1, 2, or 3 without verifying credentials or checking a secret token.
*   **Architectural Impact**: Allows any local or cross-site process capable of executing an HTTP request to elevate the system's execution context to `Poziom 3 (Full OS Control)`.
*   **Remediation Strategy**: Implement a cryptographically secure startup token (shared-secret pattern). The FastAPI backend must generate a single-use token on startup, write it to a secured memory-mapped file or pipe, and require all privilege-modifying endpoints to supply this token via a `X-Blyskawica-Token` header.

```python
# Proposed Remediation in main.py:
import secrets
from fastapi import Header, HTTPException

STARTUP_TOKEN = secrets.token_hex(32)

def verify_startup_token(x_token: str = Header(None)):
    if not x_token or x_token != STARTUP_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized. Invalid startup token.")

@app.post("/api/permission_level")
async def set_permission_level_endpoint(
    level: int = Form(...),
    x_token: str = Header(None)
):
    verify_startup_token(x_token)
    # ... execution logic
```

*   **Verification Plan**: Send an unauthenticated POST request to `/api/permission_level` and verify it returns `401 Unauthorized`. Supply the generated token and confirm successful elevation.

---

### [C2] Unauthenticated Privilege Elevation (Tauri IPC)

*   **Vulnerability Analysis**: The Tauri command `set_permission_level` in [lib.rs](file:///c:/Projekty/Blyskawica_V8/sparkle_app/src-tauri/src/lib.rs#L177) updates `inner.permission_level` directly based on a parameter sent from Javascript.
*   **Architectural Impact**: If a malicious script runs within the WebView, it can call the Rust backend directly and bypass the Sandbox restriction.
*   **Remediation Strategy**: Restrict access to Tauri commands. Instead of allowing arbitrary elevation, implement a prompt-based confirmation (using native OS dialogs) before elevating permissions to Level 2 or 3.

```rust
// Proposed Remediation in lib.rs:
#[tauri::command]
async fn set_permission_level(
    app: tauri::AppHandle,
    level: u8, 
    state: State<'_, AppState>
) -> Result<String, String> {
    if level < 1 || level > 3 {
        return Err("Invalid permission level".into());
    }
    
    // Require explicit user consent via native OS Dialog for level 3
    if level == 3 {
        use tauri_plugin_dialog::DialogExt;
        let confirmed = app.dialog()
            .message("Błyskawica requires Full OS Control. Grant access?")
            .title("Security Warning")
            .blocking_show(); // Or async confirmation
            
        if !confirmed {
            return Err("User denied permission elevation.".into());
        }
    }
    
    let mut inner = state.0.lock().unwrap();
    inner.permission_level = level;
    Ok(format!("Permission elevated to Level {}", level))
}
```

*   **Verification Plan**: Invoke `set_permission_level(3)` from the Javascript console and verify a blocking modal dialog prompts the user for confirmation.

---

### [C3] WebView Security Policy Deficiencies (Tauri Config)

*   **Vulnerability Analysis**: The Tauri configuration file [tauri.conf.json](file:///c:/Projekty/Blyskawica_V8/sparkle_app/src-tauri/tauri.conf.json) disables the Content Security Policy (`"csp": null`) and enables `"withGlobalTauri": true`.
*   **Architectural Impact**: Disabling CSP exposes the app to Cross-Site Scripting (XSS) attacks. Enabling `withGlobalTauri` allows any script on the window to call Rust backend functions directly via the global `window.__TAURI__` variable.
*   **Remediation Strategy**: Re-enable CSP with strict restrictions. Disable `withGlobalTauri`.

```json
// Proposed changes in tauri.conf.json:
{
  "app": {
    "withGlobalTauri": false,
    "security": {
      "csp": "default-src 'self'; connect-src 'self' http://localhost:11434 http://127.0.0.1:8000; style-src 'self' 'unsafe-inline';"
    }
  }
}
```

*   **Verification Plan**: Open the developer console in the Tauri app and execute `window.__TAURI__.invoke`. Verify it throws an `undefined` error. Verify that external script tags fail to load due to CSP violation.

---

### [C4] Arbitrary Write Vulnerability (FastAPI)

*   **Vulnerability Analysis**: The endpoint `/api/ide/vibe_code` permits writing arbitrary file contents to the disk. While it implements a directory traversal check (`is_inside_workspace`), this restriction is completely bypassed if the global `permission_level` is set to 3.
*   **Architectural Impact**: Remote code execution (RCE) on the host machine. If an attacker elevates permissions (via C1), they can write batch files or executables to system directories (e.g., startup folder).
*   **Remediation Strategy**: Strictly enforce path boundaries. Even at Poziom 3, file writes must not be allowed in sensitive Windows system folders (such as `System32` or `Windows/System32/drivers`). Additionally, enforce the startup token verification (from C1).

```python
# Proposed check in main.py:
def is_restricted_system_path(filepath: Path) -> bool:
    path_str = str(filepath.resolve()).lower().replace("\\", "/")
    restricted_directories = [
        "c:/windows",
        "c:/program files",
        "c:/program files (x86)",
        "c:/users/default",
        "c:/users/all users"
    ]
    return any(path_str.startswith(rdir) for rdir in restricted_directories)

# Inside vibe_code endpoint:
if is_restricted_system_path(target_path):
    raise HTTPException(status_code=403, detail="Write operation to system folders is prohibited.")
```

*   **Verification Plan**: Elevate to Level 3, attempt to write to `c:\Windows\test.txt` and verify the server blocks the action with a `403 Forbidden` response.

---

### [H1] Host Command Injection (Tauri Rust Core)

*   **Vulnerability Analysis**: The Tauri command `execute_system_action` in `lib.rs` implements `set_wallpaper` by running a shell command in PowerShell:
    ```rust
    let command_str = format!("... SystemParametersInfo(20, 0, \"{}\", 3)", path.to_string_lossy());
    std::process::Command::new("powershell").arg("-Command").arg(&command_str)
    ```
    If `path` contains double quotes or PowerShell code injection sequences (e.g. `"; Start-Process cmd.exe -ArgumentList '/c calc.exe' #`), arbitrary PowerShell commands will be executed.
*   **Architectural Impact**: Privilege elevation to native command execution. An attacker who has the ability to pass arbitrary paths can execute arbitrary payloads on the operating system.
*   **Remediation Strategy**: Avoid formatting paths into string-based PowerShell command calls. Use native Rust bindings (e.g., standard file writing or a direct Windows API binding using the `windows` crate) instead of shelling out to PowerShell.

```rust
// Proposed Remediation in Cargo.toml: Add 'windows' crate dependencies
// in lib.rs (replaces shelling out to powershell):
#[cfg(target_os = "windows")]
fn win32_set_wallpaper(path: &Path) -> Result<(), String> {
    use std::ffi::OsStr;
    use std::os::windows::ffi::OsStrExt;
    
    let path_wide: Vec<u16> = path.as_os_str()
        .encode_wide()
        .chain(std::iter::once(0))
        .collect();
        
    unsafe {
        use windows::Win32::UI::WindowsAndMessaging::{
            SystemParametersInfoW, SYSTEM_PARAMETERS_INFO_ACTION, SYSTEM_PARAMETERS_INFO_UPDATE_FLAGS
        };
        let success = SystemParametersInfoW(
            SYSTEM_PARAMETERS_INFO_ACTION(20), // SPI_SETDESKWALLPAPER
            0,
            Some(path_wide.as_ptr() as *mut std::ffi::c_void),
            SYSTEM_PARAMETERS_INFO_UPDATE_FLAGS(3) // SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
        );
        if success.as_bool() {
            Ok(())
        } else {
            Err("SystemParametersInfoW failed.".into())
        }
    }
}
```

*   **Verification Plan**: Call `execute_system_action` with `path` set to `"C:\\path\\image.jpg\"; calc.exe; #"` and confirm that no calculator process spawns, and that standard Win32 execution is used.

---

### [H2] Lack of Session/Token Authentication between Tauri and Python

*   **Vulnerability Analysis**: The Tauri frontend communicates with Python FastAPI backend via HTTP. There is no session management, authentication token, or signature verification.
*   **Architectural Impact**: Any application running on the local system can scan port 8000 and send commands to Błyskawica FastAPI backend, acting on behalf of the user.
*   **Remediation Strategy**: FastAPI backend should generate a unique session token on launch, and share it with the Tauri wrapper (e.g., via standard environment variables or command-line parameters passed when Tauri starts the Python process).

---

## 5. Architectural Guidelines (Zero-Trust Local System Design)

For government-level and safety-critical deployments, the system must adhere to a **Zero-Trust Local Architecture**:

1.  **Process Isolation**:
    - The Python process must run in a containerized environment (Docker Sandbox) or under a restricted local user account, isolated from the administrative workspace.
    - All filesystem access must be restricted via OS-level ACLs (Access Control Lists).
2.  **Explicit Consent**:
    - File writing (`vibe_code`) or OS actions must require explicit confirmation in the UI shell (native dialog) before execution.
3.  **Cryptographic Integrity Checks**:
    - All local neural weights (`mock_weights.bin` or actual model checkpoints) must have SHA-256 integrity hashes stored in a cryptographically signed signature block. This prevents poisoning attacks where external programs replace system weights to alter decision-making behavior.
4.  **No Dynamic Shell Script Generation**:
    - Shell executions (`powershell.exe`, `cmd.exe`) should be completely removed from both Rust and Python backends. System actions must use direct system calls (C APIs / Win32 APIs).
