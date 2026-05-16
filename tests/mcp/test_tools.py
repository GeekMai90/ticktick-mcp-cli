import inspect

import pytest

from ticktask.mcp import tools
from ticktask.mcp.server import INSTALL_HINT, build_server


class FakeService:
    def list_projects(self):
        return [{"id": "p1", "name": "Inbox"}]

    def list_tasks(self, project=None, status="open", today_only=False):
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
