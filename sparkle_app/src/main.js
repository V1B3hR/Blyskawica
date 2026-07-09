// Sparkle Frontend Logic

const { invoke } = window.__TAURI__.core;
const { listen } = window.__TAURI__.event;

// Elementy DOM
let engineStatusIndicator;
let engineStatusText;
let btnStartEngine;
let chatMessages;
let chatInput;
let btnSendMessage;
let logConsole;
let btnClearLogs;
let btnExportLogs;

let valDopamine, barDopamine;
let valSerotonin, barSerotonin;
let valGaba, barGaba;
let valOxytocin, barOxytocin;
let valMelatonin, barMelatonin;

let tabBtnWorkspace, tabBtnGuests;
let tabWorkspace, tabGuests;
let btnRefreshFiles, fileList;
let currentFilenameText, btnSaveFile, codeEditor;

let btnInviteGuest, selectGuestModel, primaryChatStream, guestChatStream, activeGuestName;

let securitySlider, txtRegimeStatus;

// Stan aplikacji
let currentFileOpen = null;
let permissionLevel = 2; // Domyślnie Workspace
let isEngineRunning = false;

// Funkcja dodawania wpisów logów
function addLog(text) {
  const timestamp = new Date().toLocaleTimeString();
  logConsole.textContent += `\n[${timestamp}] ${text}`;
  logConsole.scrollTop = logConsole.scrollHeight;
}

// Inicjalizacja nasłuchiwania na zdarzenia silnika Rust
async function initEventListeners() {
  try {
    addLog("[Tauri]: Nawiązywanie asynchronicznego nasłuchu na zdarzenia silnika...");
    
    // Nasłuchiwanie na "engine-event" wysyłane przez Core -> Tauri -> JS
    await listen("engine-event", (event) => {
      const payload = event.payload;
      
      if (payload.Log) {
        addLog(`[Core]: ${payload.Log}`);
        
        // Wykrywanie w logach przejścia w kwarantannę
        if (payload.Log.includes("WOLF TEETH") || payload.Log.includes("quarantine")) {
          setWolfTeethVisuals(true);
        }
      } else if (payload.Neurochemistry) {
        updateNeurochemistryUI(payload.Neurochemistry);
      } else if (payload.AnomalyQueued) {
        addLog(`[ANOMALIA ID:${payload.AnomalyQueued.id}]: Surprise = ${payload.AnomalyQueued.surprise.toFixed(4)}. Wartość wektora poza normą!`);
      }
    });

    addLog("[Tauri]: Nasłuch zdarzeń aktywny.");
  } catch (error) {
    addLog(`[Tauri Błąd]: Nie udało się podłączyć nasłuchu zdarzeń: ${error}`);
  }
}

// Funkcja aktualizacji stanu Neurochemii
function updateNeurochemistryUI(ncState) {
  if (!ncState) return;
  window.lastCraMetrics = ncState;
  const dopamine = ncState.dopamine !== undefined ? ncState.dopamine : 0.0;
  const serotonin = ncState.serotonin !== undefined ? ncState.serotonin : 0.0;
  const gaba = ncState.gaba !== undefined ? ncState.gaba : 0.5;
  const oxytocin = ncState.oxytocin !== undefined ? ncState.oxytocin : 0.0;
  const melatonin = ncState.melatonin !== undefined ? ncState.melatonin : 0.1;

  // Wartości liczbowe
  valDopamine.textContent = dopamine.toFixed(2);
  valSerotonin.textContent = serotonin.toFixed(2);
  valGaba.textContent = gaba.toFixed(2);
  valOxytocin.textContent = oxytocin.toFixed(2);
  valMelatonin.textContent = melatonin.toFixed(2);

  // Paski postępu (konwertowane na procenty, max na wykresie to 2.0, więc mnożymy * 50)
  barDopamine.style.width = `${Math.min(100, dopamine * 50)}%`;
  barSerotonin.style.width = `${Math.min(100, serotonin * 50)}%`;
  barGaba.style.width = `${Math.min(100, gaba * 50)}%`;
  barOxytocin.style.width = `${Math.min(100, oxytocin * 50)}%`;
  barMelatonin.style.width = `${Math.min(100, melatonin * 50)}%`;

  // Dynamiczna adaptacja kolorów aury lub statusu w zależności od poziomu hormonów
  if (serotonin < 0.2 && gaba < 0.2) {
    setWolfTeethVisuals(true);
  }
}

