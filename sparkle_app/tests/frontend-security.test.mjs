import assert from "node:assert/strict";
import { readdir, readFile } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";
import { escapeHtml } from "../src/modules/html.js";

const testDirectory = dirname(fileURLToPath(import.meta.url));
const applicationDirectory = resolve(testDirectory, "..");
const frontendDirectory = join(applicationDirectory, "src");
const repositoryDirectory = resolve(applicationDirectory, "..");

async function collectJavaScriptFiles(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const files = await Promise.all(
    entries.map(async (entry) => {
      const entryPath = join(directory, entry.name);
      if (entry.isDirectory()) {
        return collectJavaScriptFiles(entryPath);
      }
      return entry.isFile() && entry.name.endsWith(".js") ? [entryPath] : [];
    }),
  );

  return files.flat();
}

async function loadFrontendSources() {
  const files = await collectJavaScriptFiles(frontendDirectory);
  return Promise.all(
    files.map(async (filePath) => ({
      filePath,
      source: await readFile(filePath, "utf8"),
    })),
  );
}

function registeredTauriCommands(source) {
  const handler = source.match(/tauri::generate_handler!\s*\[([\s\S]*?)\]/);
  assert.ok(handler, "Tauri command handler must be declared");

  return new Set(
    [...handler[1].matchAll(/\b([a-z][a-z0-9_]*)\b/g)].map((match) => match[1]),
  );
}

test("frontend sources do not use HTML injection sinks", async () => {
  const prohibitedSinks = [
    "innerHTML",
    "outerHTML",
    "insertAdjacentHTML",
    "document.write",
  ];

  for (const { filePath, source } of await loadFrontendSources()) {
    for (const sink of prohibitedSinks) {
      assert.equal(
        source.includes(sink),
        false,
        `${filePath} must not use ${sink}; render untrusted content with DOM nodes and textContent instead`,
      );
    }
  }
});

test("CSP keeps network connections local to the application", async () => {
  const configPath = join(applicationDirectory, "src-tauri", "tauri.conf.json");
  const config = JSON.parse(await readFile(configPath, "utf8"));
  const csp = config.app.security.csp;

  assert.match(csp, /default-src 'self'/);
  assert.match(csp, /connect-src 'self'/);
  assert.doesNotMatch(csp, /\b(?:https?|wss?):|localhost/i);
});

test("non-Windows privilege prompts fail closed", async () => {
  const rustSource = await readFile(
    join(repositoryDirectory, "sparkle_app", "src-tauri", "src", "lib.rs"),
    "utf8",
  );

  assert.match(
    rustSource,
    /#\[cfg\(not\(target_os = "windows"\)\)\]\s*fn show_confirm_dialog\([^)]*\) -> bool\s*\{\s*false\s*\}/s,
  );
});

test("recreatable artifact cleanup remains permission-gated and confirmed", async () => {
  const rustSource = await readFile(
    join(repositoryDirectory, "sparkle_app", "src-tauri", "src", "lib.rs"),
    "utf8",
  );

  assert.match(
    rustSource,
    /fn clear_recreatable_runtime_artifacts[\s\S]*?require_permission_level\(permission_level, 2,[\s\S]*?show_confirm_dialog/s,
  );
});

test("online connector registry defaults to offline and gates loopback status", async () => {
  const rustSource = await readFile(
    join(repositoryDirectory, "sparkle_app", "src-tauri", "src", "lib.rs"),
    "utf8",
  );

  assert.match(rustSource, /online_mode:\s*false/);
  assert.match(
    rustSource,
    /fn set_online_mode[\s\S]*?if !enabled \{\s*inner\.connector_consents\.clear\(\);\s*\}/s,
  );
  assert.match(
    rustSource,
    /connector_access_granted\([\s\S]*?LEGACY_SIDECAR_STATUS_CONNECTOR_ID/s,
  );
  assert.match(rustSource, /if backend_alive && sidecar_status_allowed/);
});

test("permission report remains read-only and exposes all three levels", async () => {
  const rustSource = await readFile(
    join(repositoryDirectory, "sparkle_app", "src-tauri", "src", "lib.rs"),
    "utf8",
  );

  assert.match(rustSource, /fn get_permission_report\([^)]*\) -> Result<serde_json::Value, String>/);
  assert.match(rustSource, /"current_level": current_level/);
  assert.match(rustSource, /"level": 1/);
  assert.match(rustSource, /"level": 2/);
  assert.match(rustSource, /"level": 3/);
});

test("exported HTML transcript values are escaped", async () => {
  const chatSource = await readFile(join(frontendDirectory, "modules", "chat.js"), "utf8");

  assert.equal(
    escapeHtml('<img src=x onerror="alert(1)"> & text'),
    "&lt;img src=x onerror=&quot;alert(1)&quot;&gt; &amp; text",
  );
  assert.match(chatSource, /escapeHtml\(message\.sender\)/);
  assert.match(chatSource, /escapeHtml\(message\.timestamp\)/);
  assert.match(chatSource, /escapeHtml\(message\.text\)/);
});

test("every frontend IPC invocation has a registered Rust command", async () => {
  const rustSource = await readFile(
    join(repositoryDirectory, "sparkle_app", "src-tauri", "src", "lib.rs"),
    "utf8",
  );
  const registeredCommands = registeredTauriCommands(rustSource);
  const invokedCommands = new Set();

  for (const { source } of await loadFrontendSources()) {
    for (const match of source.matchAll(/\binvoke\(\s*["']([a-z_][a-z0-9_]*)["']/g)) {
      invokedCommands.add(match[1]);
    }
  }

  assert.ok(invokedCommands.size > 0, "frontend must invoke at least one native command");
  for (const command of invokedCommands) {
    assert.ok(
      registeredCommands.has(command),
      `frontend invokes ${command}, but it is not registered by Tauri`,
    );
  }
});
