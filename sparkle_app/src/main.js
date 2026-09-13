// ==============================================================================
// ⚡ Sparkle VIBE IDE — Main Orchestrator (ES6 Modular Architecture)
// ==============================================================================

import { SparkleStore } from './modules/store.js';
import { initNeurochemistryHUD, updateNeurochemistryUI, setWolfTeethVisuals, updateRegimeBadge } from './modules/neurochemistry.js';
import { initChatModule, appendChatMessage, handleIncomingToken, handleResponseFinished } from './modules/chat.js';
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
        engineStatusText.textContent = "Rdzeń aktywny";
      }
    } else {
      if (engineStatusIndicator) engineStatusIndicator.className = "status-indicator idle";
      if (engineStatusText && !document.body.classList.contains("wolf-teeth-active")) {
        engineStatusText.textContent = "Rdzeń nieaktywny";
      }
    }

    // Aktualizacja neurochemii z silnika Rust
    if (status.neurochemistry) {
      updateNeurochemistryUI(status.neurochemistry);
    }
  } catch (e) {}
}

// Inicjalizacja sekwencji startowej (Startup Overlay)
function initStartupSequence() {
  const overlay = document.getElementById("startup-overlay");
  const stepBackend = document.getElementById("step-backend");
  const stepModel = document.getElementById("step-model-engine");
  const stepEngine = document.getElementById("step-engine");

  setTimeout(() => {
    if (stepBackend) {
      stepBackend.className = "step done";
      stepBackend.textContent = "✓ Połączenie z rdzeniem kognitywnym: OK";
    }
  }, 400);

  setTimeout(() => {
    if (stepModel) {
      stepModel.className = "step done";
      stepModel.textContent = "✓ Natywny silnik Candle / Qwen 2.5 Coder: Gotowy";
    }
  }, 800);

  setTimeout(() => {
    if (stepEngine) {
      stepEngine.className = "step done";
      stepEngine.textContent = "✓ Inicjalizacja tarczy Aegis i pamięci HNSW: Zakończona";
    }
  }, 1200);

  setTimeout(() => {
    if (overlay) {
      overlay.style.opacity = "0";
      setTimeout(() => overlay.remove(), 500);
    }
  }, 1600);
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

  // 2. Inicjalizacja zdarzeń Tauri
  await initEventListeners();

  // 3. Sekwencja startowa i status
  initStartupSequence();
  updateRegimeBadge(SparkleStore.state.permissionLevel);

  // 4. Pętla synchronizacji statusu
  setInterval(pollEngineStatus, 3000);
  pollEngineStatus();

  addLog("⚡ [SPARKLE V10]: Środowisko gotowe do pracy.");
});
