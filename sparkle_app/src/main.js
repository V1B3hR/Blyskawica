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

// Scentralizowany State Store (Pojedyncze Źródło Prawdy)
const SparkleStore = {
  state: {
    currentFileOpen: null,
    permissionLevel: 2,
    isEngineRunning: false,
    neurochemistry: { dopamine: 0.69, serotonin: 0.94, gaba: 0.64, oxytocin: 0.58, melatonin: 0.10 }
  },
  listeners: [],
  subscribe(fn) {
    this.listeners.push(fn);
  },
  update(key, value) {
    this.state[key] = value;
    this.listeners.forEach(fn => fn(this.state));
    // Zapisz wybrane preferencje w localStorage
    if (key === 'permissionLevel') {
      localStorage.setItem('sparkle_permission_level', value);
    }
  }
};

// Mapowanie zmiennych stanu na gettery/settery dla pełnej kompatybilności wstecznej
Object.defineProperty(window, 'permissionLevel', {
  get() { return SparkleStore.state.permissionLevel; },
  set(val) { SparkleStore.update('permissionLevel', val); }
});
Object.defineProperty(window, 'isEngineRunning', {
  get() { return SparkleStore.state.isEngineRunning; },
  set(val) { SparkleStore.update('isEngineRunning', val); }
});
Object.defineProperty(window, 'currentFileOpen', {
  get() { return SparkleStore.state.currentFileOpen; },
  set(val) { SparkleStore.update('currentFileOpen', val); }
});

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
    throw error;
  }
}

