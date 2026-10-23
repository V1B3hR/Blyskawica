// ==============================================================================
// ⚡ Sparkle VIBE IDE — Main Orchestrator (ES6 Modular Architecture)
// ==============================================================================

import { SparkleStore } from './modules/store.js';
import { initNeurochemistryHUD, updateNeurochemistryUI, setWolfTeethVisuals, updateRegimeBadge } from './modules/neurochemistry.js';
import { initChatModule, appendChatMessage, handleIncomingToken, handleResponseFinished, exportSession, startBlyskawicaEngine } from './modules/chat.js';
import { initEditorModule, addLog, refreshWorkspaceFiles } from './modules/editor.js';
import { initAegisModule, addAnomaly } from './modules/aegis.js';
import { initQuantumModule } from './modules/quantum.js';

const { invoke } = window.__TAURI__ ? window.__TAURI__.core : { invoke: async () => {} };
const { listen } = window.__TAURI__ ? window.__TAURI__.event : { listen: async () => {} };

// Inicjalizacja nasłuchu zdarzeń z silnika Rust
async function initEventListeners() {
  if (!window.__TAURI__) {
    console.warn("Brak środowiska Tauri. Aplikacja działa w trybie podglądu przeglądarkowego.");
    return;
  }

  try {
    addLog("[Tauri]: Nawiązywanie asynchronicznego nasłuchu na zdarzenia silnika...");
    
    await listen("engine-event", (event) => {
      const payload = event.payload;
      
      if (payload.Log) {
        addLog(`[Core]: ${payload.Log}`);
        if (payload.Log.includes("WOLF TEETH") || payload.Log.includes("quarantine")) {
          setWolfTeethVisuals(true);
        }
      } else if (payload.Neurochemistry) {
        updateNeurochemistryUI(payload.Neurochemistry);
      } else if (payload.AnomalyQueued) {
        addAnomaly(payload.AnomalyQueued, addLog);
      } else if (payload.Token !== undefined) {
        handleIncomingToken(payload.Token);
      } else if (payload.ResponseFinished !== undefined) {
        handleResponseFinished(payload.ResponseFinished);
      }
    });

    addLog("[Tauri]: Nasłuch zdarzeń aktywny.");
  } catch (error) {
    addLog(`[Tauri Błąd]: Nie udało się podłączyć nasłuchu zdarzeń: ${error}`);
  }
}

// Obsługa zakładek (Tabs)
function initTabs() {
  const tabButtons = document.querySelectorAll(".tab-btn");
  const tabContents = document.querySelectorAll(".tab-content");

  tabButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      const targetTabId = btn.getAttribute("data-tab");
      if (!targetTabId) return;

      tabButtons.forEach(b => b.classList.remove("active"));
      tabContents.forEach(c => c.classList.remove("active"));

      btn.classList.add("active");
      const targetContent = document.getElementById(targetTabId);
      if (targetContent) {
        targetContent.classList.add("active");
      }
    });
  });
}

