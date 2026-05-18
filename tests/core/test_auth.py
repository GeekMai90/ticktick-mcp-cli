import json
from datetime import UTC, datetime, timedelta
from urllib.parse import parse_qs, urlparse

from ticktask.core.auth import AuthManager
from ticktask.core.config import ConfigStore
from ticktask.core.errors import ConfigError
import httpx


class FakeKeyring:
    def __init__(self) -> None:
        self.values = {}

    def get_password(self, service_name: str, username: str) -> str | None:
        return self.values.get((service_name, username))

    def set_password(self, service_name: str, username: str, password: str) -> None:
        self.values[(service_name, username)] = password

    def delete_password(self, service_name: str, username: str) -> None:
        self.values.pop((service_name, username), None)


class LockedKeyring(FakeKeyring):
    def get_password(self, service_name: str, username: str) -> str | None:
        raise RuntimeError("backend locked")


class ProbeOnlyLockedKeyring(FakeKeyring):
    def get_password(self, service_name: str, username: str) -> str | None:
        if username == "__probe__":
            return None
        raise RuntimeError("backend locked during secret read")


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


def test_auth_init_keyring_storage_hydrates_tokens_without_file_secrets(tmp_path, monkeypatch) -> None:
    fake_keyring = FakeKeyring()
    monkeypatch.setattr(
        "ticktask.core.credentials.KeyringCredentialStore._load_backend",
        staticmethod(lambda: fake_keyring),
    )
    config_path = tmp_path / "config.json"
    manager = AuthManager(ConfigStore(config_path))

    manager.init(
        service="dida365",
        client_id="client",
        client_secret="secret",
        redirect_uri="http://localhost/callback",
        access_token="token",
        refresh_token="refresh",
        token_storage="keyring",
    )

    raw = json.loads(config_path.read_text(encoding="utf-8"))
    profile_raw = raw["profiles"]["dida365"]
    assert profile_raw["token_storage"] == "keyring"
    assert "client_secret" not in profile_raw
    assert "access_token" not in profile_raw
    assert "refresh_token" not in profile_raw

    status = manager.status()
    assert status.configured is True
    assert status.authenticated is True
    assert status.has_refresh_token is True
    assert status.token_storage == "keyring"
    assert status.keyring_available is True

    profile = manager.require_token()
    assert profile.client_secret == "secret"
    assert profile.access_token == "token"
    assert profile.refresh_token == "refresh"


def test_auth_status_reports_keyring_unavailable_without_reclassifying_profile(
    tmp_path, monkeypatch
) -> None:
    config_path = tmp_path / "config.json"
    fake_keyring = FakeKeyring()
    monkeypatch.setattr(
        "ticktask.core.credentials.KeyringCredentialStore._load_backend",
        staticmethod(lambda: fake_keyring),
    )
    manager = AuthManager(ConfigStore(config_path))
    manager.init(
        service="dida365",
        client_id="client",
        client_secret="secret",
        redirect_uri="http://localhost/callback",
        token_storage="keyring",
    )

    def unavailable():
        raise ConfigError("keyring package missing")

    monkeypatch.setattr(
        "ticktask.core.credentials.KeyringCredentialStore._load_backend",
        staticmethod(unavailable),
    )

    status = manager.status()
    assert status.service == "dida365"
    assert status.token_storage == "keyring"
    assert status.configured is False
    assert status.authenticated is False
    assert status.keyring_available is False
    assert "keyring package missing" in (status.keyring_hint or "")


def test_auth_status_reports_locked_keyring_without_crashing(tmp_path, monkeypatch) -> None:
    fake_keyring = FakeKeyring()
    monkeypatch.setattr(
        "ticktask.core.credentials.KeyringCredentialStore._load_backend",
        staticmethod(lambda: fake_keyring),
    )
    manager = AuthManager(ConfigStore(tmp_path / "config.json"))
    manager.init(
        service="dida365",
        client_id="client",
        client_secret="secret",
        redirect_uri="http://localhost/callback",
        token_storage="keyring",
    )
    monkeypatch.setattr(
        "ticktask.core.credentials.KeyringCredentialStore._load_backend",
        staticmethod(lambda: LockedKeyring()),
    )

    status = manager.status()

    assert status.token_storage == "keyring"
    assert status.keyring_available is False
    assert "backend locked" in (status.keyring_hint or "")


def test_auth_status_handles_probe_success_but_secret_read_failure(tmp_path, monkeypatch) -> None:
    fake_keyring = FakeKeyring()
    monkeypatch.setattr(
        "ticktask.core.credentials.KeyringCredentialStore._load_backend",
        staticmethod(lambda: fake_keyring),
    )
    manager = AuthManager(ConfigStore(tmp_path / "config.json"))
    manager.init(
        service="dida365",
        client_id="client",
        client_secret="secret",
        redirect_uri="http://localhost/callback",
        access_token="token",
        refresh_token="refresh",
        token_storage="keyring",
    )
    monkeypatch.setattr(
        "ticktask.core.credentials.KeyringCredentialStore._load_backend",
        staticmethod(lambda: ProbeOnlyLockedKeyring()),
    )

    status = manager.status()

    assert status.token_storage == "keyring"
    assert status.configured is False
    assert status.authenticated is False
    assert status.has_refresh_token is False
    assert status.keyring_available is False
    assert "backend locked during secret read" in (status.keyring_hint or "")


