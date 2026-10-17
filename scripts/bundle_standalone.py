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

def create_standalone_bundle() -> bool:
    print("=" * 70)
    print("⚡ TWORZENIE PACZKI BŁYSKAWICA STANDALONE (OFFLINE PORTABLE)")
    print("=" * 70)

    repo_root = Path(__file__).resolve().parent.parent
    release_exe = repo_root / "target" / "release" / "sparkle_app.exe"
    model_dir = repo_root / "model"

    # Domyślny docelowy folder Standalone wskazany przez Architekta:
    custom_target = Path(r"C:\Projekty\Błyskawica standalone")
    if custom_target.parent.exists():
        dist_dir = custom_target
    else:
        dist_dir = repo_root.parent / "Błyskawica standalone"

    if not release_exe.exists():
        print(f"❌ BŁĄD: Nie znaleziono pliku wykonywalnego release: {release_exe}")
        print("Najpierw uruchom: cargo build --release --bin sparkle_app")
        return False

    print(f"\n[1/4] Przygotowanie katalogu docelowego: {dist_dir}...")
    dist_dir.mkdir(parents=True, exist_ok=True)
    # Zgodnie z wolą Architekta: W folderze znajdują się pliki użytkownika - NIGDY ich nie czyścimy (bez rmtree)!

    print(f"\n[2/4] Aktualizacja natywnej aplikacji sparkle_app.exe ({release_exe.stat().st_size / (1024*1024):.2f} MB)...")
    dest_exe = dist_dir / "sparkle_app.exe"
    shutil.copy2(release_exe, dest_exe)
    print(f"  ✓ Zapisano najnowszą skompilowaną aplikację: {dest_exe}")

    print("\n[3/4] Weryfikacja wag modelu i tokenizatora (ochrona istniejących plików)...")
    dest_model_dir = dist_dir / "model"
    dest_model_dir.mkdir(exist_ok=True)

    # Tokenizer - zachowaj jeśli już istnieje
    dest_tokenizer = dest_model_dir / "tokenizer.json"
    tokenizer_src = model_dir / "tokenizer.json"
    if dest_tokenizer.exists() and dest_tokenizer.stat().st_size > 0:
        print(f"  ✓ Istniejący tokenizator zachowany: {dest_tokenizer.name} ({dest_tokenizer.stat().st_size / 1024:.1f} KB)")
    elif tokenizer_src.exists():
        print(f"  ✓ Kopiowanie tokenizatora: {tokenizer_src.name}")
        shutil.copy2(tokenizer_src, dest_tokenizer)
    else:
        print("  ⚠️ OSTRZEŻENIE: Brak tokenizer.json")

    # Szukanie modelu GGUF - zachowaj istniejące modele w dest_model_dir
    existing_dest_gguf = list(dest_model_dir.glob("*.gguf"))
    if existing_dest_gguf:
        for f in existing_dest_gguf:
            print(f"  ✓ Istniejący model GGUF zachowany: {f.name} ({f.stat().st_size / (1024*1024):.2f} MB)")
    else:
        gguf_files = list(model_dir.glob("*.gguf"))
        if gguf_files:
            preferred = next((f for f in gguf_files if "7b" in f.name.lower()), gguf_files[0])
            print(f"  ✓ Wykryto model GGUF: {preferred.name} ({preferred.stat().st_size / (1024*1024):.2f} MB)")
            dest_gguf = dest_model_dir / preferred.name
            try:
                os.link(preferred, dest_gguf)
                print("    ✓ Błyskawiczny NTFS Hardlink utworzony.")
            except Exception:
                print("    Kopiowanie pliku...")
                shutil.copy2(preferred, dest_gguf)
        else:
            print("  ⚠️ OSTRZEŻENIE: Brak plików .gguf w katalogu model/!")

    print("\n[4/4] Weryfikacja plików startowych i manifestu...")
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
