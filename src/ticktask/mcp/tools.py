from __future__ import annotations

from typing import Any

from ticktask.core.auth import AuthManager
from ticktask.core.config import ConfigStore
from ticktask.core.results import err, ok
from ticktask.core.services import TicktaskService


def _make_service() -> TicktaskService:
    return TicktaskService()


def ticktask_doctor() -> dict[str, Any]:
    try:
        store = ConfigStore()
        status = AuthManager(store).status()
        return ok(
            {
                "config_path": store.path_string(),
                "service": status.service,
                "base_url": status.base_url,
                "configured": status.configured,
                "authenticated": status.authenticated,
            }
        )
    except Exception as exc:
        return err(exc)


def ticktask_auth_status(service: str | None = None) -> dict[str, Any]:
    try:
        return ok(AuthManager().status(service).to_dict())
    except Exception as exc:
        return err(exc)


def ticktask_list_projects() -> dict[str, Any]:
    try:
        projects = _make_service().list_projects()
        return ok(projects, {"count": len(projects)})
    except Exception as exc:
        return err(exc)


def ticktask_list_tasks(
    project: str | None = None,
    status: str = "open",
) -> dict[str, Any]:
    try:
        tasks = _make_service().list_tasks(project=project, status=status)
        return ok(tasks, {"count": len(tasks)})
    except Exception as exc:
        return err(exc)


def ticktask_search_tasks(
    query: str,
) -> dict[str, Any]:
    try:
        tasks = _make_service().search_tasks(query)
        return ok(tasks, {"count": len(tasks), "query": query})
    except Exception as exc:
        return err(exc)


def ticktask_create_task(
    title: str,
    project: str | None = None,
    content: str | None = None,
    due: str | None = None,
    priority: str = "none",
) -> dict[str, Any]:
    try:
        task = _make_service().create_task(title, project, content, due, priority)
        return ok(task)
    except Exception as exc:
        return err(exc)


def ticktask_complete_task(
    task_id: str,
    project_id: str,
    yes: bool = False,
) -> dict[str, Any]:
    try:
        result = _make_service().complete_task(
            task_id=task_id,
            project_id=project_id,
            confirmed=yes,
        )
        return ok(result)
    except Exception as exc:
        return err(exc)


def ticktask_today() -> dict[str, Any]:
    try:
        tasks = _make_service().list_tasks(status="open", today_only=True)
        return ok(tasks, {"count": len(tasks)})
    except Exception as exc:
        return err(exc)
