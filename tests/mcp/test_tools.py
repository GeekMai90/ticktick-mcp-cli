import inspect

import pytest

from ticktask.mcp import tools
from ticktask.mcp.server import INSTALL_HINT, build_server


class FakeService:
    def list_projects(self):
        return [{"id": "p1", "name": "Inbox"}]

    def list_tasks(self, project=None, status="open", today_only=False, start_date=None, end_date=None, tag=None, filter_preset=None):
        return [{"id": "t1", "title": "Task", "project_id": "p1", "tags": [tag] if tag else []}]

    def filter_tasks(self, tag=None, project=None, status="open", priority=None, start_date=None, end_date=None):
        return [{"id": "ft1", "title": "Filtered", "tags": [tag]}]

    def search_tasks(self, query):
        return [{"id": "t1", "title": query}]

    def create_task(self, title, project=None, content=None, due=None, priority="none"):
        return {"id": "new", "title": title}

    def complete_task(self, task_id, project_id, confirmed):
        if not confirmed:
            from ticktask.core.errors import ConfirmationRequiredError

            raise ConfirmationRequiredError("confirm")
        return {"task_id": task_id, "project_id": project_id}

    def get_task(self, task_id, project_id):
        return {"id": task_id, "project_id": project_id}

    def update_task(self, task_id, project_id, title=None, content=None, due=None, priority=None):
        return {"id": task_id, "project_id": project_id, "title": title}

    def set_task_reminders(self, task_id, project_id, reminders):
        return {"id": task_id, "project_id": project_id, "raw": {"reminders": reminders}}

    def clear_task_reminders(self, task_id, project_id):
        return {"id": task_id, "project_id": project_id, "raw": {"reminders": []}}

    def set_task_repeat(self, task_id, project_id, preset=None, rrule=None):
        return {"id": task_id, "project_id": project_id, "raw": {"repeatFlag": rrule or f"RRULE:FREQ={preset.upper()}"}}

    def clear_task_repeat(self, task_id, project_id):
        return {"id": task_id, "project_id": project_id, "raw": {"repeatFlag": ""}}

    def add_task_tag(self, task_id, project_id, tag):
        return {"id": task_id, "project_id": project_id, "tags": [tag]}

    def remove_task_tag(self, task_id, project_id, tag):
        return {"id": task_id, "project_id": project_id, "tags": []}

    def delete_task(self, task_id, project_id, confirmed):
        if not confirmed:
            from ticktask.core.errors import ConfirmationRequiredError

            raise ConfirmationRequiredError("confirm")
        return {"task_id": task_id, "project_id": project_id}

    def move_task(self, task_id, from_project_id, to_project_id):
        return {"task_id": task_id, "to_project_id": to_project_id}

    def batch_complete_tasks(self, task_ids, project_id, dry_run=True, confirmed=False):
        return {"action": "complete", "task_ids": task_ids, "project_id": project_id, "dry_run": dry_run, "confirmed": confirmed}

    def batch_delete_tasks(self, task_ids, project_id, dry_run=True, confirmed=False):
        return {"action": "delete", "task_ids": task_ids, "project_id": project_id, "dry_run": dry_run, "confirmed": confirmed}

    def batch_move_tasks(self, task_ids, from_project_id, to_project_id, dry_run=True, confirmed=False):
        return {"action": "move", "task_ids": task_ids, "from_project_id": from_project_id, "to_project_id": to_project_id, "dry_run": dry_run, "confirmed": confirmed}

    def create_project(self, name, color=None, sort_order=None, view_mode=None, kind=None):
        return {"id": "p-new", "name": name, "raw": {"color": color}}

    def update_project(
        self, project_id, name=None, color=None, sort_order=None, view_mode=None, kind=None, closed=None
    ):
        return {"id": project_id, "name": name, "raw": {"closed": closed}}

    def delete_project(self, project_id, confirmed):
        if not confirmed:
            from ticktask.core.errors import ConfirmationRequiredError

            raise ConfirmationRequiredError("confirm")
        return {"project_id": project_id, "result": {}}

    def add_checklist_item(self, task_id, project_id, title):
        return {"id": task_id, "items": [{"id": "i-new", "title": title}]}

    def update_checklist_item(self, task_id, project_id, item_id, title=None, status=None):
        return {"id": task_id, "items": [{"id": item_id, "title": title, "status": status}]}

    def complete_checklist_item(self, task_id, project_id, item_id):
        return {"id": task_id, "items": [{"id": item_id, "status": 1}]}

    def delete_checklist_item(self, task_id, project_id, item_id, confirmed):
        if not confirmed:
            from ticktask.core.errors import ConfirmationRequiredError

            raise ConfirmationRequiredError("confirm")
        return {"id": task_id, "items": []}

    def completed_tasks(self, preset=None, start_date=None, end_date=None, project=None):
        return [{"id": "t2", "status": 2}]

    def task_analytics(self, preset=None, start_date=None, end_date=None, project=None):
        return {
            "period": {"preset": preset, "start": start_date, "end": end_date},
            "scope": {"project": project},
            "summary": {"open_count": 3, "completed_count": 2, "overdue_count": 1, "total_count": 5},
            "project_throughput": [],
            "tag_distribution": {"agent": 2},
        }

    def export_tasks(self, output_format, project=None, status="open", start_date=None, end_date=None):
        return "exported"

    def export_focuses(self, output_format, from_time, to_time, focus_type=0):
        return "focus-exported"

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

    def list_focuses(self, from_time, to_time, focus_type=0):
        return [{"id": "f1", "focus_type": focus_type}]

    def get_focus(self, focus_id, focus_type=0):
        return {"id": focus_id, "focus_type": focus_type}

    def delete_focus(self, focus_id, focus_type=0, confirmed=False):
        if not confirmed:
            from ticktask.core.errors import ConfirmationRequiredError
            raise ConfirmationRequiredError("confirm")
        return {"focus_id": focus_id, "focus_type": focus_type, "result": {}}


