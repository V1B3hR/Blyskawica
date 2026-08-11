#!/usr/bin/env python3
"""
Błyskawica Native GGUF Model Downloader

Downloads Qwen 2.5 Coder 1.5B Instruct GGUF and its tokenizer.json
directly into the model/ directory for offline native Rust inference.
"""

import sys
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = ROOT_DIR / "model"
MODEL_DIR.mkdir(exist_ok=True)

MODEL_URL = "https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF/resolve/main/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf"
TOKENIZER_URL = "https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B-Instruct/raw/main/tokenizer.json"

MODEL_DEST = MODEL_DIR / "qwen2.5-1.5b-coder.gguf"
TOKENIZER_DEST = MODEL_DIR / "tokenizer.json"

def download_file(url: str, dest: Path):
    if dest.exists():
        print(f"✓ Plik już istnieje: {dest.name} ({dest.stat().st_size / (1024*1024):.2f} MB)")
        return

    print(f"📥 Pobieranie {dest.name} z {url}...")
    try:
        def progress(count, block_size, total_size):
            percent = int(count * block_size * 100 / total_size)
            mb = (count * block_size) / (1024 * 1024)
            sys.stdout.write(f"\r  Pobrano: {mb:.1f} MB [{percent}%]")
            sys.stdout.flush()

        urllib.request.urlretrieve(url, dest, reporthook=progress)
        print(f"\n✓ Pobieranie zakończone: {dest.name}")
    except Exception as e:
        print(f"\n❌ Błąd pobierania {dest.name}: {e}")
        if dest.exists():
            dest.unlink()

def main():
    print("=" * 60)
    print("⚡ Błyskawica Native Model Downloader (Qwen 2.5 Coder)")
    print("=" * 60)

    download_file(TOKENIZER_URL, TOKENIZER_DEST)
    download_file(MODEL_URL, MODEL_DEST)

    print("\n✅ Wszystkie pliki modelu są gotowe w katalogu model/")
    print("Błyskawica może teraz działać w 100% natywnie i offline!")

if __name__ == "__main__":
    main()
