"""
Testy bezpieczeństwa: weryfikacja odporności na Path Traversal i ochrona katalogów systemowych.
"""

import os
import unittest
from pathlib import Path

from blyskawica_app.backend.security import (
    is_inside_workspace,
    is_protected_core_file,
    is_restricted_system_path,
)


class TestPathTraversalSecurity(unittest.TestCase):
    """Testy walidacji ścieżek, ochrony przed wyjściem poza workspace i katalogów systemowych."""

    def setUp(self):
        self.workspace = Path(__file__).resolve().parent.parent.parent
        self.dummy_safe_file = self.workspace / "blyskawica_app" / "test_file.txt"

    def test_safe_path_inside_workspace(self):
        """Prawidłowa ścieżka wewnątrz workspace powinna być zaakceptowana."""
        self.assertTrue(is_inside_workspace(self.dummy_safe_file, self.workspace))
        self.assertTrue(is_inside_workspace(self.workspace / "README.md", self.workspace))
        self.assertTrue(is_inside_workspace(self.workspace, self.workspace))

    def test_directory_traversal_dot_dot(self):
        """Próby wyjścia przez ../ lub ..\\ powinny być natychmiast wykryte i zablokowane."""
        traversal_attempts = [
            self.workspace / ".." / "outside.txt",
            self.workspace / ".." / ".." / "windows" / "system32",
            self.workspace / "blyskawica_app" / ".." / ".." / "secret.key",
            "../secret.env",
            "../../../../boot.ini",
            "..\\..\\windows\\system32\\cmd.exe",
        ]
        for bad_path in traversal_attempts:
            with self.subTest(bad_path=str(bad_path)):
                # When resolved relative to workspace, these escape it
                self.assertFalse(
                    is_inside_workspace(self.workspace / bad_path if isinstance(bad_path, str) else bad_path, self.workspace),
                    f"Ścieżka {bad_path} nie powinna być dozwolona w workspace!"
                )

    def test_restricted_system_paths(self):
        """Ścieżki do kluczowych katalogów systemowych Windows muszą być zidentyfikowane jako restricted."""
        system_paths = [
            "C:/Windows",
            "c:/windows/system32/cmd.exe",
            "C:\\Windows\\System32\\drivers\\etc\\hosts",
            "c:/program files/sensitive_app",
            "C:/Program Files (x86)/common files",
            "C:/Users/Default/NTUSER.DAT",
            "c:/users/all users/secret",
        ]
        for sys_path in system_paths:
            with self.subTest(sys_path=sys_path):
                self.assertTrue(
                    is_restricted_system_path(sys_path),
                    f"Katalog systemowy {sys_path} powinien być restricted!"
                )

    def test_unrestricted_safe_paths(self):
        """Bezpieczne pliki w repozytorium nie mogą być fałszywie oznaczane jako restricted."""
        safe_paths = [
            self.workspace / "blyskawica_app" / "backend" / "main.py",
            self.workspace / "checkpoints" / "model.pt",
            self.workspace / "docs" / "README.md",
        ]
        for safe in safe_paths:
            with self.subTest(safe=str(safe)):
                # Normal workspace path outside C:\Windows should not be restricted
                raw = str(safe).lower().replace("\\", "/")
                if not raw.startswith("c:/windows") and not raw.startswith("c:/program files"):
                    self.assertFalse(is_restricted_system_path(safe))

    def test_protected_core_files(self):
        """Kluczowe pliki tożsamości i silnika Błyskawicy muszą być chronione przed nadpisaniem."""
        core_files = [
            self.workspace / "welcome_v9.py",
            self.workspace / "blyskawica_start.py",
            self.workspace / "adaptiveneuralnetwork" / "central_nervous_system" / "alive_node.py",
            self.workspace / "blyskawica_app" / "backend" / "main.py",
            self.workspace / "blyskawica_app" / "backend" / "immortality.py",
        ]
        for core in core_files:
            with self.subTest(core=str(core)):
                self.assertTrue(is_protected_core_file(core), f"{core} powinien być chroniony!")


if __name__ == "__main__":
    unittest.main()
