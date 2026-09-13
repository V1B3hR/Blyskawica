"""
Testy bezpieczeństwa: weryfikacja polityki CORS i zaostrzonych nagłówków HTTP.
"""

import unittest
from fastapi.testclient import TestClient

from blyskawica_app.backend.main import app
from blyskawica_app.backend.security import ALLOWED_CORS_ORIGINS, ALLOWED_CORS_HEADERS


class TestCORSAndHeadersSecurity(unittest.TestCase):
    """Weryfikacja zaostrzonej konfiguracji CORS i nagłówków."""

    def setUp(self):
        self.client = TestClient(app)

    def test_allowed_cors_origins(self):
        """Autoryzowane domeny aplikacji Sparkle i Tauri powinny być dopuszczane."""
        for origin in ALLOWED_CORS_ORIGINS:
            with self.subTest(origin=origin):
                res = self.client.options(
                    "/api/permission_level",
                    headers={
                        "Origin": origin,
                        "Access-Control-Request-Method": "GET"
                    }
                )
                self.assertEqual(
                    res.headers.get("access-control-allow-origin"),
                    origin,
                    f"Origin {origin} powinien być zaakceptowany w nagłówku odpowiedzi"
                )

    def test_blocked_unauthorized_cors_origins(self):
        """Nieznane i złośliwe domeny nie mogą otrzymać nagłówka Access-Control-Allow-Origin."""
        unauthorized_origins = [
            "http://malicious.org",
            "https://attacker-site.com",
            "http://evil.domain.xyz",
            "http://localhost:3000",  # Unapproved port
        ]
        for bad_origin in unauthorized_origins:
            with self.subTest(origin=bad_origin):
                res = self.client.options(
                    "/api/permission_level",
                    headers={
                        "Origin": bad_origin,
                        "Access-Control-Request-Method": "GET"
                    }
                )
                self.assertNotEqual(
                    res.headers.get("access-control-allow-origin"),
                    bad_origin,
                    f"Origin {bad_origin} NIE może otrzymać nagłówka allow-origin!"
                )

    def test_allowed_headers_in_preflight(self):
        """Kluczowe nagłówki sesyjne muszą być dozwolone w CORS preflight."""
        res = self.client.options(
            "/api/ide/vibe_code",
            headers={
                "Origin": "http://localhost:8000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type, x-blyskawica-token"
            }
        )
        allow_headers = res.headers.get("access-control-allow-headers", "").lower()
        self.assertIn("content-type", allow_headers)
        self.assertIn("x-blyskawica-token", allow_headers)


if __name__ == "__main__":
    unittest.main()
