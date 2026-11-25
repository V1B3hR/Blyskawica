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
from typing import Any

from fastapi import HTTPException
from fastapi.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

logger = logging.getLogger("BlyskawicaSecurity")

# Inicjalizacja tokenu sesji (ze zmiennej środowiskowej lub bezpieczny losowy)
STARTUP_TOKEN: str = os.environ.get("X_BLY_TOKEN", secrets.token_hex(32))

# Zaostrzone reguły CORS - autoryzowane domeny aplikacji Sparkle / Tauri
ALLOWED_CORS_ORIGINS: list[str] = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "tauri://localhost",
    "http://tauri.localhost",
    "https://tauri.localhost",
]

# Ściśle określone nagłówki HTTP (ochrona przed arbitrary headers)
ALLOWED_CORS_HEADERS: list[str] = [
    "X-Blyskawica-Token",
    "X-Token",
    "X-Internal-Request",
    "Content-Type",
    "Authorization",
    "Accept",
    "Origin",
]

# Chronione pliki i katalogi zawierające tożsamość i silnik
PROTECTED_CORE_PATTERNS: list[str] = [
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
RESTRICTED_SYSTEM_DIRECTORIES: list[str] = [
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

RESTRICTED_USER_SUBDIRECTORIES: list[str] = [
    ".ssh",
    ".aws",
    ".gnupg",
    ".config/gcloud",
]


def is_inside_workspace(target_path: str | Path, base_dir: str | Path | None = None) -> bool:
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

        target_str = str(target_path).replace("\\", "/")
        if not Path(target_str).is_absolute():
            resolved_target = (resolved_base / target_str).resolve()
        else:
            resolved_target = Path(target_str).resolve()
        return resolved_target.is_relative_to(resolved_base)
    except (ValueError, Exception):
        return False


def is_protected_core_file(filepath: str | Path) -> bool:
    """Sprawdza, czy ścieżka odnosi się do chronionych plików tożsamości i rdzenia Błyskawicy."""
    try:
        resolved = Path(filepath).resolve()
        path_str = str(resolved).lower().replace("\\", "/")
        return any(pattern in path_str for pattern in PROTECTED_CORE_PATTERNS)
    except Exception:
        return False


def is_restricted_system_path(filepath: str | Path) -> bool:
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
    x_token: Any | None = None,
    x_fallback_token: Any | None = None
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
        self._history: dict[str, collections.deque] = collections.defaultdict(collections.deque)
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

    def is_allowed(self, client_key: str) -> tuple[bool, int, int]:
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


class RateLimitMiddleware:
    """ASGI middleware nakładający limity zapytań na endpointy API.

    Nie dziedziczy po ``BaseHTTPMiddleware``. Ta warstwa Starlette tworzy
    dodatkowy kanał zadań, który w bieżącym zestawie FastAPI/Starlette może
    zablokować synchronicznego ``TestClient``. Natywny middleware ASGI nie ma
    tego ograniczenia i zachowuje streaming odpowiedzi aplikacji.
    """

    def __init__(self, app: ASGIApp, max_requests: int = 120, window_seconds: float = 60.0) -> None:
        self.app = app
        self.limiter = InMemoryRateLimiter(max_requests=max_requests, window_seconds=window_seconds)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Pomijaj sprawdzanie zasobów statycznych, aby nie blokować UI
        path = scope["path"]
        if not path.startswith("/api/"):
            await self.app(scope, receive, send)
            return

        client = scope.get("client")
        client_host = client[0] if client else "unknown_client"
        allowed, remaining, retry_after = self.limiter.is_allowed(client_host)

        if not allowed:
            logger.warning(f"Rate limit przekroczony dla {client_host} na {path}. Retry-After: {retry_after}s")
            response = JSONResponse(
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
            await response(scope, receive, send)
            return

        async def send_with_rate_limit_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                message["headers"] = [
                    (key, value)
                    for key, value in message.get("headers", [])
                    if key.lower() not in {b"x-ratelimit-limit", b"x-ratelimit-remaining"}
                ]
                message["headers"].extend(
                    [
                        (b"x-ratelimit-limit", str(self.limiter.max_requests).encode("ascii")),
                        (b"x-ratelimit-remaining", str(remaining).encode("ascii")),
                    ]
                )
            await send(message)

        await self.app(scope, receive, send_with_rate_limit_headers)


class UploadPayloadGuardMiddleware:
    """Ochrona przed wyczerpaniem dysku i pamięci przy nieautoryzowanym lub zbyt dużym uploadzie.

    Weryfikuje nagłówek Content-Length oraz zlicza odebrane bajty w strumieniu ASGI
    przed rozpoczęciem parsowania multipart/form-data przez FastAPI/Starlette.
    Dla endpointu /api/upload/ weryfikuje również wczesny token autoryzacyjny
    X-Blyskawica-Token w nagłówkach HTTP przed konsumpcją ciała zapytania.
    """

    def __init__(self, app: ASGIApp, max_upload_bytes: int = 25 * 1024 * 1024) -> None:
        self.app = app
        self.max_upload_bytes = max_upload_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        if path.startswith("/api/upload/"):
            headers = dict(scope.get("headers", []))
            auth_header = headers.get(b"x-blyskawica-token") or headers.get(b"x-token")
            token_val = auth_header.decode("utf-8", errors="replace") if auth_header else None

            if not token_val or not STARTUP_TOKEN or not hmac.compare_digest(token_val, STARTUP_TOKEN):
                response = JSONResponse(
                    status_code=401,
                    content={"status": "error", "message": "Brak lub nieprawidłowy token sesyjny (odmowa przed przyjęciem danych)."},
                )
                await response(scope, receive, send)
                return

            content_length_bytes = headers.get(b"content-length")
            if content_length_bytes:
                try:
                    content_length = int(content_length_bytes.decode("ascii"))
                    if content_length > self.max_upload_bytes:
                        response = JSONResponse(
                            status_code=413,
                            content={"status": "error", "message": "Plik przekracza limit 25 MiB."},
                        )
                        await response(scope, receive, send)
                        return
                except ValueError:
                    pass

            received_bytes = 0

            async def bounded_receive() -> Message:
                nonlocal received_bytes
                message = await receive()
                if message["type"] == "http.request":
                    body = message.get("body", b"")
                    received_bytes += len(body)
                    if received_bytes > self.max_upload_bytes:
                        raise HTTPException(status_code=413, detail="Plik przekracza limit 25 MiB.")
                return message

            try:
                await self.app(scope, bounded_receive, send)
            except HTTPException as e:
                response = JSONResponse(status_code=e.status_code, content={"status": "error", "message": e.detail})
                await response(scope, receive, send)
            return

        await self.app(scope, receive, send)

