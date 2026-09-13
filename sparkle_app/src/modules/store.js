// Centralized Reactive State Store for Sparkle VIBE IDE
// Single source of truth for all UI modules

export const SparkleStore = {
  state: {
    currentFileOpen: null,
    permissionLevel: 2,
    isEngineRunning: false,
    neurochemistry: { 
      dopamine: 0.69, 
      serotonin: 0.94, 
      gaba: 0.64, 
      oxytocin: 0.58, 
      melatonin: 0.10,
      cortisol: 0.14,
      temperature: 36.6 
    },
    quarantinedAnomalies: [],
    activeGuestModel: "Brak",
    activeStreamingBubble: null,
    workspacePath: "."
  },
  listeners: [],
  subscribe(fn) {
    this.listeners.push(fn);
    return () => {
      this.listeners = this.listeners.filter(listener => listener !== fn);
    };
  },
  update(key, value) {
    this.state[key] = value;
    this.listeners.forEach(fn => fn(this.state, key, value));
  },
  getState() {
    return this.state;
  }
};

// Global backward-compatible aliases for legacy event handlers
if (typeof window !== 'undefined') {
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
}