def test_auth_init_rejects_invalid_token_storage_before_writing_config(tmp_path) -> None:
    config_path = tmp_path / "config.json"
    manager = AuthManager(ConfigStore(config_path))

    try:
        manager.init(
            service="dida365",
            client_id="client",
            client_secret="secret",
            redirect_uri="http://localhost/callback",
            access_token="token",
            token_storage="bogus",
        )
    except ConfigError as exc:
        assert "Unsupported token storage" in str(exc)
    else:  # pragma: no cover - assertion branch
        raise AssertionError("invalid token storage should fail")
    assert not config_path.exists()


def test_auth_status_without_config_is_not_authenticated(tmp_path) -> None:
    status = AuthManager(ConfigStore(tmp_path / "missing.json")).status()
    assert status.configured is False
    assert status.authenticated is False


def test_auth_authorization_url_and_code_exchange_are_mockable(tmp_path) -> None:
    manager = AuthManager(ConfigStore(tmp_path / "config.json"))
    manager.init("ticktick", "client", "secret", "http://localhost/callback")
    assert manager.authorization_url() == (
        "https://ticktick.com/oauth/authorize?"
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

    assert seen["url"] == "https://ticktick.com/oauth/token"
    assert "grant_type=authorization_code" in seen["body"]
    assert "code=callback-code" in seen["body"]
    assert profile.access_token == "new-access"
    assert profile.refresh_token == "new-refresh"
    assert profile.expires_at is not None


def test_auth_authorization_url_uses_dida365_web_host(tmp_path) -> None:
    manager = AuthManager(ConfigStore(tmp_path / "config.json"))
    manager.init("dida365", "client", "secret", "http://localhost/callback")

    assert manager.authorization_url() == (
        "https://dida365.com/oauth/authorize?"
        "client_id=client&redirect_uri=http%3A%2F%2Flocalhost%2Fcallback&response_type=code"
    )


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
        assert str(request.url) == "https://dida365.com/oauth/token"
        assert "grant_type=refresh_token" in request.read().decode()
        return httpx.Response(200, json={"access_token": "new-access", "expires_in": 60})

    profile = manager.refresh(http_client=httpx.Client(transport=httpx.MockTransport(handler)))
    assert profile.access_token == "new-access"
    assert profile.refresh_token == "old-refresh"


def test_begin_login_generates_state_and_pkce_and_stores_verifier(tmp_path) -> None:
    manager = AuthManager(ConfigStore(tmp_path / "config.json"))
    manager.init("ticktick", "client", "secret", "http://localhost/callback")

    flow = manager.begin_login()
    query = parse_qs(urlparse(flow.authorization_url).query)

    assert len(flow.state) >= 32
    assert len(flow.code_verifier) >= 43
    assert query["state"] == [flow.state]
    assert query["code_challenge_method"] == ["S256"]
    assert query["code_challenge"] == [flow.code_challenge]
    assert manager.store.load().get_profile().oauth_state == flow.state
    assert manager.store.load().get_profile().code_verifier == flow.code_verifier


def test_login_with_code_sends_stored_pkce_verifier_and_validates_state(tmp_path) -> None:
    manager = AuthManager(ConfigStore(tmp_path / "config.json"))
    manager.init("ticktick", "client", "secret", "http://localhost/callback")
    flow = manager.begin_login()
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["body"] = request.read().decode()
        return httpx.Response(200, json={"access_token": "new-access"})

    profile = manager.login_with_code(
        "callback-code",
        state=flow.state,
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    assert "code_verifier=" in seen["body"]
    assert flow.code_verifier in seen["body"]
    assert profile.access_token == "new-access"
    assert profile.oauth_state is None
    assert profile.code_verifier is None


def test_parse_callback_url_extracts_code_and_checks_state(tmp_path) -> None:
    manager = AuthManager(ConfigStore(tmp_path / "config.json"))
    manager.init("ticktick", "client", "secret", "http://localhost/callback")
    flow = manager.begin_login()

    callback = manager.parse_callback_url(f"http://localhost/callback?code=abc&state={flow.state}")

    assert callback == {"code": "abc", "state": flow.state}


def test_require_token_auto_refreshes_expired_access_token(tmp_path) -> None:
    manager = AuthManager(ConfigStore(tmp_path / "config.json"))
    expired = (datetime.now(UTC) - timedelta(minutes=1)).isoformat()
    manager.init(
        "dida365",
        "client",
        "secret",
        "http://localhost/callback",
        access_token="old-access",
        refresh_token="refresh",
        expires_at=expired,
    )

    def handler(request: httpx.Request) -> httpx.Response:
        assert "grant_type=refresh_token" in request.read().decode()
        return httpx.Response(200, json={"access_token": "fresh-access", "expires_in": 3600})

    profile = manager.require_token(http_client=httpx.Client(transport=httpx.MockTransport(handler)))

    assert profile.access_token == "fresh-access"


def test_require_token_keeps_valid_access_token_without_refresh(tmp_path) -> None:
    manager = AuthManager(ConfigStore(tmp_path / "config.json"))
    future = (datetime.now(UTC) + timedelta(hours=1)).isoformat()
    manager.init(
        "ticktick",
        "client",
        "secret",
        "http://localhost/callback",
        access_token="valid-access",
        refresh_token="refresh",
        expires_at=future,
    )

    profile = manager.require_token(
        http_client=httpx.Client(
            transport=httpx.MockTransport(lambda _request: httpx.Response(500, json={}))
        )
    )

    assert profile.access_token == "valid-access"
