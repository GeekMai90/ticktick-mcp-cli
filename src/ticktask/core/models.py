from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


def _first(raw: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = raw.get(key)
        if value is not None:
            return value
    return None


@dataclass
class Project:
    id: str
    name: str
    raw: dict[str, Any]

    @classmethod
    def from_api(cls, raw: dict[str, Any]) -> Project:
        project_id = str(_first(raw, "id", "projectId") or "")
        name = str(_first(raw, "name", "title") or project_id)
        return cls(id=project_id, name=name, raw=raw)

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "name": self.name, "raw": self.raw}


@dataclass
class Task:
    id: str
    project_id: str | None
    title: str
    content: str | None
    status: int | str | None
    due_date: str | None
    priority: int | str | None
    kind: str | None
    items: list[dict[str, Any]]
    tags: list[str]
    reminders: list[str]
    repeat_flag: str | None
    raw: dict[str, Any]

    @classmethod
    def from_api(cls, raw: dict[str, Any], project_id: str | None = None) -> Task:
        task_id = str(_first(raw, "id", "taskId") or "")
        resolved_project_id = _first(raw, "projectId", "project_id") or project_id
        content = _first(raw, "content", "desc", "description")
        return cls(
            id=task_id,
            project_id=str(resolved_project_id) if resolved_project_id else None,
            title=str(_first(raw, "title", "name") or task_id),
            content=str(content) if content is not None else None,
            status=_first(raw, "status"),
            due_date=_first(raw, "dueDate", "due_date", "startDate"),
            priority=_first(raw, "priority"),
            kind=_first(raw, "kind"),
            items=list(raw.get("items") or []),
            tags=[str(tag) for tag in (raw.get("tags") or []) if tag is not None],
            reminders=[str(reminder) for reminder in (raw.get("reminders") or []) if reminder is not None],
            repeat_flag=_first(raw, "repeatFlag", "repeat_flag"),
            raw=raw,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def is_completed(self) -> bool:
        return self.status in {2, "2", "completed", "done"}


@dataclass
class Habit:
    id: str
    name: str
    status: int | str | None
    total_checkins: int | None
    raw: dict[str, Any]

    @classmethod
    def from_api(cls, raw: dict[str, Any]) -> Habit:
        habit_id = str(_first(raw, "id", "habitId") or "")
        total = _first(raw, "totalCheckIns", "total_checkins")
        return cls(
            id=habit_id,
            name=str(_first(raw, "name", "title") or habit_id),
            status=_first(raw, "status"),
            total_checkins=int(total) if total is not None else None,
            raw=raw,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Focus:
    id: str
    focus_type: int | None
    task_id: str | None
    start_time: str | None
    end_time: str | None
    duration: int | None
    raw: dict[str, Any]

    @classmethod
    def from_api(cls, raw: dict[str, Any]) -> Focus:
        focus_id = str(_first(raw, "id", "focusId") or "")
        duration = _first(raw, "duration")
        focus_type = _first(raw, "type", "focus_type")
        return cls(
            id=focus_id,
            focus_type=int(focus_type) if focus_type is not None else None,
            task_id=str(_first(raw, "taskId", "task_id")) if _first(raw, "taskId", "task_id") is not None else None,
            start_time=_first(raw, "startTime", "start_time"),
            end_time=_first(raw, "endTime", "end_time"),
            duration=int(duration) if duration is not None else None,
            raw=raw,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


PRIORITY_MAP = {
    "none": 0,
    "low": 1,
    "medium": 3,
    "high": 5,
}

