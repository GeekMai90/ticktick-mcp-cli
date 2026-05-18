from __future__ import annotations

from dataclasses import asdict, dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Event
from typing import Any, Callable
from urllib.parse import parse_qs, urlparse

from ticktask.core.errors import AuthError


@dataclass
class LocalCallbackResult:
    callback_url: str
    code: str
    state: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class _SingleUseHTTPServer(HTTPServer):
    result: LocalCallbackResult | None = None
    error: Exception | None = None


def wait_for_oauth_callback(
    redirect_uri: str,
    timeout_seconds: int = 120,
    success_message: str = "Ticktask OAuth login received. You can close this tab.",
    before_wait: Callable[[], None] | None = None,
) -> LocalCallbackResult:
    """Wait for one OAuth callback request on the configured localhost redirect URI."""
    parsed = urlparse(redirect_uri)
    if parsed.scheme != "http":
        raise AuthError("Local OAuth callback server requires an http redirect URI.")
    host = parsed.hostname or "localhost"
    if host not in {"localhost", "127.0.0.1"}:
        raise AuthError(
            "Local OAuth callback server only supports localhost redirect URIs.",
            hint="Use --no-browser and --callback-url for non-local redirect URIs.",
        )
    if not parsed.port:
        raise AuthError(
            "Local OAuth callback server requires a redirect URI with an explicit port.",
            hint="Configure auth with a redirect URI like http://localhost:8080/callback.",
        )
    expected_path = parsed.path or "/"
    done = Event()

    class CallbackHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802 - stdlib handler API
            request_url = f"http://{host}:{parsed.port}{self.path}"
            request = urlparse(self.path)
            if request.path != expected_path:
                self._respond(404, "Not Found")
                return
            query = parse_qs(request.query)
            error = _first(query, "error")
            code = _first(query, "code")
            state = _first(query, "state")
            if error:
                self.server.error = AuthError(f"OAuth callback returned error: {error}")  # type: ignore[attr-defined]
                self._respond(400, "OAuth callback returned an error. You can close this tab.")
                done.set()
                return
            if not code:
                self.server.error = AuthError("OAuth callback did not include a code.")  # type: ignore[attr-defined]
                self._respond(400, "OAuth callback was missing a code. You can close this tab.")
                done.set()
                return
            self.server.result = LocalCallbackResult(  # type: ignore[attr-defined]
                callback_url=request_url,
                code=code,
                state=state,
            )
            self._respond(200, success_message)
            done.set()

        def log_message(self, format: str, *args: Any) -> None:  # noqa: A002 - stdlib signature
            return

        def _respond(self, status: int, message: str) -> None:
            body = f"<html><body><p>{message}</p></body></html>".encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    server = _SingleUseHTTPServer((host, parsed.port), CallbackHandler)
    server.timeout = 0.2
    if before_wait:
        before_wait()
    try:
        deadline = max(1, int(timeout_seconds)) / server.timeout
        attempts = 0
        while not done.is_set() and attempts < deadline:
            server.handle_request()
            attempts += 1
    finally:
        server.server_close()
    if server.error:
        raise server.error
    if server.result:
        return server.result
    raise AuthError(
        "Timed out waiting for OAuth callback.",
        hint="Retry with --local-server or use --no-browser and --callback-url.",
    )


def _first(query: dict[str, list[str]], key: str) -> str | None:
    values = query.get(key)
    if not values:
        return None
    return values[0]
