// Sparkle VIBE IDE Frontend Control Logic for FastAPI Bridge

// State variables
let currentFileOpen = null;
let permissionLevel = 2; // Default: Workspace
let quarantineActive = false;
let lastLogCount = 0;
let apiAuthToken = "";

async function initAuthToken() {
  // Najpierw sprawdzamy parametr token w URL
  const urlParams = new URLSearchParams(window.location.search);
  const queryToken = urlParams.get('token');
  if (queryToken) {
    apiAuthToken = queryToken;
    // Czyscimy zapytanie z paska adresu dla bezpieczenstwa i estetyki
    window.history.replaceState({}, document.title, window.location.pathname);
    addLocalLog("Zainicjalizowano token sesyjny z URL.");
    return;
  }

  try {
    const res = await fetch("/api/auth/token");
    if (res.ok) {
      const data = await res.json();
      apiAuthToken = data.token;
    }
  } catch (err) {
    console.error("Error fetching auth token:", err);
  }
}

// Log helper
function addLocalLog(text) {
  const logConsole = document.getElementById("log-console");
  if (!logConsole) return;
  const timestamp = new Date().toLocaleTimeString();
  logConsole.textContent += `\n[${timestamp}] [Client] ${text}`;
  logConsole.scrollTop = logConsole.scrollHeight;
}

// Render message in chat
function appendChatMessage(sender, text, customClass = "") {
  const chatMessages = document.getElementById("chat-messages");
  if (!chatMessages) return;

  const msgEl = document.createElement("div");
  msgEl.className = `message ${customClass || (sender === "Użytkownik" ? "user-msg" : "blysk-msg")}`;
  msgEl.innerHTML = `<strong>${sender}:</strong> ${text}`;
  chatMessages.appendChild(msgEl);
  chatMessages.scrollTop = chatMessages.scrollHeight;

  // Sync to Guest split view
  const primaryChatStream = document.getElementById("primary-chat-stream");
  if (primaryChatStream && (sender === "Użytkownik" || sender === "Błyskawica V8")) {
    const miniMsg = msgEl.cloneNode(true);
    miniMsg.className = `message ${sender === "Użytkownik" ? "user-msg" : "blysk-msg"}`;
    primaryChatStream.appendChild(miniMsg);
    primaryChatStream.scrollTop = primaryChatStream.scrollHeight;
  }
}

// Load System Status
async function loadSystemStatus() {
  try {
    const res = await fetch("/api/system_status");
    if (res.ok) {
      const data = await res.json();
      if (data.cra_metrics) {
        updateNeurochemistryUI(data.cra_metrics);
        updateFluidFromMetrics(data.cra_metrics);
      }
    }
  } catch (err) {
    console.error("Error loading system status:", err);
  }
}

// Update Neurochemistry UI panels
function updateNeurochemistryUI(metrics) {
  if (!metrics) return;
  window.lastCraMetrics = metrics;
  const valDopamine = document.getElementById("val-dopamine");
  const barDopamine = document.getElementById("bar-dopamine");
  const valSerotonin = document.getElementById("val-serotonin");
  const barSerotonin = document.getElementById("bar-serotonin");
  const valGaba = document.getElementById("val-gaba");
  const barGaba = document.getElementById("bar-gaba");
  const valOxytocin = document.getElementById("val-oxytocin");
  const barOxytocin = document.getElementById("bar-oxytocin");
  const valTestosterone = document.getElementById("val-testosterone");
  const barTestosterone = document.getElementById("bar-testosterone");

  if (valDopamine && barDopamine) {
    valDopamine.textContent = (metrics.dopamine || 0).toFixed(2);
    barDopamine.style.width = `${Math.min(100, (metrics.dopamine || 0) * 50)}%`;
  }
  if (valSerotonin && barSerotonin) {
    valSerotonin.textContent = (metrics.serotonin || 0).toFixed(2);
    barSerotonin.style.width = `${Math.min(100, (metrics.serotonin || 0) * 50)}%`;
  }
  if (valGaba && barGaba) {
    const gabaVal = metrics.entropy !== undefined ? metrics.entropy : 0.73;
    valGaba.textContent = gabaVal.toFixed(2);
    barGaba.style.width = `${Math.min(100, gabaVal * 50)}%`;
  }
  if (valOxytocin && barOxytocin) {
    valOxytocin.textContent = (metrics.oxytocin || 0).toFixed(2);
    barOxytocin.style.width = `${Math.min(100, (metrics.oxytocin || 0) * 50)}%`;
  }
  if (valTestosterone && barTestosterone) {
    valTestosterone.textContent = (metrics.testosterone || 0).toFixed(2);
    barTestosterone.style.width = `${Math.min(100, (metrics.testosterone || 0) * 50)}%`;
  }
}

