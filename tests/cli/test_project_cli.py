import json

from typer.testing import CliRunner

from ticktask.cli.app import app

runner = CliRunner()


def test_project_list_json(monkeypatch) -> None:
    class FakeService:
        def list_projects(self):
            return [{"id": "p1", "name": "Inbox", "raw": {}}]

    monkeypatch.setattr("ticktask.cli.project.TicktaskService", lambda: FakeService())
    result = runner.invoke(app, ["project", "list", "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["data"][0]["id"] == "p1"
