import os
import shutil
import urllib.request
import zipfile
from pathlib import Path

REPOS = {
    "nethical": "https://github.com/V1B3hR/nethical/archive/refs/heads/main.zip",
    "GCS-v7-with-empathy": "https://github.com/V1B3hR/GCS-v7-with-empathy/archive/refs/heads/main.zip",
    "bioart": "https://github.com/V1B3hR/bioart/archive/refs/heads/main.zip",
    "nethical-recon": "https://github.com/V1B3hR/nethical-recon/archive/refs/heads/main.zip",
    "AiMedRes": "https://github.com/V1B3hR/AiMedRes/archive/refs/heads/main.zip"
}

BASE_DIR = Path(__file__).resolve().parent
EXT_DIR = BASE_DIR / "extensions"
EXT_DIR.mkdir(exist_ok=True)

import sys


def is_safe_zip_path(target_dir: Path, path: Path) -> bool:
    try:
        resolved_target = target_dir.resolve()
        resolved_path = path.resolve()
        return resolved_path.is_relative_to(resolved_target)
    except Exception:
        return False


def safe_extract_zip(zip_file: zipfile.ZipFile, extract_to: Path) -> None:
    extract_to_resolved = extract_to.resolve()
    for member in zip_file.infolist():
        member_path = extract_to_resolved / member.filename
        if not is_safe_zip_path(extract_to_resolved, member_path):
            raise RuntimeError(f"Zip Slip detected! Malicious path inside archive: {member.filename}")
    if sys.version_info >= (3, 12):
        getattr(zip_file, "extractall")(extract_to, filter="data")
    else:
        zip_file.extractall(extract_to)


def download_and_extract() -> None:
    for name, url in REPOS.items():
        print(f"Downloading {name}...")
        zip_path = EXT_DIR / f"{name}.zip"
        try:
            urllib.request.urlretrieve(url, zip_path)

            print(f"Extracting {name} safely...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                safe_extract_zip(zip_ref, EXT_DIR)

            # GitHub zips usually extract to a folder named repo-main
            extracted_folder = EXT_DIR / f"{name}-main"
            final_folder = EXT_DIR / name

            if final_folder.exists():
                shutil.rmtree(final_folder)

            os.rename(extracted_folder, final_folder)
            os.remove(zip_path)
            print(f"[OK] Successfully integrated {name}")
        except Exception as e:
            print(f"[ERROR] Failed to process {name}: {e}")

if __name__ == "__main__":
    download_and_extract()
