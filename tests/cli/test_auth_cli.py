import json

from typer.testing import CliRunner

from ticktask.cli.app import app

runner = CliRunner()


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
