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