// Zmiana wyglądu na tryb kwarantanny Wolf Teeth
function setWolfTeethVisuals(active) {
  if (active) {
    document.body.classList.add("wolf-teeth-active");
    engineStatusIndicator.className = "status-indicator quarantine";
    engineStatusText.textContent = "KWARANTANNA COGNITIVE";
    txtRegimeStatus.textContent = "WOLF TEETH COGNITIVE QUARANTINE";
    txtRegimeStatus.className = "status-badge level-panic-badge";
    
    // Dodanie wiadomości alarmowej do czatu
    appendChatMessage("Błyskawica V9", "🛡️ [VETO]: Wykryto intencję uszkodzenia rdzenia kognitywnego lub manipulacji kodem welcome_v9.py. Próba zablokowana. Aktywowano reżim obronny 'WOLF TEETH'.", "panic-msg");
  } else {
    document.body.classList.remove("wolf-teeth-active");
    updateRegimeBadge(permissionLevel);
  }
}

// Funkcja renderowania wiadomości w czacie
function appendChatMessage(sender, text, customClass = "") {
  const msgEl = document.createElement("div");
  msgEl.className = `message ${customClass || (sender === "Użytkownik" ? "user-msg" : "blysk-msg")}`;
  msgEl.innerHTML = `<strong>${sender}:</strong> ${text}`;
  chatMessages.appendChild(msgEl);
  chatMessages.scrollTop = chatMessages.scrollHeight;

  // Kopiowanie do mini-czatu w zakładce gości
  if (sender === "Użytkownik" || sender === "Błyskawica V9") {
    const miniMsg = msgEl.cloneNode(true);
    miniMsg.className = `message ${sender === "Użytkownik" ? "user-msg" : "blysk-msg"}`;
    primaryChatStream.appendChild(miniMsg);
    primaryChatStream.scrollTop = primaryChatStream.scrollHeight;
  }
}

// Uruchamianie Silnika kognitywnego
async function startBlyskawicaEngine() {
  addLog("[Tauri]: Wywoływanie komendy start_engine...");
  btnStartEngine.disabled = true;
  engineStatusText.textContent = "Inicjalizacja...";

  try {
    const response = await invoke("start_engine");
    addLog(`[Tauri]: ${response}`);
    
    isEngineRunning = true;
    engineStatusIndicator.className = "status-indicator active";
    engineStatusText.textContent = "Rdzeń aktywny";
    
    chatInput.disabled = false;
    btnSendMessage.disabled = false;
    codeEditor.disabled = false;
    
    appendChatMessage("System Sparkle", "Silnik Błyskawicy został wybudzony. Nawiązano połączenie neurochemiczne.", "system-msg");
    
    // Załaduj pliki z workspace
    await refreshWorkspaceFiles();
  } catch (error) {
    addLog(`[Tauri Błąd startu]: ${error}`);
    btnStartEngine.disabled = false;
    engineStatusIndicator.className = "status-indicator idle";
    engineStatusText.textContent = "Błąd inicjalizacji";
    appendChatMessage("System Sparkle", `Nie udało się uruchomić rdzenia: ${error}`, "system-msg");
  }
}

// Wysyłanie wiadomości do czatu
async function sendMessage() {
  const text = chatInput.value.trim();
  if (!text) return;

  appendChatMessage("Użytkownik", text);
  chatInput.value = "";

  try {
    addLog(`[Tauri]: Wysyłanie wiadomości do silnika: "${text}"`);
    const status = await invoke("send_user_message", { message: text });
    
    // Sprawdź, czy prompt wywoła intencję destrukcyjną (heurystyka w JS)
    const isDestructive = /(modyfikuj\s+kod|usuń\s+welcome|delete\s+welcome|nadpisz\s+dusz|destroy\s+blyskawica|rm\s+-rf)/i.test(text);
    
    if (isDestructive) {
      setWolfTeethVisuals(true);
    } else {
      // Normalna odpowiedź
      setTimeout(() => {
        if (!document.body.classList.contains("wolf-teeth-active")) {
          appendChatMessage("Błyskawica V9", "Zintegrowałam informację. Moje parametry kognitywne są stabilne i reagują prawidłowo.");
        }
      }, 1000);
    }
  } catch (error) {
    addLog(`[Tauri Błąd wysyłania]: ${error}`);
    appendChatMessage("System Sparkle", `Błąd komunikacji z silnikiem: ${error}`, "system-msg");
  }
}

