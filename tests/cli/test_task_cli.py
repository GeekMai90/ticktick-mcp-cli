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