def test_mcp_tool_functions_use_stable_result_shape(monkeypatch) -> None:
    monkeypatch.setattr(tools, "_make_service", lambda: FakeService())
    payload = tools.ticktask_list_projects()
    assert payload["ok"] is True
    assert payload["meta"]["count"] == 1


def test_mcp_complete_requires_confirmation(monkeypatch) -> None:
    monkeypatch.setattr(tools, "_make_service", lambda: FakeService())
    payload = tools.ticktask_complete_task("t1", "p1")
    assert payload["ok"] is False
    assert payload["error"]["code"] == "CONFIRMATION_REQUIRED"


def test_mcp_new_tools(monkeypatch) -> None:
    monkeypatch.setattr(tools, "_make_service", lambda: FakeService())
    assert tools.ticktask_get_task("t1", "p1")["ok"] is True
    assert tools.ticktask_update_task("t1", "p1", title="Renamed")["data"]["title"] == "Renamed"
    assert tools.ticktask_delete_task("t1", "p1")["error"]["code"] == "CONFIRMATION_REQUIRED"
    assert tools.ticktask_move_task("t1", "p1", "p2")["data"]["to_project_id"] == "p2"
    assert tools.ticktask_batch_complete_tasks(["t1", "t2"], "p1")["data"]["dry_run"] is True
    assert tools.ticktask_batch_delete_tasks(["t1"], "p1", dry_run=False, yes=True)["data"]["confirmed"] is True
    assert tools.ticktask_batch_move_tasks(["t1"], "p1", "p2")["data"]["action"] == "move"
    assert tools.ticktask_completed(period="today")["meta"]["count"] == 1
    assert tools.ticktask_task_analytics(period="week", project="Inbox")["data"]["summary"]["completed_count"] == 2
    assert tools.ticktask_export_tasks("json")["data"]["content"] == "exported"
    assert tools.ticktask_export_focuses("jsonl", "2026-01-01", "2026-01-30")["data"]["content"] == "focus-exported"
    assert tools.ticktask_create_project("Focus", color="#00aa00")["data"]["id"] == "p-new"
    assert tools.ticktask_update_project("p1", name="Renamed")["data"]["name"] == "Renamed"
    assert tools.ticktask_delete_project("p1")["error"]["code"] == "CONFIRMATION_REQUIRED"
    assert tools.ticktask_delete_project("p1", yes=True)["data"]["project_id"] == "p1"
    assert tools.ticktask_add_checklist_item("t1", "p1", "New")["data"]["items"][0]["title"] == "New"
    assert tools.ticktask_update_checklist_item("t1", "p1", "i1", title="Renamed")["data"]["items"][0]["title"] == "Renamed"
    assert tools.ticktask_complete_checklist_item("t1", "p1", "i1")["data"]["items"][0]["status"] == 1
    assert tools.ticktask_delete_checklist_item("t1", "p1", "i1")["error"]["code"] == "CONFIRMATION_REQUIRED"
    assert tools.ticktask_delete_checklist_item("t1", "p1", "i1", yes=True)["data"]["items"] == []
    assert tools.ticktask_list_tasks(tag="agent", filter_preset="high-priority")["data"][0]["tags"] == ["agent"]
    assert tools.ticktask_filter_tasks(tag="agent", priority="high")["data"][0]["id"] == "ft1"
    assert tools.ticktask_add_task_tag("t1", "p1", "agent")["data"]["tags"] == ["agent"]
    assert tools.ticktask_remove_task_tag("t1", "p1", "agent")["data"]["tags"] == []
    assert tools.ticktask_set_task_reminders("t1", "p1", ["TRIGGER:PT10M"])["data"]["raw"]["reminders"] == ["TRIGGER:PT10M"]
    assert tools.ticktask_clear_task_reminders("t1", "p1")["data"]["raw"]["reminders"] == []
    assert tools.ticktask_set_task_repeat("t1", "p1", preset="weekly")["data"]["raw"]["repeatFlag"] == "RRULE:FREQ=WEEKLY"
    assert tools.ticktask_clear_task_repeat("t1", "p1")["data"]["raw"]["repeatFlag"] == ""
    assert tools.ticktask_list_habits()["data"][0]["id"] == "h1"
    assert tools.ticktask_get_habit("h1")["data"]["name"] == "Read"
    assert tools.ticktask_create_habit("Write")["data"]["id"] == "h-new"
    assert tools.ticktask_update_habit("h1", name="Read more")["data"]["name"] == "Read more"
    assert tools.ticktask_checkin_habit("h1", 20260101)["data"]["stamp"] == 20260101
    assert tools.ticktask_habit_checkins(["h1"], 20260101, 20260131)["data"][0]["habitId"] == "h1"
    assert tools.ticktask_list_focuses("2026-01-01", "2026-01-02", focus_type=1)["data"][0]["focus_type"] == 1
    assert tools.ticktask_get_focus("f1", focus_type=0)["data"]["id"] == "f1"
    assert tools.ticktask_delete_focus("f1", focus_type=0)["error"]["code"] == "CONFIRMATION_REQUIRED"
    assert tools.ticktask_delete_focus("f1", focus_type=0, yes=True)["data"]["focus_id"] == "f1"


