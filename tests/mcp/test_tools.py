import inspect

import pytest

from ticktask.mcp import tools
from ticktask.mcp.server import INSTALL_HINT, build_server


class FakeService:
    def list_projects(self):
        return [{"id": "p1", "name": "Inbox"}]

    def list_tasks(self, project=None, status="open", today_only=False, start_date=None, end_date=None):
        return [{"id": "t1", "title": "Task", "project_id": "p1"}]

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

    def delete_task(self, task_id, project_id, confirmed):
        if not confirmed:
            from ticktask.core.errors import ConfirmationRequiredError

            raise ConfirmationRequiredError("confirm")
        return {"task_id": task_id, "project_id": project_id}

    def move_task(self, task_id, from_project_id, to_project_id):
        return {"task_id": task_id, "to_project_id": to_project_id}

    def completed_tasks(self, preset=None, start_date=None, end_date=None, project=None):
        return [{"id": "t2", "status": 2}]

    def export_tasks(self, output_format, project=None, status="open", start_date=None, end_date=None):
        return "exported"


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
    assert tools.ticktask_completed(period="today")["meta"]["count"] == 1
    assert tools.ticktask_export_tasks("json")["data"]["content"] == "exported"


def test_public_mcp_tool_signatures_are_json_serializable() -> None:
    public_tools = [
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
        tools.ticktask_completed,
        tools.ticktask_export_tasks,
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