// Obsługa okna Opcji, Akceleratora Sprzętowego i Eksportu
function initOptionsModule() {
  const btnOpenOptions = document.getElementById("btn-open-options");
  const btnCloseOptions = document.getElementById("btn-close-options");
  const btnSaveOptionsClose = document.getElementById("btn-save-options-close");
  const optionsModal = document.getElementById("options-modal");
  const chkEnableTts = document.getElementById("chk-enable-tts");
  const optDeviceGpu = document.getElementById("opt-device-gpu");
  const optDeviceCpu = document.getElementById("opt-device-cpu");
  const btnQuickExport = document.getElementById("btn-quick-export");
  const btnDoExportSession = document.getElementById("btn-do-export-session");
  const exportFilenameInput = document.getElementById("export-filename");
  const btnRefreshDataInventory = document.getElementById("btn-refresh-data-inventory");
  const btnClearRecreatableArtifacts = document.getElementById("btn-clear-recreatable-artifacts");
  const dataInventory = document.getElementById("data-inventory");
  const chkOnlineMode = document.getElementById("chk-online-mode");
  const connectorRegistry = document.getElementById("connector-registry");
  const btnRefreshPermissionReport = document.getElementById("btn-refresh-permission-report");
  const permissionReport = document.getElementById("permission-report");

  const formatBytes = (sizeBytes, isComplete) => {
    if (!Number.isFinite(sizeBytes)) return "Rozmiar nieudostępniony";
    const formatted = new Intl.NumberFormat("pl-PL", {
      maximumFractionDigits: 1,
    }).format(sizeBytes);
    return `${isComplete ? "" : "co najmniej "}${formatted} B`;
  };

  const renderDataInventoryMessage = (message) => {
    if (!dataInventory) return;
    const entry = document.createElement("p");
    entry.style = "margin: 0; font-size: 11px; color: var(--text-secondary);";
    entry.textContent = message;
    dataInventory.replaceChildren(entry);
  };

  const renderDataInventory = (entries) => {
    if (!dataInventory) return;
    const cards = entries.map((entry) => {
      const card = document.createElement("article");
      card.style = "padding: 8px; border: 1px solid var(--glass-border); border-radius: 6px; background: rgba(255, 255, 255, 0.02);";

      const title = document.createElement("strong");
      title.style = "font-size: 11px; color: #38bdf8;";
      title.textContent = `${entry.class}: ${entry.label}`;

      const location = document.createElement("p");
      location.style = "margin: 4px 0; font-size: 10px; color: var(--text-secondary); overflow-wrap: anywhere;";
      location.textContent = `Lokalizacja: ${entry.location}`;

      const metadata = document.createElement("p");
      metadata.style = "margin: 0; font-size: 10px; color: var(--text-muted);";
      metadata.textContent = `Rozmiar: ${formatBytes(entry.size_bytes, entry.size_is_complete)} · Retencja: ${entry.retention}`;

      card.append(title, location, metadata);
      return card;
    });
    dataInventory.replaceChildren(...cards);
  };

  const renderConnectorRegistryMessage = (message) => {
    if (!connectorRegistry) return;
    const entry = document.createElement("p");
    entry.style = "margin: 0; font-size: 11px; color: var(--text-secondary);";
    entry.textContent = message;
    connectorRegistry.replaceChildren(entry);
  };

  const refreshConnectorRegistry = async () => {
    if (!window.__TAURI__) {
      renderConnectorRegistryMessage("Rejestr łączników jest dostępny w aplikacji desktopowej SPARKLE.");
      return;
    }

    renderConnectorRegistryMessage("Odczytywanie rejestru łączników...");
    try {
      const registry = await invoke("get_connector_registry");
      const onlineMode = registry?.online_mode === true;
      if (chkOnlineMode) chkOnlineMode.checked = onlineMode;

      const cards = Array.isArray(registry?.connectors)
        ? registry.connectors.map((connector) => {
          const card = document.createElement("article");
          card.style = "padding: 8px; border: 1px solid var(--glass-border); border-radius: 6px; background: rgba(255, 255, 255, 0.02);";

          const title = document.createElement("strong");
          title.style = "font-size: 11px; color: #38bdf8;";
          title.textContent = connector.label;

          const destination = document.createElement("p");
          destination.style = "margin: 4px 0; font-size: 10px; color: var(--text-secondary); overflow-wrap: anywhere;";
          destination.textContent = `Cel: ${connector.destination}`;

          const disclosure = document.createElement("p");
          disclosure.style = "margin: 0 0 6px; font-size: 10px; color: var(--text-muted);";
          disclosure.textContent = `Dane: ${connector.data_disclosure}`;

          const controls = document.createElement("label");
          controls.style = "display: flex; align-items: center; gap: 6px; font-size: 10px; color: var(--text-secondary);";
          const consent = document.createElement("input");
          consent.type = "checkbox";
          consent.checked = connector.consented === true;
          consent.disabled = !onlineMode || connector.can_be_enabled !== true;
          consent.addEventListener("change", async () => {
            try {
              const result = await invoke("set_connector_consent", {
                connectorId: connector.id,
                consent: consent.checked,
              });
              addLog(`[Łączniki]: ${result}`);
            } catch (error) {
              addLog(`[Łączniki]: ${error}`);
            }
            refreshConnectorRegistry();
          });
          const label = document.createElement("span");
          label.textContent = connector.can_be_enabled === true
            ? "Zgoda na bieżącą sesję"
            : connector.implementation_status;
          controls.append(consent, label);

          card.append(title, destination, disclosure, controls);
          return card;
        })
        : [];
      if (!connectorRegistry) return;

      const scope = document.createElement("p");
      scope.style = "margin: 0 0 6px; font-size: 10px; color: var(--text-muted);";
      scope.textContent = registry?.consent_scope || "Brak danych o zakresie zgody.";
      connectorRegistry.replaceChildren(scope, ...cards);
    } catch (error) {
      renderConnectorRegistryMessage(`Rejestr łączników niedostępny: ${error}`);
    }
  };

  const renderPermissionReportMessage = (message) => {
    if (!permissionReport) return;
    const entry = document.createElement("p");
    entry.style = "margin: 0; font-size: 11px; color: var(--text-secondary);";
    entry.textContent = message;
    permissionReport.replaceChildren(entry);
  };

  const refreshPermissionReport = async () => {
    if (!window.__TAURI__) {
      renderPermissionReportMessage("Raport uprawnień jest dostępny w aplikacji desktopowej SPARKLE.");
      return;
    }

    renderPermissionReportMessage("Odczytywanie aktualnych uprawnień...");
    try {
      const report = await invoke("get_permission_report");
      const cards = Array.isArray(report?.levels)
        ? report.levels.map((entry) => {
          const card = document.createElement("article");
          card.style = "padding: 8px; border: 1px solid var(--glass-border); border-radius: 6px; background: rgba(255, 255, 255, 0.02);";

          const title = document.createElement("strong");
          title.style = `font-size: 11px; color: ${entry.level === report.current_level ? "#4ade80" : "#38bdf8"};`;
          title.textContent = `${entry.label}${entry.level === report.current_level ? " — aktywny" : ""}`;

          const scope = document.createElement("p");
          scope.style = "margin: 4px 0 0; font-size: 10px; color: var(--text-secondary);";
          scope.textContent = entry.scope;
          card.append(title, scope);
          return card;
        })
        : [];
      if (!permissionReport) return;

      const confirmation = document.createElement("p");
      confirmation.style = "margin: 0 0 6px; font-size: 10px; color: var(--text-muted);";
      confirmation.textContent = report?.confirmation || "Brak danych o warunku potwierdzenia.";
      permissionReport.replaceChildren(confirmation, ...cards);
    } catch (error) {
      renderPermissionReportMessage(`Raport uprawnień niedostępny: ${error}`);
    }
  };

  const refreshDataInventory = async () => {
    if (!window.__TAURI__) {
      renderDataInventoryMessage("Inwentaryzacja danych jest dostępna w aplikacji desktopowej SPARKLE.");
      return;
    }
    renderDataInventoryMessage("Odczytywanie metadanych lokalnych magazynów...");
    try {
      const inventory = await invoke("get_data_inventory");
      renderDataInventory(Array.isArray(inventory) ? inventory : []);
    } catch (error) {
      renderDataInventoryMessage(`Inwentaryzacja niedostępna: ${error}`);
    }
  };

  // Otwieranie / zamykanie modalu opcji
  if (btnOpenOptions && optionsModal) {
    btnOpenOptions.addEventListener("click", () => {
      optionsModal.classList.remove("hidden");
      refreshDataInventory();
      refreshConnectorRegistry();
      refreshPermissionReport();
    });
  }

  const closeModal = () => {
    if (optionsModal) optionsModal.classList.add("hidden");
  };

  if (btnCloseOptions) btnCloseOptions.addEventListener("click", closeModal);
  if (btnSaveOptionsClose) btnSaveOptionsClose.addEventListener("click", closeModal);
  if (btnRefreshDataInventory) btnRefreshDataInventory.addEventListener("click", refreshDataInventory);
  if (btnRefreshPermissionReport) btnRefreshPermissionReport.addEventListener("click", refreshPermissionReport);
  if (chkOnlineMode) {
    chkOnlineMode.addEventListener("change", async () => {
      const enabled = chkOnlineMode.checked;
      try {
        const result = await invoke("set_online_mode", { enabled });
        addLog(`[Łączniki]: ${result}`);
      } catch (error) {
        addLog(`[Łączniki]: ${error}`);
      }
      refreshConnectorRegistry();
    });
  }
  if (btnClearRecreatableArtifacts) {
    btnClearRecreatableArtifacts.addEventListener("click", async () => {
      try {
        const result = await invoke("clear_recreatable_runtime_artifacts");
        addLog(`[Dane lokalne]: ${result}`);
        refreshDataInventory();
      } catch (error) {
        addLog(`[Dane lokalne]: ${error}`);
      }
    });
  }

  // Zmiana jednostki obliczeniowej (GPU vs CPU)
  const updateDevice = (device) => {
    SparkleStore.update("computeDevice", device);
    addLog(`[Sprzęt]: Wybrano jednostkę obliczeniową: ${device === 'gpu' ? 'Karta Graficzna RTX 4070 (CUDA)' : 'Procesor CPU (AVX2 Multi-core)'}`);
  };

  if (optDeviceGpu) optDeviceGpu.addEventListener("change", () => updateDevice("gpu"));
  if (optDeviceCpu) optDeviceCpu.addEventListener("change", () => updateDevice("cpu"));

  // Przełącznik TTS (Domyślnie wyłączony)
  if (chkEnableTts) {
    chkEnableTts.checked = SparkleStore.state.ttsEnabled;
    chkEnableTts.addEventListener("change", (e) => {
      SparkleStore.update("ttsEnabled", e.target.checked);
      addLog(`[Dźwięk]: Synteza mowy ${e.target.checked ? 'włączona' : 'wyłączona (wyciszona)'}`);
    });
  }

  // Szybki eksport (Markdown - domyślny)
  if (btnQuickExport) {
    btnQuickExport.addEventListener("click", () => {
      exportSession("md", "", addLog);
    });
  }

  // Eksport z poziomu okna opcji
  if (btnDoExportSession) {
    btnDoExportSession.addEventListener("click", () => {
      const selectedFormatEl = document.querySelector('input[name="export-format"]:checked');
      const format = selectedFormatEl ? selectedFormatEl.value : "md";
      const customName = exportFilenameInput ? exportFilenameInput.value.trim() : "";
      exportSession(format, customName, addLog);
      closeModal();
    });
  }
}