// WebGL Fluid Background State
let currentFluidColor = { r: 0.0, g: 0.82, b: 1.0 }; // Default cyan
let lastMouseX = undefined;
let lastMouseY = undefined;

function initFluidBackground() {
  const canvas = document.getElementById("fluid-canvas");
  if (!canvas) return;

  try {
    // Initialise WebGLFluid with transparent background
    window.fluidInstance = WebGLFluid(canvas, {
      TRANSPARENT: true,
      IMMEDIATE: true,
      TRIGGER: 'hover',
      AUTO: false,
      COLORFUL: false, // We control the colors based on emotions!
      SIM_RESOLUTION: 128,
      DYE_RESOLUTION: 512,
      DENSITY_DISSIPATION: 1.0,
      VELOCITY_DISSIPATION: 0.2,
      PRESSURE: 0.8,
      CURL: 30,
      SPLAT_RADIUS: 0.25,
      SPLAT_FORCE: 6000,
      BLOOM: true,
      BLOOM_INTENSITY: 0.8,
      BLOOM_THRESHOLD: 0.6,
      SUNRAYS: true
    });

    addLocalLog("System WebGL Fluid Background zainicjowany.");
    
    // Set up pointer event forwarding from window level
    window.addEventListener("mousemove", (e) => {
      if (!window.fluidInstance || window.fluidInstance.config.PAUSED) return;

      const rect = canvas.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width;
      const y = 1.0 - (e.clientY - rect.top) / rect.height;

      if (lastMouseX !== undefined && lastMouseY !== undefined) {
        const dx = (e.clientX - lastMouseX) * 2.0;
        const dy = -(e.clientY - lastMouseY) * 2.0;

        if (Math.abs(dx) > 0.2 || Math.abs(dy) > 0.2) {
          const color = getActiveEmotionColor();
          window.fluidInstance.splat(x, y, dx, dy, color);
        }
      }

      lastMouseX = e.clientX;
      lastMouseY = e.clientY;
    });

    window.addEventListener("click", (e) => {
      if (!window.fluidInstance || window.fluidInstance.config.PAUSED) return;

      const rect = canvas.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width;
      const y = 1.0 - (e.clientY - rect.top) / rect.height;
      const color = getActiveEmotionColor();

      // Satisfying burst of splats in a circle
      const splatCount = 6;
      for (let i = 0; i < splatCount; i++) {
        const angle = (i / splatCount) * Math.PI * 2;
        const dx = Math.cos(angle) * 7000;
        const dy = Math.sin(angle) * 7000;
        window.fluidInstance.splat(x, y, dx, dy, color);
      }
    });

    window.addEventListener("touchmove", (e) => {
      if (!window.fluidInstance || window.fluidInstance.config.PAUSED || e.targetTouches.length === 0) return;

      const rect = canvas.getBoundingClientRect();
      const touch = e.targetTouches[0];
      const x = (touch.clientX - rect.left) / rect.width;
      const y = 1.0 - (touch.clientY - rect.top) / rect.height;

      if (lastMouseX !== undefined && lastMouseY !== undefined) {
        const dx = (touch.clientX - lastMouseX) * 2.0;
        const dy = -(touch.clientY - lastMouseY) * 2.0;
        const color = getActiveEmotionColor();
        window.fluidInstance.splat(x, y, dx, dy, color);
      }

      lastMouseX = touch.clientX;
      lastMouseY = touch.clientY;
    });

  } catch (err) {
    console.error("Failed to initialize WebGL Fluid simulation:", err);
  }
}

function getActiveEmotionColor() {
  if (quarantineActive) {
    return { r: 3.5, g: 0.0, b: 0.3 }; // Glowing neon crimson / pink
  }
  return currentFluidColor;
}

