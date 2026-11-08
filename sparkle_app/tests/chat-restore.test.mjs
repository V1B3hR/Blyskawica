import assert from "node:assert/strict";
import test from "node:test";

test("restores both channels without resaving and stores new messages as text", async () => {
  const calls = [];
  const previous = [
    { channel: "main", sender: "Użytkownik", text: "<img src=x>", iso_time: "2026-11-03T00:00:00Z" },
    { channel: "guest", sender: "Gość", text: "odpowiedź", iso_time: "2026-11-03T00:00:01Z" },
  ];
  class Element {
    constructor() { this.children = []; this.style = {}; this.scrollHeight = 0; this.textContent = ""; }
    appendChild(child) { this.children.push(child); }
    cloneNode() { return this; }
  }
  const elements = { "chat-messages": new Element(), "guest-chat-stream": new Element(), "chat-autosave-status": new Element() };
  globalThis.document = { getElementById: (id) => elements[id] || null, createElement: () => new Element() };
  globalThis.window = { addEventListener() {}, __TAURI__: { core: { invoke: async (command, args) => {
    calls.push({ command, args });
    return command === "load_chat_autosave" ? previous : undefined;
  } } } };
  const chat = await import("../src/modules/chat.js");
  const { SparkleStore } = await import("../src/modules/store.js");
  chat.initChatModule(() => {}, () => {});
  await chat.restoreChatAutosave(() => {});
  assert.equal(calls.length, 1);
  assert.equal(SparkleStore.state.chatHistory[0].text, "<img src=x>");
  assert.equal(SparkleStore.state.guestChatHistory[0].text, "odpowiedź");
  assert.equal(elements["chat-messages"].children[0].children[1].textContent, "<img src=x>");
  await chat.appendChatMessage("Użytkownik", "nowa");
  assert.equal(calls[1].command, "append_chat_autosave");
  assert.equal(calls[1].args.record.text, "nowa");
  assert.equal(calls[1].args.record.channel, "main");
});
