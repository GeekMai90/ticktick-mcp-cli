import json

from typer.testing import CliRunner

from ticktask.cli.app import app

runner = CliRunner()


def test_habit_cli_json(monkeypatch) -> None:
    class FakeService:
        def list_habits(self):
            return [{"id": "h1", "name": "Read"}]

        def get_habit(self, habit_id):
            return {"id": habit_id, "name": "Read"}

        def create_habit(self, name, **kwargs):
            return {"id": "h-new", "name": name, "raw": kwargs}

        def update_habit(self, habit_id, **kwargs):
            return {"id": habit_id, "name": kwargs.get("name")}

        def checkin_habit(self, habit_id, stamp, value=1):
            return {"habitId": habit_id, "stamp": stamp, "value": value}

        def habit_checkins(self, habit_ids, from_stamp, to_stamp):
            return [{"habitId": habit_ids[0], "from": from_stamp, "to": to_stamp}]

    monkeypatch.setattr("ticktask.cli.habit.TicktaskService", lambda: FakeService())

    listed = runner.invoke(app, ["habit", "list", "--json"])
    assert listed.exit_code == 0
    assert json.loads(listed.stdout)["data"][0]["id"] == "h1"

    got = runner.invoke(app, ["habit", "get", "h1", "--json"])
    assert got.exit_code == 0
    assert json.loads(got.stdout)["data"]["name"] == "Read"

    created = runner.invoke(app, ["habit", "create", "Write", "--goal", "1", "--unit", "time", "--json"])
    assert created.exit_code == 0
    assert json.loads(created.stdout)["data"]["id"] == "h-new"

    updated = runner.invoke(app, ["habit", "update", "h1", "--name", "Read more", "--json"])
    assert updated.exit_code == 0
    assert json.loads(updated.stdout)["data"]["name"] == "Read more"

    checkin = runner.invoke(app, ["habit", "checkin", "h1", "20260101", "--value", "1", "--json"])
    assert checkin.exit_code == 0
    assert json.loads(checkin.stdout)["data"]["stamp"] == 20260101

    history = runner.invoke(app, ["habit", "history", "h1", "--from", "20260101", "--to", "20260131", "--json"])
    assert history.exit_code == 0
    assert json.loads(history.stdout)["data"][0]["habitId"] == "h1"


def test_focus_cli_json(monkeypatch) -> None:
    class FakeService:
        def list_focuses(self, from_time, to_time, focus_type=0):
            return [{"id": "f1", "focus_type": focus_type, "start_time": from_time, "end_time": to_time}]

        def get_focus(self, focus_id, focus_type=0):
            return {"id": focus_id, "focus_type": focus_type}

        def delete_focus(self, focus_id, focus_type=0, confirmed=False):
            if not confirmed:
                from ticktask.core.errors import ConfirmationRequiredError
                raise ConfirmationRequiredError("confirm")
            return {"focus_id": focus_id, "focus_type": focus_type, "result": {}}

    monkeypatch.setattr("ticktask.cli.focus.TicktaskService", lambda: FakeService())

    listed = runner.invoke(app, ["focus", "list", "--from", "2026-01-01", "--to", "2026-01-02", "--type", "1", "--json"])
    assert listed.exit_code == 0
    assert json.loads(listed.stdout)["data"][0]["focus_type"] == 1

    got = runner.invoke(app, ["focus", "get", "f1", "--type", "0", "--json"])
    assert got.exit_code == 0
    assert json.loads(got.stdout)["data"]["id"] == "f1"

    denied = runner.invoke(app, ["focus", "delete", "f1", "--type", "0", "--json"])
    assert denied.exit_code == 1
    assert json.loads(denied.stdout)["error"]["code"] == "CONFIRMATION_REQUIRED"

    deleted = runner.invoke(app, ["focus", "delete", "f1", "--type", "0", "--yes", "--json"])
    assert deleted.exit_code == 0
    assert json.loads(deleted.stdout)["data"]["focus_id"] == "f1"
