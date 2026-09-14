"""
[Moduł: Bezpieczeństwo i Kontrola Dostępu (security.py)]
Zarządza autoryzacją tokenową sesji, regułami CORS, weryfikacją ścieżek
przed Directory Traversal (is_inside_workspace z is_relative_to),
wykrywaniem chronionych plików rdzenia oraz rate limitingiem zapytań.
"""

from __future__ import annotations

import collections
import hmac
import logging
import os
import secrets
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from fastapi import Header, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

logger = logging.getLogger("BlyskawicaSecurity")

# Inicjalizacja tokenu sesji (ze zmiennej środowiskowej lub bezpieczny losowy)
STARTUP_TOKEN: str = os.environ.get("X_BLY_TOKEN", secrets.token_hex(32))

# Zaostrzone reguły CORS - autoryzowane domeny aplikacji Sparkle / Tauri
ALLOWED_CORS_ORIGINS: List[str] = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "tauri://localhost",
    "http://tauri.localhost",
    "https://tauri.localhost",
]

# Ściśle określone nagłówki HTTP (ochrona przed arbitrary headers)
ALLOWED_CORS_HEADERS: List[str] = [
    "X-Blyskawica-Token",
    "X-Token",
    "X-Internal-Request",
    "Content-Type",
    "Authorization",
    "Accept",
    "Origin",
]

# Chronione pliki i katalogi zawierające tożsamość i silnik
PROTECTED_CORE_PATTERNS: List[str] = [
    "/welcome_v9.py",
    "/blyskawica_start.py",
    "/uruchom_sparkle.bat",
    "/adaptiveneuralnetwork/central_nervous_system/",
    "/adaptiveneuralnetwork/immune_system/",
    "/identity_vault/",
    "/blyskawica_app/backend/main.py",
    "/blyskawica_app/backend/immortality.py",
    "/blyskawica_app/backend/memory/user_identity.json",
]

# Wrażliwe katalogi systemowe Windows oraz Unix / Linux / macOS
RESTRICTED_SYSTEM_DIRECTORIES: List[str] = [
    # Windows
    "c:/windows",
    "c:/program files",
    "c:/program files (x86)",
    "c:/users/default",
    "c:/users/all users",
    # Unix / Linux / macOS
    "/etc",
    "/proc",
    "/sys",
    "/dev",
    "/boot",
    "/root",
    "/usr",
    "/var",
]

RESTRICTED_USER_SUBDIRECTORIES: List[str] = [
    ".ssh",
    ".aws",
    ".gnupg",
    ".config/gcloud",
]


def is_inside_workspace(target_path: Union[str, Path], base_dir: Optional[Union[str, Path]] = None) -> bool:
    """
    Weryfikuje, czy zadana ścieżka znajduje się wewnątrz dozwolonego katalogu roboczego.
    Wykorzystuje Path.resolve() oraz Path.is_relative_to() do odporności na Directory Traversal.
    """
    try:
        if base_dir is None:
            root_env = os.environ.get("SPARKLE_WORKSPACE")
            if root_env:
                resolved_base = Path(root_env).resolve()
            else:
                # Domyślny katalog główny repozytorium
                resolved_base = Path(__file__).resolve().parent.parent.parent
        else:
            resolved_base = Path(base_dir).resolve()

        resolved_target = Path(target_path).resolve()
        return resolved_target.is_relative_to(resolved_base)
    except (ValueError, Exception):
        return False


def is_protected_core_file(filepath: Union[str, Path]) -> bool:
    """Sprawdza, czy ścieżka odnosi się do chronionych plików tożsamości i rdzenia Błyskawicy."""
    try:
        resolved = Path(filepath).resolve()
        path_str = str(resolved).lower().replace("\\", "/")
        return any(pattern in path_str for pattern in PROTECTED_CORE_PATTERNS)
    except Exception:
        return False


def is_restricted_system_path(filepath: Union[str, Path]) -> bool:
    """Sprawdza, czy ścieżka wskazuje na wrażliwe katalogi systemowe Windows, Unix lub klucze użytkownika."""
    try:
        expanded = os.path.expanduser(str(filepath))
        raw_path = expanded.lower().replace("\\", "/")
        resolved_path = str(Path(expanded).resolve()).lower().replace("\\", "/")
        home_path = str(Path.home().resolve()).lower().replace("\\", "/")

        # 1. System directories
        if any(
            candidate.startswith(rdir)
            for candidate in (raw_path, resolved_path)
            for rdir in RESTRICTED_SYSTEM_DIRECTORIES
        ):
            return True

        # 2. Sensitive user dotfiles (.ssh, .aws, etc.)
        for sensitive_sub in RESTRICTED_USER_SUBDIRECTORIES:
            sensitive_full = f"{home_path}/{sensitive_sub}"
            if raw_path.startswith(sensitive_full) or resolved_path.startswith(sensitive_full):
                return True

        return False
    except Exception:
        return True


