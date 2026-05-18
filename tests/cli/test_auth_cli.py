import json

from typer.testing import CliRunner

from ticktask.cli.app import app

runner = CliRunner()


class FakeKeyring:
    def __init__(self) -> None:
        self.values = {}

    def get_password(self, service_name: str, username: str) -> str | None:
        return self.values.get((service_name, username))

    def set_password(self, service_name: str, username: str, password: str) -> None:
        self.values[(service_name, username)] = password

    def delete_password(self, service_name: str, username: str) -> None:
        self.values.pop((service_name, username), None)


def test_auth_init_and_status_json(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("TICKTASK_CONFIG_DIR", str(tmp_path))
    result = runner.invoke(
        app,
        [
            "auth",
            "init",
            "--service",
            "dida365",
            "--client-id",
            "client",
            "--client-secret",
            "secret",
            "--redirect-uri",
            "http://localhost",
            "--access-token",
            "token",
            "--json",
        ],
    )
    assert result.exit_code == 0
    assert json.loads(result.stdout)["data"]["service"] == "dida365"

    status = runner.invoke(app, ["auth", "status", "--json"])
    assert status.exit_code == 0
    payload = json.loads(status.stdout)
    assert payload["data"]["configured"] is True
    assert payload["data"]["authenticated"] is True


def test_auth_init_keyring_storage_does_not_write_secrets_to_config(tmp_path, monkeypatch) -> None:
    fake_keyring = FakeKeyring()
    monkeypatch.setenv("TICKTASK_CONFIG_DIR", str(tmp_path))
    monkeypatch.setattr(
        "ticktask.core.credentials.KeyringCredentialStore._load_backend",
        staticmethod(lambda: fake_keyring),
    )

    result = runner.invoke(
        app,
        [
            "auth",
            "init",
            "--service",
            "dida365",
            "--client-id",
            "client",
            "--client-secret",
            "secret",
            "--redirect-uri",
            "http://localhost",
            "--access-token",
            "token",
            "--refresh-token",
            "refresh",
            "--token-storage",
            "keyring",
            "--json",
        ],
    )
    assert result.exit_code == 0
    assert json.loads(result.stdout)["data"]["token_storage"] == "keyring"

    raw_config = json.loads((tmp_path / "config.json").read_text(encoding="utf-8"))
    profile_raw = raw_config["profiles"]["dida365"]
    assert "client_secret" not in profile_raw
    assert "access_token" not in profile_raw
    assert "refresh_token" not in profile_raw

    status = runner.invoke(app, ["auth", "status", "--json"])
    assert status.exit_code == 0
    payload = json.loads(status.stdout)["data"]
    assert payload["authenticated"] is True
    assert payload["has_refresh_token"] is True
    assert payload["token_storage"] == "keyring"
    assert payload["keyring_available"] is True


def test_auth_init_rejects_invalid_token_storage_without_writing_config(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("TICKTASK_CONFIG_DIR", str(tmp_path))

    result = runner.invoke(
        app,
        [
            "auth",
            "init",
            "--service",
            "dida365",
            "--client-id",
            "client",
            "--client-secret",
            "secret",
            "--redirect-uri",
            "http://localhost",
            "--access-token",
            "token",
            "--token-storage",
            "bogus",
            "--json",
        ],
    )

    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert "Unsupported token storage" in payload["error"]["message"]
    assert not (tmp_path / "config.json").exists()


def test_auth_login_code_and_refresh_json(monkeypatch) -> None:
    class FakeProfile:
        service = "ticktick"
        refresh_token = "refresh"
        expires_at = "2026-01-01T00:00:00+00:00"

        def has_token(self):
            return True

    class FakeFlow:
        authorization_url = "https://ticktick.com/oauth/authorize?client_id=client&state=state"
        state = "state"

    class FakeManager:
        def begin_login(self, service=None):
            return FakeFlow()

        def parse_callback_url(self, callback_url, service=None):
            assert callback_url == "http://localhost/callback?code=abc&state=state"
            return {"code": "abc", "state": "state"}

        def login_with_code(self, code, service=None, state=None):
            assert code == "abc"
            assert state in (None, "state")
            return FakeProfile()

        def refresh(self, service=None):
            return FakeProfile()

    monkeypatch.setattr("ticktask.cli.auth.AuthManager", lambda: FakeManager())
    login = runner.invoke(app, ["auth", "login", "--code", "abc", "--state", "state", "--json"])
    assert login.exit_code == 0
    assert json.loads(login.stdout)["data"]["authenticated"] is True

    callback_login = runner.invoke(
        app,
        [
            "auth",
            "login",
            "--callback-url",
            "http://localhost/callback?code=abc&state=state",
            "--json",
        ],
    )
    assert callback_login.exit_code == 0
    assert json.loads(callback_login.stdout)["data"]["authenticated"] is True

    begin = runner.invoke(app, ["auth", "login", "--no-browser", "--json"])
    assert begin.exit_code == 0
    begin_payload = json.loads(begin.stdout)["data"]
    assert begin_payload["authorization_url"].endswith("state=state")
    assert begin_payload["state"] == "state"

    refresh = runner.invoke(app, ["auth", "refresh", "--json"])
    assert refresh.exit_code == 0
    assert json.loads(refresh.stdout)["data"]["has_refresh_token"] is True
