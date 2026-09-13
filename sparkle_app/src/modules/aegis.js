// Aegis Sentinel, Security Posture & Anomaly Quarantine Module
import { SparkleStore } from './store.js';
import { updateRegimeBadge } from './neurochemistry.js';

const { invoke } = window.__TAURI__ ? window.__TAURI__.core : { invoke: async () => {} };

let quarantinedAnomalies = [];
let aegisBadge, hwTelemetryBadge, securitySlider;

export function initAegisModule(addLogFn) {
  aegisBadge = document.getElementById("aegis-sentinel-badge");
  hwTelemetryBadge = document.getElementById("hw-telemetry-badge");
  securitySlider = document.getElementById("security-slider");

  if (securitySlider) {
    securitySlider.value = SparkleStore.state.permissionLevel;
    securitySlider.addEventListener("input", async (e) => {
      const level = parseInt(e.target.value, 10);
      try {
        const res = await invoke("set_permission_level", { level });
        SparkleStore.update("permissionLevel", level);
        updateRegimeBadge(level);
        if (addLogFn) addLogFn(`🛡️ [Uprawnienia]: ${res}`);
      } catch (err) {
        if (addLogFn) addLogFn(`⚠️ [Uprawnienia]: ${err}`);
        securitySlider.value = SparkleStore.state.permissionLevel;
      }
    });
  }

  // Uruchomienie cyklicznej telemetrii sprzętowej
  setInterval(updateHardwareTelemetry, 4000);
  updateHardwareTelemetry();
}

export function addAnomaly(anomaly, addLogFn) {
  quarantinedAnomalies.push({
    id: anomaly.id,
    surprise: anomaly.surprise,
    text: anomaly.text || `Wektor #${anomaly.id}`
  });
  if (addLogFn) {
    addLogFn(`[ANOMALIA ID:${anomaly.id}]: Surprise = ${anomaly.surprise.toFixed(4)}. Wartość wektora poza normą!`);
  }
  renderQuarantineList(addLogFn);
}

export function renderQuarantineList(addLogFn) {
  const listEl = document.getElementById("quarantine-list");
  const countBadge = document.getElementById("quarantine-count-badge");
  if (!listEl) return;

  if (countBadge) {
    countBadge.textContent = `Kolejka kwarantanny: ${quarantinedAnomalies.length} anomalii`;
  }

  if (quarantinedAnomalies.length === 0) {
    const emptyEl = document.createElement("div");
    emptyEl.className = "quarantine-empty";
    emptyEl.style = "padding: 24px; text-align: center; color: var(--text-muted); font-size: 13px;";
    emptyEl.textContent = "Brak zakolejkowanych anomalii. Wszystkie przetworzone wektory pozostają spójne z kotwicą rzeczywistości.";
    listEl.replaceChildren(emptyEl);
    return;
  }

  listEl.replaceChildren();
  quarantinedAnomalies.forEach((item, index) => {
    const itemEl = document.createElement("div");
    itemEl.style = "background: rgba(15, 23, 42, 0.75); border: 1px solid var(--glass-border); border-left: 4px solid #b82eff; border-radius: 6px; padding: 10px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;";
    
    const infoDiv = document.createElement("div");
    const strongId = document.createElement("strong");
    strongId.style.color = "#f0abfc";
    strongId.textContent = `ID #${item.id}`;
    
    const surpriseSpan = document.createElement("span");
    surpriseSpan.style.color = "#f59e0b";
    surpriseSpan.style.fontWeight = "600";
    surpriseSpan.textContent = ` (Zaskoczenie: ${item.surprise.toFixed(4)})`;

    const textSpan = document.createElement("span");
    textSpan.style = "color: var(--text-secondary); font-size: 12px; display: block; margin-top: 4px;";
    textSpan.textContent = `"${item.text}"`;

    infoDiv.appendChild(strongId);
    infoDiv.appendChild(surpriseSpan);
    infoDiv.appendChild(textSpan);

    const actionsDiv = document.createElement("div");
    const btnDismiss = document.createElement("button");
    btnDismiss.className = "control-btn small";
    btnDismiss.textContent = "Odrzuć";
    btnDismiss.style = "background: rgba(239, 68, 68, 0.2); border-color: #ef4444; color: #fca5a5; font-size: 11px;";
    btnDismiss.onclick = () => {
      quarantinedAnomalies.splice(index, 1);
      renderQuarantineList(addLogFn);
      if (addLogFn) addLogFn(`[Epistemic Ledger]: Odrzucono anomalię ID:${item.id}`);
    };

    actionsDiv.appendChild(btnDismiss);
    itemEl.appendChild(infoDiv);
    itemEl.appendChild(actionsDiv);
    listEl.appendChild(itemEl);
  });
}

export async function updateHardwareTelemetry() {
  try {
    const telemetry = await invoke("get_hardware_telemetry");
    if (telemetry && hwTelemetryBadge) {
      const cpu = telemetry.cpu_usage_percent ? telemetry.cpu_usage_percent.toFixed(1) : "0.0";
      const ram = telemetry.memory_usage_percent ? telemetry.memory_usage_percent.toFixed(1) : "0.0";
      hwTelemetryBadge.textContent = `CPU: ${cpu}% | RAM: ${ram}%`;
      
      if (telemetry.thermal_alert) {
        hwTelemetryBadge.style.borderColor = "#ef4444";
        hwTelemetryBadge.style.color = "#fca5a5";
      } else {
        hwTelemetryBadge.style.borderColor = "var(--glass-border)";
        hwTelemetryBadge.style.color = "var(--text-secondary)";
      }
    }
  } catch (e) {}
}

export async function scanLocalModels(addLogFn) {
  try {
    const scanRes = await invoke("scan_local_models");
    if (scanRes && scanRes.models && addLogFn) {
      addLogFn(`🔍 [Wykrywanie Modeli]: Znaleziono ${scanRes.count} lokalnych modeli w systemie.`);
    }
  } catch (e) {}
}
