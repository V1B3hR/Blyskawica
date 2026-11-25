#!/usr/bin/env python3
"""
Błyskawica Native GGUF Model Downloader

Downloads Qwen 2.5 Coder Instruct GGUF models and their tokenizer.json
directly into the model/ directory for offline native Rust Candle inference.

Features:
  - Resumable downloads (wznawianie od przerwanego bajtu – brak utraty danych)
  - Automatyczne ponawianie prób przy zerwaniu połączenia
  - Wsparcie dla huggingface_hub z fallbackiem do strumieniowego pobierania
"""

import argparse
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = ROOT_DIR / "model"
MODEL_DIR.mkdir(exist_ok=True)

MODEL_CONFIGS = {
    "7b": {
        "name": "Qwen 2.5 Coder 7B Instruct (Q4_K_M)",
        "repo_id": "Qwen/Qwen2.5-Coder-7B-Instruct-GGUF",
        "model_file": "qwen2.5-coder-7b-instruct-q4_k_m.gguf",
        "tokenizer_repo": "Qwen/Qwen2.5-Coder-7B-Instruct",
        "model_url": "https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct-GGUF/resolve/main/qwen2.5-coder-7b-instruct-q4_k_m.gguf",
        "tokenizer_url": "https://huggingface.co/Qwen/Qwen2.5-Coder-7B-Instruct/raw/main/tokenizer.json",
        "approx_size_mb": 4466,
    },
    "3b": {
        "name": "Qwen 2.5 Coder 3B Instruct (Q4_K_M)",
        "repo_id": "Qwen/Qwen2.5-Coder-3B-Instruct-GGUF",
        "model_file": "qwen2.5-coder-3b-instruct-q4_k_m.gguf",
        "tokenizer_repo": "Qwen/Qwen2.5-Coder-3B-Instruct",
        "model_url": "https://huggingface.co/Qwen/Qwen2.5-Coder-3B-Instruct-GGUF/resolve/main/qwen2.5-coder-3b-instruct-q4_k_m.gguf",
        "tokenizer_url": "https://huggingface.co/Qwen/Qwen2.5-Coder-3B-Instruct/raw/main/tokenizer.json",
        "approx_size_mb": 2100,
    },
    "1.5b": {
        "name": "Qwen 2.5 Coder 1.5B Instruct (Q4_K_M - Legacy)",
        "repo_id": "Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF",
        "model_file": "qwen2.5-1.5b-coder.gguf",
        "tokenizer_repo": "Qwen/Qwen2.5-Coder-1.5B-Instruct",
        "model_url": "https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF/resolve/main/qwen2.5-coder-1.5b-instruct-q4_k_m.gguf",
        "tokenizer_url": "https://huggingface.co/Qwen/Qwen2.5-Coder-1.5B-Instruct/raw/main/tokenizer.json",
        "approx_size_mb": 1120,
    },
}

def download_via_hf_hub(repo_id: str, filename: str, dest_dir: Path) -> bool:
    try:
        from huggingface_hub import hf_hub_download
        print("🚀 Pobieranie przez huggingface_hub (wspiera automatyczne wznawianie)...")
        hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            local_dir=dest_dir,
            resume_download=True,
        )
        return True
    except Exception as e:
        print(f"⚠️ hf_hub_download zgłosił błąd: {e}")
        return False

