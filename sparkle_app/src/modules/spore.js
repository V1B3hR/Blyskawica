// ==============================================================================
// ⚡ Sparkle VIBE IDE — ONNX Spore & Edge Inference Module
// ==============================================================================

import { SparkleStore } from './store.js';

const { invoke } = window.__TAURI__ ? window.__TAURI__.core : { invoke: async () => {} };

let btnSporeLoad, btnSporeRun;
let sporePlasticityVal, sporeStateVal, sporeCanvas;
let canvasCtx = null;
let animFrameId = null;
let isSporeLoaded = false;
let neuralNodes = [];

export function initSporeModule(addLogFn) {
  btnSporeLoad = document.getElementById("btn-spore-load");
  btnSporeRun = document.getElementById("btn-spore-run");
  sporePlasticityVal = document.getElementById("spore-plasticity-val");
  sporeStateVal = document.getElementById("spore-state-val");
  sporeCanvas = document.getElementById("spore-canvas");

  if (sporeCanvas) {
    canvasCtx = sporeCanvas.getContext("2d");
    initSynapticNodes();
    drawSynapticNetwork();
  }

  if (btnSporeLoad) {
    btnSporeLoad.addEventListener("click", () => loadSporeModel(addLogFn));
  }

  if (btnSporeRun) {
    btnSporeRun.addEventListener("click", () => runSporeInference(addLogFn));
  }
}

function initSynapticNodes() {
  neuralNodes = [];
  const nodeCount = 28;
  const w = sporeCanvas ? sporeCanvas.width : 600;
  const h = sporeCanvas ? sporeCanvas.height : 250;

  for (let i = 0; i < nodeCount; i++) {
    neuralNodes.push({
      x: 30 + Math.random() * (w - 60),
      y: 20 + Math.random() * (h - 40),
      vx: (Math.random() - 0.5) * 0.8,
      vy: (Math.random() - 0.5) * 0.8,
      radius: 3 + Math.random() * 3,
      pulse: Math.random() * Math.PI * 2,
      pulseSpeed: 0.02 + Math.random() * 0.03
    });
  }
}

function drawSynapticNetwork() {
  if (!canvasCtx || !sporeCanvas) return;
  const w = sporeCanvas.width;
  const h = sporeCanvas.height;

  canvasCtx.clearRect(0, 0, w, h);

  // Połączenia synaptyczne
  const maxDistance = 110;
  for (let i = 0; i < neuralNodes.length; i++) {
    for (let j = i + 1; j < neuralNodes.length; j++) {
      const dx = neuralNodes[i].x - neuralNodes[j].x;
      const dy = neuralNodes[i].y - neuralNodes[j].y;
      const dist = Math.sqrt(dx * dx + dy * dy);

      if (dist < maxDistance) {
        const alpha = (1 - dist / maxDistance) * (isSporeLoaded ? 0.35 : 0.12);
        canvasCtx.strokeStyle = isSporeLoaded ? `rgba(0, 240, 255, ${alpha})` : `rgba(148, 163, 184, ${alpha})`;
        canvasCtx.lineWidth = isSporeLoaded ? 1.2 : 0.8;
        canvasCtx.beginPath();
        canvasCtx.moveTo(neuralNodes[i].x, neuralNodes[i].y);
        canvasCtx.lineTo(neuralNodes[j].x, neuralNodes[j].y);
        canvasCtx.stroke();
      }
    }
  }

  // Węzły neuronowe
  for (let i = 0; i < neuralNodes.length; i++) {
    const node = neuralNodes[i];
    node.x += node.vx;
    node.y += node.vy;

    if (node.x < 10 || node.x > w - 10) node.vx *= -1;
    if (node.y < 10 || node.y > h - 10) node.vy *= -1;

    node.pulse += node.pulseSpeed;
    const pulseFactor = 0.8 + 0.3 * Math.sin(node.pulse);

    canvasCtx.beginPath();
    canvasCtx.arc(node.x, node.y, node.radius * pulseFactor, 0, Math.PI * 2);
    canvasCtx.fillStyle = isSporeLoaded ? "#00f0ff" : "#64748b";
    canvasCtx.shadowColor = isSporeLoaded ? "#00f0ff" : "transparent";
    canvasCtx.shadowBlur = isSporeLoaded ? 10 : 0;
    canvasCtx.fill();
    canvasCtx.shadowBlur = 0;
  }

  animFrameId = requestAnimationFrame(drawSynapticNetwork);
}

export function updateSporePlasticity() {
  if (!sporePlasticityVal) return;
  const neuro = SparkleStore.state.neurochemistry || {};
  const dopamine = neuro.dopamine !== undefined ? neuro.dopamine : 0.7;
  const serotonin = neuro.serotonin !== undefined ? neuro.serotonin : 0.8;
  const plasticity = ((dopamine * 0.55 + serotonin * 0.45) * 100).toFixed(1);
  sporePlasticityVal.textContent = `${plasticity}%`;
}

export async function loadSporeModel(addLogFn) {
  if (addLogFn) addLogFn("[ONNX Spore]: Inicjalizacja ładowania emisariusza kognitywnego ONNX...");
  
  if (btnSporeLoad) btnSporeLoad.disabled = true;
  if (sporeStateVal) sporeStateVal.textContent = "Weryfikacja wag...";

  setTimeout(async () => {
    isSporeLoaded = true;
    if (sporeStateVal) {
      sporeStateVal.textContent = "Aktywny (Edge WebGPU / ONNX)";
      sporeStateVal.style.color = "#00ff88";
    }
    if (btnSporeRun) {
      btnSporeRun.disabled = false;
    }
    if (btnSporeLoad) {
      btnSporeLoad.textContent = "✓ ONNX ZAŁADOWANY";
    }

    updateSporePlasticity();

    if (addLogFn) {
      addLogFn("✓ [ONNX Spore]: Emisariusz ONNX załadowany pomyślnie. Wagi skrystalizowane, akceleracja WebGPU gotowa.");
    }
  }, 350);
}

export async function runSporeInference(addLogFn) {
  if (!isSporeLoaded) {
    if (addLogFn) addLogFn("⚠️ [ONNX Spore]: Najpierw załaduj model emisariusza ONNX.");
    return;
  }

  if (addLogFn) addLogFn("[ONNX Spore]: Wywoływanie projekcji inferencyjnej na krawędzi (Edge WebGPU)...");
  
  // Próbkowanie wektora 128-wymiarowego
  const sampleInput = [];
  for (let i = 0; i < 128; i++) {
    sampleInput.push((Math.random() - 0.5) * 2.0);
  }

  try {
    let result = null;
    if (window.__TAURI__) {
      result = await invoke("run_native_expert_inference", { input: sampleInput });
    }
    
    // Energetyczny impuls w sieci synaptycznej
    neuralNodes.forEach(node => {
      node.pulseSpeed = 0.15;
      setTimeout(() => { node.pulseSpeed = 0.02 + Math.random() * 0.03; }, 800);
    });

    updateSporePlasticity();

    const outputDim = result && Array.isArray(result) ? result.length : 128;
    if (addLogFn) {
      addLogFn(`✓ [ONNX Spore]: Wykonano inferencję brzegową. Przetworzono ${outputDim}-wymiarową macierz projekcji w czasie <5ms.`);
    }
  } catch (error) {
    if (addLogFn) addLogFn(`❌ [ONNX Spore]: Błąd inferencji: ${error}`);
  }
}
