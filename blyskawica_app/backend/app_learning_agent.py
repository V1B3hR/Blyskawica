"""
[Moduł: Agent Uczenia Aplikacji (AppLearningAgent)]
Umożliwia Błyskawicy dynamiczne uczenie się obsługi nieznanych aplikacji.
Gdy użytkownik pyta o nową aplikację, agent przeszukuje internet (DuckDuckGo),
wyodrębnia skróty klawiszowe i instrukcje, po czym zapisuje je w lokalnej bazie.
"""

import os
import json
import logging
import urllib.parse
import re
import httpx
from pathlib import Path

logger = logging.getLogger("AppLearningAgent")
MEMORY_DIR = Path("c:/Projekty/Blyskawica_V8/blyskawica_app/memory")

class AppLearningAgent:
    def __init__(self, db_path: Path = MEMORY_DIR / "app_manuals.json"):
        self.db_path = db_path
        self.manuals = {}
        self._load_db()

    def _load_db(self):
        """Wczytuje lokalną bazę podręczników aplikacji."""
        try:
            if not self.db_path.parent.exists():
                self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            if self.db_path.exists():
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    self.manuals = json.load(f)
                logger.info(f"[AppLearningAgent] Wczytano {len(self.manuals)} instrukcji z bazy.")
            else:
                self.manuals = {}
                self._save_db()
        except Exception as e:
            logger.error(f"[AppLearningAgent] Błąd wczytywania bazy manuals: {e}")
            self.manuals = {}

    def _save_db(self):
        """Zapisuje bazę podręczników na dysku."""
        try:
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(self.manuals, f, ensure_ascii=False, indent=4)
            logger.debug("[AppLearningAgent] Baza instrukcji została zapisana.")
        except Exception as e:
            logger.error(f"[AppLearningAgent] Błąd zapisu bazy manuals: {e}")

    async def learn_app(self, app_name: str) -> dict:
        """
        Sprawdza czy aplikacja jest w bazie. Jeśli nie, wyszukuje ją w sieci,
        tworzy zwięzły podręcznik i zapisuje go.
        """
        app_key = app_name.strip().lower()
        if app_key in self.manuals:
            logger.info(f"[AppLearningAgent] Aplikacja '{app_name}' jest już znana.")
            return self.manuals[app_key]

        logger.info(f"[AppLearningAgent] Nieznana aplikacja: '{app_name}'. Rozpoczęto wyszukiwanie wiedzy...")
        
        # Przygotowanie zapytań do DuckDuckGo
        queries = [
            f"Jak używać {app_name} poradnik instrukcja skróty klawiszowe",
            f"{app_name} manual keyboard shortcuts guide"
        ]
        
        all_snippets = []
        
        for q in queries:
            try:
                url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(q)}"
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36'}
                
                async with httpx.AsyncClient(timeout=6.0, follow_redirects=True) as client:
                    res = await client.get(url, headers=headers)
                    if res.status_code == 200:
                        html = res.text
                        # Wyciąganie snippetów i tytułów
                        matches = re.findall(r'<div class="result__body">.*?<a class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL)
                        for snippet in matches[:4]:
                            clean_snippet = re.sub(r'<[^>]+>', '', snippet).strip()
                            clean_snippet = urllib.parse.unquote(clean_snippet)
                            if clean_snippet not in all_snippets:
                                all_snippets.append(clean_snippet)
            except Exception as e:
                logger.warning(f"[AppLearningAgent] Błąd podczas wyszukiwania dla zapytania '{q}': {e}")

        # Jeśli nie znaleziono żadnych informacji
        if not all_snippets:
            return {
                "name": app_name,
                "learned": False,
                "summary": "Nie udało się pobrać szczegółowych informacji z sieci. Aplikacja wymaga manualnego zbadania.",
                "shortcuts": []
            }

        # Budowanie podręcznika na podstawie snippetów
        summary_text = "\n".join(all_snippets[:5])
        
        # Ekstrakcja podstawowych skrótów klawiszowych (prosta heurystyka)
        shortcuts = []
        found_keys = re.findall(r'(ctrl\s*\+\s*[a-z0-9]|alt\s*\+\s*[a-z0-9]|shift\s*\+\s*[a-z0-9]|f[1-9][0-2]?)', summary_text.lower())
        for key in found_keys:
            key_clean = key.strip().upper()
            if key_clean not in shortcuts:
                shortcuts.append(key_clean)

        app_data = {
            "name": app_name,
            "learned": True,
            "summary": f"Podręcznik stworzony na podstawie wiedzy sieciowej:\n{summary_text[:800]}...",
            "shortcuts": shortcuts[:8],  # limit 8 skrótów
            "source": "DuckDuckGo Web Search"
        }

        # Zapisz do pamięci
        self.manuals[app_key] = app_data
        self._save_db()
        
        logger.info(f"[AppLearningAgent] Pomyślnie nauczono się obsługi: {app_name}. Znalezione skróty: {shortcuts[:8]}")
        return app_data

    def get_app_context(self, app_name: str) -> str:
        """Zwraca sformatowany podręcznik dla silnika kognitywnego."""
        app_key = app_name.strip().lower()
        if app_key not in self.manuals:
            return ""
            
        data = self.manuals[app_key]
        shortcuts_str = ", ".join(data["shortcuts"]) if data["shortcuts"] else "brak wykrytych"
        return (
            f"\n[Podręcznik Kognitywny Aplikacji - {data['name']}]:\n"
            f"Opis/Użycie: {data['summary']}\n"
            f"Kluczowe skróty klawiszowe: {shortcuts_str}\n"
        )
