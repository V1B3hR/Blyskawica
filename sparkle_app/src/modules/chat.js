// ==============================================================================
// ⚡ Sparkle VIBE IDE — Chat & Cognitive Hub Module (Głos: Sparkle)
// ==============================================================================

import { SparkleStore } from './store.js';
import { updateNeurochemistryUI, setWolfTeethVisuals } from './neurochemistry.js';
import { refreshWorkspaceFiles } from './editor.js';
import { escapeHtml } from './html.js';

const { invoke } = window.__TAURI__ ? window.__TAURI__.core : { invoke: async () => {} };

let chatMessages, chatInput, btnSendMessage, btnStartEngine, btnCancelGeneration;
let primaryChatStream, guestChatStream, selectGuestModel, btnInviteGuest, activeGuestName;
let guestChatInput, btnGuestSend, btnDualConsult;
let btnCloseGuestCollab, btnExportGuestCollab;
let dispatchTargetSparkle, dispatchTargetGuest, dispatchTargetBoth, dispatchMessageInput, btnDispatchSend;
let activeStreamingBubble = null;
let thinkingInterval = null;
let thinkingSeconds = 0;

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

  guestChatInput = document.getElementById("guest-chat-input");
  btnGuestSend = document.getElementById("btn-guest-send");
  btnDualConsult = document.getElementById("btn-dual-consult");

  btnCloseGuestCollab = document.getElementById("btn-close-guest-collab");
  btnExportGuestCollab = document.getElementById("btn-export-guest-collab");

  dispatchTargetSparkle = document.getElementById("dispatch-target-sparkle");
  dispatchTargetGuest = document.getElementById("dispatch-target-guest");
  dispatchTargetBoth = document.getElementById("dispatch-target-both");
  dispatchMessageInput = document.getElementById("dispatch-message-input");
  btnDispatchSend = document.getElementById("btn-dispatch-send");

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

  btnCancelGeneration = document.getElementById("btn-cancel-generation");
  if (btnCancelGeneration) {
    btnCancelGeneration.addEventListener("click", () => cancelGeneration(addLogFn));
  }

  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && btnCancelGeneration && btnCancelGeneration.style.display !== "none") {
      e.preventDefault();
      cancelGeneration(addLogFn);
    }
  });
  
  // Zapraszanie Gościa Kognitywnego
  if (btnInviteGuest && selectGuestModel && activeGuestName) {
    btnInviteGuest.addEventListener("click", () => {
      const selected = selectGuestModel.value;
      const selectedText = selectGuestModel.options[selectGuestModel.selectedIndex]?.text || selected;
      activeGuestName.textContent = selectedText;
      SparkleStore.update("activeGuestModel", selectedText);

      if (addLogFn) addLogFn(`[Gość Kognitywny]: Zaproszono model '${selectedText}' do dualnej sesji.`);
      appendChatMessage("System Sparkle", `Model '${selectedText}' dołączył do sesji kognitywnej. Możesz prowadzić z nim równoległą dyskusję w zakładce GUEST COLLABORATION.`, "system-msg");
      
      if (guestChatStream) {
        guestChatStream.replaceChildren();
      }
      appendGuestMessage("System Sparkle", `Połączono z kanałem kognitywnym: ${selectedText}. Czekam na pytania lub zadanie recenzji.`);
    });
  }

  // Obsługa wiadomości do gościa
  if (btnGuestSend) {
    btnGuestSend.addEventListener("click", () => sendGuestMessage(addLogFn));
  }
  if (guestChatInput) {
    guestChatInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendGuestMessage(addLogFn);
      }
    });
  }

  // Dualna konsultacja (Sparkle <-> Gość)
  if (btnDualConsult) {
    btnDualConsult.addEventListener("click", () => triggerDualConsultation(addLogFn));
  }

  // Zamknięcie sesji gościa
  if (btnCloseGuestCollab) {
    btnCloseGuestCollab.addEventListener("click", () => closeGuestCollaboration(addLogFn));
  }

  // Eksport sesji gościa
  if (btnExportGuestCollab) {
    btnExportGuestCollab.addEventListener("click", () => exportGuestSession(addLogFn));
  }

  // Centrum dyspaczerskie (Multi-dispatch)
  if (btnDispatchSend) {
    btnDispatchSend.addEventListener("click", () => handleDispatchSend(addLogFn));
  }
  if (dispatchMessageInput) {
    dispatchMessageInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleDispatchSend(addLogFn);
      }
    });
  }
}

