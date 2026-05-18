from __future__ import annotations

from threading import Thread
from urllib.request import urlopen
import socket

import pytest

from ticktask.core.errors import AuthError
from ticktask.core.oauth_server import wait_for_oauth_callback


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("localhost", 0))
        return int(sock.getsockname()[1])


def test_wait_for_oauth_callback_returns_code_and_state() -> None:
    port = _free_port()
    redirect_uri = f"http://localhost:{port}/callback"
    result_holder = {}
    error_holder = {}

    def wait() -> None:
        try:
            result_holder["result"] = wait_for_oauth_callback(redirect_uri, timeout_seconds=3)
        except Exception as exc:  # pragma: no cover - surfaced below
            error_holder["error"] = exc

    thread = Thread(target=wait)
    thread.start()
    with urlopen(f"http://localhost:{port}/callback?code=abc&state=state") as response:
        assert response.status == 200
    thread.join(timeout=5)

    assert "error" not in error_holder
    result = result_holder["result"]
    assert result.code == "abc"
    assert result.state == "state"
    assert result.callback_url.endswith("/callback?code=abc&state=state")


def test_wait_for_oauth_callback_rejects_non_local_redirect_uri() -> None:
    with pytest.raises(AuthError, match="localhost"):
        wait_for_oauth_callback("http://example.com/callback", timeout_seconds=1)


def test_wait_for_oauth_callback_rejects_ipv6_loopback_until_supported() -> None:
    with pytest.raises(AuthError, match="localhost"):
        wait_for_oauth_callback("http://[::1]:18766/callback", timeout_seconds=1)


def test_wait_for_oauth_callback_requires_explicit_port() -> None:
    with pytest.raises(AuthError, match="explicit port"):
        wait_for_oauth_callback("http://localhost/callback", timeout_seconds=1)
