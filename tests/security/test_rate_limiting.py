"""
Testy bezpieczeństwa: weryfikacja rate limitingu (InMemoryRateLimiter i RateLimitMiddleware).
"""

import time
import unittest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from blyskawica_app.backend.security import InMemoryRateLimiter, RateLimitMiddleware


class TestRateLimitingSecurity(unittest.TestCase):
    """Testy algorytmu i middleware ograniczającego częstotliwość zapytań (Rate Limiting)."""

    def test_in_memory_rate_limiter_allows_under_limit(self):
        """Zapytania poniżej limitu powinny być akceptowane."""
        limiter = InMemoryRateLimiter(max_requests=5, window_seconds=10.0)
        client_key = "127.0.0.1"

        for i in range(5):
            allowed, remaining, retry_after = limiter.is_allowed(client_key)
            self.assertTrue(allowed, f"Zapytanie #{i+1} powinno być dozwolone")
            self.assertEqual(remaining, 5 - (i + 1))
            self.assertEqual(retry_after, 0)

    def test_in_memory_rate_limiter_blocks_over_limit(self):
        """Zapytanie przekraczające limit powinno zostać odrzucone z czasem retry_after."""
        limiter = InMemoryRateLimiter(max_requests=3, window_seconds=5.0)
        client_key = "192.168.1.50"

        for _ in range(3):
            limiter.is_allowed(client_key)

        # 4 zapytanie powinno zostać zablokowane
        allowed, remaining, retry_after = limiter.is_allowed(client_key)
        self.assertFalse(allowed)
        self.assertEqual(remaining, 0)
        self.assertGreater(retry_after, 0)

    def test_rate_limiter_isolated_by_client(self):
        """Różni klienci powinni mieć niezależne pule zapytań."""
        limiter = InMemoryRateLimiter(max_requests=2, window_seconds=10.0)
        client_a = "10.0.0.1"
        client_b = "10.0.0.2"

        limiter.is_allowed(client_a)
        limiter.is_allowed(client_a)
        blocked_a, _, _ = limiter.is_allowed(client_a)
        self.assertFalse(blocked_a)

        # Klient B nie powinien być zablokowany
        allowed_b, remaining_b, _ = limiter.is_allowed(client_b)
        self.assertTrue(allowed_b)
        self.assertEqual(remaining_b, 1)

    def test_rate_limit_middleware_in_fastapi(self):
        """Test działania middleware na instancji testowej FastAPI."""
        test_app = FastAPI()
        test_app.add_middleware(RateLimitMiddleware, max_requests=3, window_seconds=5.0)

        @test_app.get("/api/test_endpoint")
        def sample_endpoint():
            return {"status": "ok"}

        client = TestClient(test_app)

        # 3 dozwolone zapytania
        for i in range(3):
            res = client.get("/api/test_endpoint")
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.headers.get("X-RateLimit-Limit"), "3")
            self.assertIn("X-RateLimit-Remaining", res.headers)

        # 4 zapytanie -> HTTP 429 Too Many Requests
        res_blocked = client.get("/api/test_endpoint")
        self.assertEqual(res_blocked.status_code, 429)
        self.assertIn("Retry-After", res_blocked.headers)
        data = res_blocked.json()
        self.assertEqual(data["status"], "error")
        self.assertIn("Rate limit", data["message"])


if __name__ == "__main__":
    unittest.main()