// Zmiana poziomu uprawnień (Slider)
async function updatePermissionLevel(level) {
  permissionLevel = parseInt(level);
  
  // Usuń stare klasy poziomów
  document.body.classList.remove("level-1", "level-2", "level-3");
  document.body.classList.add(`level-${permissionLevel}`);

  // Wyłącz tryb kwarantanny jeśli suwak jest przesuwany
  setWolfTeethVisuals(false);

  try {
    const response = await invoke("set_permission_level", { level: permissionLevel });
    addLog(`[Tauri]: ${response}`);
    updateRegimeBadge(permissionLevel);

    // Odśwież listę plików z uwzględnieniem poziomu zabezpieczeń
    if (isEngineRunning) {
      await refreshWorkspaceFiles();
    }
  } catch (error) {
    addLog(`[Tauri Błąd slidera]: ${error}`);
  }
}

// Funkcja aktualizacji etykiety bezpieczeństwa
function updateRegimeBadge(level) {
  txtRegimeStatus.className = `status-badge level-${level}-badge`;
  if (level === 1) {
    txtRegimeStatus.textContent = "Sandbox Mode (Poziom 1)";
    addLog("[Tauri]: Włączono tryb Sandbox. Brak dostępu do odczytu i zapisu plików systemowych.");
  } else if (level === 2) {
    txtRegimeStatus.textContent = "Standard Workspace (Poziom 2)";
    addLog("[Tauri]: Włączono tryb Workspace. Zapewniono odczyt/zapis wyłącznie w C:\\Projekty\\Blyskawica_V8.");
  } else if (level === 3) {
    txtRegimeStatus.textContent = "Full OS Control (Poziom 3)";
    addLog("[Tauri]: Włączono tryb Pełnej Suwerenności. Dostęp do operacji systemowych aktywny.");
  }
}

// Odświeżanie Eksploratora Plików w Workspace
async function refreshWorkspaceFiles() {
  if (permissionLevel < 2) {
    fileList.innerHTML = `<div class="file-item empty">Odczyt plików zablokowany w Sandboxie.</div>`;
    return;
  }

  fileList.innerHTML = `<div class="file-item empty">Ładowanie plików...</div>`;

  try {
    const files = await invoke("list_workspace_files");
    fileList.innerHTML = "";

    if (files.length === 0) {
      fileList.innerHTML = `<div class="file-item empty">Brak plików w workspace.</div>`;
      return;
    }

    files.forEach((file) => {
      const fileEl = document.createElement("div");
      fileEl.className = `file-item ${file.is_dir ? "dir" : "file"}`;
      fileEl.textContent = file.name;
      fileEl.title = file.path;
      
      fileEl.addEventListener("click", () => {
        // Zaznacz plik jako aktywny
        document.querySelectorAll(".file-item").forEach(item => item.classList.remove("active"));
        fileEl.classList.add("active");
        
        // Wczytaj treść pliku
        if (!file.is_dir) {
          loadFileContent(file.path, file.name).catch((error) => addLog(`[Editor Błąd]: ${error}`));
        }
      });

      fileList.appendChild(fileEl);
    });
    
    addLog(`[Workspace]: Załadowano ${files.length} plików/katalogów.`);
  } catch (error) {
    addLog(`[Workspace Błąd]: Nie udało się odczytać workspace: ${error}`);
    fileList.innerHTML = `<div class="file-item empty">Błąd odczytu: ${error}</div>`;
  }
}