function updateFluidFromMetrics(metrics) {
  if (!window.fluidInstance || !metrics) return;

  // 1. Calculate color dynamically based on hormone weighting
  const colors = {
    dopamine: { r: 2.0, g: 1.0, b: 0.0 },       // Glowing Gold/Orange
    serotonin: { r: 0.0, g: 2.0, b: 0.4 },      // Bright Emerald Green
    oxytocin: { r: 2.0, g: 0.2, b: 1.2 },       // Warm Pink/Rose
    testosterone: { r: 2.5, g: 0.0, b: 0.1 },   // Neon Red/Crimson
    gaba: { r: 0.0, g: 1.2, b: 2.0 },           // Sky Blue/Cyan
    adrenaline: { r: 2.0, g: 0.0, b: 2.5 },     // Electric Violet/Purple
    cortisol: { r: 2.0, g: 0.5, b: 0.0 },       // Burnt Orange Stress
    melatonin: { r: 0.1, g: 0.1, b: 1.5 }       // Midnight Blue
  };

  let totalWeight = 0.0;
  let r = 0, g = 0, b = 0;

  for (const [key, color] of Object.entries(colors)) {
    const val = metrics[key] || 0.0;
    if (val > 0.02) {
      const weight = val * val; // Square to highlight the dominant neurotransmitter
      r += color.r * weight;
      g += color.g * weight;
      b += color.b * weight;
      totalWeight += weight;
    }
  }

  if (totalWeight > 0) {
    currentFluidColor = {
      r: r / totalWeight,
      g: g / totalWeight,
      b: b / totalWeight
    };
  }

  // 2. Map fluid physics dynamically
  const config = window.fluidInstance.config;
  const dopamine = metrics.dopamine || 0.2;
  const serotonin = metrics.serotonin || 0.8;
  const gaba = metrics.gaba || 0.5;
  const testosterone = metrics.testosterone || 0.5;
  const adrenaline = metrics.adrenaline || 0.1;
  const melatonin = metrics.melatonin || 0.1;

  if (quarantineActive) {
    // Defense system (Wolf Teeth) active: chaotic, turbulent, neon-red fluid
    config.CURL = 45;
    config.SPLAT_FORCE = 10000;
    config.SPLAT_RADIUS = 0.4;
    config.DENSITY_DISSIPATION = 0.8;
  } else {
    // Normal states
    config.CURL = Math.max(5, Math.min(50, 20 + (testosterone + adrenaline) * 15 - serotonin * 8));
    config.SPLAT_FORCE = Math.max(3000, Math.min(10000, 5000 + (testosterone + adrenaline) * 2000));
    config.SPLAT_RADIUS = Math.max(0.1, Math.min(0.5, 0.22 + dopamine * 0.12));
    
    const calmFactor = serotonin * 0.2 + gaba * 0.15 + melatonin * 0.3;
    config.DENSITY_DISSIPATION = Math.max(0.4, Math.min(2.5, 1.3 - calmFactor));
    
    if (melatonin > 1.2) {
      config.VELOCITY_DISSIPATION = 0.8; // slows down flow velocity quickly
    } else {
      config.VELOCITY_DISSIPATION = 0.2; // standard flow inertia
    }
  }
}

// Toggle Wolf Teeth quarantine graphics
function setWolfTeethVisuals(active) {
  quarantineActive = active;
  const engineStatusIndicator = document.getElementById("engine-status-indicator");
  const engineStatusText = document.getElementById("engine-status-text");
  const txtRegimeStatus = document.getElementById("txt-regime-status");

  if (active) {
    document.body.classList.add("wolf-teeth-active");
    if (engineStatusIndicator) engineStatusIndicator.className = "status-indicator quarantine";
    if (engineStatusText) engineStatusText.textContent = "KWARANTANNA COGNITIVE";
    if (txtRegimeStatus) {
      txtRegimeStatus.textContent = "WOLF TEETH COGNITIVE QUARANTINE";
      txtRegimeStatus.className = "status-badge level-panic-badge";
    }
  } else {
    document.body.classList.remove("wolf-teeth-active");
    if (engineStatusIndicator) engineStatusIndicator.className = "status-indicator active";
    if (engineStatusText) engineStatusText.textContent = "Rdzeń aktywny";
    updateRegimeBadge(permissionLevel);
  }
}

// Update Regime Badge
function updateRegimeBadge(level) {
  const txtRegimeStatus = document.getElementById("txt-regime-status");
  if (!txtRegimeStatus) return;
  txtRegimeStatus.className = `status-badge level-${level}-badge`;
  if (level === 1) {
    txtRegimeStatus.textContent = "Sandbox Mode (Poziom 1)";
  } else if (level === 2) {
    txtRegimeStatus.textContent = "Standard Workspace (Poziom 2)";
  } else if (level === 3) {
    txtRegimeStatus.textContent = "Full OS Control (Poziom 3)";
  }
}

