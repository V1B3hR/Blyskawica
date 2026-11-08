import assert from "node:assert/strict";
import test from "node:test";

test("cancel waits for the terminal response before allowing the next message", async () => {
  let finishSend;
  const requests = [];
  class Element {
    constructor() {
      this.children = []; this.style = {}; this.disabled = false;
      this.scrollHeight = 0; this.textContent = "";
      this.classList = { contains: () => false, remove() {} };
    }
    appendChild(child) { this.children.push(child); }
    replaceChildren() { this.children = []; }
    addEventListener() {}
    remove() {}
    cloneNode() { return this; }
  }
  const send = new Element();
  const cancel = new Element(); cancel.style.display = "none";
  const elements = { "chat-messages": new Element(), "btn-send-message": send, "btn-cancel-generation": cancel };
  globalThis.document = {
    getElementById: (id) => elements[id] || null,
    createElement: () => new Element(),
    createTextNode: (text) => ({ textContent: text }),
  };
  globalThis.window = { addEventListener() {}, __TAURI__: { core: { invoke: async (command) => {
    requests.push(command);
    if (command === "send_user_message") return new Promise((resolve) => { finishSend = resolve; });
    return undefined;
  } } } };
  const chat = await import("../src/modules/chat.js");
  chat.initChatModule(() => {}, () => {});
  const sending = chat.sendMessageText("pierwsze", () => {});
  await new Promise((resolve) => setTimeout(resolve, 0));
  assert.equal(send.disabled, true);
  assert.equal(cancel.style.display, "none");
  assert.equal(typeof finishSend, "function");
  finishSend();
  await sending;
  assert.equal(cancel.style.display, "inline-flex");
  await chat.cancelGeneration(() => {});
  assert.equal(send.disabled, true);
  assert.equal(cancel.disabled, true);
  await chat.sendMessageText("drugie", () => {});
  assert.equal(requests.filter((item) => item === "send_user_message").length, 1);
  chat.handleResponseFinished("część [Przerwano]");
  assert.equal(send.disabled, false);
  assert.equal(cancel.style.display, "none");
});
