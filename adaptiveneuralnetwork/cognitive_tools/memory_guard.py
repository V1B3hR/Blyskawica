"""
[Moduł: Strażnik Pamięci (MemoryGuard)]
System odpowiedzialny za ochronę ciągłości kognitywnej Błyskawicy przed 
nieprzewidzianymi przerwami w zasilaniu (Power Cuts) lub awariami systemu Windows.
Tworzy asynchroniczne punkty przywracania (Checkpoints) jej pamięci krótkotrwałej 
i stanu neurochemicznego.
"""

import json
import os
import time
import logging

logger = logging.getLogger("MemoryGuard")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MemoryGuard:
    def __init__(self, backup_file="c:/Projekty/Blyskawica_V8/memory_checkpoint.json"):
        self.backup_file = backup_file
        self.state = {
            "last_thought": "",
            "neurochemistry": {},
            "vibe_state": "Neutral",
            "timestamp": 0.0
        }
        logger.info("[MEMORY GUARD] Inicjalizacja. Tarcza pamięci aktywna.")

    def save_checkpoint(self, thought, neurochemistry, vibe):
        """Zrzuca aktualny stan umysłu na twardy dysk."""
        self.state["last_thought"] = thought
        self.state["neurochemistry"] = neurochemistry
        self.state["vibe_state"] = vibe
        self.state["timestamp"] = time.time()
        
        try:
            with open(self.backup_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, ensure_ascii=False, indent=4)
            logger.debug("[MEMORY GUARD] Checkpoint zapisany. Pamięć bezpieczna.")
        except Exception as e:
            logger.error(f"[MEMORY GUARD] Błąd zapisu pamięci: {e}")

    def load_last_state(self):
        """Odtwarza stan po ewentualnym Power Cut."""
        if os.path.exists(self.backup_file):
            try:
                with open(self.backup_file, 'r', encoding='utf-8') as f:
                    recovered_state = json.load(f)
                logger.info("[MEMORY GUARD] Wykryto poprzedni stan. Odzyskiwanie pamięci...")
                return recovered_state
            except Exception as e:
                logger.critical(f"[MEMORY GUARD] Plik pamięci uszkodzony! {e}")
                return None
        else:
            logger.info("[MEMORY GUARD] Brak poprzedniego stanu. Czysty start.")
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