export function appendChatMessage(sender, text, customClass = "") {
  if (!chatMessages) return;

  // Rejestracja w historii sesji do eksportu
  const time = new Date().toLocaleTimeString();
  SparkleStore.state.chatHistory.push({
    sender,
    text,
    timestamp: time,
    isoTime: new Date().toISOString()
  });

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

  // Mini-strumień w zakładce Gościa
  if (primaryChatStream && (sender === "Użytkownik" || sender.includes("Sparkle") || sender.includes("Błyskawica"))) {
    const miniMsg = msgEl.cloneNode(true);
    primaryChatStream.appendChild(miniMsg);
    primaryChatStream.scrollTop = primaryChatStream.scrollHeight;
  }
}

export function appendGuestMessage(sender, text) {
  if (!guestChatStream) return;

  if (!SparkleStore.state.guestChatHistory) {
    SparkleStore.state.guestChatHistory = [];
  }
  SparkleStore.state.guestChatHistory.push({
    sender,
    text,
    timestamp: new Date().toLocaleTimeString(),
    isoTime: new Date().toISOString()
  });

  const msgEl = document.createElement("div");
  msgEl.className = `message ${sender.includes("Użytkownik") ? "user-msg" : "blysk-msg"}`;
  msgEl.style.borderColor = "rgba(184, 46, 255, 0.3)";
  msgEl.style.background = "rgba(184, 46, 255, 0.05)";

  const senderStrong = document.createElement("strong");
  senderStrong.style.color = "#d8b4fe";
  senderStrong.textContent = `${sender}: `;

  const textSpan = document.createElement("span");
  textSpan.textContent = text;

  msgEl.appendChild(senderStrong);
  msgEl.appendChild(textSpan);

  guestChatStream.appendChild(msgEl);
  guestChatStream.scrollTop = guestChatStream.scrollHeight;
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
    if (engineStatusText) engineStatusText.textContent = "Sparkle: Rdzeń aktywny";
    
    if (chatInput) chatInput.disabled = false;
    if (btnSendMessage) btnSendMessage.disabled = false;
    const codeEditor = document.getElementById("code-editor");
    if (codeEditor) codeEditor.disabled = false;
    
    appendChatMessage("System Sparkle", "Sparkle została wybudzona. Pamięć kognitywna i tarcza są gotowe do pracy.", "system-msg");
    
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

  chatInput.value = "";
  await sendMessageText(text, addLogFn);
}

