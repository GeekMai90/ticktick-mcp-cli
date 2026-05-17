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

    class FakeManager:
        def authorization_url(self, service=None):
            return "https://api.ticktick.com/oauth/authorize?client_id=client"

        def login_with_code(self, code, service=None):
            assert code == "abc"
            return FakeProfile()

        def refresh(self, service=None):
            return FakeProfile()

    monkeypatch.setattr("ticktask.cli.auth.AuthManager", lambda: FakeManager())
    login = runner.invoke(app, ["auth", "login", "--code", "abc", "--json"])
    assert login.exit_code == 0
    assert json.loads(login.stdout)["data"]["authenticated"] is True

    refresh = runner.invoke(app, ["auth", "refresh", "--json"])
    assert refresh.exit_code == 0
    assert json.loads(refresh.stdout)["data"]["has_refresh_token"] is True
