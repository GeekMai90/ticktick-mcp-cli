import json

from typer.testing import CliRunner

from ticktask.cli.app import app

runner = CliRunner()


def test_integration_smoke_is_skipped_unless_enabled(monkeypatch) -> None:
    monkeypatch.delenv("TICKTASK_INTEGRATION", raising=False)

    result = runner.invoke(app, ["integration", "smoke", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["data"] == {
        "enabled": False,
        "skipped": True,
        "project_count": None,
    }


def test_integration_smoke_lists_projects_when_enabled(monkeypatch) -> None:
    monkeypatch.setenv("TICKTASK_INTEGRATION", "1")

    class FakeService:
        def list_projects(self):
            return [{"id": "p1", "name": "Inbox"}, {"id": "p2", "name": "Work"}]

    monkeypatch.setattr("ticktask.cli.integration.TicktaskService", lambda service=None: FakeService())

    result = runner.invoke(app, ["integration", "smoke", "--service", "dida365", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["data"] == {
        "enabled": True,
        "skipped": False,
        "service": "dida365",
        "project_count": 2,
    }