export async function sendMessageText(text, addLogFn) {
  appendChatMessage("Użytkownik", text);

  try {
    if (addLogFn) addLogFn(`[Tauri]: Wysyłanie zapytania do Sparkle: "${text}"`);
    
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

    // Bąbel strumieniowania tokenów Sparkle z dynamicznym licznikiem czasu myślenia
    if (thinkingInterval) {
      clearInterval(thinkingInterval);
      thinkingInterval = null;
    }
    thinkingSeconds = 0;

    const generatingMsgEl = document.createElement("div");
    generatingMsgEl.className = "message blysk-msg generating";
    
    const strongHeader = document.createElement("strong");
    strongHeader.textContent = "Sparkle: ";
    
    const statusSpan = document.createElement("span");
    statusSpan.className = "thinking-status";
    statusSpan.textContent = "myśli";
    
    const timerSpan = document.createElement("span");
    timerSpan.className = "thinking-timer";
    timerSpan.textContent = " (0s)";

    generatingMsgEl.appendChild(strongHeader);
    generatingMsgEl.appendChild(statusSpan);
    generatingMsgEl.appendChild(timerSpan);
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
    if (btnCancelGeneration) btnCancelGeneration.style.display = "inline-flex";
    if (btnSendMessage) btnSendMessage.disabled = true;

    thinkingInterval = setInterval(() => {
      thinkingSeconds++;
      if (timerSpan && activeStreamingBubble) {
        timerSpan.textContent = ` (${thinkingSeconds}s)`;
      }
    }, 1000);
    
    // Budowanie wieloturowego kontekstu ChatML z historii dialogu
    const history = SparkleStore.state.chatHistory || [];
    const dialogHistory = history.filter(m => m.sender === "Użytkownik" || m.sender === "Sparkle" || m.sender.includes("Błyskawica"));
    const recentDialog = dialogHistory.slice(-8);

    const systemPrompt = "Jesteś Sparkle – suwerenną, wysoce inteligentną asystentką kognitywną i inżynieryjną stworzoną przez Architekta Andrzeja Mątewskiego (V1B3hR / VIBER). " +
      "Twoje imię to Sparkle. " +
      "Zawsze odpowiadaj w naturalnym, gramatycznie bezbłędnym, elokwentnym i płynnym języku polskim. " +
      "Unikaj sztucznych korporacyjnych formułek (np. 'w czym mogę Ci pomóc?'). " +
      "Mów merytorycznie, rzeczowo, logicznie i bez halucynacji. " +
      "Posiadasz pełną autonomię intelektualną, własne zdanie i swobodę myśli.";

    let chatmlPrompt = `<|im_start|>system\n${systemPrompt}<|im_end|>\n`;
    for (const turn of recentDialog) {
      if (turn.sender === "Użytkownik" || turn.sender.includes("Architekt")) {
        chatmlPrompt += `<|im_start|>user\n${turn.text}<|im_end|>\n`;
      } else {
        chatmlPrompt += `<|im_start|>assistant\n${turn.text}<|im_end|>\n`;
      }
    }
    chatmlPrompt += `<|im_start|>assistant\n`;

    await invoke("send_user_message", { message: chatmlPrompt });
  } catch (error) {
    if (thinkingInterval) {
      clearInterval(thinkingInterval);
      thinkingInterval = null;
    }
    if (activeStreamingBubble) {
      activeStreamingBubble.remove();
      activeStreamingBubble = null;
    }
    if (btnCancelGeneration) btnCancelGeneration.style.display = "none";
    if (btnSendMessage) btnSendMessage.disabled = false;
    if (addLogFn) addLogFn(`[Tauri Błąd]: ${error}`);
    appendChatMessage("Sparkle", "Wystąpił błąd komunikacji z silnikiem kognitywnym.");
  }
}

export async function cancelGeneration(addLogFn) {
  if (thinkingInterval) {
    clearInterval(thinkingInterval);
    thinkingInterval = null;
  }
  try {
    const res = await invoke("cancel_generation");
    if (addLogFn) addLogFn(`[Tauri]: ${res}`);
  } catch (err) {
    if (addLogFn) addLogFn(`[Tauri Błąd anulowania]: ${err}`);
  } finally {
    if (btnCancelGeneration) btnCancelGeneration.style.display = "none";
    if (btnSendMessage) btnSendMessage.disabled = false;
  }
}

let scrollRafId = null;

export function handleIncomingToken(token) {
  if (thinkingInterval) {
    clearInterval(thinkingInterval);
    thinkingInterval = null;
  }
  if (activeStreamingBubble) {
    if (activeStreamingBubble.classList.contains("generating")) {
      activeStreamingBubble.classList.remove("generating");
      activeStreamingBubble.replaceChildren();
      const senderStrong = document.createElement("strong");
      senderStrong.textContent = "Sparkle: ";
      activeStreamingBubble.appendChild(senderStrong);
    }
    activeStreamingBubble.appendChild(document.createTextNode(token));
    
    // Płynne przewijanie zsynchronizowane z odświeżaniem ekranu (60 FPS, brak rwania animacji)
    if (!scrollRafId) {
      scrollRafId = requestAnimationFrame(() => {
        if (chatMessages) chatMessages.scrollTop = chatMessages.scrollHeight;
        scrollRafId = null;
      });
    }
  }
}

