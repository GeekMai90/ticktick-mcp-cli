import json

from typer.testing import CliRunner

from ticktask.cli.app import app

runner = CliRunner()


def test_task_add_json(monkeypatch) -> None:
    class FakeService:
        def create_task(self, title, project=None, content=None, due=None, priority="none"):
            return {"id": "t1", "title": title, "project_id": project, "raw": {}}

    monkeypatch.setattr("ticktask.cli.task.TicktaskService", lambda: FakeService())
    result = runner.invoke(app, ["task", "add", "Write tests", "--json"])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["data"]["title"] == "Write tests"


def test_task_complete_requires_yes_json(monkeypatch) -> None:
    class FakeService:
        def complete_task(self, task_id, project_id, confirmed):
            from ticktask.core.errors import ConfirmationRequiredError

            if not confirmed:
                raise ConfirmationRequiredError("Completing a task requires explicit confirmation.")
            return {"task_id": task_id, "project_id": project_id}

    monkeypatch.setattr("ticktask.cli.task.TicktaskService", lambda: FakeService())
    result = runner.invoke(
        app,
        ["task", "complete", "t1", "--project-id", "p1", "--json"],
    )
    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    assert payload["error"]["code"] == "CONFIRMATION_REQUIRED"


def test_done_alias(monkeypatch) -> None:
    class FakeService:
        def complete_task(self, task_id, project_id, confirmed):
            return {"task_id": task_id, "project_id": project_id, "confirmed": confirmed}

    monkeypatch.setattr("ticktask.cli.task.TicktaskService", lambda: FakeService())
    result = runner.invoke(app, ["done", "t1", "--project-id", "p1", "--yes", "--json"])
    assert result.exit_code == 0
    assert json.loads(result.stdout)["data"]["confirmed"] is True


def test_task_get_update_delete_move_json(monkeypatch) -> None:
    class FakeService:
        def get_task(self, task_id, project_id):
            return {"id": task_id, "project_id": project_id, "title": "Loaded"}

        def update_task(self, task_id, project_id, title=None, content=None, due=None, priority=None):
            return {"id": task_id, "project_id": project_id, "title": title, "priority": priority}

        def delete_task(self, task_id, project_id, confirmed):
            if not confirmed:
                from ticktask.core.errors import ConfirmationRequiredError

                raise ConfirmationRequiredError("Deleting a task requires explicit confirmation.")
            return {"task_id": task_id, "project_id": project_id, "confirmed": confirmed}

        def move_task(self, task_id, from_project_id, to_project_id):
            return {
                "task_id": task_id,
                "from_project_id": from_project_id,
                "to_project_id": to_project_id,
            }

    monkeypatch.setattr("ticktask.cli.task.TicktaskService", lambda: FakeService())
    got = runner.invoke(app, ["task", "get", "t1", "--project-id", "p1", "--json"])
    assert got.exit_code == 0
    assert json.loads(got.stdout)["data"]["title"] == "Loaded"

    updated = runner.invoke(
        app,
        [
            "task",
            "update",
            "t1",
            "--project-id",
            "p1",
            "--title",
            "Renamed",
            "--priority",
            "high",
            "--json",
        ],
    )
    assert updated.exit_code == 0
    assert json.loads(updated.stdout)["data"]["title"] == "Renamed"

    deleted = runner.invoke(app, ["task", "delete", "t1", "--project-id", "p1", "--json"])
    assert deleted.exit_code == 1
    assert json.loads(deleted.stdout)["error"]["code"] == "CONFIRMATION_REQUIRED"

    moved = runner.invoke(
        app,
        ["task", "move", "t1", "--from-project-id", "p1", "--to-project-id", "p2", "--json"],
    )
    assert moved.exit_code == 0
    assert json.loads(moved.stdout)["data"]["to_project_id"] == "p2"


def test_completed_command_json(monkeypatch) -> None:
    class FakeService:
        def completed_tasks(self, preset=None, start_date=None, end_date=None, project=None):
            return [{"id": "t1", "project_id": project, "title": preset, "status": 2}]

    monkeypatch.setattr("ticktask.cli.app.TicktaskService", lambda: FakeService())
    result = runner.invoke(app, ["completed", "today", "--project", "Inbox", "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["meta"]["count"] == 1
    assert payload["data"][0]["title"] == "today"