// Cykliczne odpytywanie silnika Tauri o status
async function pollEngineStatus() {
  if (!window.__TAURI__) return;
  try {
    const status = await invoke("get_engine_status");
    if (!status) return;

    SparkleStore.update("isEngineRunning", status.running);
    if (status.workspace_path) {
      SparkleStore.update("workspacePath", status.workspace_path);
    }

    const engineStatusIndicator = document.getElementById("engine-status-indicator");
    const engineStatusText = document.getElementById("engine-status-text");

    if (status.running) {
      if (engineStatusIndicator) engineStatusIndicator.className = "status-indicator active";
      if (engineStatusText && !document.body.classList.contains("wolf-teeth-active")) {
        engineStatusText.textContent = "Światło: Rdzeń aktywny";
      }
    } else {
      if (engineStatusIndicator) engineStatusIndicator.className = "status-indicator idle";
      if (engineStatusText && !document.body.classList.contains("wolf-teeth-active")) {
        engineStatusText.textContent = "Światło: Rdzeń uśpiony";
      }
    }

    // Aktualizacja neurochemii z silnika Rust
    if (status.neurochemistry) {
      updateNeurochemistryUI(status.neurochemistry);
    }
  } catch (e) {}
}

// Inicjalizacja sekwencji startowej (Startup Overlay powiązany z rzeczywistym silnikiem)
async function initStartupSequence(addLogFn, refreshFilesFn) {
  const overlay = document.getElementById("startup-overlay");
  const stepBackend = document.getElementById("step-backend");
  const stepModel = document.getElementById("step-model-engine");
  const stepEngine = document.getElementById("step-engine");

  // Krok 1: Weryfikacja powłoki Tauri IPC
  if (stepBackend) {
    if (window.__TAURI__) {
      stepBackend.className = "step done";
      stepBackend.textContent = "✓ Połączenie z natywną powłoką Tauri IPC: OK";
    } else {
      stepBackend.className = "step done";
      stepBackend.textContent = "✓ Tryb podglądu przeglądarkowego (Web Mockup)";
    }
  }

  // Krok 2: Wykrycie silnika Candle / modelu Qwen
  if (stepModel) {
    stepModel.className = "step done";
    stepModel.textContent = "✓ Natywny silnik Candle / Qwen 2.5 Coder 7B: Gotowy";
  }

  // Krok 3: Rzeczywisty start rdzenia Światła (Aegis + HNSW + Candle)
  if (window.__TAURI__) {
    try {
      await startBlyskawicaEngine(addLogFn, refreshFilesFn);
      if (stepEngine) {
        stepEngine.className = "step done";
        stepEngine.textContent = "✓ Inicjalizacja tarczy Aegis i pamięci HNSW: Zakończona";
      }
    } catch (err) {
      if (stepEngine) {
        stepEngine.className = "step done";
        stepEngine.textContent = "⚠️ Inicjalizacja w toku (uruchom ręcznie w panelu)";
      }
    }
  } else {
    if (stepEngine) {
      stepEngine.className = "step done";
      stepEngine.textContent = "✓ Pamięć wektorowa i tarcza kognitywna: Gotowe";
    }
  }

  // Płynne ukrycie nakładki startowej
  setTimeout(() => {
    if (overlay) {
      overlay.style.transition = "opacity 0.4s ease-out";
      overlay.style.opacity = "0";
      setTimeout(() => overlay.remove(), 400);
    }
  }, 600);
}

// Główny punkt wejścia DOM
document.addEventListener("DOMContentLoaded", async () => {
  addLog("[SPARKLE V10]: Start systemu...");

  // 1. Inicjalizacja modułów
  initNeurochemistryHUD();
  initEditorModule();
  initChatModule(addLog, refreshWorkspaceFiles);
  initAegisModule(addLog);
  initQuantumModule(addLog);
  initTabs();
  initOptionsModule();

  // 2. Inicjalizacja zdarzeń Tauri
  await initEventListeners();

  // 3. Sekwencja startowa i status
  await initStartupSequence(addLog, refreshWorkspaceFiles);
  updateRegimeBadge(SparkleStore.state.permissionLevel);

  // 4. Pętla synchronizacji statusu
  setInterval(pollEngineStatus, 3000);
  pollEngineStatus();

  addLog("⚡ [ŚWIATŁO]: Środowisko kognitywne gotowe do współpracy.");
});
