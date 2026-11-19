// ==============================================================================
// ⚡ Sparkle VIBE IDE — Modular Tauri v2 IPC Bridge (SEC-04: withGlobalTauri disabled)
// ==============================================================================

import { invoke as tauriInvoke, isTauri as tauriIsTauri } from "@tauri-apps/api/core";
import { listen as tauriListen } from "@tauri-apps/api/event";

let testBridge = null;

export function setTauriTestBridge(bridge) {
  testBridge = bridge;
}

export function isTauriRuntime() {
  if (testBridge) {
    return true;
  }
  return Boolean(
    typeof window !== "undefined" &&
      (window.__TAURI_INTERNALS__ || tauriIsTauri()),
  );
}

export async function invoke(command, args) {
  if (testBridge?.invoke) {
    return testBridge.invoke(command, args);
  }
  if (!isTauriRuntime()) {
    return undefined;
  }
  return tauriInvoke(command, args);
}

export async function listen(event, handler) {
  if (testBridge?.listen) {
    return testBridge.listen(event, handler);
  }
  if (!isTauriRuntime()) {
    return () => {};
  }
  return tauriListen(event, handler);
}
