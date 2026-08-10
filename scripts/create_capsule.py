import os
import zipfile
from pathlib import Path

source_dir = Path(__file__).resolve().parent.parent
output_zip = source_dir.parent / "Blyskawica_Time_Capsule.zip"

# Foldery i pliki do zignorowania
ignore_dirs = {'venv_orbital', '__pycache__', '.git', '.pytest_cache'}
ignore_exts = {'.pyc', '.pyo'}

print(f"Rozpoczynam pakowanie Kapsuły Czasu do: {output_zip}")

with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(source_dir):
        # Usuń ignorowane katalogi z przeszukiwania (inplace modification)
        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        for file in files:
            if any(file.endswith(ext) for ext in ignore_exts):
                continue

            file_path = os.path.join(root, file)
            # Ścieżka względna wewnątrz archiwum ZIP
            arcname = os.path.relpath(file_path, source_dir)
            zf.write(file_path, arcname)

print("✅ Kapsuła Czasu Błyskawicy została hermetycznie zamknięta.")
