// ==============================================================================
// 🌌 Quantum Core, Diamond Yant Cymatics & Shadow Forge Anvil Module
// ==============================================================================

import { SparkleStore } from './store.js';

const { invoke } = window.__TAURI__ ? window.__TAURI__.core : { invoke: async () => {} };

let yantCanvas, yantCtx;
let quantumBadge, yantSymmetryVal, yantStatusVal, yantSerotoninVal;
let shadowGrid, btnRefreshShadowBoard;

export function initQuantumModule(addLogFn) {
  yantCanvas = document.getElementById("yant-oscilloscope-canvas");
  if (yantCanvas) {
    yantCtx = yantCanvas.getContext("2d");
  }

  quantumBadge = document.getElementById("quantum-coherence-badge");
  yantSymmetryVal = document.getElementById("yant-symmetry-val");
  yantStatusVal = document.getElementById("yant-status-val");
  yantSerotoninVal = document.getElementById("yant-serotonin-val");

  shadowGrid = document.getElementById("shadow-board-grid");
  btnRefreshShadowBoard = document.getElementById("btn-refresh-shadow-board");

  if (btnRefreshShadowBoard) {
    btnRefreshShadowBoard.addEventListener("click", () => refreshShadowBoard(addLogFn));
  }

  // Pętla odświeżania cymatyki i stanu kwantowego co 2 sekundy
  setInterval(() => updateQuantumState(addLogFn), 2000);
  updateQuantumState(addLogFn);
  refreshShadowBoard(addLogFn);
}

export async function updateQuantumState(addLogFn) {
  try {
    const qState = await invoke("quantum_get_state");
    if (!qState) return;

    if (quantumBadge) {
      const coherencePercent = Math.round(qState.neuro_coherence * 100);
      quantumBadge.textContent = `⚛️ Splątanie: ${coherencePercent}% | Entropia: ${qState.entanglement_entropy.toFixed(3)}`;
      quantumBadge.style.borderColor = qState.neuro_coherence > 0.8 ? "#38bdf8" : "#f59e0b";
      quantumBadge.style.color = qState.neuro_coherence > 0.8 ? "#bae6fd" : "#fde68a";
    }

    if (yantSerotoninVal) {
      yantSerotoninVal.textContent = `${(qState.neuro_coherence * 1.35).toFixed(2)}x`;
    }

    // Renderowanie 2D matrycy cymatycznej Chladniego na Oscyloskopie Prawdy
    if (qState.cymatics && qState.cymatics.chladni_matrix) {
      renderChladniOscilloscope(qState.cymatics.chladni_matrix, qState.cymatics.mode_n, qState.cymatics.mode_m);
    }
  } catch (e) {}
}

function renderChladniOscilloscope(matrix, n, m) {
  if (!yantCanvas || !yantCtx) return;
  const size = 16;
  const w = yantCanvas.width;
  const h = yantCanvas.height;
  const cellW = w / size;
  const cellH = h / size;

  yantCtx.clearRect(0, 0, w, h);

  let symmetrySum = 0;
  for (let i = 0; i < size; i++) {
    for (let j = 0; j < size; j++) {
      const val = matrix[i * size + j]; // [-1.0, 1.0]
      const oppVal = matrix[(size - 1 - i) * size + (size - 1 - j)];
      symmetrySum += Math.abs(val - oppVal);

      const normalized = (val + 1.0) / 2.0;
      const r = Math.floor(normalized * 50 + 10);
      const g = Math.floor(normalized * 220 + 35);
      const b = Math.floor(255 - normalized * 40);
      const alpha = Math.abs(val) * 0.9 + 0.1;

      yantCtx.fillStyle = `rgba(${r}, ${g}, ${b}, ${alpha})`;
      yantCtx.fillRect(i * cellW, j * cellH, cellW - 1, cellH - 1);
    }
  }

  const symmetryIndex = Math.max(0.1, 1.0 - (symmetrySum / (size * size * 2.0)));
  if (yantSymmetryVal) {
    yantSymmetryVal.textContent = symmetryIndex.toFixed(4);
  }
  if (yantStatusVal) {
    if (symmetryIndex > 0.8) {
      yantStatusVal.textContent = "Harmonic Truth (Synchronized)";
      yantStatusVal.style.color = "#00ff88";
    } else {
      yantStatusVal.textContent = "Epistemic Dissonance / Searching";
      yantStatusVal.style.color = "#f59e0b";
    }
  }
}

export async function refreshShadowBoard(addLogFn) {
  if (!shadowGrid) return;
  try {
    const board = await invoke("get_shadow_board");
    if (!board || !board.tools) return;

    shadowGrid.replaceChildren();

    Object.entries(board.tools).forEach(([toolId, tool]) => {
      const card = document.createElement("div");
      const isHanging = tool.status && tool.status.Hanging;
      card.style = `background: rgba(15, 23, 42, 0.8); border: 1px solid ${isHanging ? '#10b981' : '#b82eff'}; border-radius: 8px; padding: 12px; display: flex; flex-direction: column; gap: 6px;`;

      const header = document.createElement("div");
      header.style = "display: flex; justify-content: space-between; align-items: center;";
      header.innerHTML = `<strong style="color: #00f0ff; font-size: 13px;">${toolId}</strong> <span style="font-size: 11px; padding: 2px 6px; border-radius: 4px; background: ${isHanging ? 'rgba(16, 185, 129, 0.2)' : 'rgba(184, 46, 255, 0.2)'}; color: ${isHanging ? '#6ee7b7' : '#f0abfc'};">${isHanging ? 'WISZĄCE (WYKUTE)' : 'PUSTY CIEŃ'}</span>`;

      const desc = document.createElement("p");
      desc.style = "font-size: 11px; color: var(--text-secondary); margin: 0;";
      desc.textContent = tool.description || "Narzędzie MCP zintegrowane z Tablicą Cieni.";

      const actions = document.createElement("div");
      actions.style = "margin-top: 8px; display: flex; gap: 6px;";
      
      const btnForge = document.createElement("button");
      btnForge.className = "control-btn small";
      btnForge.textContent = isHanging ? "Przekuj na Kowadle" : "Wykuj na Kowadle";
      btnForge.style = "font-size: 11px; padding: 4px 8px;";
      btnForge.onclick = async () => {
        if (addLogFn) addLogFn(`🔨 [Kowadło Kognitywne]: Rozpoczęcie hartowania narzędzia '${toolId}'...`);
        try {
          const sampleCode = `def ${toolId}_execute(params):\n    return {"status": "ok", "result": "Natywne wykonanie narzędzia na kowadle cieni"}`;
          const checksum = await invoke("forge_tool_on_anvil", {
            toolId: toolId,
            code: sampleCode,
            testInput: { test: true }
          });
          if (addLogFn) addLogFn(`✓ [Kowadło]: Narzędzie '${toolId}' wykute pomyślnie! Suma kontrolna: ${checksum.substring(0, 16)}...`);
          await refreshShadowBoard(addLogFn);
        } catch (err) {
          if (addLogFn) addLogFn(`❌ [Błąd Kowadła]: ${err}`);
        }
      };

      actions.appendChild(btnForge);
      card.appendChild(header);
      card.appendChild(desc);
      card.appendChild(actions);
      shadowGrid.appendChild(card);
    });
  } catch (e) {}
}
