// Code Editor & Workspace File Manager Module
import { SparkleStore } from './store.js';

const { invoke } = window.__TAURI__ ? window.__TAURI__.core : { invoke: async () => {} };

let fileList, btnRefreshFiles, currentFilenameText, btnSaveFile, codeEditor;
let btnNewFile, btnOpenFile, btnSaveAsFile;
let logConsole, btnClearLogs, btnExportLogs;

export function initEditorModule() {
  fileList = document.getElementById("file-list");
  btnRefreshFiles = document.getElementById("btn-refresh-files");
  currentFilenameText = document.getElementById("current-filename");
  btnSaveFile = document.getElementById("btn-save-file");
  codeEditor = document.getElementById("code-editor");

  btnNewFile = document.getElementById("btn-new-file");
  btnOpenFile = document.getElementById("btn-open-file");
  btnSaveAsFile = document.getElementById("btn-save-as-file");

  logConsole = document.getElementById("log-console");
  btnClearLogs = document.getElementById("btn-clear-logs");
  btnExportLogs = document.getElementById("btn-export-logs");

  if (btnRefreshFiles) {
    btnRefreshFiles.addEventListener("click", refreshWorkspaceFiles);
  }
  if (btnSaveFile) {
    btnSaveFile.addEventListener("click", saveCurrentFile);
  }
  if (btnNewFile) {
    btnNewFile.addEventListener("click", createNewFile);
  }
  if (btnOpenFile) {
    btnOpenFile.addEventListener("click", openFileDialog);
  }
  if (btnSaveAsFile) {
    btnSaveAsFile.addEventListener("click", saveAsFile);
  }
  if (btnClearLogs) {
    btnClearLogs.addEventListener("click", clearLogs);
  }
  if (btnExportLogs) {
    btnExportLogs.addEventListener("click", exportLogs);
  }
  if (codeEditor) {
    codeEditor.addEventListener("keydown", (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "s") {
        e.preventDefault();
        saveCurrentFile();
      }
    });
  }
}

export function addLog(text) {
  if (!logConsole) return;
  const timestamp = new Date().toLocaleTimeString();
  logConsole.textContent += `\n[${timestamp}] ${text}`;
  logConsole.scrollTop = logConsole.scrollHeight;
}

export function clearLogs() {
  if (logConsole) {
    logConsole.textContent = "Logi wyczyszczone.";
  }
}

export async function exportLogs() {
  if (!logConsole) return;
  const logsText = logConsole.textContent;
  try {
    const result = await invoke("export_logs", { logs: logsText });
    addLog(`✓ ${result}`);
  } catch (error) {
    addLog(`❌ Błąd eksportu logów: ${error}`);
  }
}

export async function refreshWorkspaceFiles() {
  if (!fileList) return;
  fileList.replaceChildren();

  const loadingEl = document.createElement("div");
  loadingEl.className = "file-item file-loading";
  loadingEl.textContent = "Ładowanie plików z przestrzeni roboczej...";
  fileList.appendChild(loadingEl);

  try {
    const files = await invoke("list_workspace_files");
    fileList.replaceChildren();

    if (!files || files.length === 0) {
      const emptyEl = document.createElement("div");
      emptyEl.className = "file-item file-empty";
      emptyEl.textContent = "Brak plików w katalogu roboczym.";
      fileList.appendChild(emptyEl);
      return;
    }

    files.sort((a, b) => (b.is_dir - a.is_dir) || a.name.localeCompare(b.name));

    files.forEach(file => {
      const itemEl = document.createElement("div");
      itemEl.className = `file-item ${file.is_dir ? 'is-directory' : 'is-file'}`;
      
      const iconSpan = document.createElement("span");
      iconSpan.className = "file-icon";
      iconSpan.textContent = file.is_dir ? "📁 " : "📄 ";
      
      const nameSpan = document.createElement("span");
      nameSpan.className = "file-name";
      nameSpan.textContent = file.name;
      
      itemEl.appendChild(iconSpan);
      itemEl.appendChild(nameSpan);

      if (!file.is_dir) {
        itemEl.addEventListener("click", () => openWorkspaceFile(file.path, file.name));
      }
      fileList.appendChild(itemEl);
    });
  } catch (error) {
    fileList.replaceChildren();
    const errorEl = document.createElement("div");
    errorEl.className = "file-item file-error";
    errorEl.textContent = `Błąd wczytywania: ${error}`;
    fileList.appendChild(errorEl);
  }
}

export async function openWorkspaceFile(path, filename) {
  addLog(`[Pliki]: Otwieranie ${filename}...`);
  try {
    const content = await invoke("read_workspace_file", { path });
    if (codeEditor) {
      codeEditor.value = content;
      codeEditor.disabled = false;
    }
    if (currentFilenameText) {
      currentFilenameText.textContent = filename;
    }
    if (btnSaveFile) {
      btnSaveFile.disabled = false;
    }
    SparkleStore.update("currentFileOpen", path);
    addLog(`✓ Otwarto plik: ${filename}`);
  } catch (error) {
    addLog(`❌ Błąd odczytu pliku: ${error}`);
  }
}

export async function saveCurrentFile() {
  const currentPath = SparkleStore.state.currentFileOpen;
  if (!currentPath) {
    addLog("[Pliki]: Brak wybranego pliku do zapisu.");
    return;
  }
  const content = codeEditor ? codeEditor.value : "";
  addLog(`[Pliki]: Zapisywanie ${currentPath}...`);
  try {
    const res = await invoke("write_workspace_file", { path: currentPath, content });
    addLog(`✓ ${res}`);
  } catch (error) {
    addLog(`❌ Błąd zapisu pliku: ${error}`);
  }
}

export function createNewFile() {
  const filename = prompt("Podaj nazwę nowego pliku:");
  if (!filename) return;
  if (codeEditor) {
    codeEditor.value = "";
    codeEditor.disabled = false;
  }
  if (currentFilenameText) {
    currentFilenameText.textContent = filename;
  }
  if (btnSaveFile) {
    btnSaveFile.disabled = false;
  }
  SparkleStore.update("currentFileOpen", filename);
  addLog(`[Pliki]: Utworzono nowy dokument '${filename}'. Kliknij Zapisz, aby zapisać na dysku.`);
}

export function openFileDialog() {
  const filename = prompt("Podaj względną ścieżkę do pliku:");
  if (filename) {
    openWorkspaceFile(filename, filename);
  }
}

export function saveAsFile() {
  const filename = prompt("Zapisz plik jako (nazwa):", currentFilenameText ? currentFilenameText.textContent : "nowy_plik.py");
  if (!filename) return;
  SparkleStore.update("currentFileOpen", filename);
  if (currentFilenameText) currentFilenameText.textContent = filename;
  saveCurrentFile();
}
