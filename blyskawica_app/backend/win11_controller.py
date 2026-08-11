"""
[Moduł: Kontroler Windows 11 (Win11Controller)]
Zapewnia lekki, niskopoziomowy dostęp do informacji o systemie Windows 11.
Pobiera dane o aktywnym oknie, uruchomionych procesach oraz dostępności
aplikacji Microsoft 365/Office bez nadmiernego obciążania procesora.
"""

import logging
import os
import sys
import winreg

import psutil

logger = logging.getLogger("Win11Controller")

# Ctypes importy dla Windows
if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    psapi = ctypes.windll.psapi
else:
    user32 = None
    kernel32 = None
    psapi = None


class Win11Controller:
    """
    Udostępnia metody do badania stanu systemu operacyjnego Windows 11.
    Zaprojektowany tak, aby zminimalizować narzut CPU/GPU.
    """

    def __init__(self):
        logger.info("[Win11Controller] Zainicjalizowano lekki kontroler systemu.")

    def get_active_window_info(self) -> dict:
        """
        Zwraca informacje o oknie, na którym obecnie skupia się użytkownik.
        Wymaga Win32 API. Zwraca bezpieczny słownik na innych platformach.
        """
        result = {
            "title": "Brak aktywnego okna",
            "process_name": "unknown",
            "pid": 0,
            "process_path": "",
            "is_office_app": False
        }

        if sys.platform != "win32" or user32 is None:
            return result

        try:
            # 1. Pobierz uchwyt aktywnego okna
            hwnd = user32.GetForegroundWindow()
            if not hwnd:
                return result

            # 2. Pobierz tytuł okna
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buffer = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buffer, length + 1)
                result["title"] = buffer.value
            else:
                result["title"] = "Brak tytułu okna"

            # 3. Pobierz PID procesu
            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            result["pid"] = pid.value

            # 4. Pobierz nazwę i ścieżkę procesu
            if pid.value > 0:
                # PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
                process_handle = kernel32.OpenProcess(0x1000, False, pid.value)
                if process_handle:
                    try:
                        # Pobranie ścieżki
                        path_buffer = ctypes.create_unicode_buffer(1024)
                        size = wintypes.DWORD(1024)
                        # QueryFullProcessImageNameW jest lepsze niż GetModuleFileNameExW (mniej problemów z uprawnieniami)
                        if kernel32.QueryFullProcessImageNameW(process_handle, 0, path_buffer, ctypes.byref(size)):
                            result["process_path"] = path_buffer.value
                            result["process_name"] = os.path.basename(path_buffer.value)
                    finally:
                        kernel32.CloseHandle(process_handle)

                # Fallback, jeśli win32 API nie pobierze nazwy, użyj psutil
                if result["process_name"] == "unknown":
                    try:
                        proc = psutil.Process(pid.value)
                        result["process_name"] = proc.name()
                        result["process_path"] = proc.exe()
                    except Exception:
                        pass

            # 5. Oznacz czy to jest aplikacja biurowa MS Office / M365
            proc_lower = result["process_name"].lower()
            office_executables = ["winword.exe", "excel.exe", "powerpnt.exe", "outlook.exe", "onenote.exe", "msaccess.exe", "teams.exe"]
            if any(o_exe in proc_lower for o_exe in office_executables):
                result["is_office_app"] = True

        except Exception as e:
            logger.error(f"Błąd podczas pobierania informacji o aktywnym oknie: {e}")

        return result

    def get_installed_office_apps(self) -> dict:
        """
        Sprawdza rejestr Windows pod kątem obecności zainstalowanych aplikacji pakietu Office/Microsoft 365.
        Zwraca listę znalezionych aplikacji wraz ze ścieżkami.
        """
        apps = {
            "Word": {"installed": False, "path": ""},
            "Excel": {"installed": False, "path": ""},
            "PowerPoint": {"installed": False, "path": ""},
            "Outlook": {"installed": False, "path": ""},
            "Teams": {"installed": False, "path": ""}
        }

        if sys.platform != "win32":
            return apps

        office_registry_mappings = {
            "Word": (r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\Winword.exe", ""),
            "Excel": (r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\excel.exe", ""),
            "PowerPoint": (r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\powerpnt.exe", ""),
            "Outlook": (r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\outlook.exe", ""),
            "Teams": (r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\Teams.exe", "")
        }

        for app_name, (reg_path, value_name) in office_registry_mappings.items():
            # Sprawdź w HKEY_LOCAL_MACHINE i HKEY_CURRENT_USER
            for root_key in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
                try:
                    with winreg.OpenKey(root_key, reg_path) as key:
                        val, _ = winreg.QueryValueEx(key, value_name)
                        if val:
                            apps[app_name]["installed"] = True
                            apps[app_name]["path"] = str(val)
                            break
                except FileNotFoundError:
                    continue
                except Exception as e:
                    logger.debug(f"Błąd odczytu rejestru dla {app_name}: {e}")

            # Fallback dla powszechnych ścieżek
            if not apps[app_name]["installed"]:
                common_paths = []
                if app_name == "Word":
                    common_paths.append(r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE")
                elif app_name == "Excel":
                    common_paths.append(r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE")
                elif app_name == "PowerPoint":
                    common_paths.append(r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE")
                elif app_name == "Outlook":
                    common_paths.append(r"C:\Program Files\Microsoft Office\root\Office16\OUTLOOK.EXE")

                for cp in common_paths:
                    if os.path.exists(cp):
                        apps[app_name]["installed"] = True
                        apps[app_name]["path"] = cp
                        break

        return apps

    def get_running_office_apps(self) -> list:
        """
        Zwraca listę aktualnie działających aplikacji biurowych Microsoft 365.
        """
        running_apps = []
        office_executables = {
            "winword.exe": "Word",
            "excel.exe": "Excel",
            "powerpnt.exe": "PowerPoint",
            "outlook.exe": "Outlook",
            "teams.exe": "Teams"
        }

        for proc in psutil.process_iter(['name']):
            try:
                proc_name = proc.info['name']
                if proc_name and proc_name.lower() in office_executables:
                    app_name = office_executables[proc_name.lower()]
                    if app_name not in running_apps:
                        running_apps.append(app_name)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        return running_apps


if __name__ == "__main__":
    controller = Win11Controller()
    print("Aktywne okno:", controller.get_active_window_info())
    print("Zainstalowane aplikacje Office:", controller.get_installed_office_apps())
    print("Uruchomione aplikacje Office:", controller.get_running_office_apps())