def test_public_mcp_tool_signatures_are_json_serializable() -> None:
    public_tools = [
        tools.ticktask_describe_tools,
        tools.ticktask_doctor,
        tools.ticktask_auth_status,
        tools.ticktask_list_projects,
        tools.ticktask_list_tasks,
        tools.ticktask_search_tasks,
        tools.ticktask_create_task,
        tools.ticktask_complete_task,
        tools.ticktask_today,
        tools.ticktask_get_task,
        tools.ticktask_update_task,
        tools.ticktask_delete_task,
        tools.ticktask_move_task,
        tools.ticktask_batch_complete_tasks,
        tools.ticktask_batch_delete_tasks,
        tools.ticktask_batch_move_tasks,
        tools.ticktask_set_task_reminders,
        tools.ticktask_clear_task_reminders,
        tools.ticktask_set_task_repeat,
        tools.ticktask_clear_task_repeat,
        tools.ticktask_filter_tasks,
        tools.ticktask_add_task_tag,
        tools.ticktask_remove_task_tag,
        tools.ticktask_cli_parity,
        tools.ticktask_list_habits,
        tools.ticktask_get_habit,
        tools.ticktask_create_habit,
        tools.ticktask_update_habit,
        tools.ticktask_checkin_habit,
        tools.ticktask_habit_checkins,
        tools.ticktask_list_focuses,
        tools.ticktask_get_focus,
        tools.ticktask_delete_focus,
        tools.ticktask_completed,
        tools.ticktask_task_analytics,
        tools.ticktask_export_tasks,
        tools.ticktask_export_focuses,
        tools.ticktask_create_project,
        tools.ticktask_update_project,
        tools.ticktask_delete_project,
        tools.ticktask_add_checklist_item,
        tools.ticktask_update_checklist_item,
        tools.ticktask_complete_checklist_item,
        tools.ticktask_delete_checklist_item,
    ]
    for tool in public_tools:
        assert "service_obj" not in inspect.signature(tool).parameters