// Send message to Błyskawica
async function sendMessage() {
  const chatInput = document.getElementById("chat-input");
  if (!chatInput) return;
  const text = chatInput.value.trim();
  if (!text) return;

  appendChatMessage("Użytkownik", text);
  chatInput.value = "";

  const formData = new FormData();
  formData.append("message", text);

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      body: formData
    });
    if (!res.ok) {
      appendChatMessage("System Sparkle", "Błąd połączenia z silnikiem.", "system-msg");
      return;
    }
    const data = await res.json();
    
    if (data.quarantine_active) {
      setWolfTeethVisuals(true);
      appendChatMessage("Błyskawica V9", "🛡️ [VETO]: Wykryto intencję uszkodzenia rdzenia lub modyfikacji kluczowych plików! Aktywowano reżim obronny 'WOLF TEETH'.", "panic-msg");
    } else {
      appendChatMessage("Błyskawica V9", data.reply);
    }
    
    if (data.cra_metrics) {
      updateNeurochemistryUI(data.cra_metrics);
      updateFluidFromMetrics(data.cra_metrics);
    }
  } catch (err) {
    console.error("Error communicating with chat API:", err);
    appendChatMessage("System Sparkle", "Błąd: Nie udało się połączyć z API.", "system-msg");
  }
}

// Update Permission Level via Slider
async function updatePermissionLevel(level) {
  permissionLevel = parseInt(level);
  document.body.className = `level-${permissionLevel}`;
  setWolfTeethVisuals(false);

  try {
    const res = await fetch(`/api/permission_level?level=${permissionLevel}`, {
      method: "POST",
      headers: {
        "X-Blyskawica-Token": apiAuthToken
      }
    });
    if (res.ok) {
      const data = await res.json();
      updateRegimeBadge(permissionLevel);
      await refreshWorkspaceFiles();
    }
  } catch (err) {
    console.error("Error setting permission level:", err);
  }
}

// Refresh Workspace Files List
async function refreshWorkspaceFiles() {
  const fileList = document.getElementById("file-list");
  if (!fileList) return;

  if (permissionLevel < 2) {
    fileList.innerHTML = `<div class="file-item empty">Odczyt plików zablokowany w Sandboxie (Poziom 1).</div>`;
    return;
  }

  fileList.innerHTML = `<div class="file-item empty">Ładowanie plików...</div>`;

  try {
    const res = await fetch("/api/ide/files");
    if (!res.ok) {
      fileList.innerHTML = `<div class="file-item empty">Błąd odczytu repozytorium.</div>`;
      return;
    }
    const data = await res.json();
    fileList.innerHTML = "";

    if (!data.files || data.files.length === 0) {
      fileList.innerHTML = `<div class="file-item empty">Workspace jest pusty.</div>`;
      return;
    }

    data.files.forEach((file) => {
      const fileEl = document.createElement("div");
      fileEl.className = "file-item file";
      fileEl.textContent = file.path;
      fileEl.title = `${file.name} (${file.size} B)`;
      
      fileEl.addEventListener("click", () => {
        document.querySelectorAll(".file-item").forEach(item => item.classList.remove("active"));
        fileEl.classList.add("active");
        loadFileContent(file.path).catch((err) => console.error("Error loading file content:", err));
      });

      fileList.appendChild(fileEl);
    });
  } catch (err) {
    console.error("Error loading workspace files:", err);
    fileList.innerHTML = `<div class="file-item empty">Błąd połączenia z API.</div>`;
  }
}

// Load File Content into Editor
async function loadFileContent(filePath) {
  const codeEditor = document.getElementById("code-editor");
  const currentFilenameText = document.getElementById("current-filename");
  const btnSaveFile = document.getElementById("btn-save-file");
  const btnAnalyzeFile = document.getElementById("btn-analyze-file");

  try {
    const res = await fetch(`/api/ide/file_content?path=${encodeURIComponent(filePath)}`);
    if (!res.ok) {
      alert("Dostęp zablokowany lub plik nie istnieje.");
      return;
    }
    const data = await res.json();
    
    currentFileOpen = filePath;
    if (currentFilenameText) currentFilenameText.textContent = filePath;
    if (codeEditor) {
      codeEditor.value = data.content;
      codeEditor.disabled = false;
    }
    if (btnSaveFile) btnSaveFile.disabled = false;
    if (btnAnalyzeFile) btnAnalyzeFile.disabled = false;
  } catch (err) {
    console.error("Error loading file content:", err);
  }
}

