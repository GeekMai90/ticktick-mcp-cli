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


def test_project_create_update_delete_json(monkeypatch) -> None:
    class FakeService:
        def create_project(self, name, color=None, sort_order=None, view_mode=None, kind=None):
            return {
                "id": "p-new",
                "name": name,
                "raw": {"color": color, "sortOrder": sort_order, "viewMode": view_mode, "kind": kind},
            }

        def update_project(
            self, project_id, name=None, color=None, sort_order=None, view_mode=None, kind=None, closed=None
        ):
            return {"id": project_id, "name": name, "raw": {"closed": closed}}

        def delete_project(self, project_id, confirmed):
            if not confirmed:
                from ticktask.core.errors import ConfirmationRequiredError

                raise ConfirmationRequiredError("confirm")
            return {"project_id": project_id, "result": {}}

    monkeypatch.setattr("ticktask.cli.project.TicktaskService", lambda: FakeService())

    created = runner.invoke(
        app,
        [
            "project",
            "create",
            "Focus",
            "--color",
            "#00aa00",
            "--view-mode",
            "list",
            "--json",
        ],
    )
    assert created.exit_code == 0
    assert json.loads(created.stdout)["data"]["id"] == "p-new"

    updated = runner.invoke(
        app, ["project", "update", "p1", "--name", "Renamed", "--closed", "--json"]
    )
    assert updated.exit_code == 0
    assert json.loads(updated.stdout)["data"]["name"] == "Renamed"

    denied = runner.invoke(app, ["project", "delete", "p1", "--json"])
    assert denied.exit_code == 1
    assert json.loads(denied.stdout)["error"]["code"] == "CONFIRMATION_REQUIRED"

    deleted = runner.invoke(app, ["project", "delete", "p1", "--yes", "--json"])
    assert deleted.exit_code == 0
    assert json.loads(deleted.stdout)["data"]["project_id"] == "p1"
