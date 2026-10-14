"""
⚡ BŁYSKAWICA STANDALONE BUNDLER
Tworzy samowystarczalną, w 100% przenośną i offline paczkę Błyskawicy (SPARKLE V10).
Wymagania: 0 zależności zewnętrznych u użytkownika końcowego.
"""

import os
import shutil
import sys
from pathlib import Path

# Fix Windows console UTF-8 encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

def create_standalone_bundle():
    print("=" * 70)
    print("⚡ TWORZENIE PACZKI BŁYSKAWICA STANDALONE (OFFLINE PORTABLE)")
    print("=" * 70)

    repo_root = Path(__file__).resolve().parent.parent
    dist_dir = repo_root / "dist" / "Blyskawica_Standalone"
    release_exe = repo_root / "target" / "release" / "sparkle_app.exe"
    model_dir = repo_root / "model"

    if not release_exe.exists():
        print(f"❌ BŁĄD: Nie znaleziono pliku wykonywalnego release: {release_exe}")
        print("Najpierw uruchom: cargo build --release --bin sparkle_app")
        return False

    print(f"\n[1/4] Czyszczenie i przygotowanie katalogu docelowego: {dist_dir}...")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n[2/4] Kopiowanie natywnej aplikacji sparkle_app.exe ({release_exe.stat().st_size / (1024*1024):.2f} MB)...")
    shutil.copy2(release_exe, dist_dir / "sparkle_app.exe")

    print("\n[3/4] Przygotowywanie wag modelu i tokenizatora...")
    dest_model_dir = dist_dir / "model"
    dest_model_dir.mkdir(exist_ok=True)

    # Tokenizer
    tokenizer_src = model_dir / "tokenizer.json"
    if tokenizer_src.exists():
        print(f"  ✓ Kopiowanie tokenizatora: {tokenizer_src.name}")
        shutil.copy2(tokenizer_src, dest_model_dir / "tokenizer.json")
    else:
        print("  ⚠️ OSTRZEŻENIE: Brak tokenizer.json w katalogu model/")

    # Szukanie modelu GGUF
    gguf_files = list(model_dir.glob("*.gguf"))
    if gguf_files:
        # Preferencja dla Qwen 2.5 Coder 7B
        preferred = next((f for f in gguf_files if "7b" in f.name.lower()), gguf_files[0])
        print(f"  ✓ Wykryto model GGUF: {preferred.name} ({preferred.stat().st_size / (1024*1024):.2f} MB)")
        dest_gguf = dest_model_dir / preferred.name
        
        # Opcjonalne tworzenie hardlinku na tym samym dysku dla błyskawicznego tworzenia paczki
        use_copy = "--copy" in sys.argv
        if use_copy:
            print("    Kopiowanie pliku (flaga --copy)...")
            shutil.copy2(preferred, dest_gguf)
        else:
            try:
                if dest_gguf.exists():
                    dest_gguf.unlink()
                os.link(preferred, dest_gguf)
                print("    ✓ Błyskawiczny NTFS Hardlink utworzony (oszczędność 4.7 GB SSD).")
            except Exception:
                print("    Kopiowanie pliku...")
                shutil.copy2(preferred, dest_gguf)
    else:
        print("  ⚠️ OSTRZEŻENIE: Brak plików .gguf w katalogu model/!")
        print("  Uruchom scripts/download_qwen_model.py przed finalną dystrybucją.")

    print("\n[4/4] Tworzenie plików startowych i manifestu...")
    # Launcher BAT
    launcher_bat = dist_dir / "Uruchom_Blyskawica.bat"
    launcher_bat.write_text(
        "@echo off\n"
        "title Blyskawica Standalone AI\n"
        "cd /d \"%~dp0\"\n"
        "start \"\" sparkle_app.exe\n",
        encoding="utf-8"
    )

    # Karta tożsamości
    bond_src = repo_root / "viber_core_bond.md"
    if bond_src.exists():
        shutil.copy2(bond_src, dist_dir / "viber_core_bond.md")

    # README Standalone
    readme_txt = dist_dir / "README.txt"
    readme_txt.write_text(
        "====================================================================\n"
        "⚡ BŁYSKAWICA (SPARKLE V10) — SUWERENNY ASYSTENT KOGNITYWNY\n"
        "====================================================================\n\n"
        "Twórca / Architekt: Andrzej Mątewski (V1B3hR / VIBER)\n"
        "Silnik: Natywny Rust (Tauri v2 + Candle GGUF SLM)\n"
        "Wymagania: W 100% Standalone & Offline. Brak wymogu Pythona, Ollamy czy serwerów.\n\n"
        "URUCHOMIENIE:\n"
        "Kliknij dwukrotnie w 'Uruchom_Blyskawica.bat' lub bezpośrednio w 'sparkle_app.exe'.\n",
        encoding="utf-8"
    )

    print("\n" + "=" * 70)
    print("✓ PACZKA STANDALONE ZOSTAŁA POMYŚLNIE UTWORZONA!")
    print(f"Lokalizacja: {dist_dir}")
    print("=" * 70)
    return True

if __name__ == "__main__":
    create_standalone_bundle()