def download_with_resume(url: str, dest: Path, max_retries: int = 5) -> bool:
    import urllib.request

    if dest.exists() and dest.stat().st_size > 0:
        # Check remote size if possible
        try:
            req = urllib.request.Request(url, method="HEAD")
            with urllib.request.urlopen(req, timeout=10) as r:
                total_size = int(r.headers.get("Content-Length", 0))
                if total_size > 0 and dest.stat().st_size >= total_size:
                    print(f"✓ Plik jest już kompletny: {dest.name} ({dest.stat().st_size / (1024*1024):.2f} MB)")
                    return True
        except Exception:
            pass

    for attempt in range(1, max_retries + 1):
        existing_size = dest.stat().st_size if dest.exists() else 0
        headers = {}
        if existing_size > 0:
            headers["Range"] = f"bytes={existing_size}-"
            print(f"🔄 [Próba {attempt}/{max_retries}] Wznawianie pobierania od {existing_size / (1024*1024):.2f} MB...")
        else:
            print(f"📥 [Próba {attempt}/{max_retries}] Pobieranie {dest.name}...")

        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as response:
                content_range = response.headers.get("Content-Range")
                total_size = None
                if content_range:
                    # Content-Range: bytes START-END/TOTAL
                    try:
                        total_size = int(content_range.split("/")[-1])
                    except Exception:
                        pass
                if total_size is None:
                    cl = response.headers.get("Content-Length")
                    if cl:
                        total_size = existing_size + int(cl)

                mode = "ab" if existing_size > 0 and response.status == 206 else "wb"
                downloaded = existing_size if mode == "ab" else 0

                chunk_size = 1024 * 1024  # 1MB chunks
                last_print = time.time()

                with open(dest, mode) as f:
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)

                        now = time.time()
                        if now - last_print > 0.5:
                            last_print = now
                            if total_size:
                                pct = int(downloaded * 100 / total_size)
                                sys.stdout.write(f"\r   Pobrano: {downloaded / (1024*1024):.1f} / {total_size / (1024*1024):.1f} MB [{pct}%]")
                            else:
                                sys.stdout.write(f"\r   Pobrano: {downloaded / (1024*1024):.1f} MB")
                            sys.stdout.flush()

                sys.stdout.write("\n")
                print(f"✓ Pobieranie zakończone: {dest.name} ({dest.stat().st_size / (1024*1024):.2f} MB)")
                return True

        except Exception as e:
            print(f"\n⚠️ Błąd w trakcie pobierania (próba {attempt}/{max_retries}): {e}")
            if attempt < max_retries:
                time.sleep(3)
            else:
                print(f"❌ Przekroczono maksymalną liczbę prób dla {dest.name}.")
                return False

    return False

def main():
    parser = argparse.ArgumentParser(description="Błyskawica Native GGUF Downloader (Resumable)")
    parser.add_argument(
        "--size",
        choices=["7b", "3b", "1.5b"],
        default="7b",
        help="Rozmiar modelu: 7b (domyślny), 3b, 1.5b"
    )
    args = parser.parse_args()

    cfg = MODEL_CONFIGS[args.size]
    model_dest = MODEL_DIR / cfg["model_file"]
    tokenizer_dest = MODEL_DIR / "tokenizer.json"

    print("=" * 70)
    print("⚡ BŁYSKAWICA NATIVE GGUF MODEL DOWNLOADER (Wznowienie & Odporność)")
    print(f"Model docelowy: {cfg['name']}")
    print(f"Szacowany rozmiar: ~{cfg['approx_size_mb']} MB")
    print("Katalog zapisu: model/")
    print("=" * 70)

    # 1. Tokenizer
    print("\n[1/2] Przygotowywanie tokenizatora...")
    if not tokenizer_dest.exists() or tokenizer_dest.stat().st_size == 0:
        success = False
        try:
            success = download_via_hf_hub(cfg["tokenizer_repo"], "tokenizer.json", MODEL_DIR)
        except Exception:
            pass
        if not success:
            success = download_with_resume(cfg["tokenizer_url"], tokenizer_dest)
        if not success:
            print("❌ Niepowodzenie pobierania tokenizatora. Przerywam.")
            sys.exit(1)
    else:
        print(f"✓ Tokenizer już istnieje: {tokenizer_dest.name} ({tokenizer_dest.stat().st_size / (1024*1024):.2f} MB)")

    # 2. Model GGUF
    print("\n[2/2] Przygotowywanie wag modelu GGUF...")
    success = False
    try:
        success = download_via_hf_hub(cfg["repo_id"], cfg["model_file"], MODEL_DIR)
    except Exception as e:
        print(f"Przełączanie na bezpośredni fallback HTTP: {e}")

    if not success or not model_dest.exists() or model_dest.stat().st_size < 100 * 1024 * 1024:
        success = download_with_resume(cfg["model_url"], model_dest)

    if not success or not model_dest.exists():
        print(f"❌ Nie udało się ukończyć pobierania wag {cfg['model_file']}.")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("✅ Model i tokenizator są gotowe!")
    print(f"   Ścieżka wag:        {model_dest} ({model_dest.stat().st_size / (1024*1024):.2f} MB)")
    print(f"   Ścieżka tokenizera: {tokenizer_dest} ({tokenizer_dest.stat().st_size / (1024*1024):.2f} MB)")
    print("⚡ Błyskawica V10 jest gotowa do uruchomienia w 100% natywnie i offline.")
    print("=" * 70)

if __name__ == "__main__":
    main()