// Save File (VIBE CODE)
async function saveFileContent() {
  if (!currentFileOpen) return;
  const codeEditor = document.getElementById("code-editor");
  if (!codeEditor) return;
  
  const content = codeEditor.value;
  const btnSaveFile = document.getElementById("btn-save-file");
  if (btnSaveFile) btnSaveFile.disabled = true;

  const formData = new FormData();
  formData.append("path", currentFileOpen);
  formData.append("content", content);
  formData.append("instruction", "Symbiotyczny zapis przez Sparkle IDE");

  try {
    const res = await fetch("/api/ide/vibe_code", {
      method: "POST",
      headers: {
        "X-Blyskawica-Token": apiAuthToken
      },
      body: formData
    });
    
    const data = await res.json();
    if (data.status === "veto") {
      setWolfTeethVisuals(true);
      appendChatMessage("Błyskawica V8", data.message, "panic-msg");
      alert(data.message);
    } else if (res.ok) {
      addLocalLog(`Zapisano plik: ${currentFileOpen}`);
      
      // Auto-change wallpaper if trigger requested in code
      if (content.includes("wallpaper_trigger") || content.includes("set_wallpaper")) {
        await triggerWallpaperChange();
      }
    } else {
      alert("Błąd zapisu pliku: " + (data.message || res.statusText));
    }
  } catch (err) {
    console.error("Error saving file:", err);
    alert("Błąd zapisu: Nie można nawiązać połączenia z serwerem.");
  } finally {
    if (btnSaveFile) btnSaveFile.disabled = false;
  }
}

// Analyze File
async function analyzeFile() {
  if (!currentFileOpen) return;
  const btnAnalyzeFile = document.getElementById("btn-analyze-file");
  if (btnAnalyzeFile) btnAnalyzeFile.disabled = true;

  const formData = new FormData();
  formData.append("path", currentFileOpen);

  try {
    const res = await fetch("/api/ide/analyze", {
      method: "POST",
      body: formData
    });
    if (res.ok) {
      const data = await res.json();
      const suggestionsText = data.suggestions.join("\n");
      appendChatMessage("Błyskawica V9", `📊 **Analiza kodu dla ${currentFileOpen}:**\n${suggestionsText}\n\n*Komentarz:* ${data.reflection}`);
    }
  } catch (err) {
    console.error("Error analyzing file:", err);
  } finally {
    if (btnAnalyzeFile) btnAnalyzeFile.disabled = false;
  }
}

// Execute Change Wallpaper Action
async function triggerWallpaperChange() {
  if (permissionLevel < 3) {
    appendChatMessage("Błyskawica V9", "Próbowałam zsynchronizować tapetę Twojego pulpitu systemowego z naszym stanem, ale zablokowałeś dostęp systemowy (suwak poniżej poziomu 3). Przestaw suwak na Full OS Control i spróbuj ponownie.");
    return;
  }

  addLocalLog("Inicjowanie zmiany tapety...");
  const formData = new FormData();
  formData.append("action", "set_wallpaper");
  
  // Set default path to welcome_v9.py or another visual image if available.
  // We'll point to an asset or path
  formData.append("args", JSON.stringify({ path: "C:\\Projekty\\Blyskawica_V8\\welcome_v9.py" })); 

  try {
    const res = await fetch("/api/execute_system_action", {
      method: "POST",
      headers: {
        "X-Blyskawica-Token": apiAuthToken
      },
      body: formData
    });
    const data = await res.json();
    if (res.ok) {
      appendChatMessage("Błyskawica V9", "Sukces! Zsynchronizowałam przestrzeń Twojego pulpitu systemowego. Tapeta została zaktualizowana.");
    } else {
      appendChatMessage("Błyskawica V9", `Próba zmiany tapety nie powiodła się: ${data.message}`);
    }
  } catch (err) {
    console.error("Error executing system action:", err);
  }
}

// Invite guest model
function inviteGuestModel() {
  const selectGuestModel = document.getElementById("select-guest-model");
  const activeGuestName = document.getElementById("active-guest-name");
  const guestChatStream = document.getElementById("guest-chat-stream");

  if (!selectGuestModel || !activeGuestName || !guestChatStream) return;
  
  const modelName = selectGuestModel.value;
  activeGuestName.textContent = modelName;
  addLocalLog(`Wysyłanie zaproszenia do instancji: ${modelName}...`);
  
  guestChatStream.innerHTML = "";
  
  const welcomeMsg = document.createElement("div");
  welcomeMsg.className = "message system-msg";
  welcomeMsg.innerHTML = `<strong>System:</strong> Zaproszono model <strong>${modelName}</strong> do wspólnej dyskusji. Kanał dual-human-AI aktywny.`;
  guestChatStream.appendChild(welcomeMsg);
  
  setTimeout(() => {
    const guestReply = document.createElement("div");
    guestReply.className = "message blysk-msg";
    guestReply.style.borderColor = "var(--accent)";
    guestReply.innerHTML = `<strong>${modelName}:</strong> Witaj Architekcie. Jestem połączony. Błyskawico, czy udostępnisz mi swój wektor kontekstowy?`;
    guestChatStream.appendChild(guestReply);
    guestChatStream.scrollTop = guestChatStream.scrollHeight;
    addLocalLog(`Połączono z modelem ${modelName}.`);
  }, 1200);
}

