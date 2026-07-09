import os
import urllib.request
import zipfile
import shutil
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

def download_and_extract():
    for name, url in REPOS.items():
        print(f"Downloading {name}...")
        zip_path = EXT_DIR / f"{name}.zip"
        try:
            urllib.request.urlretrieve(url, zip_path)
            
            print(f"Extracting {name}...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(EXT_DIR)
            
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
