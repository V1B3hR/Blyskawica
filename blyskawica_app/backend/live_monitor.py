"""
[Moduł: Monitor LIVE (LiveMonitor)]
Odpowiada za asynchroniczne śledzenie aktywności użytkownika w Windows 11.
Działa w tle jako pętla asyncio, aktualizując kontekst bez narzutu na CPU.
"""

import asyncio
import logging
from datetime import datetime

from blyskawica_app.backend.win11_controller import Win11Controller

logger = logging.getLogger("LiveMonitor")

class LiveMonitor:
    def __init__(self, check_interval: float = 2.0):
        self.controller = Win11Controller()
        self.check_interval = check_interval
        self.active_context = {
            "title": "Brak aktywnego okna",
            "process_name": "unknown",
            "pid": 0,
            "process_path": "",
            "is_office_app": False,
            "last_updated": datetime.now().isoformat()
        }
        self._running = False
        self._task = None

    async def start(self):
        """Uruchamia monitorowanie w tle jako asynchroniczne zadanie."""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info("[LiveMonitor] Monitor aktywności uruchomiony w tle.")

    async def stop(self):
        """Zatrzymuje monitorowanie."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("[LiveMonitor] Monitor aktywności zatrzymany.")

    async def _run_loop(self):
        """Główna lekka pętla monitorująca."""
        while self._running:
            try:
                info = self.controller.get_active_window_info()

                # Zapisz tylko jeśli nastąpiła zmiana okna lub procesu (optymalizacja)
                if (info["title"] != self.active_context["title"] or
                        info["pid"] != self.active_context["pid"]):

                    self.active_context = info
                    self.active_context["last_updated"] = datetime.now().isoformat()

                    logger.debug(
                        f"[LiveMonitor] Zmiana okna: {info['title']} ({info['process_name']})"
                    )
            except Exception as e:
                logger.error(f"[LiveMonitor] Błąd w pętli monitora: {e}")

            await asyncio.sleep(self.check_interval)

    def get_context_prompt_override(self) -> str:
        """
        Zwraca systemowy wstrzykiwany prompt opisujący obecne działanie użytkownika.
        Używane jako dynamiczny kontekst dla LLM.
        """
        title = self.active_context.get("title", "Nieznane okno")
        proc = self.active_context.get("process_name", "nieznany proces")

        if proc == "unknown" or title == "Brak aktywnego okna":
            return ""

        return (
            f"\n[Kontekst Windows 11 LIVE - {datetime.now().strftime('%H:%M:%S')}]: "
            f"Użytkownik ma obecnie otwarte okno o tytule: \"{title}\" (aplikacja: {proc}). "
            f"Możesz odwołać się do tego okna, jeśli użytkownik prosi o instrukcję, "
            f"pomoc lub wyjaśnienie związane z tym programem."
        )


# Globalna instancja monitora
live_monitor_instance = LiveMonitor(check_interval=2.0)
