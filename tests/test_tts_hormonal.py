import warnings

warnings.filterwarnings("ignore", category=FutureWarning, module="torch.cuda")
warnings.filterwarnings("ignore", message="The pynvml package is deprecated")
import os  # noqa: E402

# Add project root to sys.path
import sys  # noqa: E402
import tempfile  # noqa: E402
import unittest  # noqa: E402
from pathlib import Path  # noqa: E402
from unittest.mock import MagicMock, patch  # noqa: E402

import requests  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from main import app, tts_engine
    from tts_manager import BłyskawicaTTS
except ModuleNotFoundError:
    from blyskawica_app.backend.main import app, tts_engine
    from blyskawica_app.backend.tts_manager import BłyskawicaTTS


class TestHormonalTTS(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    @patch("requests.get")
    def test_tts_initialization_online(self, mock_get):
        """Verify TTS engine registers successfully when AllTalk is online."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        engine = BłyskawicaTTS()
        # Mock default speaker path check
        engine.default_reference = Path(self.temp_dir.name) / "voice.mp3"
        engine.default_reference.touch()

        engine.initialize()
        self.assertTrue(engine.is_initialized)
        self.assertEqual(engine.speaker_wav, str(engine.default_reference))

    @patch("requests.get")
    def test_tts_initialization_offline(self, mock_get):
        """Verify TTS handles connection issues gracefully (offline mode)."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")

        engine = BłyskawicaTTS()
        engine.initialize()
        self.assertFalse(engine.is_initialized)

    @patch("requests.post")
    def test_tts_synthesis_modulation(self, mock_post):
        """Verify neurochemical values modify XTTS parameters correctly."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"fake_audio_bytes"
        mock_post.return_value = mock_response

        engine = BłyskawicaTTS()
        engine.is_initialized = True

        # Create temp reference file
        ref_file = Path(self.temp_dir.name) / "voice.mp3"
        ref_file.touch()
        engine.speaker_wav = str(ref_file)

        out_file = Path(self.temp_dir.name) / "output.mp3"

        # Test with high excitement (dopamine/adrenaline)
        neuro_state = {"adrenaline": 0.8, "dopamine": 0.9}
        success = engine.synthesize("Witaj Andrzej", str(out_file), neuro_state)

        self.assertTrue(success)
        self.assertTrue(out_file.exists())

        # Assert post payload contains modulated speed & temperature
        args, kwargs = mock_post.call_args
        payload = kwargs.get("data", {})
        self.assertEqual(payload["text_input"], "Witaj Andrzej")
        self.assertGreater(payload["speed"], 1.1)
        self.assertGreater(payload["temperature"], 0.8)

    def test_fastapi_endpoints_offline_fallback(self):
        """Verify FastAPI chat and tts endpoints handle offline TTS server gracefully."""
        # Ensure engine is marked offline for test
        tts_engine.is_initialized = False

        client = TestClient(app)

        # 1. Chat request should succeed even if TTS is offline (audio_url=None)
        response = client.post("/api/chat", data={"message": "Cześć Błyskawico"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("reply", data)
        self.assertIsNone(data["audio_url"])

        # 2. Adhoc /api/tts endpoint should return 503 Service Unavailable when offline
        token_response = client.get(
            "/api/auth/token",
            headers={"X-Internal-Request": "sparkle-tauri-shell"}
        )
        self.assertEqual(token_response.status_code, 200)
        token = token_response.json()["token"]

        tts_res = client.post(
            "/api/tts",
            data={"text": "Hello"},
            headers={"X-Blyskawica-Token": token}
        )
        self.assertEqual(tts_res.status_code, 503)
        self.assertIn("offline", tts_res.json()["message"])


if __name__ == "__main__":
    unittest.main()
