from typer.testing import CliRunner

from ticktask.cli.app import app

runner = CliRunner()


def test_help() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Agent-friendly CLI" in result.stdout


def test_doctor_json_without_config(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("TICKTASK_CONFIG_DIR", str(tmp_path))
    result = runner.invoke(app, ["doctor", "--json"])
    assert result.exit_code == 0
    assert '"ok": true' in result.stdout
    assert '"configured": false' in result.stdout
