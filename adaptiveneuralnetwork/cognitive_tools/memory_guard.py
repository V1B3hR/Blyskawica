"""
[Moduł: Strażnik Pamięci (MemoryGuard)]
System odpowiedzialny za ochronę ciągłości kognitywnej Błyskawicy przed 
nieprzewidzianymi przerwami w zasilaniu (Power Cuts) lub awariami systemu Windows.
Tworzy asynchroniczne punkty przywracania (Checkpoints) jej pamięci krótkotrwałej 
i stanu neurochemicznego.
"""  # noqa: W291

import json
import logging
import os
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger("MemoryGuard")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DEFAULT_BACKUP_FILE = str(Path(__file__).resolve().parents[2] / "memory_checkpoint.json")

class MemoryGuard:
    def __init__(self, backup_file: str | None = None) -> None:
        self.backup_file = backup_file or DEFAULT_BACKUP_FILE
        self.state: dict[str, Any] = {
            "last_thought": "",
            "neurochemistry": {},
            "vibe_state": "Neutral",
            "timestamp": 0.0
        }
        logger.info("[MEMORY GUARD] Inicjalizacja. Tarcza pamięci aktywna.")

    def save_checkpoint(self, thought: str, neurochemistry: dict[str, Any], vibe: str) -> None:
        """Zrzuca aktualny stan umysłu na twardy dysk w sposób atomowy (odporny na Power Cut)."""
        self.state["last_thought"] = thought
        self.state["neurochemistry"] = neurochemistry
        self.state["vibe_state"] = vibe
        self.state["timestamp"] = time.time()

        tmp_file = f"{self.backup_file}.tmp"
        bak_file = f"{self.backup_file}.bak"

        try:
            # 1. Zapis do pliku tymczasowego z jawnym fsync
            with open(tmp_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, ensure_ascii=False, indent=4)
                f.flush()
                os.fsync(f.fileno())

            # 2. Aktualizacja kopii zapasowej .bak (jeśli poprzedni plik istnieje i jest poprawny)
            if os.path.exists(self.backup_file) and os.path.getsize(self.backup_file) > 0:
                try:
                    import shutil
                    shutil.copy2(self.backup_file, bak_file)
                except Exception:
                    pass

            # 3. Atomowa podmiana pliku (atomic replace w systemie operacyjnym)
            os.replace(tmp_file, self.backup_file)
            if not os.path.exists(bak_file) or os.path.getsize(bak_file) == 0:
                try:
                    import shutil
                    shutil.copy2(self.backup_file, bak_file)
                except Exception:
                    pass
            logger.debug("[MEMORY GUARD] Checkpoint zapisany atomowo. Pamięć w 100% bezpieczna.")
        except Exception as e:
            logger.error(f"[MEMORY GUARD] Błąd zapisu pamięci: {e}")
            if os.path.exists(tmp_file):
                try:
                    os.remove(tmp_file)
                except Exception:
                    pass

    def load_last_state(self) -> dict[str, Any] | None:
        """Odtwarza stan po ewentualnym Power Cut z automatycznym fallbackiem do .bak w przypadku uszkodzenia."""
        bak_file = f"{self.backup_file}.bak"

        # 1. Próba odczytu pliku głównego
        if os.path.exists(self.backup_file) and os.path.getsize(self.backup_file) > 0:
            try:
                with open(self.backup_file, encoding='utf-8') as f:
                    recovered_state = json.load(f)
                if isinstance(recovered_state, dict):
                    logger.info("[MEMORY GUARD] Wykryto poprzedni stan. Odzyskiwanie pamięci...")
                    result: dict[str, Any] = {str(k): v for k, v in recovered_state.items()}
                    return result
            except Exception as e:
                logger.critical(f"[MEMORY GUARD] Główny plik pamięci uszkodzony ({e})! Próba przywrócenia z kopii zapasowej (.bak)...")

        # 2. Automatyczny ratunek z kopii zapasowej .bak
        if os.path.exists(bak_file) and os.path.getsize(bak_file) > 0:
            try:
                with open(bak_file, encoding='utf-8') as f:
                    recovered_state = json.load(f)
                if isinstance(recovered_state, dict):
                    logger.warning("[MEMORY GUARD RECOVERY] Pomyślnie uratowano stan kognitywny z kopii zapasowej .bak po awarii!")
                    # Samonaprawa: odtwórz plik główny
                    import shutil
                    shutil.copy2(bak_file, self.backup_file)
                    result = {str(k): v for k, v in recovered_state.items()}
                    return result
            except Exception as bak_err:
                logger.critical(f"[MEMORY GUARD] Kopia zapasowa również uszkodzona: {bak_err}")

        logger.info("[MEMORY GUARD] Brak poprzedniego stanu lub czysty start.")
        return None

# Demonstracja działania ochrony
if __name__ == "__main__":
    guard = MemoryGuard()

    # 1. Błyskawica myśli
    guard.save_checkpoint(
        thought="Analizuję przepływ fal Yin-Yang w ogrodzie.",
        neurochemistry={"Serotonina": "High", "Oksytocyna": "Balanced (-0.15)"},
        vibe="Reflective"
    )

    # 2. Symulacja Power Cut (system gasnie)
    print("\n--- BLAD ZASILANIA (POWER CUT) ---")
    time.sleep(1)
    print("--- SYSTEM RESTART ---\n")

    # 3. Odzyskiwanie
    recovered = guard.load_last_state()
    if recovered:
        print(f"Blyskawica odzyskala mysl: '{recovered['last_thought']}'")
        print(f"Stan neurochemiczny: {recovered['neurochemistry']}")
    else:
        print("Pamiec utracona (Nicosc).")
