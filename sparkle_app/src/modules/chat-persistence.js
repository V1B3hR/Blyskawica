// Serialize writes and keep messages queued while the user confirms R2 removal.
export function createChatPersistence(invoke, onStatus) {
  let chain = Promise.resolve();
  let gate = null;
  let release = null;
  let pending = 0;
  let failed = false;

  async function load() {
    try {
      const records = await invoke("load_chat_autosave");
      onStatus("saved");
      return records;
    } catch (error) {
      failed = true;
      onStatus("error", error);
      return [];
    }
  }

  function append(record) {
    pending += 1;
    onStatus("pending");
    const wait = gate;
    const result = chain.then(async () => {
      if (wait) await wait;
      try {
        await invoke("append_chat_autosave", { record });
        pending -= 1;
        if (!failed) onStatus(pending ? "pending" : "saved");
        return true;
      } catch (error) {
        pending -= 1;
        failed = true;
        onStatus("error", error);
        return false;
      }
    });
    chain = result;
    return result;
  }

  async function pause() {
    if (gate) throw new Error("Autozapis jest już wstrzymany");
    const prior = chain;
    gate = new Promise((resolve) => { release = resolve; });
    await prior;
  }

  function resume(cleared = false) {
    if (cleared) failed = false;
    if (release) release();
    gate = null;
    release = null;
  }

  return { load, append, pause, resume };
}
