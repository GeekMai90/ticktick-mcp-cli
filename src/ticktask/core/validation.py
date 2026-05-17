from __future__ import annotations

from datetime import date, timedelta

from ticktask.core.errors import ValidationError

_PRIORITY_ALIASES = {
    "none": "none",
    "normal": "none",
    "0": "none",
    "low": "low",
    "p3": "low",
    "1": "low",
    "medium": "medium",
    "med": "medium",
    "p2": "medium",
    "3": "medium",
    "high": "high",
    "p1": "high",
    "5": "high",
}

_TASK_STATUS_ALIASES = {
    "open": "open",
    "todo": "open",
    "active": "open",
    "0": "open",
    "completed": "completed",
    "complete": "completed",
    "done": "completed",
    "2": "completed",
    "all": "all",
    "any": "all",
}

_PROJECT_KIND_ALIASES = {
    "task": "TASK",
    "tasks": "TASK",
    "todo": "TASK",
    "note": "NOTE",
    "notes": "NOTE",
}

_VIEW_MODE_ALIASES = {
    "list": "list",
    "kanban": "kanban",
    "timeline": "timeline",
}

_WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


def normalize_task_date(value: str | date | None, *, today: date | None = None) -> str | None:
    if value is None:
        return None
    if isinstance(value, date):
        return value.isoformat()
    raw = value.strip()
    if not raw:
        raise ValidationError("Date value cannot be empty.")
    lowered = raw.casefold()
    base = today or date.today()
    if lowered == "today":
        return base.isoformat()
    if lowered == "tomorrow":
        return (base + timedelta(days=1)).isoformat()
    if lowered.startswith("next "):
        weekday_name = lowered.removeprefix("next ").strip()
        if weekday_name in _WEEKDAYS:
            return _next_weekday(base, _WEEKDAYS[weekday_name]).isoformat()
    try:
        return date.fromisoformat(raw).isoformat()
    except ValueError as exc:
        raise ValidationError(
            f"Unsupported date value `{value}`.",
            hint="Use YYYY-MM-DD, today, tomorrow, or next <weekday>.",
        ) from exc


def normalize_priority(value: str | None) -> str | None:
    return _normalize_choice(
        value,
        _PRIORITY_ALIASES,
        "priority",
        "Use one of: none, low, medium, high.",
    )


def normalize_task_status(value: str | None) -> str | None:
    return _normalize_choice(
        value,
        _TASK_STATUS_ALIASES,
        "task status",
        "Use one of: open, completed, all.",
    )


def normalize_project_kind(value: str | None) -> str | None:
    return _normalize_choice(
        value,
        _PROJECT_KIND_ALIASES,
        "project kind",
        "Use one of: TASK, NOTE.",
    )


def normalize_view_mode(value: str | None) -> str | None:
    return _normalize_choice(
        value,
        _VIEW_MODE_ALIASES,
        "view mode",
        "Use one of: list, kanban, timeline.",
    )


def _normalize_choice(
    value: str | None,
    aliases: dict[str, str],
    label: str,
    hint: str,
) -> str | None:
    if value is None:
        return None
    raw = value.strip()
    if not raw:
        raise ValidationError(f"{label.capitalize()} cannot be empty.", hint=hint)
    normalized = aliases.get(raw.casefold())
    if normalized is None:
        raise ValidationError(f"Unknown {label} `{value}`.", hint=hint)
    return normalized


def _next_weekday(base: date, weekday: int) -> date:
    days_ahead = (weekday - base.weekday()) % 7
    if days_ahead == 0:
        days_ahead = 7
    return base + timedelta(days=days_ahead)