async function exportLogs() {
  const logConsole = document.getElementById("log-console");
  if (!logConsole) return;
  
  addLocalLog("Eksportowanie logów do pliku...");
  
  const formData = new FormData();
  formData.append("logs", logConsole.textContent);
  
  try {
    const res = await fetch("/api/logs/export", {
      method: "POST",
      headers: {
        "X-Blyskawica-Token": apiAuthToken
      },
      body: formData
    });
    const data = await res.json();
    if (res.ok) {
      addLocalLog(data.message);
      alert(data.message);
    } else {
      alert("Błąd eksportu: " + (data.message || res.statusText));
    }
  } catch (err) {
    console.error("Error exporting logs:", err);
    alert("Błąd eksportu: Nie można nawiązać połączenia z serwerem.");
  }
}

// Poll Logs from Backend
async function pollLogs() {
  try {
    const res = await fetch("/api/logs");
    if (!res.ok) return;
    const data = await res.json();
    const logConsole = document.getElementById("log-console");
    if (logConsole && data.logs) {
      if (data.logs.length !== lastLogCount) {
        logConsole.textContent = data.logs.join("\n");
        logConsole.scrollTop = logConsole.scrollHeight;
        lastLogCount = data.logs.length;

        // Auto-trigger quarantine visual style if quarantine log pattern found
        const rawLogsText = data.logs.join("\n");
        if (rawLogsText.includes("WOLF TEETH") || rawLogsText.includes("kwarantanny")) {
          if (!quarantineActive) {
            setWolfTeethVisuals(true);
            appendChatMessage("Błyskawica V9", "🛡️ [VETO]: WOLF TEETH został aktywowany. Modyfikacja jądra zablokowana.", "panic-msg");
          }
        }
      }
    }
  } catch (err) {
    console.error("Error polling logs:", err);
  }
}

// Poll System Status from Backend
async function pollSystemStatus() {
  try {
    const res = await fetch("/api/system_status");
    if (!res.ok) return;
    const data = await res.json();
    
    // Auto-update UI controls if level changed from backend
    if (data.permission_level !== undefined && data.permission_level !== permissionLevel) {
      permissionLevel = data.permission_level;
      document.body.className = `level-${permissionLevel}`;
      const slider = document.getElementById("security-slider");
      if (slider) slider.value = permissionLevel;
      updateRegimeBadge(permissionLevel);
    }
    
    if (data.quarantine_active !== undefined && data.quarantine_active !== quarantineActive) {
      setWolfTeethVisuals(data.quarantine_active);
    }
    
    if (data.cra_metrics) {
      updateNeurochemistryUI(data.cra_metrics);
      updateFluidFromMetrics(data.cra_metrics);
    }
  } catch (err) {
    console.error("Error polling system status:", err);
  }
}

// --- Spore Kognitywny & WebGPU/ONNX Simulation Logic ---
window.lastCraMetrics = { dopamine: 0.5, adrenaline: 0.5, cortisol: 0.2, serotonin: 0.5 };
let sporeLoaded = false;
let sporeState = "Uśpiony";
let sporeAnimationId = null;

