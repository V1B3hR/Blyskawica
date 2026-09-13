// Chat & Language Model Orchestration Module (Tauri Candle SLM)
import { SparkleStore } from './store.js';
import { updateNeurochemistryUI, setWolfTeethVisuals } from './neurochemistry.js';

const { invoke } = window.__TAURI__ ? window.__TAURI__.core : { invoke: async () => {} };

let chatMessages, chatInput, btnSendMessage, btnStartEngine;
let primaryChatStream, guestChatStream, selectGuestModel, btnInviteGuest, activeGuestName;
let activeStreamingBubble = null;

export function initChatModule(addLogFn, refreshFilesFn) {
  chatMessages = document.getElementById("chat-messages");
  chatInput = document.getElementById("chat-input");
  btnSendMessage = document.getElementById("btn-send-message");
  btnStartEngine = document.getElementById("btn-start-engine");
  
  primaryChatStream = document.getElementById("primary-chat-stream");
  guestChatStream = document.getElementById("guest-chat-stream");
  selectGuestModel = document.getElementById("select-guest-model");
  btnInviteGuest = document.getElementById("btn-invite-guest");
  activeGuestName = document.getElementById("active-guest-name");

  if (btnSendMessage) {
    btnSendMessage.addEventListener("click", () => sendMessage(addLogFn));
  }
  if (chatInput) {
    chatInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage(addLogFn);
      }
    });
  }
  if (btnStartEngine) {
    btnStartEngine.addEventListener("click", () => startBlyskawicaEngine(addLogFn, refreshFilesFn));
  }
  if (btnInviteGuest && selectGuestModel && activeGuestName) {
    btnInviteGuest.addEventListener("click", () => {
      const selected = selectGuestModel.value;
      activeGuestName.textContent = selected;
      if (addLogFn) addLogFn(`[Gość Kognitywny]: Zaproszono model '${selected}' do konsultacji.`);
      appendChatMessage("System Sparkle", `Model '${selected}' dołączył do sesji kognitywnej.`, "system-msg");
    });
  }
}

export function appendChatMessage(sender, text, customClass = "") {
  if (!chatMessages) return;
  const msgEl = document.createElement("div");
  msgEl.className = `message ${customClass || (sender === "Użytkownik" ? "user-msg" : "blysk-msg")}`;
  
  const senderStrong = document.createElement("strong");
  senderStrong.textContent = `${sender}: `;
  
  const textSpan = document.createElement("span");
  textSpan.textContent = text;
  
  msgEl.appendChild(senderStrong);
  msgEl.appendChild(textSpan);
  
  chatMessages.appendChild(msgEl);
  chatMessages.scrollTop = chatMessages.scrollHeight;

  if (primaryChatStream && (sender === "Użytkownik" || sender.includes("Błyskawica"))) {
    const miniMsg = msgEl.cloneNode(true);
    primaryChatStream.appendChild(miniMsg);
    primaryChatStream.scrollTop = primaryChatStream.scrollHeight;
  }
}

export async function startBlyskawicaEngine(addLogFn, refreshFilesFn) {
  if (addLogFn) addLogFn("[Tauri]: Wywoływanie komendy start_engine...");
  if (btnStartEngine) btnStartEngine.disabled = true;
  const engineStatusText = document.getElementById("engine-status-text");
  const engineStatusIndicator = document.getElementById("engine-status-indicator");
  if (engineStatusText) engineStatusText.textContent = "Inicjalizacja...";

  try {
    const response = await invoke("start_engine");
    if (addLogFn) addLogFn(`[Tauri]: ${response}`);
    
    SparkleStore.update("isEngineRunning", true);
    if (engineStatusIndicator) engineStatusIndicator.className = "status-indicator active";
    if (engineStatusText) engineStatusText.textContent = "Rdzeń aktywny";
    
    if (chatInput) chatInput.disabled = false;
    if (btnSendMessage) btnSendMessage.disabled = false;
    const codeEditor = document.getElementById("code-editor");
    if (codeEditor) codeEditor.disabled = false;
    
    appendChatMessage("System Sparkle", "Silnik Błyskawicy został wybudzony. Nawiązano połączenie neurochemiczne.", "system-msg");
    
    if (refreshFilesFn) await refreshFilesFn();
  } catch (error) {
    if (addLogFn) addLogFn(`[Tauri Błąd startu]: ${error}`);
    if (btnStartEngine) btnStartEngine.disabled = false;
    if (engineStatusIndicator) engineStatusIndicator.className = "status-indicator idle";
    if (engineStatusText) engineStatusText.textContent = "Błąd inicjalizacji";
    appendChatMessage("System Sparkle", `Nie udało się uruchomić rdzenia: ${error}`, "system-msg");
  }
}

