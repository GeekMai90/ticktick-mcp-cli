from __future__ import annotations

from collections.abc import Callable
from datetime import date
from typing import Any

from ticktask.core.auth import AuthManager
from ticktask.core.client import TicktaskClient
from ticktask.core.config import ProfileConfig
from ticktask.core.errors import (
    AmbiguousOperationError,
    ConfirmationRequiredError,
    NotFoundError,
)
from ticktask.core.models import PRIORITY_MAP, Project, Task


ClientFactory = Callable[[ProfileConfig], TicktaskClient]


def default_client_factory(profile: ProfileConfig) -> TicktaskClient:
    return TicktaskClient(profile.base_url, profile.access_token or "")


class TicktaskService:
    def __init__(
        self,
        auth: AuthManager | None = None,
        service: str | None = None,
        client_factory: ClientFactory | None = None,
    ) -> None:
        self.auth = auth or AuthManager()
        self.service = service
        self.client_factory = client_factory or default_client_factory

    def _with_client(self) -> TicktaskClient:
        profile = self.auth.require_token(self.service)
        return self.client_factory(profile)

    def list_projects(self) -> list[dict[str, Any]]:
        client = self._with_client()
        try:
            return [Project.from_api(item).to_dict() for item in client.list_projects()]
        finally:
            client.close()

    def get_project_data(self, project_id: str) -> dict[str, Any]:
        client = self._with_client()
        try:
            return client.project_data(project_id)
        finally:
            client.close()

    def list_tasks(
        self,
        project: str | None = None,
        status: str = "open",
        today_only: bool = False,
    ) -> list[dict[str, Any]]:
        client = self._with_client()
        try:
            projects = [Project.from_api(item) for item in client.list_projects()]
            selected = self._select_projects(projects, project)
            tasks: list[Task] = []
            if status == "completed":
                if project:
                    for item in selected:
                        data = client.completed_tasks(item.id)
                        for raw_task in self._extract_tasks(data):
                            tasks.append(Task.from_api(raw_task, project_id=item.id))
                else:
                    for raw_task in self._extract_tasks(client.completed_tasks()):
                        tasks.append(Task.from_api(raw_task))
            else:
                for item in selected:
                    data = client.project_data(item.id)
                    for raw_task in self._extract_tasks(data):
                        tasks.append(Task.from_api(raw_task, project_id=item.id))
            if status == "open":
                tasks = [task for task in tasks if not task.is_completed()]
            elif status == "completed":
                pass
            elif status != "all":
                raise NotFoundError(f"Unknown task status filter `{status}`.")
            if today_only:
                today = date.today().isoformat()
                tasks = [task for task in tasks if task.due_date and task.due_date[:10] == today]
            return [task.to_dict() for task in tasks]
        finally:
            client.close()

    def search_tasks(self, query: str, status: str = "all") -> list[dict[str, Any]]:
        needle = query.casefold()
        tasks = [
            Task.from_api(task)
            for task in self.list_tasks(project=None, status=status)
            if needle in (task.get("title") or "").casefold()
            or needle in (task.get("content") or "").casefold()
            or needle in (task.get("id") or "").casefold()
        ]
        return [task.to_dict() for task in tasks]

    def create_task(
        self,
        title: str,
        project: str | None = None,
        content: str | None = None,
        due: str | None = None,
        priority: str = "none",
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"title": title}
        if content:
            payload["content"] = content
        if due:
            payload["dueDate"] = due
        if priority:
            payload["priority"] = PRIORITY_MAP.get(priority, 0)

        client = self._with_client()
        try:
            if project:
                projects = [Project.from_api(item) for item in client.list_projects()]
                selected = self._select_one_project(projects, project)
                payload["projectId"] = selected.id
            return Task.from_api(client.create_task(payload), payload.get("projectId")).to_dict()
        finally:
            client.close()

    def complete_task(self, task_id: str, project_id: str, confirmed: bool) -> dict[str, Any]:
        if not confirmed:
            raise ConfirmationRequiredError("Completing a task requires explicit confirmation.")
        if not project_id:
            raise AmbiguousOperationError("Completing a task requires `project_id`.")
        client = self._with_client()
        try:
            result = client.complete_task(project_id, task_id)
            return {"task_id": task_id, "project_id": project_id, "result": result}
        finally:
            client.close()

    @staticmethod
    def _extract_tasks(data: Any) -> list[dict[str, Any]]:
        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]
        if not isinstance(data, dict):
            return []
        tasks: list[dict[str, Any]] = []
        for key in ("tasks", "task", "items"):
            values = data.get(key)
            if isinstance(values, list):
                tasks.extend(item for item in values if isinstance(item, dict))
        columns = data.get("columns")
        if isinstance(columns, list):
            for column in columns:
                if isinstance(column, dict) and isinstance(column.get("tasks"), list):
                    tasks.extend(item for item in column["tasks"] if isinstance(item, dict))
        return tasks

    @staticmethod
    def _select_projects(projects: list[Project], value: str | None) -> list[Project]:
        if not value:
            return projects
        return [TicktaskService._select_one_project(projects, value)]

    @staticmethod
    def _select_one_project(projects: list[Project], value: str) -> Project:
        exact = [item for item in projects if item.id == value or item.name == value]
        if len(exact) == 1:
            return exact[0]
        if len(exact) > 1:
            raise AmbiguousOperationError(f"Project `{value}` matches multiple projects.")
        fuzzy = [item for item in projects if value.casefold() in item.name.casefold()]
        if len(fuzzy) == 1:
            return fuzzy[0]
        if len(fuzzy) > 1:
            names = ", ".join(project.name for project in fuzzy)
            raise AmbiguousOperationError(
                f"Project `{value}` is ambiguous.",
                hint=f"Use a project ID. Matches: {names}.",
            )
        raise NotFoundError(f"Project `{value}` was not found.")