def test_build_server_succeeds_when_mcp_is_available() -> None:
    pytest.importorskip("mcp.server.fastmcp")
    build_server()


def test_mcp_missing_package_hint(monkeypatch) -> None:
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "mcp.server.fastmcp":
            raise ImportError("missing mcp")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    try:
        build_server()
    except RuntimeError as exc:
        assert INSTALL_HINT in str(exc)
    else:
        raise AssertionError("expected RuntimeError")



def test_mcp_tool_definitions_are_rich_and_complete() -> None:
    definitions = tools.ticktask_describe_tools()["data"]
    public_tool_names = {
        name
        for name, value in vars(tools).items()
        if name.startswith("ticktask_") and callable(value) and name != "ticktask_describe_tools"
    }
    assert set(definitions) == public_tool_names

    for name, definition in definitions.items():
        assert definition["name"] == name
        assert definition["description"]
        assert definition["cli_command"]
        assert definition["examples"]
        for example in definition["examples"]:
            assert "arguments" in example
            assert "description" in example

    assert definitions["ticktask_list_tasks"]["parameters"]["status"]["enum"] == ["open", "completed", "all"]
    assert definitions["ticktask_list_tasks"]["parameters"]["filter_preset"]["enum"] == [
        "today",
        "overdue",
        "upcoming",
        "high-priority",
        "no-date",
    ]
    assert definitions["ticktask_create_task"]["parameters"]["priority"]["enum"] == [
        "none",
        "low",
        "medium",
        "high",
    ]
    assert definitions["ticktask_export_tasks"]["parameters"]["output_format"]["enum"] == [
        "json",
        "jsonl",
        "csv",
        "markdown",
    ]
    assert definitions["ticktask_export_focuses"]["parameters"]["output_format"]["enum"] == [
        "json",
        "jsonl",
        "csv",
        "markdown",
    ]
    assert definitions["ticktask_set_task_repeat"]["parameters"]["preset"]["enum"] == [
        "daily",
        "weekly",
        "monthly",
        "yearly",
    ]
    assert definitions["ticktask_batch_delete_tasks"]["confirmation_required"] is True
    assert definitions["ticktask_batch_delete_tasks"]["destructive"] is True
    assert definitions["ticktask_task_analytics"]["cli_command"] == "ticktask task analytics"
    assert definitions["ticktask_task_analytics"]["destructive"] is False
    assert definitions["ticktask_task_analytics"]["parameters"]["period"]["enum"] == ["today", "yesterday", "week"]
    assert definitions["ticktask_delete_task"]["confirmation_required"] is True
    assert definitions["ticktask_delete_checklist_item"]["confirmation_required"] is True


def test_mcp_cli_parity_matrix_groups_tools_by_cli_command() -> None:
    matrix = tools.ticktask_cli_parity()["data"]
    commands = {row["cli_command"] for row in matrix}
    assert "ticktask project list" in commands
    assert "ticktask task list" in commands
    assert "ticktask task tag add" in commands
    assert "ticktask task batch complete" in commands
    assert "ticktask task batch delete" in commands
    assert "ticktask task batch move" in commands
    assert "ticktask task item delete" in commands
    assert "ticktask task reminder set" in commands
    assert "ticktask task repeat set" in commands
    assert "ticktask export tasks" in commands
    assert "ticktask export focus" in commands
    assert all(row["mcp_tool"].startswith("ticktask_") for row in matrix)
    assert all(row["examples"] for row in matrix)


