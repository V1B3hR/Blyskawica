// Neurochemistry HUD & CRA Engine Visualizer Module
import { SparkleStore } from './store.js';

let valDopamine, barDopamine;
let valSerotonin, barSerotonin;
let valGaba, barGaba;
let valOxytocin, barOxytocin;
let valMelatonin, barMelatonin;
let engineStatusIndicator, engineStatusText, txtRegimeStatus;

export function initNeurochemistryHUD() {
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

  engineStatusIndicator = document.getElementById("engine-status-indicator");
  engineStatusText = document.getElementById("engine-status-text");
  txtRegimeStatus = document.getElementById("txt-regime-status");

  // Initial update from store
  updateNeurochemistryUI(SparkleStore.state.neurochemistry);
}

export function updateNeurochemistryUI(ncState) {
  if (!ncState) return;
  SparkleStore.state.neurochemistry = ncState;
  
  const dopamine = ncState.dopamine !== undefined ? ncState.dopamine : 0.0;
  const serotonin = ncState.serotonin !== undefined ? ncState.serotonin : 0.0;
  const gaba = ncState.gaba !== undefined ? ncState.gaba : 0.5;
  const oxytocin = ncState.oxytocin !== undefined ? ncState.oxytocin : 0.0;
  const melatonin = ncState.melatonin !== undefined ? ncState.melatonin : 0.1;

  if (valDopamine) valDopamine.textContent = dopamine.toFixed(2);
  if (valSerotonin) valSerotonin.textContent = serotonin.toFixed(2);
  if (valGaba) valGaba.textContent = gaba.toFixed(2);
  if (valOxytocin) valOxytocin.textContent = oxytocin.toFixed(2);
  if (valMelatonin) valMelatonin.textContent = melatonin.toFixed(2);

  if (barDopamine) barDopamine.style.width = `${Math.min(100, dopamine * 50)}%`;
  if (barSerotonin) barSerotonin.style.width = `${Math.min(100, serotonin * 50)}%`;
  if (barGaba) barGaba.style.width = `${Math.min(100, gaba * 50)}%`;
  if (barOxytocin) barOxytocin.style.width = `${Math.min(100, oxytocin * 50)}%`;
  if (barMelatonin) barMelatonin.style.width = `${Math.min(100, melatonin * 50)}%`;

  // Autonomiczna adaptacja obronna
  if (serotonin < 0.2 && gaba < 0.2) {
    setWolfTeethVisuals(true);
  }
}

export function setWolfTeethVisuals(active) {
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
    updateRegimeBadge(SparkleStore.state.permissionLevel);
  }
}

export function updateRegimeBadge(level) {
  if (!txtRegimeStatus) return;
  document.body.className = `level-${level}`;
  
  if (level === 1) {
    txtRegimeStatus.textContent = "Tryb Sandbox (Poziom 1)";
    txtRegimeStatus.className = "status-badge level-1-badge";
  } else if (level === 2) {
    txtRegimeStatus.textContent = "Katalog Roboczy (Poziom 2)";
    txtRegimeStatus.className = "status-badge level-2-badge";
  } else if (level === 3) {
    txtRegimeStatus.textContent = "Pełny Dostęp do Systemu (Poziom 3)";
    txtRegimeStatus.className = "status-badge level-3-badge";
  }
}