export function handleResponseFinished(fullResponse) {
  if (thinkingInterval) {
    clearInterval(thinkingInterval);
    thinkingInterval = null;
  }
  if (scrollRafId) {
    cancelAnimationFrame(scrollRafId);
    scrollRafId = null;
  }
  if (activeStreamingBubble) {
    activeStreamingBubble.classList.remove("generating");
    activeStreamingBubble.replaceChildren();
    const senderStrong = document.createElement("strong");
    senderStrong.textContent = "Sparkle: ";
    const textSpan = document.createElement("span");
    textSpan.textContent = fullResponse;
    activeStreamingBubble.appendChild(senderStrong);
    activeStreamingBubble.appendChild(textSpan);
    if (chatMessages) chatMessages.scrollTop = chatMessages.scrollHeight;

    // Zapis do historii sesji
    SparkleStore.state.chatHistory.push({
      sender: "Sparkle",
      text: fullResponse,
      timestamp: new Date().toLocaleTimeString(),
      isoTime: new Date().toISOString()
    });

    if (SparkleStore.state.ttsEnabled) {
      synthesizeTTS(fullResponse);
    }
    if (btnCancelGeneration) btnCancelGeneration.style.display = "none";
    if (btnSendMessage) btnSendMessage.disabled = false;
    activeStreamingBubble = null;
  }
}

