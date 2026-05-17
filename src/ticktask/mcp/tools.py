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


def ticktask_create_project(
    name: str,
    color: str | None = None,
    sort_order: int | None = None,
    view_mode: str | None = None,
    kind: str | None = None,
) -> dict[str, Any]:
    try:
        return ok(
            _make_service().create_project(
                name=name,
                color=color,
                sort_order=sort_order,
                view_mode=view_mode,
                kind=kind,
            )
        )
    except Exception as exc:
        return err(exc)


def ticktask_update_project(
    project_id: str,
    name: str | None = None,
    color: str | None = None,
    sort_order: int | None = None,
    view_mode: str | None = None,
    kind: str | None = None,
    closed: bool | None = None,
) -> dict[str, Any]:
    try:
        return ok(
            _make_service().update_project(
                project_id=project_id,
                name=name,
                color=color,
                sort_order=sort_order,
                view_mode=view_mode,
                kind=kind,
                closed=closed,
            )
        )
    except Exception as exc:
        return err(exc)


def ticktask_delete_project(project_id: str, yes: bool = False) -> dict[str, Any]:
    try:
        return ok(_make_service().delete_project(project_id=project_id, confirmed=yes))
    except Exception as exc:
        return err(exc)

def ticktask_list_tasks(
    project: str | None = None,
    status: str = "open",
    start_date: str | None = None,
    end_date: str | None = None,
    tag: str | None = None,
    filter_preset: str | None = None,
) -> dict[str, Any]:
    try:
        tasks = _make_service().list_tasks(
            project=project,
            status=status,
            start_date=start_date,
            end_date=end_date,
            tag=tag,
            filter_preset=filter_preset,
        )
        return ok(tasks, {"count": len(tasks)})
    except Exception as exc:
        return err(exc)