export async function sendMessage(addLogFn) {
  if (!chatInput) return;
  const text = chatInput.value.trim();
  if (!text) return;

  appendChatMessage("Użytkownik", text);
  chatInput.value = "";

  try {
    if (addLogFn) addLogFn(`[Tauri]: Wysyłanie wiadomości do silnika Rust: "${text}"`);
    
    // Skanowanie psychologiczne Aegis Psyche ONNX
    try {
      const vadReport = await invoke("aegis_evaluate_psyche_vad", { text: text });
      if (vadReport && vadReport.is_manipulative) {
        if (addLogFn) addLogFn(`🛡️ [Aegis Psyche ONNX]: Wykryto manipulację! Indeks: ${vadReport.manipulation_index}`);
        if (addLogFn) addLogFn(`🛡️ [Aegis Antidotum]: ${vadReport.assertive_antidote}`);
      } else if (vadReport && vadReport.vad_state_name) {
        if (addLogFn) addLogFn(`✨ [Aegis VAD Rezonans]: Stan '${vadReport.vad_state_name}' (Walencja: ${vadReport.vad_coordinates.valence.toFixed(2)})`);
      }
    } catch (e) {}

    // Bąbel strumieniowania tokenów
    const generatingMsgEl = document.createElement("div");
    generatingMsgEl.className = "message blysk-msg generating";
    const strongHeader = document.createElement("strong");
    strongHeader.textContent = "Błyskawica V10:";
    generatingMsgEl.appendChild(strongHeader);
    generatingMsgEl.appendChild(document.createTextNode(" "));
    for (let i = 0; i < 3; i++) {
      const dot = document.createElement("span");
      dot.className = "typing-dot";
      dot.textContent = ".";
      generatingMsgEl.appendChild(dot);
    }
    chatMessages.appendChild(generatingMsgEl);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    activeStreamingBubble = generatingMsgEl;

    await invoke("send_user_message", { message: text });
  } catch (error) {
    if (activeStreamingBubble) {
      activeStreamingBubble.remove();
      activeStreamingBubble = null;
    }
    if (addLogFn) addLogFn(`[Tauri Błąd]: ${error}`);
    appendChatMessage("Błyskawica V10", "Wystąpił błąd komunikacji z silnikiem kognitywnym.");
  }
}

export function handleIncomingToken(token) {
  if (activeStreamingBubble) {
    if (activeStreamingBubble.classList.contains("generating")) {
      activeStreamingBubble.classList.remove("generating");
      activeStreamingBubble.replaceChildren();
      const senderStrong = document.createElement("strong");
      senderStrong.textContent = "Błyskawica V10: ";
      activeStreamingBubble.appendChild(senderStrong);
    }
    activeStreamingBubble.appendChild(document.createTextNode(token));
    if (chatMessages) chatMessages.scrollTop = chatMessages.scrollHeight;
  }
}

export function handleResponseFinished(fullResponse) {
  if (activeStreamingBubble) {
    activeStreamingBubble.classList.remove("generating");
    activeStreamingBubble.replaceChildren();
    const senderStrong = document.createElement("strong");
    senderStrong.textContent = "Błyskawica V10: ";
    const textSpan = document.createElement("span");
    textSpan.textContent = fullResponse;
    activeStreamingBubble.appendChild(senderStrong);
    activeStreamingBubble.appendChild(textSpan);
    if (chatMessages) chatMessages.scrollTop = chatMessages.scrollHeight;
    synthesizeTTS(fullResponse);
    activeStreamingBubble = null;
  }
}

export function synthesizeTTS(text) {
  if (!text) return;
  const cleanText = text.replace(/<[^>]*>?/gm, '');
  if ('speechSynthesis' in window) {
    try {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(cleanText.substring(0, 300));
      utterance.lang = 'pl-PL';
      utterance.rate = 1.0;
      window.speechSynthesis.speak(utterance);
    } catch (e) {}
  }
}
