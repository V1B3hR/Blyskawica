import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def get_target_triple():
    machine = platform.machine().lower()
    system = platform.system().lower()
    
    if machine in ["amd64", "x86_64"]:
        arch = "x86_64"
    elif machine in ["arm64", "aarch64"]:
        arch = "aarch64"
    else:
        arch = machine
        
    if system == "windows":
        return f"{arch}-pc-windows-msvc"
    elif system == "darwin":
        return f"{arch}-apple-darwin"
    else:
        return f"{arch}-unknown-linux-gnu"


def main():
    print("🛠️ [Build Sidecar]: Rozpoczęcie odtwarzalnego procesu kompilacji...")

    # 1. Definiowanie ścieżek
    current_dir = Path(__file__).resolve().parent.parent
    backend_script = current_dir / "blyskawica_app" / "backend" / "main.py"
    dist_dir = current_dir / "dist"
    build_dir = current_dir / "build"
    tauri_bin_dir = current_dir / "sparkle_app" / "src-tauri" / "bin"

    tauri_bin_dir.mkdir(parents=True, exist_ok=True)

    # Użycie sys.executable gwarantuje użycie aktywnego środowiska wirtualnego Python
    python_exe = sys.executable
    print(f"✓ Środowisko Python: {python_exe}")

    # Hidden imports i zbierane pakiety dla PyInstallera
    hidden_imports = [
        "fastapi",
        "uvicorn",
        "psutil",
        "httpx",
        "requests",
        "numpy",
        "dotenv",
    ]

    hidden_flags = []
    for imp in hidden_imports:
        hidden_flags.extend(["--hidden-import", imp])

    # 2. Uruchomienie PyInstallera via module execution (python -m PyInstaller)
    exe_name = "blyskawica_backend"
    cmd = [
        python_exe, "-m", "PyInstaller",
        "--onefile",
        "--noconsole",
        "--name", exe_name,
        "--distpath", str(dist_dir),
        "--workpath", str(build_dir),
    ] + hidden_flags + [str(backend_script)]

    print(f"🚀 Uruchamianie kompilacji: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
        print("✓ PyInstaller zakończył kompilację pomyślnie.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Błąd podczas kompilacji PyInstaller: {e}")
        sys.exit(1)

    # 3. Kopiowanie z odpowiednim target-triple dla Tauri
    target_triple = get_target_triple()
    ext = ".exe" if sys.platform == "win32" else ""
    src_exe = dist_dir / f"{exe_name}{ext}"
    dest_exe = tauri_bin_dir / f"{exe_name}-{target_triple}{ext}"

    if src_exe.exists():
        print(f"📦 Kopiowanie skompilowanego pliku do katalogu Tauri: {dest_exe}")
        shutil.copy2(src_exe, dest_exe)

        # Fallback z czystą nazwą
        shutil.copy2(src_exe, tauri_bin_dir / f"{exe_name}{ext}")
        print(f"🎉 [Build Sidecar]: Sukces! Sidecar wariantu {target_triple} gotowy.")
    else:
        print(f"❌ Błąd: Nie znaleziono pliku wynikowego {src_exe}")
        sys.exit(1)


if __name__ == "__main__":
    main()
