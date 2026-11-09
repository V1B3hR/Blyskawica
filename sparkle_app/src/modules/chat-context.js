const REJECTED_RESPONSES = new Set([
  "Żądanie zostało odrzucone przez kontrolę bezpieczeństwa.",
  "Żądanie zostało odrzucone przez filtr bezpieczeństwa.",
]);

// Keep complete accepted turns and the current user message. Rejected and
// abandoned turns remain in history but cannot repeatedly poison the prompt.
export function dialogForModel(history) {
  const result = [];
  let pendingUser = null;
  for (const message of history) {
    const isUser = message.sender === "Użytkownik";
    const isAssistant = message.sender === "Sparkle" || message.sender.includes("Błyskawica");
    if (isUser) {
      pendingUser = message;
    } else if (isAssistant && pendingUser) {
      if (!REJECTED_RESPONSES.has(message.text)) result.push(pendingUser, message);
      pendingUser = null;
    }
  }
  if (pendingUser) result.push(pendingUser);
  return result;
}
