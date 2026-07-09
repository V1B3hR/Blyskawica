import unittest
import sys
import json
import os
from unittest import mock
from fastapi.testclient import TestClient
from blyskawica_app.backend.main import app
from blyskawica_app.backend.win11_controller import Win11Controller
from blyskawica_app.backend.live_monitor import LiveMonitor
from blyskawica_app.backend.app_learning_agent import AppLearningAgent


class TestWindows11Integration(unittest.IsolatedAsyncioTestCase):
    """Testy jednostkowe i integracyjne dla monitora LIVE, uczenia aplikacji oraz zgód systemowych."""

    def setUp(self):
        self.client = TestClient(app)
        self.controller = Win11Controller()

    def test_win11_controller_active_window(self):
        """Weryfikuje, czy kontroler zwraca poprawny kształt danych o aktywnym oknie."""
        info = self.controller.get_active_window_info()
        self.assertIsInstance(info, dict)
        self.assertIn("title", info)
        self.assertIn("process_name", info)
        self.assertIn("pid", info)
        self.assertIn("process_path", info)
        self.assertIn("is_office_app", info)

    def test_win11_controller_office_detection(self):
        """Weryfikuje, czy kontroler nie rzuca błędów przy detekcji MS Office."""
        installed = self.controller.get_installed_office_apps()
        self.assertIsInstance(installed, dict)
        for app_name in ["Word", "Excel", "PowerPoint", "Outlook", "Teams"]:
            self.assertIn(app_name, installed)
            self.assertIn("installed", installed[app_name])
            self.assertIn("path", installed[app_name])

    def test_live_monitor_prompt_override(self):
        """Weryfikuje wstrzykiwanie promptu kognitywnego z monitora LIVE."""
        monitor = LiveMonitor()
        # Mockuj stan aktywnego okna
        monitor.active_context = {
            "title": "MójDokument.docx - Microsoft Word",
            "process_name": "WINWORD.EXE",
            "pid": 1234,
            "process_path": "C:\\Office\\WINWORD.EXE",
            "is_office_app": True
        }
        prompt = monitor.get_context_prompt_override()
        self.assertIn("Użytkownik ma obecnie otwarte okno o tytule: \"MójDokument.docx - Microsoft Word\"", prompt)
        self.assertIn("WINWORD.EXE", prompt)

    @mock.patch("httpx.AsyncClient.get")
    async def test_app_learning_agent_learn(self, mock_get):
        """Testuje asynchroniczne pobieranie wiedzy o nieznanej aplikacji przez DuckDuckGo."""
        from pathlib import Path

        # Przygotuj fikcyjną odpowiedź HTML
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.text = """
        <div class="result__body">
            <a class="result__snippet" href="http://test.com">Użyj skrótu Ctrl+S aby zapisać oraz Ctrl+P aby wydrukować w aplikacji TestApp.</a>
        </div>
        """
        
        # Używamy AsyncMock do emulacji asynchronicznego pobierania przez httpx
        mock_get_async = mock.AsyncMock(return_value=mock_response)
        mock_get.side_effect = mock_get_async

        # Ścieżka tymczasowa
        temp_db = Path("c:/Projekty/Blyskawica_V8/scratch/temp_manuals_test.json")
        if temp_db.exists():
            try:
                temp_db.unlink()
            except Exception:
                pass

        agent = AppLearningAgent(db_path=temp_db)
        # Podmień _save_db, aby nie pisać na dysk (dla bezpieczeństwa i izolacji)
        agent._save_db = mock.MagicMock()

        app_data = await agent.learn_app("TestApp")
        self.assertTrue(app_data["learned"])
        self.assertEqual(app_data["name"], "TestApp")
        self.assertIn("CTRL+S", app_data["shortcuts"])
        self.assertIn("CTRL+P", app_data["shortcuts"])

        if temp_db.exists():
            try:
                temp_db.unlink()
            except Exception:
                pass

    @mock.patch("blyskawica_app.backend.main.ask_windows_consent")
    @mock.patch("blyskawica_app.backend.main.verify_startup_token")
    def test_execute_system_action_consent_approved(self, mock_verify, mock_consent):
        """Weryfikuje, czy akcja systemowa wykonuje się przy aprobacie użytkownika."""
        mock_consent.return_value = True
        mock_verify.return_value = None

        # Ustaw uprawnienia na Poziom 3
        import blyskawica_app.backend.main as bly_main
        bly_main.permission_level = 3

        # Wyślij żądanie utworzenia katalogu testowego
        temp_folder = "c:/Projekty/Blyskawica_V8/scratch/test_folder_consent"
        response = self.client.post(
            "/api/execute_system_action",
            data={"action": "create_folder", "args": json.dumps({"path": temp_folder})},
            headers={"X-Blyskawica-Token": "test_token"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("został utworzony", response.json()["message"])

        # Posprzątaj
        import shutil
        if os.path.exists(temp_folder):
            shutil.rmtree(temp_folder)

    @mock.patch("blyskawica_app.backend.main.ask_windows_consent")
    @mock.patch("blyskawica_app.backend.main.verify_startup_token")
    def test_execute_system_action_consent_denied(self, mock_verify, mock_consent):
        """Weryfikuje, czy akcja systemowa zostaje zablokowana w przypadku odmowy użytkownika."""
        mock_consent.return_value = False
        mock_verify.return_value = None

        import blyskawica_app.backend.main as bly_main
        bly_main.permission_level = 3

        response = self.client.post(
            "/api/execute_system_action",
            data={"action": "create_folder", "args": json.dumps({"path": "some_path"})},
            headers={"X-Blyskawica-Token": "test_token"}
        )
        self.assertEqual(response.status_code, 403)
        self.assertIn("Operacja anulowana przez użytkownika", response.json()["message"])
