from __future__ import annotations

from collections.abc import Callable
from datetime import date, datetime
from typing import Any

from ticktask.core.auth import AuthManager
from ticktask.core.client import TicktaskClient
from ticktask.core.config import ProfileConfig
from ticktask.core.dates import parse_date_range
from ticktask.core.errors import (
    AmbiguousOperationError,
    ConfirmationRequiredError,
    NotFoundError,
    ValidationError,
)
from ticktask.core.exporters import serialize_tasks
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
        start_date: str | date | datetime | None = None,
        end_date: str | date | datetime | None = None,
    ) -> list[dict[str, Any]]:
        client = self._with_client()
        try:
            projects = [Project.from_api(item) for item in client.list_projects()]
            selected = self._select_projects(projects, project)
            tasks: list[Task] = []
            if status == "completed":
                completed_range = parse_date_range(
                    from_date=str(start_date) if start_date is not None else None,
                    to_date=str(end_date) if end_date is not None else None,
                )
                if project:
                    project_ids = [item.id for item in selected]
                    data = client.completed_tasks(
                        start_date=completed_range.start,
                        end_date=completed_range.end,
                        project_ids=project_ids,
                    )
                    project_id = project_ids[0] if len(project_ids) == 1 else None
                    for raw_task in self._extract_tasks(data):
                        tasks.append(Task.from_api(raw_task, project_id=project_id))
                else:
                    data = client.completed_tasks(
                        start_date=completed_range.start,
                        end_date=completed_range.end,
                    )
                    for raw_task in self._extract_tasks(data):
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

    def completed_tasks(
        self,
        preset: str | None = None,
        start_date: str | date | datetime | None = None,
        end_date: str | date | datetime | None = None,
        project: str | None = None,
    ) -> list[dict[str, Any]]:
        range_ = parse_date_range(
            preset,
            str(start_date) if start_date is not None else None,
            str(end_date) if end_date is not None else None,
        )
        return self.list_tasks(
            project=project,
            status="completed",
            start_date=range_.start,
            end_date=range_.end,
        )

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

    def get_task(self, task_id: str, project_id: str) -> dict[str, Any]:
        if not project_id:
            raise AmbiguousOperationError("Getting a task requires `project_id`.")
        client = self._with_client()
        try:
            return Task.from_api(client.get_task(project_id, task_id), project_id=project_id).to_dict()
        finally:
            client.close()

    def update_task(
        self,
        task_id: str,
        project_id: str,
        title: str | None = None,
        content: str | None = None,
        due: str | None = None,
        priority: str | None = None,
    ) -> dict[str, Any]:
        if not project_id:
            raise AmbiguousOperationError("Updating a task requires `project_id`.")
        payload: dict[str, Any] = {"id": task_id, "projectId": project_id}
        if title is not None:
            payload["title"] = title
        if content is not None:
            payload["content"] = content
        if due is not None:
            payload["dueDate"] = due
        if priority is not None:
            if priority not in PRIORITY_MAP:
                raise ValidationError(
                    f"Unknown priority `{priority}`.",
                    hint="Use one of: none, low, medium, high.",
                )
            payload["priority"] = PRIORITY_MAP[priority]
        if len(payload) == 2:
            raise ValidationError("Updating a task requires at least one changed field.")

        client = self._with_client()
        try:
            return Task.from_api(client.update_task(task_id, payload), project_id=project_id).to_dict()
        finally:
            client.close()

    def delete_task(self, task_id: str, project_id: str, confirmed: bool) -> dict[str, Any]:
        if not confirmed:
            raise ConfirmationRequiredError("Deleting a task requires explicit confirmation.")
        if not project_id:
            raise AmbiguousOperationError("Deleting a task requires `project_id`.")
        client = self._with_client()
        try:
            result = client.delete_task(project_id, task_id)
            return {"task_id": task_id, "project_id": project_id, "result": result}
        finally:
            client.close()

    def move_task(self, task_id: str, from_project_id: str, to_project_id: str) -> dict[str, Any]:
        if not from_project_id or not to_project_id:
            raise AmbiguousOperationError("Moving a task requires source and destination project IDs.")
        client = self._with_client()
        try:
            result = client.move_task(task_id, from_project_id, to_project_id)
            return {
                "task_id": task_id,
                "from_project_id": from_project_id,
                "to_project_id": to_project_id,
                "result": result,
            }
        finally:
            client.close()

    def export_tasks(
        self,
        output_format: str,
        project: str | None = None,
        status: str = "open",
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> str:
        if status == "completed":
            tasks = self.completed_tasks(start_date=start_date, end_date=end_date, project=project)
        elif status == "all":
            open_tasks = self.list_tasks(project=project, status="open")
            completed_tasks = self.completed_tasks(
                start_date=start_date,
                end_date=end_date,
                project=project,
            )
            tasks_by_key = {
                (task.get("project_id"), task.get("id")): task
                for task in [*open_tasks, *completed_tasks]
            }
            tasks = list(tasks_by_key.values())
        else:
            tasks = self.list_tasks(
                project=project,
                status=status,
                start_date=start_date,
                end_date=end_date,
            )
        return serialize_tasks(tasks, output_format)

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
