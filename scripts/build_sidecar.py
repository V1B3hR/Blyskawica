import os
import sys
import shutil
import subprocess
from pathlib import Path

def main():
    print("🛠️ [Build Sidecar]: Rozpoczęcie procesu kompilacji...")
    
    # 1. Definiowanie ścieżek
    current_dir = Path(__file__).resolve().parent.parent
    backend_script = current_dir / "blyskawica_app" / "backend" / "main.py"
    dist_dir = current_dir / "dist"
    build_dir = current_dir / "build"
    tauri_bin_dir = current_dir / "sparkle_app" / "src-tauri" / "bin"
    
    # Upewniamy się, że folder bin w src-tauri istnieje
    tauri_bin_dir.mkdir(parents=True, exist_ok=True)
    
    # Znajdź ścieżkę do pyinstallera w profilu użytkownika
    pyinstaller_bin = Path(os.environ.get("APPDATA")).parent / "Roaming" / "Python" / "Python314" / "Scripts" / "pyinstaller.exe"
    if not pyinstaller_bin.exists():
        # Fallback do zwykłego polecenia w PATH
        pyinstaller_cmd = "pyinstaller"
    else:
        pyinstaller_cmd = str(pyinstaller_bin)
        
    print(f"✓ Używany kompilator PyInstaller: {pyinstaller_cmd}")
    
    # 2. Uruchomienie PyInstallera
    # --onefile: kompilacja do pojedynczego pliku
    # --noconsole: brak wyskakującego okienka konsoli
    # --name: nazwa pliku wynikowego
    cmd = [
        pyinstaller_cmd,
        "--onefile",
        "--noconsole",
        "--name", "blyskawica_backend",
        "--distpath", str(dist_dir),
        "--workpath", str(build_dir),
        str(backend_script)
    ]
    
    print(f"🚀 Uruchamianie polecenia: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
        print("✓ PyInstaller zakończył kompilację pomyślnie.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Błąd podczas kompilacji PyInstaller: {e}")
        sys.exit(1)
        
    # 3. Kopiowanie i zmiana nazwy pod wymogi Tauri (sidecar target triple)
    # Na systemie Windows Tauri oczekuje nazwy pliku w formacie:
    # <nazwa_programu>-x86_64-pc-windows-msvc.exe
    target_triple = "x86_64-pc-windows-msvc"
    src_exe = dist_dir / "blyskawica_backend.exe"
    dest_exe = tauri_bin_dir / f"blyskawica_backend-{target_triple}.exe"
    
    if src_exe.exists():
        print(f"📦 Kopiowanie skompilowanego pliku do katalogu Tauri: {dest_exe}")
        shutil.copy2(src_exe, dest_exe)
        
        # Tworzymy też kopię o standardowej nazwie jako fallback
        shutil.copy2(src_exe, tauri_bin_dir / "blyskawica_backend.exe")
        print("🎉 [Build Sidecar]: Sukces! Backend jest w pełni przygotowany jako Sidecar w Tauri.")
    else:
        print("❌ Błąd: Nie znaleziono pliku wynikowego blyskawica_backend.exe w folderze dist.")
        sys.exit(1)

if __name__ == "__main__":
    main()