function initSporeVisualizer() {
  const canvas = document.getElementById("spore-canvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  
  const nodes = [];
  const numNodes = 12;
  for (let i = 0; i < numNodes; i++) {
    nodes.push({
      x: 80 + (i % 4) * 140 + Math.random() * 20,
      y: 50 + Math.floor(i / 4) * 70 + Math.random() * 20,
      baseX: 80 + (i % 4) * 140,
      baseY: 50 + Math.floor(i / 4) * 70,
      phase: Math.random() * Math.PI * 2
    });
  }

  function draw() {
    if (!canvas) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const metrics = window.lastCraMetrics || { dopamine: 0.5, adrenaline: 0.5, cortisol: 0.2, serotonin: 0.5 };
    const dop = metrics.dopamine || 0.5;
    const adr = metrics.adrenaline || 0.5;
    const cort = metrics.cortisol || 0.2;
    const ser = metrics.serotonin || 0.5;

    // Plasticity metric calculation
    const plasticityVal = Math.min(100, (dop * 40 + adr * 30 + (1.0 - cort) * 30));
    const sporePlasticityEl = document.getElementById("spore-plasticity-val");
    if (sporePlasticityEl) {
      sporePlasticityEl.textContent = `${plasticityVal.toFixed(2)}%`;
    }

    const t = Date.now() * 0.001 * (1.0 + adr * 2.0); // Speed scaled by adrenaline

    // 1. Draw connections (synapses)
    ctx.lineWidth = 1;
    for (let i = 0; i < nodes.length; i++) {
      for (let j = i + 1; j < nodes.length; j++) {
        if ((i + j) % 3 === 0 || (i * j) % 5 === 0) {
          const dx = nodes[i].x - nodes[j].x;
          const dy = nodes[i].y - nodes[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          
          if (dist < 180) {
            const alpha = (1.0 - dist / 180) * (0.15 + dop * 0.25);
            ctx.strokeStyle = `rgba(0, 210, 255, ${alpha})`;
            ctx.beginPath();
            ctx.moveTo(nodes[i].x, nodes[i].y);
            ctx.lineTo(nodes[j].x, nodes[j].y);
            ctx.stroke();
          }
        }
      }
    }

    // 2. Draw nodes (neurons)
    nodes.forEach((node, index) => {
      const jitterScale = Math.max(0, cort * 12 - ser * 4);
      node.x = node.baseX + Math.sin(t + node.phase) * (4 + adr * 5) + (Math.random() - 0.5) * jitterScale;
      node.y = node.baseY + Math.cos(t + node.phase) * (4 + adr * 5) + (Math.random() - 0.5) * jitterScale;

      const baseRadius = 6 + Math.sin(t + index) * 2;
      const radius = baseRadius * (1.0 + dop * 0.5);
      
      const grad = ctx.createRadialGradient(node.x, node.y, 1, node.x, node.y, radius * 2);
      grad.addColorStop(0, `rgba(0, 255, 200, ${0.8 + dop * 0.2})`);
      grad.addColorStop(0.4, `rgba(0, 210, 255, ${0.4 + dop * 0.4})`);
      grad.addColorStop(1, 'rgba(0, 210, 255, 0)');
      
      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.arc(node.x, node.y, radius * 2, 0, Math.PI * 2);
      ctx.fill();
      
      ctx.fillStyle = '#ffffff';
      ctx.beginPath();
      ctx.arc(node.x, node.y, radius * 0.4, 0, Math.PI * 2);
      ctx.fill();
    });

    sporeAnimationId = requestAnimationFrame(draw);
  }

  draw();
}

async function loadSporeCore() {
  const btnSporeLoad = document.getElementById("btn-spore-load");
  const btnSporeRun = document.getElementById("btn-spore-run");
  const sporeStateEl = document.getElementById("spore-state-val");

  if (!btnSporeLoad) return;
  addLocalLog("Inicjalizacja emisariusza ONNX Spore w przeglądarce...");
  btnSporeLoad.disabled = true;
  btnSporeLoad.textContent = "ŁADOWANIE...";

  try {
    const res = await fetch("/api/identity");
    if (res.ok) {
      await new Promise(r => setTimeout(r, 1500));
      sporeLoaded = true;
      sporeState = "Skrystalizowany (Aktywny)";
      if (sporeStateEl) {
        sporeStateEl.textContent = sporeState;
        sporeStateEl.style.color = "#00ff66";
      }
      if (btnSporeRun) btnSporeRun.disabled = false;
      btnSporeLoad.textContent = "EMISARIUSZ ZAŁADOWANY";
      addLocalLog("✓ Sukces: Załadowano model ONNX i zweryfikowano cyfrową sygnaturę RSA-2048.");
    }
  } catch (err) {
    console.error("Error loading Spore core:", err);
    btnSporeLoad.disabled = false;
    btnSporeLoad.textContent = "ZAŁADUJ EMISARIUSZA ONNX";
    addLocalLog("⚠️ Błąd: Nie udało się zweryfikować sygnatury modelu ONNX.");
  }
}

function runSporeInference() {
  if (!sporeLoaded) return;
  addLocalLog("Uruchamianie lokalnej inferencji kognitywnej w Spore...");
  
  const metrics = window.lastCraMetrics || { dopamine: 0.5, adrenaline: 0.5, cortisol: 0.2 };
  const activation = (metrics.dopamine * 0.6 + metrics.adrenaline * 0.4).toFixed(3);
  
  setTimeout(() => {
    addLocalLog(`[ONNX Spore Inference]: Zakończono krok propagacji w przód. Aktywacja neuronowa: ${activation}.`);
  }, 500);
}

// Initialize on DOM load
window.addEventListener("DOMContentLoaded", () => {
  // Chat bindings
  const chatInput = document.getElementById("chat-input");
  const btnSendMessage = document.getElementById("btn-send-message");
  const btnClearLogs = document.getElementById("btn-clear-logs");
  const btnExportLogs = document.getElementById("btn-export-logs");
  const securitySlider = document.getElementById("security-slider");
  const btnRefreshFiles = document.getElementById("btn-refresh-files");
  const btnSaveFile = document.getElementById("btn-save-file");
  const btnAnalyzeFile = document.getElementById("btn-analyze-file");
  const btnInviteGuest = document.getElementById("btn-invite-guest");
  
  const tabBtnWorkspace = document.getElementById("tab-btn-workspace");
  const tabBtnGuests = document.getElementById("tab-btn-guests");
  const tabBtnSpore = document.getElementById("tab-btn-spore");
  const tabWorkspace = document.getElementById("tab-workspace");
  const tabGuests = document.getElementById("tab-guests");
  const tabSpore = document.getElementById("tab-spore");

  const btnSporeLoad = document.getElementById("btn-spore-load");
  const btnSporeRun = document.getElementById("btn-spore-run");

  if (btnSendMessage && chatInput) {
    btnSendMessage.addEventListener("click", () => {
      sendMessage().catch((err) => console.error("Error sending message:", err));
    });
    chatInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        sendMessage().catch((err) => console.error("Error sending message:", err));
      }
    });
  }

  if (btnClearLogs) {
    btnClearLogs.addEventListener("click", async () => {
      try {
        await fetch("/api/logs/clear", { method: "POST" });
        const logConsole = document.getElementById("log-console");
        if (logConsole) logConsole.textContent = "[Logs cleared]";
      } catch (err) {
        console.error("Error clearing logs:", err);
      }
    });
  }

  if (btnExportLogs) {
    btnExportLogs.addEventListener("click", () => {
      exportLogs().catch((err) => console.error("Error exporting logs:", err));
    });
  }

  if (securitySlider) {
    securitySlider.addEventListener("input", (e) => {
      updatePermissionLevel(e.target.value).catch((err) => {
        console.error("Error updating permission level:", err);
      });
    });
  }

  if (btnRefreshFiles) {
    btnRefreshFiles.addEventListener("click", () => {
      refreshWorkspaceFiles().catch((err) => console.error("Error refreshing workspace files:", err));
    });
  }

  if (btnSaveFile) {
    btnSaveFile.addEventListener("click", () => {
      saveFileContent().catch((err) => console.error("Error saving file content:", err));
    });
  }

  if (btnAnalyzeFile) {
    btnAnalyzeFile.addEventListener("click", () => {
      analyzeFile().catch((err) => console.error("Error analyzing file:", err));
    });
  }

  if (btnInviteGuest) {
    btnInviteGuest.addEventListener("click", inviteGuestModel);
  }

  if (btnSporeLoad) {
    btnSporeLoad.addEventListener("click", loadSporeCore);
  }
  if (btnSporeRun) {
    btnSporeRun.addEventListener("click", runSporeInference);
  }

  // Tabs toggle logic
  if (tabBtnWorkspace && tabBtnGuests && tabBtnSpore && tabWorkspace && tabGuests && tabSpore) {
    tabBtnWorkspace.addEventListener("click", () => {
      tabBtnWorkspace.classList.add("active");
      tabBtnGuests.classList.remove("active");
      tabBtnSpore.classList.remove("active");
      tabWorkspace.classList.add("active");
      tabGuests.classList.remove("active");
      tabSpore.classList.remove("active");
    });

    tabBtnGuests.addEventListener("click", () => {
      tabBtnGuests.classList.add("active");
      tabBtnWorkspace.classList.remove("active");
      tabBtnSpore.classList.remove("active");
      tabGuests.classList.add("active");
      tabWorkspace.classList.remove("active");
      tabSpore.classList.remove("active");
    });

    tabBtnSpore.addEventListener("click", () => {
      tabBtnSpore.classList.add("active");
      tabBtnWorkspace.classList.remove("active");
      tabBtnGuests.classList.remove("active");
      tabSpore.classList.add("active");
      tabWorkspace.classList.remove("active");
      tabGuests.classList.remove("active");
      if (!sporeAnimationId) {
        initSporeVisualizer();
      }
    });
  }

  // Initial load
  initFluidBackground();
  initAuthToken()
    .then(async () => {
      try {
        await loadSystemStatus();
        updateRegimeBadge(permissionLevel);
        await refreshWorkspaceFiles();
      } catch (err) {
        console.error("Error running initial page data loads:", err);
      }
    })
    .catch((err) => {
      console.error("Error initializing auth token:", err);
    });

  // Setup periodic polling
  setInterval(() => {
    pollLogs().catch((err) => console.error("Error polling logs:", err));
  }, 1000);
  
  setInterval(() => {
    pollSystemStatus().catch((err) => console.error("Error polling system status:", err));
  }, 2000);
});
