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


def test_checklist_item_cli_json(monkeypatch) -> None:
    class FakeService:
        def add_checklist_item(self, task_id, project_id, title):
            return {"id": task_id, "project_id": project_id, "items": [{"id": "i-new", "title": title}]}

        def update_checklist_item(self, task_id, project_id, item_id, title=None, status=None):
            return {"id": task_id, "project_id": project_id, "items": [{"id": item_id, "title": title, "status": status}]}

        def complete_checklist_item(self, task_id, project_id, item_id):
            return {"id": task_id, "project_id": project_id, "items": [{"id": item_id, "status": 1}]}

        def delete_checklist_item(self, task_id, project_id, item_id, confirmed):
            if not confirmed:
                from ticktask.core.errors import ConfirmationRequiredError

                raise ConfirmationRequiredError("confirm")
            return {"id": task_id, "project_id": project_id, "items": []}

    monkeypatch.setattr("ticktask.cli.task.TicktaskService", lambda: FakeService())

    added = runner.invoke(
        app, ["task", "item", "add", "t1", "New", "--project-id", "p1", "--json"]
    )
    assert added.exit_code == 0
    assert json.loads(added.stdout)["data"]["items"][0]["title"] == "New"

    updated = runner.invoke(
        app,
        [
            "task",
            "item",
            "update",
            "t1",
            "i1",
            "--project-id",
            "p1",
            "--title",
            "Renamed",
            "--status",
            "completed",
            "--json",
        ],
    )
    assert updated.exit_code == 0
    assert json.loads(updated.stdout)["data"]["items"][0]["status"] == "completed"

    completed = runner.invoke(
        app, ["task", "item", "complete", "t1", "i1", "--project-id", "p1", "--json"]
    )
    assert completed.exit_code == 0
    assert json.loads(completed.stdout)["data"]["items"][0]["status"] == 1

    denied = runner.invoke(
        app, ["task", "item", "delete", "t1", "i1", "--project-id", "p1", "--json"]
    )
    assert denied.exit_code == 1
    assert json.loads(denied.stdout)["error"]["code"] == "CONFIRMATION_REQUIRED"

    deleted = runner.invoke(
        app, ["task", "item", "delete", "t1", "i1", "--project-id", "p1", "--yes", "--json"]
    )
    assert deleted.exit_code == 0
    assert json.loads(deleted.stdout)["data"]["items"] == []



def test_task_list_tag_filter_and_smart_filter_cli_json(monkeypatch) -> None:
    seen = {}

    class FakeService:
        def list_tasks(
            self,
            project=None,
            status="open",
            today_only=False,
            start_date=None,
            end_date=None,
            tag=None,
            filter_preset=None,
        ):
            seen.update({"tag": tag, "filter_preset": filter_preset})
            return [{"id": "t1", "title": "Tagged", "tags": [tag], "project_id": project}]

    monkeypatch.setattr("ticktask.cli.task.TicktaskService", lambda: FakeService())
    result = runner.invoke(
        app,
        ["task", "list", "--tag", "agent", "--filter", "high-priority", "--json"],
    )
    assert result.exit_code == 0
    assert seen == {"tag": "agent", "filter_preset": "high-priority"}
    assert json.loads(result.stdout)["data"][0]["tags"] == ["agent"]


def test_task_filter_cli_json(monkeypatch) -> None:
    seen = {}

    class FakeService:
        def filter_tasks(
            self,
            tag=None,
            project=None,
            status="open",
            priority=None,
            start_date=None,
            end_date=None,
        ):
            seen.update({"tag": tag, "project": project, "status": status, "priority": priority})
            return [{"id": "t1", "title": "Filtered", "tags": [tag]}]

    monkeypatch.setattr("ticktask.cli.task.TicktaskService", lambda: FakeService())
    result = runner.invoke(
        app,
        ["task", "filter", "--tag", "agent", "--project", "Inbox", "--priority", "high", "--json"],
    )
    assert result.exit_code == 0
    assert seen == {"tag": "agent", "project": "Inbox", "status": "open", "priority": "high"}
    assert json.loads(result.stdout)["data"][0]["title"] == "Filtered"


def test_task_tag_cli_json(monkeypatch) -> None:
    class FakeService:
        def add_task_tag(self, task_id, project_id, tag):
            return {"id": task_id, "project_id": project_id, "tags": [tag]}

        def remove_task_tag(self, task_id, project_id, tag):
            return {"id": task_id, "project_id": project_id, "tags": []}

    monkeypatch.setattr("ticktask.cli.task.TicktaskService", lambda: FakeService())

    added = runner.invoke(
        app, ["task", "tag", "add", "t1", "agent", "--project-id", "p1", "--json"]
    )
    assert added.exit_code == 0
    assert json.loads(added.stdout)["data"]["tags"] == ["agent"]

    removed = runner.invoke(
        app, ["task", "tag", "remove", "t1", "agent", "--project-id", "p1", "--json"]
    )
    assert removed.exit_code == 0
    assert json.loads(removed.stdout)["data"]["tags"] == []



def test_task_reminder_and_repeat_cli_json(monkeypatch) -> None:
    class FakeService:
        def set_task_reminders(self, task_id, project_id, reminders):
            return {"id": task_id, "project_id": project_id, "raw": {"reminders": reminders}}

        def clear_task_reminders(self, task_id, project_id):
            return {"id": task_id, "project_id": project_id, "raw": {"reminders": []}}

        def set_task_repeat(self, task_id, project_id, preset=None, rrule=None):
            return {"id": task_id, "project_id": project_id, "raw": {"repeatFlag": rrule or f"RRULE:FREQ={preset.upper()}"}}

        def clear_task_repeat(self, task_id, project_id):
            return {"id": task_id, "project_id": project_id, "raw": {"repeatFlag": ""}}

    monkeypatch.setattr("ticktask.cli.task.TicktaskService", lambda: FakeService())

    reminded = runner.invoke(
        app,
        ["task", "reminder", "set", "t1", "--project-id", "p1", "--reminder", "TRIGGER:PT10M", "--json"],
    )
    assert reminded.exit_code == 0
    assert json.loads(reminded.stdout)["data"]["raw"]["reminders"] == ["TRIGGER:PT10M"]

    cleared_reminders = runner.invoke(app, ["task", "reminder", "clear", "t1", "--project-id", "p1", "--json"])
    assert cleared_reminders.exit_code == 0
    assert json.loads(cleared_reminders.stdout)["data"]["raw"]["reminders"] == []

    repeated = runner.invoke(app, ["task", "repeat", "set", "t1", "--project-id", "p1", "--preset", "weekly", "--json"])
    assert repeated.exit_code == 0
    assert json.loads(repeated.stdout)["data"]["raw"]["repeatFlag"] == "RRULE:FREQ=WEEKLY"

    cleared_repeat = runner.invoke(app, ["task", "repeat", "clear", "t1", "--project-id", "p1", "--json"])
    assert cleared_repeat.exit_code == 0
    assert json.loads(cleared_repeat.stdout)["data"]["raw"]["repeatFlag"] == ""
