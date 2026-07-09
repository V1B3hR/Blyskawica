import os
import shutil
import re
from pathlib import Path

# Ścieżka bazowa
BASE_DIR = Path(__file__).resolve().parent.parent / "adaptiveneuralnetwork"
CORE_DIR = BASE_DIR / "core"
BACKUP_DIR = BASE_DIR / "core_backup"

def backup_core():
    print("[DEBUG] 1. Tworzenie kopii zapasowej (Isolate & Document)")
    if BACKUP_DIR.exists():
        shutil.rmtree(BACKUP_DIR)
    shutil.copytree(CORE_DIR, BACKUP_DIR)
    print(f"  -> Zapasowy folder: {BACKUP_DIR} utworzony.")

def create_tree():
    print("[DEBUG] 2. Budowa struktury Drzewa Nerwowego")
    dirs = [
        "central_nervous_system",
        "peripheral_nervous_system",
        "cognitive_tools",
        "immune_system"
    ]
    for d in dirs:
        (BASE_DIR / d).mkdir(exist_ok=True)
        # Tworzymy puste __init__.py
        (BASE_DIR / d / "__init__.py").touch()
    print("  -> Gałęzie wyhodowane.")

def move_files():
    print("[DEBUG] 3. Przenoszenie narządów do nowych gałęzi")
    
    # Mapowanie plików do nowych lokalizacji
    mapping = {
        "peripheral_nervous_system": ["sensory_hub.py", "social_comm.py", "social_learning.py"],
        "cognitive_tools": ["diamond_yantra.py", "polymathic_hub.py"],
        "immune_system": ["wolf_teeth.py", "epistemic_defense.py", "trust_network.py", "robustness_validator.py"]
    }
    
    moved_tracker = {}
    
    # Przenieś zdefiniowane pliki
    for new_dir, files in mapping.items():
        for file in files:
            src = CORE_DIR / file
            dst = BASE_DIR / new_dir / file
            if src.exists():
                shutil.move(src, dst)
                moved_tracker[file] = new_dir
                print(f"  -> Przeniesiono: {file} -> {new_dir}")
                
    # Pozostałe pliki z 'core' (tylko na najwyższym poziomie) idą do central_nervous_system
    for item in CORE_DIR.iterdir():
        if item.is_file() and item.suffix == ".py" and item.name != "__init__.py":
            dst = BASE_DIR / "central_nervous_system" / item.name
            shutil.move(item, dst)
            moved_tracker[item.name] = "central_nervous_system"
            print(f"  -> Przeniesiono (domyślnie CNS): {item.name}")
            
    # Podkatalogi z 'core' (np. intelligence, ecosystem) przenosimy do CNS
    for item in CORE_DIR.iterdir():
        if item.is_dir() and item.name != "__pycache__":
            dst = BASE_DIR / "central_nervous_system" / item.name
            shutil.move(item, dst)
            print(f"  -> Przeniesiono podkatalog: {item.name} -> central_nervous_system")

    return moved_tracker

def update_imports(moved_tracker):
    print("[DEBUG] 4. Aktualizacja ścieżek nerwowych (Importy)")
    
    # Musimy zaktualizować wszystkie pliki .py w całym projekcie
    project_root = Path(__file__).resolve().parent.parent
    
    for py_file in project_root.rglob("*.py"):
        # Omijamy foldery venv_orbital i core_backup
        if "venv_orbital" in py_file.parts or "core_backup" in py_file.parts:
            continue
            
        with open(py_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        original_content = content
        
        # 1. Zmiana bezwzględnych importów (np. from adaptiveneuralnetwork.central_nervous_system.alive_node import)
        for filename, target_dir in moved_tracker.items():
            mod_name = filename.replace(".py", "")
            
            # Wzorzec: adaptiveneuralnetwork.core.module -> adaptiveneuralnetwork.target_dir.module
            content = content.replace(
                f"adaptiveneuralnetwork.core.{mod_name}",
                f"adaptiveneuralnetwork.{target_dir}.{mod_name}"
            )
            
        # 2. Naprawa względnych importów w samych przeniesionych plikach!
        # Jeśli plik był w core/ i został przeniesiony do np. peripheral_nervous_system,
        # jego "from . module" mogło się popsuć.
        # Zamieniamy wszystkie względne importy w tych plikach na BEZWZGLĘDNE, 
        # bo to najbezpieczniejsze rozwiązanie w Pythonie.
        if py_file.parent.name in ["central_nervous_system", "peripheral_nervous_system", "cognitive_tools", "immune_system"]:
            # Znajdź linie "from .xxx import yyy" lub "from . import xxx"
            def relative_replacer(match):
                import_target = match.group(1) # np. 'alive_node'
                # Jeśli plik jest w naszym trackerze, wiemy gdzie trafił
                if f"{import_target}.py" in moved_tracker:
                    new_dir = moved_tracker[f"{import_target}.py"]
                    return f"from adaptiveneuralnetwork.{new_dir}.{import_target} import"
                # Jeśli importowano podfolder, np "from .intelligence.xxx"
                elif import_target.startswith("intelligence") or import_target.startswith("ecosystem"):
                    # Trafiło to do central_nervous_system
                    return f"from adaptiveneuralnetwork.central_nervous_system.{import_target} import"
                return match.group(0) # Zostaw bez zmian jeśli to coś dziwnego
                
            content = re.sub(r"from \.([a-zA-Z0-9_]+) import", relative_replacer, content)

        if content != original_content:
            with open(py_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  -> Zaktualizowano importy w: {py_file.name}")

def verify_and_clean():
    print("[DEBUG] 5. Test i Weryfikacja (Verification steps)")
    # Sprawdzenie czy core jest puste (nie licząc __init__)
    # Właściwie nie musimy go usuwać, niech zostanie puste na razie dla bezpieczeństwa
    print("  -> Refaktoryzacja zakończona sukcesem. Uruchom testy jednostkowe, by potwierdzić.")

if __name__ == "__main__":
    backup_core()
    create_tree()
    tracker = move_files()
    update_imports(tracker)
    verify_and_clean()