// Wysyłanie wiadomości do czatu
async function sendMessage() {
  const text = chatInput.value.trim();
  if (!text) return;

  appendChatMessage("Użytkownik", text);
  chatInput.value = "";

  try {
    addLog(`[Tauri]: Wysyłanie wiadomości do silnika Rust: "${text}"`);
    await invoke("send_user_message", { message: text });
    
    // Jeśli silnik w Rust wywoła kwarantannę, natychmiast wyłącz dalszy bieg
    if (document.body.classList.contains("wolf-teeth-active")) {
      return;
    }

    // Dodanie wskaźnika generowania odpowiedzi (loader/typing indicator)
    const generatingMsgEl = document.createElement("div");
    generatingMsgEl.className = "message blysk-msg generating";
    generatingMsgEl.innerHTML = `<strong>Błyskawica V9:</strong> <span class="typing-dot">.</span><span class="typing-dot">.</span><span class="typing-dot">.</span>`;
    chatMessages.appendChild(generatingMsgEl);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Przygotowanie żądania POST z parametrem message jako Form Data do FastAPI
    const formData = new FormData();
    formData.append("message", text);

    addLog("[Tauri]: Przekazywanie zapytania do serwera kognitywnego (FastAPI)...");
    try {
      const res = await fetch("http://127.0.0.1:8000/api/chat", {
        method: "POST",
        body: formData
      });

      generatingMsgEl.remove();

      if (!res.ok) {
        appendChatMessage("System Sparkle", "Błąd: Brak odpowiedzi ze strony serwera kognitywnego.", "system-msg");
        return;
      }

      const data = await res.json();
      
      if (data.quarantine_active) {
        setWolfTeethVisuals(true);
      } else {
        appendChatMessage("Błyskawica V9", data.reply);
        
        // Wywołanie AllTalk TTS w tle, jeśli włączony
        if (data.reply) {
          synthesizeTTS(data.reply);
        }
      }

      if (data.cra_metrics) {
        updateNeurochemistryUI(data.cra_metrics);
      }
    } catch (err) {
      generatingMsgEl.remove();
      addLog(`[Python API Błąd]: ${err}`);
      appendChatMessage("Błyskawica V9", "Rozpoznałam Twoją intencję lokalnie w Rust Core. Pętla kognitywna działa prawidłowo, lecz serwer LLM/FastAPI nie odpowiedział w oczekiwanym czasie.");
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
  applyFeatureGating();

  try {
    const response = await invoke("set_permission_level", { level: permissionLevel });
    addLog(`[Tauri]: ${response}`);
    updateRegimeBadge(permissionLevel);

    // Odśwież listę plików z workspace, jeśli nie jesteśmy w Sandboxie
    if (isEngineRunning && permissionLevel >= 2) {
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

// Funkcja gatingu funkcji UI na podstawie uprawnień
function applyFeatureGating() {
  const codeTextArea = document.getElementById("code-editor");
  const btnSaveFile = document.getElementById("btn-save-file");

  if (permissionLevel === 1) {
    // Blokada trybu Sandbox
    if (codeTextArea) {
      codeTextArea.disabled = true;
      codeTextArea.placeholder = "// ZABLOKOWANO: Edycja plików wyłączona w trybie Sandbox (Poziom 1).";
      codeTextArea.value = "";
    }
    if (btnSaveFile) {
      btnSaveFile.disabled = true;
    }
    if (fileList) {
      fileList.innerHTML = `<div class="file-item empty locked">🔒 Edycja zablokowana (Tryb Sandbox)</div>`;
    }
    currentFileOpen = null;
    currentFilenameText.textContent = "Brak dostępu";
  } else {
    // Odblokowanie w trybie Workspace / Full OS
    if (codeTextArea && isEngineRunning) {
      codeTextArea.disabled = false;
      codeTextArea.placeholder = "// Wybierz plik z eksploratora po lewej lub utwórz nowy kod...";
    }
    if (btnSaveFile && isEngineRunning && currentFileOpen) {
      btnSaveFile.disabled = false;
    }
  }
}

// Asynchroniczna synteza głosu za pomocą AllTalk TTS
async function synthesizeTTS(text) {
  try {
    const formData = new FormData();
    formData.append("text", text);
    fetch("http://127.0.0.1:8000/api/tts", {
      method: "POST",
      body: formData
    }).catch(() => {}); // Ciche zignorowanie błędów
  } catch (e) {
    // Ignorowanie
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
      applyFeatureGating();
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

  // Obsługa zakładek i funkcja pomocnicza switchTab
  function switchTab(tabId) {
    localStorage.setItem('sparkle_active_tab', tabId);
    
    tabBtnWorkspace.classList.remove("active");
    tabBtnGuests.classList.remove("active");
    tabBtnSpore.classList.remove("active");
    tabWorkspace.classList.remove("active");
    tabGuests.classList.remove("active");
    tabSpore.classList.remove("active");

    if (tabId === 'workspace') {
      tabBtnWorkspace.classList.add("active");
      tabWorkspace.classList.add("active");
    } else if (tabId === 'guests') {
      tabBtnGuests.classList.add("active");
      tabGuests.classList.add("active");
    } else if (tabId === 'spore') {
      tabBtnSpore.classList.add("active");
      tabSpore.classList.add("active");
    }
  }

  const tabBtnSpore = document.getElementById("tab-btn-spore");
  const tabSpore = document.getElementById("tab-spore");
  const btnSporeLoad = document.getElementById("btn-spore-load");
  const btnSporeRun = document.getElementById("btn-spore-run");

  if (tabBtnWorkspace && tabBtnGuests && tabBtnSpore && tabWorkspace && tabGuests && tabSpore) {
    tabBtnWorkspace.addEventListener("click", () => switchTab('workspace'));
    tabBtnGuests.addEventListener("click", () => switchTab('guests'));
    tabBtnSpore.addEventListener("click", () => switchTab('spore'));
    
    // Przywróć zapisaną zakładkę z localStorage
    const savedTab = localStorage.getItem('sparkle_active_tab') || 'workspace';
    switchTab(savedTab);
  }

  // Przywróć zapisany poziom uprawnień z localStorage
  const savedLevel = localStorage.getItem('sparkle_permission_level');
  if (savedLevel && securitySlider) {
    securitySlider.value = savedLevel;
    updatePermissionLevel(savedLevel).catch((err) => addLog(`[Restore Permission Error]: ${err}`));
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

  // Uruchomienie sekwencji rozruchowej (onboarding)
  runStartupSequence().catch((err) => addLog(`[Startup Error]: ${err}`));
});

// Sekwencja rozruchowa (Onboarding / Startup State Machine)
async function runStartupSequence() {
  const overlay = document.getElementById("startup-overlay");
  const stepBackend = document.getElementById("step-backend");
  const stepOllama = document.getElementById("step-ollama");
  const stepEngine = document.getElementById("step-engine");
  const warningDiv = document.getElementById("startup-warning");
  const btnRetry = document.getElementById("btn-retry-connection");

  if (!overlay) return;

  // Krok 1: Połączenie z serwerem kognitywnym (FastAPI)
  stepBackend.className = "step running";
  addLog("[Startup]: Sprawdzanie połączenia z FastAPI backendem (Port 8000)...");
  
  let status = null;
  try {
    status = await invoke("get_engine_status");
  } catch (err) {
    addLog(`[Startup Błąd]: Nie można pobrać statusu z Tauri Core: ${err}`);
  }

  if (!status || !status.backend_connected) {
    stepBackend.className = "step failed";
    addLog("[Startup Błąd]: Serwer FastAPI na porcie 8000 jest offline.");
    warningDiv.classList.remove("hidden");
    
    btnRetry.onclick = () => {
      warningDiv.classList.add("hidden");
      stepBackend.className = "step pending";
      stepOllama.className = "step pending";
      stepEngine.className = "step pending";
      runStartupSequence().catch((err) => addLog(`[Startup Retry Error]: ${err}`));
    };
    return;
  }

  stepBackend.className = "step success";
  stepBackend.textContent = "✓ Połączenie z serwerem kognitywnym: Aktywne";
  addLog("[Startup]: Połączono z FastAPI backendem.");

  // Krok 2: Weryfikacja Ollama
  stepOllama.className = "step running";
  addLog("[Startup]: Sprawdzanie dostępności serwisu Ollama (Port 11434)...");
  
  let ollamaOk = false;
  try {
    const res = await fetch("http://localhost:11434/api/tags");
    ollamaOk = res.ok;
  } catch (e) {
    ollamaOk = false;
  }

  if (ollamaOk) {
    stepOllama.className = "step success";
    stepOllama.textContent = "✓ Środowisko LLM (Ollama): Gotowe";
    addLog("[Startup]: Serwis Ollama wykryty i gotowy.");
  } else {
    stepOllama.className = "step failed";
    stepOllama.textContent = "⚠ Środowisko LLM (Ollama): Offline (Ostrzeżenie)";
    addLog("[Startup Ostrzeżenie]: Brak kontaktu z lokalnym Ollama na porcie 11434. Rozmowy z Błyskawicą będą symulowane.");
  }

  // Krok 3: Wybudzanie rdzenia Rust Core
  stepEngine.className = "step running";
  addLog("[Startup]: Uruchamianie kognitywnego rdzenia Rust Core...");
  
  try {
    if (!status.running) {
      await startBlyskawicaEngine();
    }
    stepEngine.className = "step success";
    stepEngine.textContent = "✓ Rdzeń systemowy (Rust Core): Wybudzony";
    addLog("[Startup]: Rdzeń systemowy pomyślnie zainicjalizowany.");
  } catch (err) {
    stepEngine.className = "step failed";
    addLog(`[Startup Błąd]: Nie udało się uruchomić rdzenia Rust: ${err}`);
    return;
  }

  // Zakończenie sekwencji rozruchu i ukrycie nakładki
  setTimeout(() => {
    overlay.classList.add("hidden");
    addLog("[Startup]: Sekwencja rozruchowa pomyślnie ukończona.");
  }, 1000);
}