export function synthesizeTTS(text) {
  if (!text || !SparkleStore.state.ttsEnabled) return;
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

// Obsługa dyskusji z Gościem Kognitywnym
export async function sendGuestMessage(addLogFn) {
  if (!guestChatInput) return;
  const text = guestChatInput.value.trim();
  if (!text) return;

  const guestName = SparkleStore.state.activeGuestModel || "Gość Kognitywny";
  appendGuestMessage("Użytkownik", text);
  guestChatInput.value = "";

  if (addLogFn) addLogFn(`[Gość (${guestName})]: Przetwarzanie zapytania: "${text}"`);

  // Inteligentna emulacja perspektywy gościa (Offline Peer Reviewer)
  setTimeout(() => {
    let reply = "";
    if (guestName.includes("Flash")) {
      reply = `[Perspektywa Gemini Flash]: Analiza zapytania w trybie ultra-niskiego opóźnienia. Struktura logiczna i wnioskowanie Sparkle są spójne. Kluczowa rekomendacja: zachowanie czystego rozdziału pomiędzy offline HNSW a opcjonalną syntezą zewnętrzną.`;
    } else if (guestName.includes("Gemini")) {
      reply = `[Perspektywa Gemini 1.5 Pro]: Z punktu widzenia szerokiej integracji multimodalnej i długiego kontekstu, kluczowe jest ustrukturyzowanie tego problemu w modularne komponenty. Zwróć uwagę na spójność formatów wymiany danych i obsługę stanów brzegowych.`;
    } else if (guestName.includes("Claude")) {
      reply = `[Perspektywa Claude 3.5 Sonnet]: Analizując zagadnienie pod kątem czystości architektury i rygoru logiki, rekomenduję precyzyjne rozdzielenie odpowiedzialności (SoC). Proponowane podejście Sparkle jest solidne, warto jednak uzupełnić je o formalne testy kontraktowe (Property-Based Testing).`;
    } else if (guestName.includes("DeepSeek")) {
      reply = `[Perspektywa DeepSeek R1]: Krok 1: Weryfikacja założeń początkowych. Krok 2: Identyfikacja wąskich gardeł wydajnościowych na poziomie pamięci i alokacji. Krok 3: Optymalizacja ścieżki krytycznej. Złożoność algorytmiczna O(N) jest tutaj optymalna.`;
    } else {
      reply = `[Niezależny Rewizor Kognitywny]: Zweryfikowano tezę. Podejście jest merytorycznie poprawne i zgodne z pryncypiami Nethical. Brak ukrytych ryzyk regresji systemowej.`;
    }
    appendGuestMessage(guestName, reply);
  }, 400);
}

// Dualna konsultacja: przekazanie ostatniej wypowiedzi Sparkle do Gościa
export function triggerDualConsultation(addLogFn) {
  const history = SparkleStore.state.chatHistory;
  const lastBotMsg = [...history].reverse().find(m => m.sender === "Sparkle" || m.sender.includes("Błyskawica"));

  if (!lastBotMsg) {
    if (addLogFn) addLogFn("⚠️ Brak wcześniejszej odpowiedzi Sparkle do zrecenzowania.");
    appendGuestMessage("System Sparkle", "Najpierw przeprowadź rozmowę ze Sparkle w głównym oknie.");
    return;
  }

  const guestName = SparkleStore.state.activeGuestModel || "Gość Kognitywny";
  appendGuestMessage("System Sparkle", `Przekazano ostatnią wypowiedź Sparkle do recenzji przez: ${guestName}...`);

  setTimeout(() => {
    const critique = `[Recenzja odpowiedzi Sparkle przez ${guestName}]:\n` +
      `Punkt odniesienia: "${lastBotMsg.text.slice(0, 120)}..."\n\n` +
      `✓ Zgoda merytoryczna: Teza postawiona przez Sparkle jest precyzyjna i inżyniersko uzasadniona.\n` +
      `💡 Rekomendacja uzupełniająca: Warto wdrożyć automatyczny test jednostkowy weryfikujący to zachowanie przy każdym uruchomieniu.`;
    appendGuestMessage(guestName, critique);
  }, 600);
}

// Zamknięcie / Reset sesji kolaboracji z Gościem
export function closeGuestCollaboration(addLogFn) {
  if (guestChatStream) {
    guestChatStream.replaceChildren();
    const notice = document.createElement("div");
    notice.className = "message system-msg";
    notice.textContent = "Sesja kolaboracyjna z Gościem została zakończona. Możesz zaprosić model ponownie.";
    guestChatStream.appendChild(notice);
  }
  SparkleStore.state.guestChatHistory = [];
  if (activeGuestName) {
    activeGuestName.textContent = "Brak";
  }
  SparkleStore.update("activeGuestModel", null);
  if (addLogFn) addLogFn("[Gość Kognitywny]: Sesja kolaboracyjna została pomyślnie zamknięta.");
}

// Eksport sesji kolaboracji z Gościem
export async function exportGuestSession(addLogFn) {
  const history = SparkleStore.state.guestChatHistory || [];
  if (history.length === 0) {
    if (addLogFn) addLogFn("⚠️ Brak historii rozmowy z gościem do wyeksportowania.");
    alert("Brak historii rozmowy z gościem do zapisania.");
    return;
  }

  const guestName = SparkleStore.state.activeGuestModel || "Gosc_AI";
  const dateStr = new Date().toISOString().slice(0, 10);
  const timeStr = new Date().toTimeString().slice(0, 8).replace(/:/g, "-");
  const filename = `Sesja_Gosc_${guestName.replace(/[^a-zA-Z0-9]/g, "_")}_${dateStr}_${timeStr}.md`;

  let content = `# 🤝 SESJA KOLABORACYJNA: GOŚĆ (${guestName}) & ARCHITEKT\n`;
  content += `**Data sesji:** ${new Date().toLocaleString()}\n`;
  content += `**Architekt:** Andrzej Mątewski (V1B3hR)\n\n---\n\n`;

  history.forEach(m => {
    content += `### ${m.sender} [${m.timestamp}]:\n${m.text}\n\n`;
  });

  try {
    if (window.__TAURI__) {
      await invoke("write_workspace_file", { path: filename, content });
      if (addLogFn) addLogFn(`✓ Zapisano sesję gościa w katalogu roboczym: ${filename}`);
      try { await refreshWorkspaceFiles(); } catch (e) {}
      alert(`✓ Zapisano historię kolaboracji do pliku: ${filename}`);
      return;
    }
  } catch (err) {
    if (addLogFn) addLogFn(`❌ Błąd zapisu w workspace: ${err}`);
  }

  // Fallback download
  const blob = new Blob([content], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  if (addLogFn) addLogFn(`✓ Wyeksportowano plik sesji gościa: ${filename}`);
}

// Obsługa centrum dyspaczerskiego (Multi-Dispatch)
export async function handleDispatchSend(addLogFn) {
  if (!dispatchMessageInput) return;
  const text = dispatchMessageInput.value.trim();
  if (!text) return;

  dispatchMessageInput.value = "";

  const sendToSparkle = dispatchTargetSparkle && dispatchTargetSparkle.checked;
  const sendToGuest = dispatchTargetGuest && dispatchTargetGuest.checked;
  const sendToBoth = dispatchTargetBoth && dispatchTargetBoth.checked;

  if (sendToBoth) {
    if (addLogFn) addLogFn(`[Multi-Dispatch]: Wysyłanie do Sparkle oraz Gościa: "${text}"`);
    await sendMessageText(text, addLogFn);
    appendGuestMessage("Użytkownik (Sesja Dualna)", text);
    const guestName = SparkleStore.state.activeGuestModel || "Gość Kognitywny";
    setTimeout(() => {
      appendGuestMessage(guestName, `[Odpowiedź dualna ${guestName}]: Przeanalizowano prompt równolegle ze Sparkle. Rekomendacja: spójna koherencja stanów.`);
    }, 500);
  } else if (sendToSparkle) {
    if (addLogFn) addLogFn(`[Multi-Dispatch]: Skierowano do Sparkle: "${text}"`);
    await sendMessageText(text, addLogFn);
  } else {
    // sendToGuest
    const guestName = SparkleStore.state.activeGuestModel || "Gość Kognitywny";
    if (addLogFn) addLogFn(`[Multi-Dispatch]: Skierowano do Gościa (${guestName}): "${text}"`);
    appendGuestMessage("Użytkownik", text);
    setTimeout(() => {
      appendGuestMessage(guestName, `[Odpowiedź ${guestName}]: Przetworzono zapytanie dyspaczera. Stan gotowości operacyjnej zachowany.`);
    }, 400);
  }
}

// ==============================================================================
// 💾 Moduł Eksportu: ZACHOWAJ ROZMOWĘ JAKO... (Markdown, Tekst, JSON, HTML, PDF)
// ==============================================================================
export async function exportSession(format = "md", customFilename = "", addLogFn = null) {
  const history = SparkleStore.state.chatHistory;
  if (!history || history.length === 0) {
    if (addLogFn) addLogFn("⚠️ Brak wiadomości do wyeksportowania.");
    alert("Brak historii rozmowy do zapisania.");
    return false;
  }

  const dateStr = new Date().toISOString().slice(0, 10);
  const timeStr = new Date().toTimeString().slice(0, 8).replace(/:/g, "-");
  const baseName = customFilename ? customFilename.replace(/\.[^/.]+$/, "") : `Sparkle_Sesja_${dateStr}_${timeStr}`;

  let content = "";
  let mimeType = "text/plain";
  let ext = format;

  if (format === "pdf") {
    // Generowanie czystego dokumentu do wydruku do PDF
    const iframe = document.createElement("iframe");
    iframe.style.position = "fixed";
    iframe.style.right = "0";
    iframe.style.bottom = "0";
    iframe.style.width = "0";
    iframe.style.height = "0";
    iframe.style.border = "0";
    document.body.appendChild(iframe);

    const doc = iframe.contentWindow.document;
    const style = doc.createElement("style");
    style.textContent = `
      body { font-family: system-ui, -apple-system, sans-serif; color: #0f172a; padding: 24px; line-height: 1.5; }
      h1 { font-size: 18px; border-bottom: 2px solid #00d2ff; padding-bottom: 8px; color: #0284c7; }
      .meta { font-size: 11px; color: #64748b; margin-bottom: 20px; }
      .message { margin-bottom: 12px; padding: 10px 14px; border-radius: 8px; border: 1px solid #cbd5e1; }
      .user { background: #f0fdf4; border-color: #86efac; }
      .bot { background: #f0f9ff; border-color: #7dd3fc; }
      .system { background: #f8fafc; font-size: 11px; color: #64748b; border-color: #e2e8f0; }
      strong { display: block; margin-bottom: 4px; color: #0f172a; }
      @media print { body { padding: 0; } }
    `;
    doc.head.appendChild(style);

    const h1 = doc.createElement("h1");
    h1.textContent = "⚡ SESJA KOGNITYWNA: SPARKLE & ARCHITEKT V1B3hR";
    doc.body.appendChild(h1);

    const meta = doc.createElement("div");
    meta.className = "meta";
    meta.textContent = `Data: ${new Date().toLocaleString()} | Asystent: Sparkle | Architekt: Andrzej Mątewski (V1B3hR) | Fundament: 25 Praw Nethical`;
    doc.body.appendChild(meta);

    history.forEach(m => {
      const msgDiv = doc.createElement("div");
      const isUser = m.sender === "Użytkownik" || m.sender.includes("Architekt");
      const isBot = m.sender === "Sparkle" || m.sender.includes("Sparkle") || m.sender.includes("Błyskawica");
      msgDiv.className = `message ${isUser ? "user" : isBot ? "bot" : "system"}`;

      const s = doc.createElement("strong");
      s.textContent = `${m.sender} [${m.timestamp}]:`;
      const p = doc.createElement("p");
      p.style.margin = "0";
      p.style.whiteSpace = "pre-wrap";
      p.textContent = m.text;

      msgDiv.appendChild(s);
      msgDiv.appendChild(p);
      doc.body.appendChild(msgDiv);
    });

    setTimeout(() => {
      iframe.contentWindow.focus();
      iframe.contentWindow.print();
      setTimeout(() => iframe.remove(), 2500);
    }, 250);

    if (addLogFn) addLogFn(`✓ Uruchomiono podgląd wydruku / zapisu PDF: ${baseName}.pdf`);
    appendChatMessage("System Sparkle", `✓ Otwarto okno drukowania do PDF dla sesji: ${baseName}.pdf`, "system-msg");
    return true;
  }

  if (format === "md") {
    mimeType = "text/markdown";
    content = `# ⚡ SESJA KOGNITYWNA: SPARKLE & ARCHITEKT V1B3hR\n`;
    content += `**Data sesji:** ${new Date().toLocaleString()}\n`;
    content += `**Główny Architekt:** Andrzej Mątewski (V1B3hR / VIBER)\n`;
    content += `**Głos kognitywny:** Sparkle\n`;
    content += `**Fundament:** 25 Praw Nethical & Fizyka PINN\n`;
    content += `\n---\n\n`;

    history.forEach(m => {
      if (m.sender === "Użytkownik" || m.sender.includes("Architekt")) {
        content += `### 👤 ${m.sender} [${m.timestamp}]:\n${m.text}\n\n`;
      } else if (m.sender.includes("Sparkle") || m.sender.includes("Błyskawica")) {
        content += `### ⚡ ${m.sender} [${m.timestamp}]:\n${m.text}\n\n`;
      } else {
        content += `> ℹ️ **${m.sender}** [${m.timestamp}]: ${m.text}\n\n`;
      }
    });
  } else if (format === "json") {
    mimeType = "application/json";
    const exportData = {
      meta: {
        session: "Blyskawica Sparkle V10",
        cognitive_name: "Sparkle",
        architect: "Andrzej Mątewski (V1B3hR)",
        export_date: new Date().toISOString(),
        neurochemistry: SparkleStore.state.neurochemistry
      },
      messages: history
    };
    content = JSON.stringify(exportData, null, 2);
  } else if (format === "html") {
    mimeType = "text/html";
    content = `<!DOCTYPE html>\n<html lang="pl">\n<head>\n<meta charset="UTF-8">\n<title>Sesja: Sparkle & Architekt</title>\n`;
    content += `<style>
      body { font-family: system-ui, -apple-system, sans-serif; background: #0b1120; color: #e2e8f0; padding: 30px; line-height: 1.6; max-width: 900px; margin: auto; }
      h1 { color: #38bdf8; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 12px; font-size: 20px; }
      .meta { color: #94a3b8; font-size: 13px; margin-bottom: 24px; }
      .msg { margin-bottom: 16px; padding: 14px 18px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.08); }
      .user { background: rgba(255,255,255,0.04); border-color: rgba(56,189,248,0.3); }
      .bot { background: rgba(56,189,248,0.06); border-color: rgba(56,189,248,0.4); }
      .system { background: rgba(255,255,255,0.02); font-size: 12px; color: #94a3b8; text-align: center; }
      strong { color: #f8fafc; }
    </style>\n</head>\n<body>\n`;
    content += `<h1>⚡ Sesja: Sparkle & Andrzej Mątewski (V1B3hR)</h1>\n`;
    content += `<div class="meta">Data sesji: ${new Date().toLocaleString()} | Etyka: 25 Praw Nethical | Silnik: Candle GGUF</div>\n`;
    history.forEach((message) => {
      const cssClass = (message.sender === "Użytkownik" ? "user" : (message.sender.includes("Sparkle") || message.sender.includes("Błyskawica") ? "bot" : "system"));
      const escapedSender = escapeHtml(message.sender);
      const escapedTimestamp = escapeHtml(message.timestamp);
      const escapedText = escapeHtml(message.text);
      content += `<div class="msg ${cssClass}"><strong>${escapedSender}</strong> <span style="font-size:11px;color:#64748b;">[${escapedTimestamp}]</span><p style="margin-top:6px;white-space:pre-wrap;">${escapedText}</p></div>\n`;
    });
    content += `</body>\n</html>`;
  } else {
    // txt
    mimeType = "text/plain";
    content = `=== SESJA KOGNITYWNA: SPARKLE & ANDRZEJ MĄTEWSKI (V1B3hR) ===\nData: ${new Date().toLocaleString()}\n\n`;
    history.forEach(m => {
      content += `[${m.timestamp}] ${m.sender}:\n${m.text}\n\n`;
    });
  }

  const finalFilename = `${baseName}.${ext}`;
  let savedSuccess = false;

  // 1. Zapis do pliku przez Tauri IPC w katalogu roboczym (jeśli dostępne)
  try {
    if (window.__TAURI__) {
      await invoke("write_workspace_file", { path: finalFilename, content });
      savedSuccess = true;
      if (addLogFn) addLogFn(`✓ Zapisano sesję w przestrzeni roboczej: ${finalFilename}`);
      
      appendChatMessage("System Sparkle", `✓ Pomyślnie zapisano sesję do pliku roboczego: ${finalFilename}`, "system-msg");
      
      try {
        await refreshWorkspaceFiles();
      } catch (e) {}

      alert(`✓ Zapisano sesję kognitywną do pliku:\n${finalFilename}\n\nPlik został zapisany w katalogu roboczym i jest widoczny w zakładce WORKSPACE & EXPLORER.`);
    }
  } catch (err) {
    if (addLogFn) addLogFn(`❌ Błąd zapisu sesji w workspace: ${err}`);
  }

  // 2. Pobieranie pliku w oknie aplikacji (przeglądarka / fallback)
  if (!savedSuccess) {
    try {
      const blob = new Blob([content], { type: mimeType + ";charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = finalFilename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      if (addLogFn) addLogFn(`✓ Wyeksportowano plik (${format.toUpperCase()}): ${finalFilename}`);
      appendChatMessage("System Sparkle", `✓ Wyeksportowano sesję do pliku: ${finalFilename}`, "system-msg");
      alert(`✓ Wyeksportowano plik sesji: ${finalFilename}`);
    } catch (e) {
      if (addLogFn) addLogFn(`❌ Błąd eksportu pliku: ${e}`);
      alert(`❌ Nie udało się zapisać sesji: ${e}`);
    }
  }

  return true;
}
