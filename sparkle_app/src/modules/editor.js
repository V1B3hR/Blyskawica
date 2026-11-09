// Code Editor & Workspace File Manager Module
import { SparkleStore } from './store.js';

const { invoke } = window.__TAURI__ ? window.__TAURI__.core : { invoke: async () => {} };

let fileList, btnRefreshFiles, currentFilenameText, btnSaveFile, codeEditor;
let btnNewFile, btnOpenFile, btnSaveAsFile, btnDeleteFile, nativeFilePicker;
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
  btnDeleteFile = document.getElementById("btn-delete-file");
  nativeFilePicker = document.getElementById("native-file-picker");

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
  if (btnDeleteFile) {
    btnDeleteFile.addEventListener("click", deleteCurrentFile);
  }
  if (btnClearLogs) {
    btnClearLogs.addEventListener("click", clearLogs);
  }
  if (btnExportLogs) {
    btnExportLogs.addEventListener("click", exportLogs);
  }
  if (nativeFilePicker) {
    nativeFilePicker.addEventListener("change", handleNativeFileSelected);
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

let currentExplorerSubdir = "";

export async function refreshWorkspaceFiles() {
  if (!fileList) return;
  fileList.replaceChildren();

  const loadingEl = document.createElement("div");
  loadingEl.className = "file-item file-loading";
  loadingEl.textContent = "Ładowanie plików z przestrzeni roboczej...";
  fileList.appendChild(loadingEl);

  try {
    const files = await invoke("list_workspace_files", { subpath: currentExplorerSubdir || null });
    fileList.replaceChildren();

    // Jeśli jesteśmy w podkatalogu, wyświetl przycisk powrotu w górę
    if (currentExplorerSubdir) {
      const upItem = document.createElement("div");
      upItem.className = "file-item is-directory is-nav-up";
      upItem.title = "Wróć do katalogu wyżej";
      
      const iconSpan = document.createElement("span");
      iconSpan.className = "file-icon";
      iconSpan.textContent = "↩️ ";
      
      const nameSpan = document.createElement("span");
      nameSpan.className = "file-name";
      nameSpan.textContent = `.. [W górę: /${currentExplorerSubdir}]`;
      
      upItem.appendChild(iconSpan);
      upItem.appendChild(nameSpan);

      upItem.addEventListener("click", () => {
        let parts = currentExplorerSubdir.replace(/\\/g, "/").split("/").filter(Boolean);
        parts.pop();
        currentExplorerSubdir = parts.join("/");
        refreshWorkspaceFiles();
      });
      fileList.appendChild(upItem);
    }

    if (!files || files.length === 0) {
      const emptyEl = document.createElement("div");
      emptyEl.className = "file-item file-empty";
      emptyEl.textContent = currentExplorerSubdir ? "Katalog jest pusty." : "Brak plików w katalogu roboczym.";
      fileList.appendChild(emptyEl);
      return;
    }

    files.sort((a, b) => (b.is_dir - a.is_dir) || a.name.localeCompare(b.name));

    files.forEach(file => {
      const itemEl = document.createElement("div");
      itemEl.className = `file-item ${file.is_dir ? 'is-directory' : 'is-file'}`;
      itemEl.style.display = "flex";
      itemEl.style.alignItems = "center";
      itemEl.style.justifyContent = "space-between";
      
      const mainPart = document.createElement("div");
      mainPart.style.display = "flex";
      mainPart.style.alignItems = "center";
      mainPart.style.gap = "6px";
      mainPart.style.overflow = "hidden";
      mainPart.style.textOverflow = "ellipsis";
      mainPart.style.whiteSpace = "nowrap";
      mainPart.style.flex = "1";

      const iconSpan = document.createElement("span");
      iconSpan.className = "file-icon";
      iconSpan.textContent = file.is_dir ? "📁 " : "📄 ";
      
      const nameSpan = document.createElement("span");
      nameSpan.className = "file-name";
      nameSpan.textContent = file.name;
      
      mainPart.appendChild(iconSpan);
      mainPart.appendChild(nameSpan);
      itemEl.appendChild(mainPart);

      // Przycisk bezpośredniego usuwania pliku (🗑️)
      if (!file.is_dir) {
        const deleteBtn = document.createElement("button");
        deleteBtn.className = "file-delete-btn";
        deleteBtn.textContent = "🗑️";
        deleteBtn.title = `Usuń plik ${file.name}`;
        deleteBtn.style.background = "none";
        deleteBtn.style.border = "none";
        deleteBtn.style.cursor = "pointer";
        deleteBtn.style.fontSize = "12px";
        deleteBtn.style.opacity = "0.6";
        deleteBtn.style.padding = "2px 4px";
        deleteBtn.style.borderRadius = "4px";

        deleteBtn.addEventListener("mouseover", () => { deleteBtn.style.opacity = "1.0"; });
        deleteBtn.addEventListener("mouseout", () => { deleteBtn.style.opacity = "0.6"; });

        deleteBtn.addEventListener("click", async (e) => {
          e.stopPropagation();
          const confirmed = confirm(`Czy na pewno chcesz usunąć plik:\n"${file.name}"?`);
          if (!confirmed) return;

          try {
            const res = await invoke("delete_workspace_file", { path: file.path });
            addLog(`✓ ${res}`);
            if (SparkleStore.state.currentFileOpen === file.path) {
              SparkleStore.update("currentFileOpen", null);
              if (codeEditor) {
                codeEditor.value = "";
                codeEditor.disabled = true;
              }
              if (currentFilenameText) currentFilenameText.textContent = "Nie wybrano pliku";
              if (btnSaveFile) btnSaveFile.disabled = true;
              if (btnSaveAsFile) btnSaveAsFile.disabled = true;
              if (btnDeleteFile) btnDeleteFile.disabled = true;
            }
            await refreshWorkspaceFiles();
          } catch (err) {
            addLog(`❌ Błąd usuwania pliku: ${err}`);
          }
        });
        itemEl.appendChild(deleteBtn);
      }

      if (file.is_dir) {
        itemEl.style.cursor = "pointer";
        itemEl.title = `Otwórz folder ${file.name}`;
        itemEl.addEventListener("click", () => {
          currentExplorerSubdir = file.path;
          refreshWorkspaceFiles();
        });
      } else {
        itemEl.style.cursor = "pointer";
        itemEl.title = `Otwórz plik ${file.name}`;
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
    if (btnSaveAsFile) {
      btnSaveAsFile.disabled = false;
    }
    if (btnDeleteFile) {
      btnDeleteFile.disabled = false;
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
    if (btnDeleteFile) {
      btnDeleteFile.disabled = false;
    }
    addLog(`✓ ${res}`);
    await refreshWorkspaceFiles();
  } catch (error) {
    addLog(`❌ Błąd zapisu pliku: ${error}`);
  }
}

export async function deleteCurrentFile() {
  const currentPath = SparkleStore.state.currentFileOpen;
  if (!currentPath) {
    addLog("[Pliki]: Brak wybranego pliku do usunięcia.");
    return;
  }
  const confirmed = confirm(`Czy na pewno chcesz usunąć aktualnie otwarty plik:\n"${currentPath}"?`);
  if (!confirmed) return;

  try {
    const result = await invoke("delete_workspace_file", { path: currentPath });
    SparkleStore.update("currentFileOpen", null);
    if (codeEditor) {
      codeEditor.value = "";
      codeEditor.disabled = true;
    }
    if (currentFilenameText) {
      currentFilenameText.textContent = "Nie wybrano pliku";
    }
    if (btnSaveFile) btnSaveFile.disabled = true;
    if (btnSaveAsFile) btnSaveAsFile.disabled = true;
    if (btnDeleteFile) btnDeleteFile.disabled = true;
    addLog(`✓ ${result}`);
    refreshWorkspaceFiles();
  } catch (error) {
    addLog(`❌ Błąd usuwania pliku: ${error}`);
  }
}

export function createNewFile() {
  const filename = prompt(
    "Utwórz nowy plik w katalogu roboczym:\n(Podaj nazwę pliku z rozszerzeniem, np. script.py, notatki.md, logic.rs):",
    "nowy_skrypt.py"
  );
  if (!filename) return;

  const cleanName = filename.trim();
  if (codeEditor) {
    codeEditor.value = "";
    codeEditor.disabled = false;
  }
  if (currentFilenameText) {
    currentFilenameText.textContent = cleanName;
  }
  if (btnSaveFile) {
    btnSaveFile.disabled = false;
  }
  if (btnSaveAsFile) {
    btnSaveAsFile.disabled = false;
  }
  if (btnDeleteFile) {
    btnDeleteFile.disabled = false;
  }
  SparkleStore.update("currentFileOpen", cleanName);
  addLog(`[Pliki]: Utworzono nowy dokument '${cleanName}'. Zapisz go przyciskiem ZAPISZ lub [Ctrl+S].`);
}

export function openFileDialog() {
  if (nativeFilePicker) {
    nativeFilePicker.click();
  } else {
    const filename = prompt("Podaj nazwę pliku w katalogu roboczym:");
    if (filename) {
      openWorkspaceFile(filename, filename);
    }
  }
}

async function handleNativeFileSelected(e) {
  const file = e.target.files && e.target.files[0];
  if (!file) return;

  addLog(`[Pliki]: Otwieranie pliku z eksploratora systemowego: ${file.name}...`);
  const reader = new FileReader();
  reader.onload = async (evt) => {
    const content = evt.target.result;
    if (codeEditor) {
      codeEditor.value = content;
      codeEditor.disabled = false;
    }
    if (currentFilenameText) {
      currentFilenameText.textContent = file.name;
    }
    if (btnSaveFile) btnSaveFile.disabled = false;
    if (btnSaveAsFile) btnSaveAsFile.disabled = false;
    if (btnDeleteFile) btnDeleteFile.disabled = false;

    SparkleStore.update("currentFileOpen", file.name);
    addLog(`✓ Wczytano plik: ${file.name} (${file.size} B)`);

    try {
      await invoke("write_workspace_file", { path: file.name, content });
      await refreshWorkspaceFiles();
    } catch (err) {
      // dozwolony fallback jeśli w trybie piaskownicy
    }
  };
  reader.onerror = () => {
    addLog(`❌ Błąd odczytu pliku z eksploratora systemowego.`);
  };
  reader.readAsText(file);
  nativeFilePicker.value = "";
}

export function saveAsFile() {
  const currentName = currentFilenameText ? currentFilenameText.textContent : "nowy_plik.py";
  const targetPath = prompt(
    "Wybierz miejsce / nazwę zapisu pliku:\n\n" +
    "• Wpisz ścieżkę w katalogu roboczym (np. folder/skrypt.py)\n" +
    "• Lub wpisz końcówkę '#export', aby natychmiast zapisać plik w dowolnym folderze na komputerze:",
    currentName
  );
  if (!targetPath) return;

  const trimmed = targetPath.trim();
  if (trimmed.endsWith("#export")) {
    const exportName = trimmed.replace("#export", "").trim() || currentName;
    const content = codeEditor ? codeEditor.value : "";
    const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = exportName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    addLog(`✓ Wyeksportowano plik na dysk: ${exportName}`);
    return;
  }

  SparkleStore.update("currentFileOpen", trimmed);
  if (currentFilenameText) currentFilenameText.textContent = trimmed;
  saveCurrentFile();
}
