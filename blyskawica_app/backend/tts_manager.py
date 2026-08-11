import logging
import os
from pathlib import Path

import requests

logger = logging.getLogger(__name__)

class BłyskawicaTTS:
    def __init__(self, api_url="http://127.0.0.1:7851"):
        self.api_url = api_url
        self.is_initialized = False
        self.speaker_wav = None # Ścieżka do próbki referencyjnej głosu Błyskawicy

        # Oczekiwany katalog z nagraniem referencyjnym
        self.media_dir = Path(__file__).resolve().parent.parent / "media_storage" / "voices"
        self.media_dir.mkdir(parents=True, exist_ok=True)

        # Domyślny plik referencyjny
        self.default_reference = self.media_dir / "blyskawica_base_voice.mp3"

    def initialize(self):
        """Sprawdza połączenie z serwerem XTTS-API."""
        logger.info(f"⏳ Szukam serwera mowy pod adresem: {self.api_url}...")
        try:
            # W API XTTS sprawdzamy endpoint /languages lub uderzamy po prostu o status
            response = requests.get(f"{self.api_url}/languages", timeout=2.0)
            if response.status_code == 200:
                self.is_initialized = True
                logger.info("✅ Pomyślnie połączono z serwerem mowy (Ośrodek Broki podłączony).")

            if self.default_reference.exists():
                self.speaker_wav = str(self.default_reference)
                logger.info("✅ Głos referencyjny Błyskawicy odnaleziony.")
            else:
                logger.warning(f"⚠️ Brak pliku referencyjnego: {self.default_reference}. "
                               f"Aby generować mowę, musisz najpierw wrzucić próbkę 3-5 sekund do tego folderu.")


        except requests.exceptions.ConnectionError:
            logger.error(f"❌ Serwer API mowy nie odpowiada ({self.api_url}). Upewnij się, że XTTS-API-Server jest włączony.")
        except Exception as e:
            logger.error(f"❌ Błąd podczas łączenia z XTTS API: {e}")

    def synthesize(self, text: str, output_path: str, neuro_state: dict = None):
        """
        Generuje audio na podstawie tekstu.
        W przyszłości neuro_state będzie modyfikować parametry generacji (Faza 3.5).
        """
        if not self.is_initialized:
            logger.warning("Model TTS nie jest zainicjalizowany. Generowanie pominięte.")
            return False

        if not self.speaker_wav or not os.path.exists(self.speaker_wav):
            logger.warning("Brak pliku referencyjnego (speaker_wav). Wymagany do XTTS.")
            return False

        try:
            def parse_metric(val, default):
                if val is None:
                    return default
                try:
                    v = float(val)
                    if v > 5.0:
                        return v / 100.0
                    return v
                except Exception:
                    return default

            adrenaline = parse_metric(neuro_state.get("adrenaline"), 0.0) if neuro_state else 0.0
            dopamine = parse_metric(neuro_state.get("dopamine"), 0.5) if neuro_state else 0.5

            speed_val = 1.0 + (adrenaline * 0.4) + (dopamine * 0.1) # Max ~1.5x speed

            # Specyfikacja AllTalk-TTS API (v2)
            payload = {
                "text_input": text,
                "text_filtering": "standard",
                "character_voice_gen": "blyskawica_base_voice.mp3",
                "language": "pl",
                "output_file_name": "blyskawica_speech",
                "tts_model": "xtts",
                "speed": round(speed_val, 2),
                "temperature": 0.7 + (adrenaline * 0.2) # Więcej adrenaliny = wyższa temperatura (większa wariancja)
            }

            logger.info(f"Wysyłam prośbę do AllTalk (XTTS)... Speed: {speed_val:.2f}")
            response = requests.post(f"{self.api_url}/api/tts-generate", data=payload)

            if response.status_code == 200:
                with open(output_path, "wb") as f:
                    f.write(response.content)
                return True
            else:
                logger.error(f"AllTalk zwrócił błąd: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"Błąd komunikacji API syntezy mowy: {e}")
            return False