def ticktask_filter_tasks(
    tag: str | None = None,
    project: str | None = None,
    status: str = "open",
    priority: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict[str, Any]:
    try:
        tasks = _make_service().filter_tasks(
            tag=tag,
            project=project,
            status=status,
            priority=priority,
            start_date=start_date,
            end_date=end_date,
        )
        return ok(tasks, {"count": len(tasks)})
    except Exception as exc:
        return err(exc)


def ticktask_add_task_tag(task_id: str, project_id: str, tag: str) -> dict[str, Any]:
    try:
        return ok(_make_service().add_task_tag(task_id=task_id, project_id=project_id, tag=tag))
    except Exception as exc:
        return err(exc)


def ticktask_remove_task_tag(task_id: str, project_id: str, tag: str) -> dict[str, Any]:
    try:
        return ok(_make_service().remove_task_tag(task_id=task_id, project_id=project_id, tag=tag))
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


def ticktask_get_task(task_id: str, project_id: str) -> dict[str, Any]:
    try:
        return ok(_make_service().get_task(task_id=task_id, project_id=project_id))
    except Exception as exc:
        return err(exc)


def ticktask_update_task(
    task_id: str,
    project_id: str,
    title: str | None = None,
    content: str | None = None,
    due: str | None = None,
    priority: str | None = None,
) -> dict[str, Any]:
    try:
        return ok(
            _make_service().update_task(
                task_id=task_id,
                project_id=project_id,
                title=title,
                content=content,
                due=due,
                priority=priority,
            )
        )
    except Exception as exc:
        return err(exc)


def ticktask_delete_task(task_id: str, project_id: str, yes: bool = False) -> dict[str, Any]:
    try:
        return ok(_make_service().delete_task(task_id=task_id, project_id=project_id, confirmed=yes))
    except Exception as exc:
        return err(exc)


def ticktask_move_task(task_id: str, from_project_id: str, to_project_id: str) -> dict[str, Any]:
    try:
        return ok(
            _make_service().move_task(
                task_id=task_id,
                from_project_id=from_project_id,
                to_project_id=to_project_id,
            )
        )
    except Exception as exc:
        return err(exc)




def ticktask_add_checklist_item(task_id: str, project_id: str, title: str) -> dict[str, Any]:
    try:
        return ok(_make_service().add_checklist_item(task_id=task_id, project_id=project_id, title=title))
    except Exception as exc:
        return err(exc)


def ticktask_update_checklist_item(
    task_id: str,
    project_id: str,
    item_id: str,
    title: str | None = None,
    status: str | int | None = None,
) -> dict[str, Any]:
    try:
        return ok(
            _make_service().update_checklist_item(
                task_id=task_id,
                project_id=project_id,
                item_id=item_id,
                title=title,
                status=status,
            )
        )
    except Exception as exc:
        return err(exc)


def ticktask_complete_checklist_item(task_id: str, project_id: str, item_id: str) -> dict[str, Any]:
    try:
        return ok(
            _make_service().complete_checklist_item(
                task_id=task_id,
                project_id=project_id,
                item_id=item_id,
            )
        )
    except Exception as exc:
        return err(exc)


def ticktask_delete_checklist_item(
    task_id: str,
    project_id: str,
    item_id: str,
    yes: bool = False,
) -> dict[str, Any]:
    try:
        return ok(
            _make_service().delete_checklist_item(
                task_id=task_id,
                project_id=project_id,
                item_id=item_id,
                confirmed=yes,
            )
        )
    except Exception as exc:
        return err(exc)

def ticktask_completed(
    period: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    project: str | None = None,
) -> dict[str, Any]:
    try:
        tasks = _make_service().completed_tasks(
            preset=period,
            start_date=start_date,
            end_date=end_date,
            project=project,
        )
        return ok(tasks, {"count": len(tasks)})
    except Exception as exc:
        return err(exc)


def ticktask_export_tasks(
    output_format: str,
    project: str | None = None,
    status: str = "open",
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict[str, Any]:
    try:
        content = _make_service().export_tasks(
            output_format=output_format,
            project=project,
            status=status,
            start_date=start_date,
            end_date=end_date,
        )
        return ok({"format": output_format, "content": content})
    except Exception as exc:
        return err(exc)






def ticktask_export_focuses(
    output_format: str,
    from_time: str,
    to_time: str,
    focus_type: int = 0,
) -> dict[str, Any]:
    try:
        content = _make_service().export_focuses(
            output_format=output_format,
            from_time=from_time,
            to_time=to_time,
            focus_type=focus_type,
        )
        return ok({"format": output_format, "content": content})
    except Exception as exc:
        return err(exc)


def ticktask_list_habits() -> dict[str, Any]:
    try:
        habits = _make_service().list_habits()
        return ok(habits, {"count": len(habits)})
    except Exception as exc:
        return err(exc)


def ticktask_get_habit(habit_id: str) -> dict[str, Any]:
    try:
        return ok(_make_service().get_habit(habit_id))
    except Exception as exc:
        return err(exc)


def ticktask_create_habit(
    name: str,
    goal: int | None = None,
    step: int | None = None,
    unit: str | None = None,
    repeat_rule: str | None = None,
) -> dict[str, Any]:
    try:
        return ok(_make_service().create_habit(name, goal=goal, step=step, unit=unit, repeat_rule=repeat_rule))
    except Exception as exc:
        return err(exc)


def ticktask_update_habit(
    habit_id: str,
    name: str | None = None,
    goal: int | None = None,
    step: int | None = None,
    unit: str | None = None,
    repeat_rule: str | None = None,
) -> dict[str, Any]:
    try:
        return ok(_make_service().update_habit(habit_id, name=name, goal=goal, step=step, unit=unit, repeat_rule=repeat_rule))
    except Exception as exc:
        return err(exc)


def ticktask_checkin_habit(habit_id: str, stamp: int, value: int = 1) -> dict[str, Any]:
    try:
        return ok(_make_service().checkin_habit(habit_id, stamp=stamp, value=value))
    except Exception as exc:
        return err(exc)


def ticktask_habit_checkins(habit_ids: list[str], from_stamp: int, to_stamp: int) -> dict[str, Any]:
    try:
        history = _make_service().habit_checkins(habit_ids, from_stamp=from_stamp, to_stamp=to_stamp)
        return ok(history, {"count": len(history)})
    except Exception as exc:
        return err(exc)


def ticktask_list_focuses(from_time: str, to_time: str, focus_type: int = 0) -> dict[str, Any]:
    try:
        focuses = _make_service().list_focuses(from_time=from_time, to_time=to_time, focus_type=focus_type)
        return ok(focuses, {"count": len(focuses)})
    except Exception as exc:
        return err(exc)


def ticktask_get_focus(focus_id: str, focus_type: int = 0) -> dict[str, Any]:
    try:
        return ok(_make_service().get_focus(focus_id=focus_id, focus_type=focus_type))
    except Exception as exc:
        return err(exc)


def ticktask_delete_focus(focus_id: str, focus_type: int = 0, yes: bool = False) -> dict[str, Any]:
    try:
        return ok(_make_service().delete_focus(focus_id=focus_id, focus_type=focus_type, confirmed=yes))
    except Exception as exc:
        return err(exc)


# Rich MCP metadata ---------------------------------------------------------
# FastMCP can infer JSON schemas from Python signatures. This registry adds the
# agent-facing layer that plain signatures cannot express well: CLI parity,
# examples, enum hints, and confirmation/destructive-operation notes.

_STATUS_ENUM = ["open", "completed", "all"]
_PRIORITY_ENUM = ["none", "low", "medium", "high"]
_FILTER_PRESET_ENUM = ["today", "overdue", "upcoming", "high-priority", "no-date"]
_CHECKLIST_STATUS_ENUM = ["open", "completed"]
_PERIOD_ENUM = ["today", "yesterday", "week"]
_EXPORT_FORMAT_ENUM = ["json", "jsonl", "csv", "markdown"]
_SERVICE_ENUM = ["ticktick", "dida365"]
_VIEW_MODE_ENUM = ["list", "kanban", "timeline"]
_PROJECT_KIND_ENUM = ["TASK", "NOTE"]
_FOCUS_TYPE_ENUM = ["0", "1"]

_TOOL_CLI_COMMANDS: dict[str, str] = {
    "ticktask_doctor": "ticktask doctor",
    "ticktask_auth_status": "ticktask auth status",
    "ticktask_list_projects": "ticktask project list",
    "ticktask_create_project": "ticktask project create",
    "ticktask_update_project": "ticktask project update",
    "ticktask_delete_project": "ticktask project delete",
    "ticktask_list_tasks": "ticktask task list",
    "ticktask_filter_tasks": "ticktask task filter",
    "ticktask_search_tasks": "ticktask task search",
    "ticktask_create_task": "ticktask task add",
    "ticktask_complete_task": "ticktask task complete",
    "ticktask_today": "ticktask today",
    "ticktask_get_task": "ticktask task get",
    "ticktask_update_task": "ticktask task update",
    "ticktask_delete_task": "ticktask task delete",
    "ticktask_move_task": "ticktask task move",
    "ticktask_add_task_tag": "ticktask task tag add",
    "ticktask_remove_task_tag": "ticktask task tag remove",
    "ticktask_add_checklist_item": "ticktask task item add",
    "ticktask_update_checklist_item": "ticktask task item update",
    "ticktask_complete_checklist_item": "ticktask task item complete",
    "ticktask_delete_checklist_item": "ticktask task item delete",
    "ticktask_completed": "ticktask completed",
    "ticktask_list_habits": "ticktask habit list",
    "ticktask_get_habit": "ticktask habit get",
    "ticktask_create_habit": "ticktask habit create",
    "ticktask_update_habit": "ticktask habit update",
    "ticktask_checkin_habit": "ticktask habit checkin",
    "ticktask_habit_checkins": "ticktask habit history",
    "ticktask_list_focuses": "ticktask focus list",
    "ticktask_get_focus": "ticktask focus get",
    "ticktask_delete_focus": "ticktask focus delete",
    "ticktask_export_tasks": "ticktask export tasks",
    "ticktask_export_focuses": "ticktask export focus",
    "ticktask_cli_parity": "ticktask --help",
}

_TOOL_DESCRIPTIONS: dict[str, str] = {
    "ticktask_doctor": "Return local configuration and authentication health for the active TickTick/Dida365 profile.",
    "ticktask_auth_status": "Return OAuth configuration and token status for a service profile without exposing secrets.",
    "ticktask_list_projects": "List projects available to the authenticated account.",
    "ticktask_create_project": "Create a project/list. Use exact returned IDs for later mutations.",
    "ticktask_update_project": "Update project metadata by exact project ID.",
    "ticktask_delete_project": "Delete a project by exact project ID; requires yes=true confirmation.",
    "ticktask_list_tasks": "List tasks from one or all projects, with local status/tag/smart-filter constraints.",
    "ticktask_filter_tasks": "Filter tasks using the official Open API filter endpoint.",
    "ticktask_search_tasks": "Search listed tasks by title, content, or ID.",
    "ticktask_create_task": "Create a task, optionally resolving a project name/ID and priority.",
    "ticktask_complete_task": "Complete a task by exact task/project IDs; requires yes=true confirmation.",
    "ticktask_today": "List open tasks due today.",
    "ticktask_get_task": "Get one task by exact task/project IDs.",
    "ticktask_update_task": "Update task fields by exact task/project IDs.",
    "ticktask_delete_task": "Delete a task by exact task/project IDs; requires yes=true confirmation.",
    "ticktask_move_task": "Move a task between projects by exact source/destination project IDs.",
    "ticktask_add_task_tag": "Add one tag to a task by exact task/project IDs.",
    "ticktask_remove_task_tag": "Remove one tag from a task by exact task/project IDs.",
    "ticktask_add_checklist_item": "Append a checklist item/subtask to a CHECKLIST task.",
    "ticktask_update_checklist_item": "Update a checklist item title and/or status by exact item ID.",
    "ticktask_complete_checklist_item": "Mark a checklist item/subtask completed by exact item ID.",
    "ticktask_delete_checklist_item": "Delete a checklist item/subtask; requires yes=true confirmation.",
    "ticktask_completed": "List completed tasks for a preset or date range.",
    "ticktask_list_habits": "List habits for the authenticated account.",
    "ticktask_get_habit": "Get one habit by exact habit ID.",
    "ticktask_create_habit": "Create a habit using the official Open API.",
    "ticktask_update_habit": "Update habit metadata by exact habit ID.",
    "ticktask_checkin_habit": "Create or update a habit check-in using YYYYMMDD stamp.",
    "ticktask_habit_checkins": "Query habit check-in history for one or more habit IDs.",
    "ticktask_list_focuses": "List focus sessions for a max 30-day time range.",
    "ticktask_get_focus": "Get one focus session by exact focus ID and type.",
    "ticktask_delete_focus": "Delete a focus session; requires yes=true confirmation.",
    "ticktask_export_tasks": "Export tasks as JSON, JSONL, CSV, or Markdown content.",
    "ticktask_export_focuses": "Export focus sessions as report-friendly JSON, JSONL, CSV, or Markdown content.",
    "ticktask_cli_parity": "Return the MCP-to-CLI parity matrix for agent planning and auditing.",
}

_PARAM_DESCRIPTIONS: dict[str, str] = {
    "service": "Service profile: ticktick for international TickTick, dida365 for China Dida365.",
    "name": "Project name.",
    "color": "Project color as a hex string, for example #00aa00.",
    "sort_order": "Project sort order integer.",
    "view_mode": "Project view mode.",
    "kind": "Project kind.",
    "closed": "Whether the project is archived/closed.",
    "project": "Project name or ID. Mutations still require exact project_id.",
    "project_id": "Exact project ID. Required for task/project-scoped mutations.",
    "task_id": "Exact task ID.",
    "item_id": "Exact checklist item/subtask ID.",
    "from_project_id": "Exact source project ID.",
    "to_project_id": "Exact destination project ID.",
    "title": "Task, project, or checklist item title.",
    "content": "Task body/content.",
    "due": "Due date string accepted by the API.",
    "priority": "Task priority.",
    "status": "Task or checklist status filter/value.",
    "start_date": "Start date, usually YYYY-MM-DD.",
    "end_date": "End date, usually YYYY-MM-DD.",
    "tag": "Tag name. Leading # is accepted and normalized away by mutation helpers.",
    "filter_preset": "Local smart filter for listed tasks.",
    "query": "Search query matched against task title, content, and ID.",
    "period": "Completed-task preset.",
    "output_format": "Export format.",
    "habit_id": "Exact habit ID.",
    "habit_ids": "One or more exact habit IDs.",
    "stamp": "Habit check-in stamp as YYYYMMDD integer.",
    "from_stamp": "Start habit history stamp as YYYYMMDD integer.",
    "to_stamp": "End habit history stamp as YYYYMMDD integer.",
    "value": "Habit check-in value.",
    "goal": "Habit goal value.",
    "step": "Habit step increment.",
    "unit": "Habit unit label.",
    "repeat_rule": "Habit recurrence rule in iCal RRULE format.",
    "focus_id": "Exact focus session ID.",
    "focus_type": "Focus type: 0=Pomodoro, 1=Timing.",
    "from_time": "Focus query start time/date. Max 30-day range.",
    "to_time": "Focus query end time/date. Max 30-day range.",
    "yes": "Explicit confirmation for destructive or irreversible operations.",
}

_PARAM_ENUMS: dict[tuple[str, str] | str, list[str]] = {
    "service": _SERVICE_ENUM,
    "priority": _PRIORITY_ENUM,
    "filter_preset": _FILTER_PRESET_ENUM,
    "period": _PERIOD_ENUM,
    "output_format": _EXPORT_FORMAT_ENUM,
    "view_mode": _VIEW_MODE_ENUM,
    "kind": _PROJECT_KIND_ENUM,
    "focus_type": _FOCUS_TYPE_ENUM,
    ("ticktask_list_tasks", "status"): _STATUS_ENUM,
    ("ticktask_filter_tasks", "status"): _STATUS_ENUM,
    ("ticktask_export_tasks", "status"): _STATUS_ENUM,
    ("ticktask_export_focuses", "output_format"): _EXPORT_FORMAT_ENUM,
    ("ticktask_update_checklist_item", "status"): _CHECKLIST_STATUS_ENUM,
}

_EXAMPLES: dict[str, list[dict[str, Any]]] = {
    "ticktask_doctor": [{"description": "Check local setup", "arguments": {}}],
    "ticktask_auth_status": [{"description": "Check Dida365 auth status", "arguments": {"service": "dida365"}}],
    "ticktask_list_projects": [{"description": "List all projects", "arguments": {}}],
    "ticktask_create_project": [{"description": "Create a list-style project", "arguments": {"name": "Focus", "view_mode": "list", "kind": "TASK"}}],
    "ticktask_update_project": [{"description": "Rename a project", "arguments": {"project_id": "PROJECT_ID", "name": "Renamed"}}],
    "ticktask_delete_project": [{"description": "Delete after exact ID verification", "arguments": {"project_id": "PROJECT_ID", "yes": True}}],
    "ticktask_list_tasks": [{"description": "Open high-priority agent-tagged tasks", "arguments": {"status": "open", "tag": "agent", "filter_preset": "high-priority"}}],
    "ticktask_filter_tasks": [{"description": "Use official filter endpoint", "arguments": {"tag": "agent", "project": "Inbox", "priority": "high", "status": "open"}}],
    "ticktask_search_tasks": [{"description": "Find tasks mentioning release", "arguments": {"query": "release"}}],
    "ticktask_create_task": [{"description": "Create a task in Inbox", "arguments": {"title": "Plan release", "project": "Inbox", "priority": "medium"}}],
    "ticktask_complete_task": [{"description": "Complete after exact target verification", "arguments": {"task_id": "TASK_ID", "project_id": "PROJECT_ID", "yes": True}}],
    "ticktask_today": [{"description": "List open tasks due today", "arguments": {}}],
    "ticktask_get_task": [{"description": "Load a task by exact IDs", "arguments": {"task_id": "TASK_ID", "project_id": "PROJECT_ID"}}],
    "ticktask_update_task": [{"description": "Rename and reprioritize", "arguments": {"task_id": "TASK_ID", "project_id": "PROJECT_ID", "title": "New title", "priority": "high"}}],
    "ticktask_delete_task": [{"description": "Delete after exact target verification", "arguments": {"task_id": "TASK_ID", "project_id": "PROJECT_ID", "yes": True}}],
    "ticktask_move_task": [{"description": "Move to another project", "arguments": {"task_id": "TASK_ID", "from_project_id": "PROJECT_ID", "to_project_id": "OTHER_PROJECT_ID"}}],
    "ticktask_add_task_tag": [{"description": "Add an agent tag", "arguments": {"task_id": "TASK_ID", "project_id": "PROJECT_ID", "tag": "agent"}}],
    "ticktask_remove_task_tag": [{"description": "Remove an agent tag", "arguments": {"task_id": "TASK_ID", "project_id": "PROJECT_ID", "tag": "agent"}}],
    "ticktask_add_checklist_item": [{"description": "Add checklist item", "arguments": {"task_id": "TASK_ID", "project_id": "PROJECT_ID", "title": "Checklist item"}}],
    "ticktask_update_checklist_item": [{"description": "Complete and rename checklist item", "arguments": {"task_id": "TASK_ID", "project_id": "PROJECT_ID", "item_id": "ITEM_ID", "title": "Renamed", "status": "completed"}}],
    "ticktask_complete_checklist_item": [{"description": "Complete checklist item", "arguments": {"task_id": "TASK_ID", "project_id": "PROJECT_ID", "item_id": "ITEM_ID"}}],
    "ticktask_delete_checklist_item": [{"description": "Delete checklist item after verification", "arguments": {"task_id": "TASK_ID", "project_id": "PROJECT_ID", "item_id": "ITEM_ID", "yes": True}}],
    "ticktask_completed": [{"description": "Completed tasks for today", "arguments": {"period": "today"}}],
    "ticktask_list_habits": [{"description": "List habits", "arguments": {}}],
    "ticktask_get_habit": [{"description": "Get habit details", "arguments": {"habit_id": "HABIT_ID"}}],
    "ticktask_create_habit": [{"description": "Create a reading habit", "arguments": {"name": "Read", "goal": 1, "unit": "time"}}],
    "ticktask_update_habit": [{"description": "Rename a habit", "arguments": {"habit_id": "HABIT_ID", "name": "Read more"}}],
    "ticktask_checkin_habit": [{"description": "Check in a habit", "arguments": {"habit_id": "HABIT_ID", "stamp": 20260101, "value": 1}}],
    "ticktask_habit_checkins": [{"description": "Query habit history", "arguments": {"habit_ids": ["HABIT_ID"], "from_stamp": 20260101, "to_stamp": 20260131}}],
    "ticktask_list_focuses": [{"description": "List Pomodoro focus sessions", "arguments": {"from_time": "2026-01-01", "to_time": "2026-01-30", "focus_type": 0}}],
    "ticktask_get_focus": [{"description": "Get focus session details", "arguments": {"focus_id": "FOCUS_ID", "focus_type": 0}}],
    "ticktask_delete_focus": [{"description": "Delete focus session after verification", "arguments": {"focus_id": "FOCUS_ID", "focus_type": 0, "yes": True}}],
    "ticktask_export_tasks": [{"description": "Export all tasks as JSONL", "arguments": {"output_format": "jsonl", "status": "all"}}],
    "ticktask_export_focuses": [{"description": "Export Pomodoro sessions as CSV", "arguments": {"output_format": "csv", "from_time": "2026-01-01", "to_time": "2026-01-30", "focus_type": 0}}],
    "ticktask_cli_parity": [{"description": "Audit MCP and CLI parity", "arguments": {}}],
}

_CONFIRMATION_TOOLS = {
    "ticktask_delete_project",
    "ticktask_complete_task",
    "ticktask_delete_task",
    "ticktask_delete_checklist_item",
    "ticktask_delete_focus",
}

_DESTRUCTIVE_TOOLS = {
    "ticktask_delete_project",
    "ticktask_complete_task",
    "ticktask_delete_task",
    "ticktask_move_task",
    "ticktask_remove_task_tag",
    "ticktask_update_project",
    "ticktask_update_task",
    "ticktask_delete_checklist_item",
    "ticktask_update_checklist_item",
    "ticktask_complete_checklist_item",
    "ticktask_update_habit",
    "ticktask_checkin_habit",
    "ticktask_delete_focus",
}


def _parameter_metadata(tool_name: str) -> dict[str, dict[str, Any]]:
    import inspect

    params: dict[str, dict[str, Any]] = {}
    if tool_name not in globals():
        return params
    for param_name, param in inspect.signature(globals()[tool_name]).parameters.items():
        if param_name.startswith("_"):
            continue
        metadata: dict[str, Any] = {
            "description": _PARAM_DESCRIPTIONS.get(param_name, param_name.replace("_", " ").capitalize()),
            "required": param.default is inspect._empty,
        }
        enum = _PARAM_ENUMS.get((tool_name, param_name)) or _PARAM_ENUMS.get(param_name)
        if enum:
            metadata["enum"] = list(enum)
        params[param_name] = metadata
    return params


def _build_tool_definitions() -> dict[str, dict[str, Any]]:
    definitions: dict[str, dict[str, Any]] = {}
    for name, cli_command in _TOOL_CLI_COMMANDS.items():
        description = _TOOL_DESCRIPTIONS[name]
        definitions[name] = {
            "name": name,
            "description": description,
            "cli_command": cli_command,
            "parameters": _parameter_metadata(name),
            "examples": _EXAMPLES[name],
            "destructive": name in _DESTRUCTIVE_TOOLS,
            "confirmation_required": name in _CONFIRMATION_TOOLS,
            "result_shape": {"ok": "boolean", "data": "object|array|string", "meta": "object", "error": "object"},
        }
        if name in globals():
            globals()[name].__doc__ = description
    return definitions


TOOL_DEFINITIONS = _build_tool_definitions()


def ticktask_describe_tools() -> dict[str, Any]:
    """Return rich MCP tool metadata, examples, enums, and confirmation requirements."""
    return ok(TOOL_DEFINITIONS, {"count": len(TOOL_DEFINITIONS)})


def ticktask_cli_parity() -> dict[str, Any]:
    """Return a CLI-to-MCP parity matrix for agent planning and documentation."""
    rows = [
        {
            "mcp_tool": name,
            "cli_command": definition["cli_command"],
            "description": definition["description"],
            "examples": definition["examples"],
            "destructive": definition["destructive"],
            "confirmation_required": definition["confirmation_required"],
        }
        for name, definition in TOOL_DEFINITIONS.items()
    ]
    return ok(rows, {"count": len(rows)})

