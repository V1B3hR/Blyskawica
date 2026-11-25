import assert from "node:assert/strict";
import test from "node:test";
import { createChatPersistence } from "../src/modules/chat-persistence.js";

test("writes are serialized and restore uses the native history", async () => {
  const writes = [];
  const events = [];
  const persistence = createChatPersistence(async (command, args) => {
    if (command === "load_chat_autosave") return [{ text: "wcześniej" }];
    await new Promise((resolve) => setTimeout(resolve, args.record.text === "pierwsza" ? 10 : 0));
    writes.push(args.record.text);
  }, (state) => events.push(state));
  assert.deepEqual(await persistence.load(), [{ text: "wcześniej" }]);
  await Promise.all([persistence.append({ text: "pierwsza" }), persistence.append({ text: "druga" })]);
  assert.deepEqual(writes, ["pierwsza", "druga"]);
  assert.equal(events.at(-1), "saved");
});

test("errors remain visible and writes pause while removal is confirmed", async () => {
  const calls = [];
  const statuses = [];
  let fail = true;
  const persistence = createChatPersistence(async (command, args) => {
    calls.push(command);
    if (command === "append_chat_autosave" && fail) throw new Error("disk error");
    return [];
  }, (status) => statuses.push(status));
  assert.equal(await persistence.append({ text: "a" }), false);
  assert.equal(statuses.at(-1), "error");
  await persistence.pause();
  const queued = persistence.append({ text: "b" });
  await new Promise((resolve) => setTimeout(resolve, 10));
  assert.equal(calls.length, 1);
  fail = false;
  persistence.resume(true);
  assert.equal(await queued, true);
  assert.equal(statuses.at(-1), "saved");
});