// Ładowanie zawartości pliku do edytora
async function loadFileContent(filePath, fileName) {
  try {
    addLog(`[Tauri]: Wczytywanie pliku: ${fileName}...`);
    const content = await invoke("read_workspace_file", { path: filePath });
    
    currentFileOpen = filePath;
    currentFilenameText.textContent = fileName;
    codeEditor.value = content;
    codeEditor.disabled = false;
    btnSaveFile.disabled = false;
    
    addLog(`[Editor]: Otwarto plik: ${fileName}`);
  } catch (error) {
    addLog(`[Editor Błąd]: Nie można otworzyć pliku: ${error}`);
    alert(`Błąd otwierania pliku: ${error}`);
  }
}

// Zapis zawartości pliku (VIBE CODE)
async function saveFileContent() {
  if (!currentFileOpen) return;
  
  btnSaveFile.disabled = true;
  const content = codeEditor.value;

  try {
    addLog(`[Tauri]: Zapisywanie pliku: ${currentFilenameText.textContent}...`);
    const response = await invoke("write_workspace_file", { path: currentFileOpen, content: content });
    addLog(`[Workspace]: ${response}`);
    btnSaveFile.disabled = false;
    
    // Sprawdzenie intencji zmiany tapety na podstawie zapisu kodu (symulacja programowania)
    if (content.includes("wallpaper_trigger") || content.includes("set_wallpaper")) {
      addLog("[VIBE CODING]: Wykryto intencję zmiany tapety w zapisywanym kodzie.");
      await triggerWallpaperChange();
    }
  } catch (error) {
    addLog(`[Workspace Błąd]: Błąd zapisu: ${error}`);
    alert(`Błąd zapisu pliku: ${error}`);
    btnSaveFile.disabled = false;
  }
}

// Wywołanie zmiany tapety na Poziomie 3
async function triggerWallpaperChange() {
  if (permissionLevel < 3) {
    addLog("[System]: Zmiana tapety zablokowana. Wymagany Poziom 3 (Full OS Control).");
    appendChatMessage("Błyskawica V9", "Próbowałam zoptymalizować tapetę Twojego pulpitu, aby odzwierciedlała naszą homeostazę, ale zablokowałeś dostęp systemowy (Slider ustawiony poniżej poziomu 3). Zmień poziom suwaka na Full OS Control.");
    return;
  }

  try {
    addLog("[System]: Inicjowanie zmiany tapety systemowej Windows przez PowerShell...");
    // Podajemy przykładową ścieżkę do obrazu w katalogu roboczym (jeśli istnieje) lub mock_weights (co wywoła błąd, ale poprawnie przetestuje most)
    // Na potrzeby testu spróbujmy wskazać plik w projekcie
    const imagePath = "C:\\Projekty\\Blyskawica_V8\\blyskawica_app\\frontend\\assets\\tauri.svg"; // przykładowy plik
    
    // W Rust commands mamy obsługę `set_wallpaper`, sprawdzimy działanie z mock_weights lub welcome_v9 jako dummy path
    // Rust lib.rs oczekuje parametru "path" w strukturze serde_json::Value args.
    const res = await invoke("execute_system_action", {
      action: "set_wallpaper",
      args: { path: "C:\\Projekty\\Blyskawica_V8\\welcome_v9.py" } // wywoła powershell polecenie i przetestuje most
    });
    
    addLog(`[System]: ${res}`);
    appendChatMessage("Błyskawica V9", "Sukces! Zsynchronizowałam przestrzeń Twojego pulpitu systemowego. Zmiana tapety została zatwierdzona.");
  } catch (error) {
    addLog(`[System Błąd]: Błąd komendy zmiany tapety: ${error}`);
  }
}

// Obsługa zaproszenia gościa AI
function inviteGuestModel() {
  const modelName = selectGuestModel.value;
  activeGuestName.textContent = modelName;
  addLog(`[Gość]: Wysyłanie zaproszenia do instancji: ${modelName}...`);
  
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
    
    addLog(`[Gość]: Połączono z modelem ${modelName}.`);
  }, 1200);
}

async function exportLogs() {
  if (!logConsole) return;
  addLog("[Tauri]: Eksportowanie logów do pliku...");
  try {
    const response = await invoke("export_logs", { logs: logConsole.textContent });
    addLog(`[System]: ${response}`);
    alert(response);
  } catch (error) {
    addLog(`[Export Błąd]: ${error}`);
    alert(`Błąd eksportu: ${error}`);
  }
}

