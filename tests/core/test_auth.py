from ticktask.core.auth import AuthManager
from ticktask.core.config import ConfigStore
import httpx


def test_auth_init_and_status(tmp_path) -> None:
    manager = AuthManager(ConfigStore(tmp_path / "config.json"))
    manager.init(
        service="ticktick",
        client_id="client",
        client_secret="secret",
        redirect_uri="http://localhost/callback",
        access_token="token",
    )

    status = manager.status()
    assert status.service == "ticktick"
    assert status.configured is True
    assert status.authenticated is True
    assert status.client_id == "client"


def test_auth_status_without_config_is_not_authenticated(tmp_path) -> None:
    status = AuthManager(ConfigStore(tmp_path / "missing.json")).status()
    assert status.configured is False
    assert status.authenticated is False


def test_auth_authorization_url_and_code_exchange_are_mockable(tmp_path) -> None:
    manager = AuthManager(ConfigStore(tmp_path / "config.json"))
    manager.init("ticktick", "client", "secret", "http://localhost/callback")
    assert manager.authorization_url() == (
        "https://api.ticktick.com/oauth/authorize?"
        "client_id=client&redirect_uri=http%3A%2F%2Flocalhost%2Fcallback&response_type=code"
    )
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["url"] = str(request.url)
        seen["body"] = request.read().decode()
        return httpx.Response(
            200,
            json={"access_token": "new-access", "refresh_token": "new-refresh", "expires_in": 3600},
        )

    profile = manager.login_with_code(
        "callback-code",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    assert seen["url"] == "https://api.ticktick.com/oauth/token"
    assert "grant_type=authorization_code" in seen["body"]
    assert "code=callback-code" in seen["body"]
    assert profile.access_token == "new-access"
    assert profile.refresh_token == "new-refresh"
    assert profile.expires_at is not None


def test_auth_refresh_is_mockable(tmp_path) -> None:
    manager = AuthManager(ConfigStore(tmp_path / "config.json"))
    manager.init(
        "dida365",
        "client",
        "secret",
        "http://localhost/callback",
        refresh_token="old-refresh",
    )

    def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == "https://api.dida365.com/oauth/token"
        assert "grant_type=refresh_token" in request.read().decode()
        return httpx.Response(200, json={"access_token": "new-access", "expires_in": 60})

    profile = manager.refresh(http_client=httpx.Client(transport=httpx.MockTransport(handler)))
    assert profile.access_token == "new-access"
    assert profile.refresh_token == "old-refresh"
