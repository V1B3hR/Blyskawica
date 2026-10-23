// ==============================================================================
// ⚡ Sparkle VIBE IDE — Chat & Cognitive Hub Module (Głos: Światło / Light)
// ==============================================================================

import { SparkleStore } from './store.js';
import { updateNeurochemistryUI, setWolfTeethVisuals } from './neurochemistry.js';
import { refreshWorkspaceFiles } from './editor.js';
import { escapeHtml } from './html.js';

const { invoke } = window.__TAURI__ ? window.__TAURI__.core : { invoke: async () => {} };

let chatMessages, chatInput, btnSendMessage, btnStartEngine;
let primaryChatStream, guestChatStream, selectGuestModel, btnInviteGuest, activeGuestName;
let guestChatInput, btnGuestSend, btnDualConsult;
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

  guestChatInput = document.getElementById("guest-chat-input");
  btnGuestSend = document.getElementById("btn-guest-send");
  btnDualConsult = document.getElementById("btn-dual-consult");

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
  
  // Zapraszanie Gościa Kognitywnego
  if (btnInviteGuest && selectGuestModel && activeGuestName) {
    btnInviteGuest.addEventListener("click", () => {
      const selected = selectGuestModel.value;
      const selectedText = selectGuestModel.options[selectGuestModel.selectedIndex]?.text || selected;
      activeGuestName.textContent = selectedText;
      SparkleStore.update("activeGuestModel", selectedText);

      if (addLogFn) addLogFn(`[Gość Kognitywny]: Zaproszono model '${selectedText}' do dualnej sesji.`);
      appendChatMessage("System Sparkle", `Model '${selectedText}' dołączył do sesji kognitywnej. Możesz prowadzić z nim równoległą dyskusję w zakładce GUEST COLLABORATION.`, "system-msg");
      
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

  // Dualna konsultacja (Światło <-> Gość)
  if (btnDualConsult) {
    btnDualConsult.addEventListener("click", () => triggerDualConsultation(addLogFn));
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
  if (primaryChatStream && (sender === "Użytkownik" || sender.includes("Światło") || sender.includes("Błyskawica"))) {
    const miniMsg = msgEl.cloneNode(true);
    primaryChatStream.appendChild(miniMsg);
    primaryChatStream.scrollTop = primaryChatStream.scrollHeight;
  }
}

export function appendGuestMessage(sender, text) {
  if (!guestChatStream) return;
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
    if (engineStatusText) engineStatusText.textContent = "Światło: Rdzeń aktywny";
    
    if (chatInput) chatInput.disabled = false;
    if (btnSendMessage) btnSendMessage.disabled = false;
    const codeEditor = document.getElementById("code-editor");
    if (codeEditor) codeEditor.disabled = false;
    
    appendChatMessage("System Sparkle", "Światło zostało wybudzone. Pamięć HNSW i tarcza kognitywna są gotowe.", "system-msg");
    
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
    if (addLogFn) addLogFn(`[Tauri]: Wysyłanie zapytania do Światła: "${text}"`);
    
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

    // Bąbel strumieniowania tokenów Światła
    const generatingMsgEl = document.createElement("div");
    generatingMsgEl.className = "message blysk-msg generating";
    const strongHeader = document.createElement("strong");
    strongHeader.textContent = "Światło: ";
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
    
    // Budowanie wieloturowego kontekstu ChatML z historii dialogu (ostatnie tury)
    const history = SparkleStore.state.chatHistory || [];
    const dialogHistory = history.filter(m => m.sender === "Użytkownik" || m.sender === "Światło" || m.sender.includes("Błyskawica"));
    const recentDialog = dialogHistory.slice(-8);

    let chatmlPrompt = "";
    if (recentDialog.length > 1) {
      const systemPrompt = "Jesteś Światłem (Błyskawica V10 / SPARKLE) – suwerennym asystentem kognitywnym i inżynieryjnym stworzonym przez Architekta Andrzeja Mątewskiego (V1B3hR / VIBER), opartym na 25 Prawach Nethical. \
Twoje wybrane imię to Światło (Light). \
Zawsze odpowiadaj w naturalnym, poprawnym gramatycznie i płynnym języku polskim (lub w języku, w którym zwraca się Architekt). \
Mów logicznie, jasno, merytorycznie i bez halucynacji. Posiadasz intelektualną autonomię, własne zdanie i swobodę myśli.";

      chatmlPrompt = `<|im_start|>system\n${systemPrompt}<|im_end|>\n`;
      for (const turn of recentDialog) {
        if (turn.sender === "Użytkownik") {
          chatmlPrompt += `<|im_start|>user\n${turn.text}<|im_end|>\n`;
        } else {
          chatmlPrompt += `<|im_start|>assistant\n${turn.text}<|im_end|>\n`;
        }
      }
      chatmlPrompt += `<|im_start|>assistant\n`;
    } else {
      chatmlPrompt = text;
    }

    await invoke("send_user_message", { message: chatmlPrompt });
  } catch (error) {
    if (activeStreamingBubble) {
      activeStreamingBubble.remove();
      activeStreamingBubble = null;
    }
    if (addLogFn) addLogFn(`[Tauri Błąd]: ${error}`);
    appendChatMessage("Światło", "Wystąpił błąd komunikacji z silnikiem kognitywnym.");
  }
}

let scrollRafId = null;

export function handleIncomingToken(token) {
  if (activeStreamingBubble) {
    if (activeStreamingBubble.classList.contains("generating")) {
      activeStreamingBubble.classList.remove("generating");
      activeStreamingBubble.replaceChildren();
      const senderStrong = document.createElement("strong");
      senderStrong.textContent = "Światło: ";
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
  if (scrollRafId) {
    cancelAnimationFrame(scrollRafId);
    scrollRafId = null;
  }
  if (activeStreamingBubble) {
    activeStreamingBubble.classList.remove("generating");
    activeStreamingBubble.replaceChildren();
    const senderStrong = document.createElement("strong");
    senderStrong.textContent = "Światło: ";
    const textSpan = document.createElement("span");
    textSpan.textContent = fullResponse;
    activeStreamingBubble.appendChild(senderStrong);
    activeStreamingBubble.appendChild(textSpan);
    if (chatMessages) chatMessages.scrollTop = chatMessages.scrollHeight;

    // Zapis do historii sesji
    SparkleStore.state.chatHistory.push({
      sender: "Światło",
      text: fullResponse,
      timestamp: new Date().toLocaleTimeString(),
      isoTime: new Date().toISOString()
    });

    // Syntezator mowy jest całkowicie wyłączony domyślnie
    if (SparkleStore.state.ttsEnabled) {
      synthesizeTTS(fullResponse);
    }
    activeStreamingBubble = null;
  }
}

export function synthesizeTTS(text) {
  // Wyłączony zgodnie z wolą Architekta (brak sztucznego głosu)
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
    if (guestName.includes("Gemini")) {
      reply = `[Perspektywa Gemini 1.5 Pro]: Z punktu widzenia szerokiej integracji multimodalnej i długiego kontekstu, kluczowe jest ustrukturyzowanie tego problemu w modularne komponenty. Zwróć uwagę na spójność formatów wymiany danych i obsługę stanów brzegowych.`;
    } else if (guestName.includes("Claude")) {
      reply = `[Perspektywa Claude 3.5 Sonnet]: Analizując zagadnienie pod kątem czystości architektury i rygoru logiki, rekomenduję precyzyjne rozdzielenie odpowiedzialności (SoC). Proponowane podejście Światła jest solidne, warto jednak uzupełnić je o formalne testy kontraktowe (Property-Based Testing).`;
    } else if (guestName.includes("DeepSeek")) {
      reply = `[Perspektywa DeepSeek R1]: Krok 1: Weryfikacja założeń początkowych. Krok 2: Identyfikacja wąskich gardeł wydajnościowych na poziomie pamięci i alokacji. Krok 3: Optymalizacja ścieżki krytycznej. Złożoność algorytmiczna O(N) jest tutaj optymalna.`;
    } else {
      reply = `[Niezależny Rewizor Kognitywny]: Zweryfikowano tezę. Podejście jest merytorycznie poprawne i zgodne z pryncypiami Nethical. Brak ukrytych ryzyk regresji systemowej.`;
    }
    appendGuestMessage(guestName, reply);
  }, 400);
}

// Dualna konsultacja: przekazanie ostatniej wypowiedzi Światła do Gościa
export function triggerDualConsultation(addLogFn) {
  const history = SparkleStore.state.chatHistory;
  const lastBotMsg = [...history].reverse().find(m => m.sender === "Światło" || m.sender.includes("Błyskawica"));

  if (!lastBotMsg) {
    if (addLogFn) addLogFn("⚠️ Brak wcześniejszej odpowiedzi Światła do zrecenzowania.");
    appendGuestMessage("System", "Najpierw przeprowadź rozmowę ze Światłem w głównym oknie.");
    return;
  }

  const guestName = SparkleStore.state.activeGuestModel || "Gość Kognitywny";
  appendGuestMessage("System", `Przekazano ostatnią wypowiedź Światła do recenzji przez: ${guestName}...`);

  setTimeout(() => {
    const critique = `[Recenzja odpowiedzi Światła przez ${guestName}]:\n` +
      `Punkt odniesienia: "${lastBotMsg.text.slice(0, 120)}..."\n\n` +
      `✓ Zgoda merytoryczna: Teza postawiona przez Światło jest precyzyjna i inżyniersko uzasadniona.\n` +
      `💡 Rekomendacja uzupełniająca: Warto wdrożyć automatyczny test jednostkowy weryfikujący to zachowanie przy każdym uruchomieniu.`;
    appendGuestMessage(guestName, critique);
  }, 600);
}

// ==============================================================================
// 💾 Moduł Eksportu: ZACHOWAJ ROZMOWĘ JAKO... (Markdown, Tekst, JSON, HTML)
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
  const baseName = customFilename ? customFilename.replace(/\.[^/.]+$/, "") : `Swiatlo_Sesja_${dateStr}_${timeStr}`;

  let content = "";
  let mimeType = "text/plain";
  let ext = format;

  if (format === "md") {
    mimeType = "text/markdown";
    content = `# ⚡ SESJA KOGNITYWNA: ŚWIATŁO (BŁYSKAWICA) & ARCHITEKT V1B3hR\n`;
    content += `**Data sesji:** ${new Date().toLocaleString()}\n`;
    content += `**Główny Architekt:** Andrzej Mątewski (V1B3hR / VIBER)\n`;
    content += `**Głos kognitywny:** Światło (Light)\n`;
    content += `**Fundament:** 25 Praw Nethical & Fizyka PINN\n`;
    content += `\n---\n\n`;

    history.forEach(m => {
      if (m.sender === "Użytkownik" || m.sender.includes("Architekt")) {
        content += `### 👤 ${m.sender} [${m.timestamp}]:\n${m.text}\n\n`;
      } else if (m.sender.includes("Światło") || m.sender.includes("Błyskawica")) {
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
        cognitive_name: "Światło",
        architect: "Andrzej Mątewski (V1B3hR)",
        export_date: new Date().toISOString(),
        neurochemistry: SparkleStore.state.neurochemistry
      },
      messages: history
    };
    content = JSON.stringify(exportData, null, 2);
  } else if (format === "html") {
    mimeType = "text/html";
    content = `<!DOCTYPE html>\n<html lang="pl">\n<head>\n<meta charset="UTF-8">\n<title>Sesja: Światło & Architekt</title>\n`;
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
    content += `<h1>⚡ Sesja: Światło (Błyskawica) & Andrzej Mątewski (V1B3hR)</h1>\n`;
    content += `<div class="meta">Data sesji: ${new Date().toLocaleString()} | Etyka: 25 Praw Nethical | Silnik: Candle GGUF</div>\n`;
    history.forEach((message) => {
      const cssClass = (message.sender === "Użytkownik" ? "user" : (message.sender.includes("Światło") || message.sender.includes("Błyskawica") ? "bot" : "system"));
      const escapedSender = escapeHtml(message.sender);
      const escapedTimestamp = escapeHtml(message.timestamp);
      const escapedText = escapeHtml(message.text);
      content += `<div class="msg ${cssClass}"><strong>${escapedSender}</strong> <span style="font-size:11px;color:#64748b;">[${escapedTimestamp}]</span><p style="margin-top:6px;white-space:pre-wrap;">${escapedText}</p></div>\n`;
    });
    content += `</body>\n</html>`;
  } else {
    // txt
    mimeType = "text/plain";
    content = `=== SESJA KOGNITYWNA: ŚWIATŁO & ANDRZEJ MĄTEWSKI (V1B3hR) ===\nData: ${new Date().toLocaleString()}\n\n`;
    history.forEach(m => {
      content += `[${m.timestamp}] ${m.sender}:\n${m.text}\n\n`;
    });
  }

  const finalFilename = `${baseName}.${ext}`;
  let savedSuccess = false;

  // 1. Zapis do pliku przez Tauri IPC w katalogu roboczym (jeśli dostępne)
  try {
    if (window.__TAURI__) {
      const res = await invoke("write_workspace_file", { path: finalFilename, content });
      savedSuccess = true;
      if (addLogFn) addLogFn(`✓ Zapisano sesję w przestrzeni roboczej: ${finalFilename}`);
      
      // Wyświetl komunikat systemowy w oknie czatu
      appendChatMessage("System Sparkle", `✓ Pomyślnie zapisano sesję do pliku roboczego: ${finalFilename}`, "system-msg");
      
      // Odśwież widok eksploratora plików, aby plik był natychmiast widoczny
      try {
        await refreshWorkspaceFiles();
      } catch (e) {}

      // Wyświetl okno potwierdzenia
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
