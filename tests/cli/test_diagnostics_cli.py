import json
import zipfile

from typer.testing import CliRunner

from ticktask.cli.app import app
from ticktask.core.config import ConfigStore, ProfileConfig

runner = CliRunner()


def test_doctor_bundle_json_writes_redacted_zip(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("TICKTASK_CONFIG_DIR", str(tmp_path / "config"))
    store = ConfigStore()
    config = store.load()
    profile = ProfileConfig.for_service("dida365", "client-id", "client-secret", "http://localhost/callback")
    profile.access_token = "access-token-secret"
    profile.refresh_token = "refresh-token-secret"
    config.set_profile(profile)
    store.save(config)
    output_path = tmp_path / "ticktask-diagnostics.zip"

    result = runner.invoke(app, ["doctor", "bundle", "--output", str(output_path), "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["data"]["bundle_path"] == str(output_path)
    assert payload["data"]["redacted"] is True
    assert "client-secret" not in result.stdout
    assert "access-token-secret" not in result.stdout
    with zipfile.ZipFile(output_path) as archive:
        diagnostics = archive.read("diagnostics.json").decode("utf-8")
    assert "client-secret" not in diagnostics
    assert "access-token-secret" not in diagnostics
    assert '"service": "dida365"' in diagnostics


def test_doctor_bundle_human_output_mentions_bundle_path(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("TICKTASK_CONFIG_DIR", str(tmp_path / "config"))
    output_path = tmp_path / "bundle.zip"

    result = runner.invoke(app, ["doctor", "bundle", "--output", str(output_path)])

    assert result.exit_code == 0
    assert str(output_path) in result.stdout
    assert "redacted" in result.stdout.lower()
    assert output_path.exists()