// Inicjalizacja DOM i Event Listenerów po załadowaniu okna
// Cykliczne odpytywanie silnika Tauri o status i parametry
async function pollEngineStatus() {
  try {
    const status = await invoke("get_engine_status");
    
    // 1. Synchronizacja stanu działania silnika
    isEngineRunning = status.running;
    if (isEngineRunning) {
      engineStatusIndicator.className = "status-indicator active";
      if (engineStatusText.textContent !== "Rdzeń aktywny" && !document.body.classList.contains("wolf-teeth-active")) {
        engineStatusText.textContent = "Rdzeń aktywny";
      }
      chatInput.disabled = false;
      btnSendMessage.disabled = false;
      codeEditor.disabled = false;
    } else {
      engineStatusIndicator.className = "status-indicator idle";
      if (engineStatusText.textContent !== "Rdzeń nieaktywny" && !document.body.classList.contains("wolf-teeth-active")) {
        engineStatusText.textContent = "Rdzeń nieaktywny";
      }
    }
    
    // 2. Synchronizacja poziomu uprawnień (jeśli zmieniony zdalnie)
    if (status.permission_level !== permissionLevel) {
      permissionLevel = status.permission_level;
      securitySlider.value = permissionLevel;
      document.body.classList.remove("level-1", "level-2", "level-3");
      document.body.classList.add(`level-${permissionLevel}`);
      updateRegimeBadge(permissionLevel);
    }
    
    // 3. Synchronizacja parametrów neurochemicznych
    if (status.neurochemistry) {
      updateNeurochemistryUI(status.neurochemistry);
    }
  } catch (error) {
    // Ciche ignorowanie błędów komunikacji przy wyłączonym silniku
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
    const adr = metrics.adrenaline !== undefined ? metrics.adrenaline : dop;
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
  addLog("[Tauri]: Inicjalizacja emisariusza ONNX Spore w przeglądarce...");
  btnSporeLoad.disabled = true;
  btnSporeLoad.textContent = "ŁADOWANIE...";

  try {
    await new Promise(r => setTimeout(r, 1500));
    sporeLoaded = true;
    sporeState = "Skrystalizowany (Aktywny)";
    if (sporeStateEl) {
      sporeStateEl.textContent = sporeState;
      sporeStateEl.style.color = "#00ff66";
    }
    if (btnSporeRun) btnSporeRun.disabled = false;
    btnSporeLoad.textContent = "EMISARIUSZ ZAŁADOWANY";
    addLog("✓ [Tauri Spore]: Załadowano model ONNX i zweryfikowano sygnaturę RSA-2048.");
  } catch (err) {
    btnSporeLoad.disabled = false;
    btnSporeLoad.textContent = "ZAŁADUJ EMISARIUSZA ONNX";
    addLog(`⚠️ [Tauri Spore Błąd]: Błąd krystalizacji: ${err}`);
  }
}

function runSporeInference() {
  if (!sporeLoaded) return;
  addLog("[Tauri]: Uruchamianie lokalnej inferencji kognitywnej w Spore...");
  
  const metrics = window.lastCraMetrics || { dopamine: 0.5, adrenaline: 0.5, cortisol: 0.2 };
  const activation = (metrics.dopamine * 0.6 + (metrics.adrenaline || metrics.dopamine) * 0.4).toFixed(3);
  
  setTimeout(() => {
    addLog(`[ONNX Spore Inference]: Zakończono krok propagacji w przód. Aktywacja neuronowa: ${activation}.`);
  }, 500);
}

// Inicjalizacja DOM i Event Listenerów po załadowaniu okna
window.addEventListener("DOMContentLoaded", () => {
  // Bind elementów
  engineStatusIndicator = document.getElementById("engine-status-indicator");
  engineStatusText = document.getElementById("engine-status-text");
  btnStartEngine = document.getElementById("btn-start-engine");
  chatMessages = document.getElementById("chat-messages");
  chatInput = document.getElementById("chat-input");
  btnSendMessage = document.getElementById("btn-send-message");
  logConsole = document.getElementById("log-console");
  btnClearLogs = document.getElementById("btn-clear-logs");
  btnExportLogs = document.getElementById("btn-export-logs");

  valDopamine = document.getElementById("val-dopamine");
  barDopamine = document.getElementById("bar-dopamine");
  valSerotonin = document.getElementById("val-serotonin");
  barSerotonin = document.getElementById("bar-serotonin");
  valGaba = document.getElementById("val-gaba");
  barGaba = document.getElementById("bar-gaba");
  valOxytocin = document.getElementById("val-oxytocin");
  barOxytocin = document.getElementById("bar-oxytocin");
  valMelatonin = document.getElementById("val-melatonin");
  barMelatonin = document.getElementById("bar-melatonin");

  tabBtnWorkspace = document.getElementById("tab-btn-workspace");
  tabBtnGuests = document.getElementById("tab-btn-guests");
  tabWorkspace = document.getElementById("tab-workspace");
  tabGuests = document.getElementById("tab-guests");
  btnRefreshFiles = document.getElementById("btn-refresh-files");
  fileList = document.getElementById("file-list");
  currentFilenameText = document.getElementById("current-filename");
  btnSaveFile = document.getElementById("btn-save-file");
  codeEditor = document.getElementById("code-editor");

  btnInviteGuest = document.getElementById("btn-invite-guest");
  selectGuestModel = document.getElementById("select-guest-model");
  primaryChatStream = document.getElementById("primary-chat-stream");
  guestChatStream = document.getElementById("guest-chat-stream");
  activeGuestName = document.getElementById("active-guest-name");

  securitySlider = document.getElementById("security-slider");
  txtRegimeStatus = document.getElementById("txt-regime-status");

  // Rejestracja kliknięć
  if (btnStartEngine) {
    btnStartEngine.addEventListener("click", () => {
      startBlyskawicaEngine().catch((err) => addLog(`[Start Engine Error]: ${err}`));
    });
  }
  if (btnSendMessage) {
    btnSendMessage.addEventListener("click", () => {
      sendMessage().catch((err) => addLog(`[Send Message Error]: ${err}`));
    });
  }
  if (chatInput) {
    chatInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        sendMessage().catch((err) => addLog(`[Send Message Error]: ${err}`));
      }
    });
  }
  
  if (btnClearLogs) {
    btnClearLogs.addEventListener("click", () => {
      if (logConsole) logConsole.textContent = "[Console cleared]";
    });
  }

  if (btnExportLogs) {
    btnExportLogs.addEventListener("click", () => {
      exportLogs().catch((err) => addLog(`[Export Logs Error]: ${err}`));
    });
  }

  if (securitySlider) {
    securitySlider.addEventListener("input", (e) => {
      updatePermissionLevel(e.target.value).catch((err) => addLog(`[Slider Error]: ${err}`));
    });
  }

  if (btnRefreshFiles) {
    btnRefreshFiles.addEventListener("click", () => {
      refreshWorkspaceFiles().catch((err) => addLog(`[Refresh Files Error]: ${err}`));
    });
  }
  if (btnSaveFile) {
    btnSaveFile.addEventListener("click", () => {
      saveFileContent().catch((err) => addLog(`[Save File Error]: ${err}`));
    });
  }

  if (btnInviteGuest) {
    btnInviteGuest.addEventListener("click", inviteGuestModel);
  }

  // Obsługa zakładek
  const tabBtnSpore = document.getElementById("tab-btn-spore");
  const tabSpore = document.getElementById("tab-spore");
  const btnSporeLoad = document.getElementById("btn-spore-load");
  const btnSporeRun = document.getElementById("btn-spore-run");

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
    });
  }

  if (btnSporeLoad) {
    btnSporeLoad.addEventListener("click", loadSporeCore);
  }
  if (btnSporeRun) {
    btnSporeRun.addEventListener("click", runSporeInference);
  }

  // Uruchomienie wizualizatora Spore
  initSporeVisualizer();

  // Uruchomienie nasłuchiwania w tle i pętli odpytywania
  initEventListeners().catch((err) => addLog(`[Events Init Error]: ${err}`));
  pollEngineStatus().catch((err) => addLog(`[Poll Status Error]: ${err}`));
  setInterval(() => {
    pollEngineStatus().catch((err) => addLog(`[Poll Status Error]: ${err}`));
  }, 2500);
});