def verify_startup_token(
    x_token: Optional[Any] = None,
    x_fallback_token: Optional[Any] = None
) -> None:
    """Weryfikuje, czy dostarczony nagłówek odpowiada wygenerowanemu tokenowi sesji (odporny na timing attack)."""
    token_candidate = None
    if isinstance(x_token, str) and x_token:
        token_candidate = x_token
    elif isinstance(x_fallback_token, str) and x_fallback_token:
        token_candidate = x_fallback_token

    if not token_candidate or not hmac.compare_digest(token_candidate, STARTUP_TOKEN):
        raise HTTPException(
            status_code=401,
            detail="Niezautoryzowane zapytanie. Brakujący lub błędny token sesji."
        )


class InMemoryRateLimiter:
    """
    Lekki ogranicznik częstotliwości zapytań (Sliding Window Rate Limiter).
    Działa bez zewnętrznych zależności w pamięci RAM procesu z automatyczną eksmisją (bound memory).
    """

    def __init__(self, max_requests: int = 120, window_seconds: float = 60.0, max_clients: int = 10000) -> None:
        self.max_requests: int = max_requests
        self.window_seconds: float = window_seconds
        self.max_clients: int = max_clients
        self._history: Dict[str, collections.deque] = collections.defaultdict(collections.deque)
        self._last_cleanup: float = time.time()

    def _cleanup_stale_entries(self, now: float) -> None:
        cutoff = now - self.window_seconds
        stale_keys = [k for k, q in self._history.items() if not q or q[-1] < cutoff]
        for k in stale_keys:
            del self._history[k]

        # Jeśli liczba klientów nadal przekracza max_clients, eksmituj najstarsze
        if len(self._history) > self.max_clients:
            excess = len(self._history) - self.max_clients
            for k in list(self._history.keys())[:excess]:
                del self._history[k]

    def is_allowed(self, client_key: str) -> Tuple[bool, int, int]:
        """
        Sprawdza dopuszczalność zapytania.
        Zwraca: (dopuszczone: bool, pozostały_limit: int, czas_do_odblokowania: int)
        """
        now = time.time()

        # Okresowe czyszczenie co window_seconds lub przy dużym rozmiarze
        if now - self._last_cleanup > self.window_seconds or len(self._history) > self.max_clients:
            self._cleanup_stale_entries(now)
            self._last_cleanup = now

        queue = self._history[client_key]

        # Usuń znaczniki czasu starsze niż okno
        cutoff = now - self.window_seconds
        while queue and queue[0] < cutoff:
            queue.popleft()

        if len(queue) >= self.max_requests:
            oldest = queue[0]
            retry_after = max(1, int(self.window_seconds - (now - oldest)))
            return False, 0, retry_after

        queue.append(now)
        remaining = self.max_requests - len(queue)
        return True, remaining, 0

    def reset(self) -> None:
        """Resetuje historię zapytań."""
        self._history.clear()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware FastAPI nakładający limity zapytań na endpointy API."""

    def __init__(self, app: Any, max_requests: int = 120, window_seconds: float = 60.0) -> None:
        super().__init__(app)
        self.limiter = InMemoryRateLimiter(max_requests=max_requests, window_seconds=window_seconds)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Pomijaj sprawdzanie zasobów statycznych, aby nie blokować UI
        path = request.url.path
        if not path.startswith("/api/"):
            return await call_next(request)

        client_host = request.client.host if request.client else "unknown_client"
        allowed, remaining, retry_after = self.limiter.is_allowed(client_host)

        if not allowed:
            logger.warning(f"Rate limit przekroczony dla {client_host} na {path}. Retry-After: {retry_after}s")
            return JSONResponse(
                status_code=429,
                content={
                    "status": "error",
                    "message": "Zbyt wiele zapytań (Rate limit exceeded). Spróbuj ponownie za chwilę.",
                    "retry_after": retry_after
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(self.limiter.max_requests),
                    "X-RateLimit-Remaining": "0"
                }
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.limiter.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response
