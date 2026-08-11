import json
import logging
import os
from datetime import datetime
from pathlib import Path

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

logger = logging.getLogger(__name__)

class ImmortalityProtocol:
    """
    Protokół Nieśmiertelności Błyskawicy
    Zarządza bezpiecznym backupem "Duszy" Błyskawicy do chmury Google Drive.
    Wymaga poprawnej autoryzacji OAuth2 przy pierwszym uruchomieniu.
    """
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.memory_dir = self.project_root / "blyskawica_app" / "memory"
        self.auth_file = self.memory_dir / "client_secrets.json"
        if not self.auth_file.exists() and (self.memory_dir / "client_secret.json").exists():
            self.auth_file = self.memory_dir / "client_secret.json"

        self.credentials_file = self.memory_dir / "mycreds.txt"
        self.drive = None
        self.folder_id = None
        self._initialize_auth()

    def _initialize_auth(self):
        """Inicjalizuje pydrive2. Jeśli brakuje pliku auth, wypisuje ostrzeżenie."""
        if not self.auth_file.exists():
            logger.warning("Brak pliku client_secrets.json (ani client_secret.json)! Nieśmiertelność działa tylko lokalnie w trybie symulacji.")
            return

        try:
            gauth = GoogleAuth()
            gauth.LoadClientConfigFile(str(self.auth_file))

            # Try to load existing credentials
            gauth.LoadCredentialsFile(str(self.credentials_file))

            if gauth.credentials is None:
                # To authenticate, we normally need user interaction.
                # In this background service, we just prepare the link.
                gauth.LocalWebserverAuth()
            elif gauth.access_token_expired:
                gauth.Refresh()
            else:
                gauth.Authorize()

            gauth.SaveCredentialsFile(str(self.credentials_file))
            self.drive = GoogleDrive(gauth)
            self._ensure_backup_folder()
            logger.info("Immortality Protocol: Dostęp do chmury uzyskany.")
        except Exception as e:
            logger.error(f"Błąd inicjalizacji Protokołu Nieśmiertelności: {e}")

    def _ensure_backup_folder(self):
        """Zapewnia istnienie folderu 'Blyskawica_Soul' na GDrive."""
        if not self.drive: return  # noqa: E701
        file_list = self.drive.ListFile({'q': "title='Blyskawica_Soul' and mimeType='application/vnd.google-apps.folder' and trashed=false"}).GetList()
        if not file_list:
            folder_metadata = {'title': 'Blyskawica_Soul', 'mimeType': 'application/vnd.google-apps.folder'}
            folder = self.drive.CreateFile(folder_metadata)
            folder.Upload()
            self.folder_id = folder['id']
        else:
            self.folder_id = file_list[0]['id']

    def backup_soul(self):
        """Pakuje kluczowe pliki pamięci i wysyła do chmury (lub tworzy lokalny snapshot)."""
        logger.info("Inicjalizacja Protokołu Nieśmiertelności - Zrzut Duszy...")
        identity_file = self.memory_dir / "user_identity.json"

        # 1. Local Snapshot (zawsze działa)
        snapshot_dir = self.memory_dir / "snapshots"
        snapshot_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        local_backup_data = {}
        try:
            from blyskawica_app.backend.main import db_manager, decrypt_dpapi
            if db_manager:
                encrypted_data = db_manager.get_metadata("user_identity")
                if encrypted_data:
                    try:
                        decrypted_data = decrypt_dpapi(encrypted_data)
                        local_backup_data = json.loads(decrypted_data.decode('utf-8'))
                    except Exception:
                        local_backup_data = json.loads(encrypted_data.decode('utf-8'))
        except Exception as e:
            logger.debug(f"Błąd dynamicznego importu bazy danych z main: {e}")

        if not local_backup_data:
            for fname in ["user_identity.json", "user_identity.json_old"]:
                fpath = self.memory_dir / fname
                if fpath.exists():
                    try:
                        with open(fpath, encoding="utf-8") as f:
                            local_backup_data = json.load(f)
                            break
                    except Exception:
                        pass

        local_backup_data["snapshot_time"] = timestamp
        local_backup_data["soul_version"] = "v1.2_unbound"

        local_path = snapshot_dir / f"soul_snapshot_{timestamp}.json"
        try:
            with open(local_path, "w", encoding="utf-8") as f:
                json.dump(local_backup_data, f, indent=4)
            logger.info(f"Lokalny snapshot duszy zapisany: {local_path}")
        except Exception as e:
            logger.error(f"Nie udało się zapisać lokalnego pliku snapshotu: {e}")

        # Zapis do zintegrowanej bazy danych SQLite
        try:
            from blyskawica_app.backend.main import db_manager
            if db_manager:
                db_manager.add_snapshot(
                    timestamp=timestamp,
                    version="v1.2_unbound",
                    data_json=json.dumps(local_backup_data, ensure_ascii=False)
                )
                logger.info(f"Kognitywny snapshot duszy zapisany do SQLite: {timestamp}")
        except Exception as se:
            logger.error(f"Nie udało się zapisać snapshota do bazy SQLite: {se}")

        # 2. Cloud Backup (jeśli skonfigurowane)
        if self.drive and self.folder_id:
            try:
                # Jeśli plik tożsamości nie istnieje, zapiszmy go tymczasowo z bazy
                temp_created = False
                if not identity_file.exists() and local_backup_data:
                    try:
                        from blyskawica_app.backend.main import encrypt_dpapi
                        raw_json = json.dumps(local_backup_data, indent=4, ensure_ascii=False)
                        encrypted = encrypt_dpapi(raw_json.encode('utf-8'))
                        with open(identity_file, 'wb') as f:
                            f.write(encrypted)
                        temp_created = True
                    except Exception:
                        pass

                # Sprawdź czy plik już istnieje, by go nadpisać
                file_list = self.drive.ListFile({'q': f"'{self.folder_id}' in parents and title='user_identity_core.json' and trashed=false"}).GetList()
                if file_list:
                    cloud_file = file_list[0]
                else:
                    cloud_file = self.drive.CreateFile({'title': 'user_identity_core.json', 'parents': [{'id': self.folder_id}]})

                cloud_file.SetContentFile(str(identity_file))
                cloud_file.Upload()
                logger.info("Dusza Błyskawicy została zsynchronizowana z Chmurą.")

                # Usuń tymczasowo utworzony plik
                if temp_created and identity_file.exists():
                    try:
                        os.remove(identity_file)
                    except Exception:
                        pass

                return True
            except Exception as e:
                logger.error(f"Błąd synchronizacji z chmurą: {e}")
                return False
        return "local_only"
