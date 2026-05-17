from __future__ import annotations

import typer

from ticktask.cli.formatters import emit_error, emit_json, print_tasks
from ticktask.core.results import ok
from ticktask.core.services import TicktaskService

app = typer.Typer(help="Task commands.")


@app.command("list")
def list_tasks(
    project: str | None = typer.Option(None, "--project", help="Project name or ID."),
    status: str = typer.Option("open", "--status", help="open, completed, or all."),
    from_date: str | None = typer.Option(None, "--from", help="Completed start date, YYYY-MM-DD."),
    to_date: str | None = typer.Option(None, "--to", help="Completed end date, YYYY-MM-DD."),
    tag: str | None = typer.Option(None, "--tag", help="Only include tasks with this tag."),
    filter_preset: str | None = typer.Option(
        None,
        "--filter",
        help="Smart filter: today, overdue, upcoming, high-priority, or no-date.",
    ),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON."),
) -> None:
    try:
        tasks = TicktaskService().list_tasks(
            project=project,
            status=status,
            start_date=from_date,
            end_date=to_date,
            tag=tag,
            filter_preset=filter_preset,
        )
        if json_output:
            emit_json(ok(tasks, {"count": len(tasks)}))
        else:
            print_tasks(tasks)
    except Exception as exc:
        emit_error(exc, json_output)


@app.command("filter")
def filter_tasks(
    tag: str | None = typer.Option(None, "--tag", help="Filter by exact tag."),
    project: str | None = typer.Option(None, "--project", help="Project name or ID."),
    status: str = typer.Option("open", "--status", help="open, completed, or all."),
    priority: str | None = typer.Option(None, "--priority", help="none, low, medium, or high."),
    from_date: str | None = typer.Option(None, "--from", help="Start date, YYYY-MM-DD."),
    to_date: str | None = typer.Option(None, "--to", help="End date, YYYY-MM-DD."),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON."),
) -> None:
    try:
        tasks = TicktaskService().filter_tasks(
            tag=tag,
            project=project,
            status=status,
            priority=priority,
            start_date=from_date,
            end_date=to_date,
        )
        if json_output:
            emit_json(ok(tasks, {"count": len(tasks)}))
        else:
            print_tasks(tasks)
    except Exception as exc:
        emit_error(exc, json_output)


@app.command("search")
def search_tasks(
    query: str,
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON."),
) -> None:
    try:
        tasks = TicktaskService().search_tasks(query)
        if json_output:
            emit_json(ok(tasks, {"count": len(tasks), "query": query}))
        else:
            print_tasks(tasks)
    except Exception as exc:
        emit_error(exc, json_output)


@app.command("add")
def add_task(
    title: str,
    project: str | None = typer.Option(None, "--project", help="Project name or ID."),
    content: str | None = typer.Option(None, "--content", help="Task body/content."),
    due: str | None = typer.Option(None, "--due", help="Due date string accepted by the API."),
    priority: str = typer.Option("none", "--priority", help="none, low, medium, or high."),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON."),
) -> None:
    try:
        task = TicktaskService().create_task(title, project, content, due, priority)
        if json_output:
            emit_json(ok(task))
        else:
            print_tasks([task])
    except Exception as exc:
        emit_error(exc, json_output)


@app.command("complete")
def complete_task(
    task_id: str,
    project_id: str = typer.Option(..., "--project-id", help="Exact project ID."),
    yes: bool = typer.Option(False, "--yes", help="Confirm completion."),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON."),
) -> None:
    try:
        result = TicktaskService().complete_task(task_id=task_id, project_id=project_id, confirmed=yes)
        if json_output:
            emit_json(ok(result))
        else:
            typer.echo(f"Completed {task_id} in project {project_id}.")
    except Exception as exc:
        emit_error(exc, json_output)


@app.command("get")
def get_task(
    task_id: str,
    project_id: str = typer.Option(..., "--project-id", help="Exact project ID."),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON."),
) -> None:
    try:
        task = TicktaskService().get_task(task_id=task_id, project_id=project_id)
        if json_output:
            emit_json(ok(task))
        else:
            print_tasks([task])
    except Exception as exc:
        emit_error(exc, json_output)


@app.command("update")
def update_task(
    task_id: str,
    project_id: str = typer.Option(..., "--project-id", help="Exact project ID."),
    title: str | None = typer.Option(None, "--title", help="New title."),
    content: str | None = typer.Option(None, "--content", help="New task body/content."),
    due: str | None = typer.Option(None, "--due", help="New due date string accepted by the API."),
    priority: str | None = typer.Option(None, "--priority", help="none, low, medium, or high."),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON."),
) -> None:
    try:
        task = TicktaskService().update_task(
            task_id=task_id,
            project_id=project_id,
            title=title,
            content=content,
            due=due,
            priority=priority,
        )
        if json_output:
            emit_json(ok(task))
        else:
            print_tasks([task])
    except Exception as exc:
        emit_error(exc, json_output)


@app.command("delete")
def delete_task(
    task_id: str,
    project_id: str = typer.Option(..., "--project-id", help="Exact project ID."),
    yes: bool = typer.Option(False, "--yes", help="Confirm deletion."),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON."),
) -> None:
    try:
        result = TicktaskService().delete_task(
            task_id=task_id,
            project_id=project_id,
            confirmed=yes,
        )
        if json_output:
            emit_json(ok(result))
        else:
            typer.echo(f"Deleted {task_id} from project {project_id}.")
    except Exception as exc:
        emit_error(exc, json_output)


@app.command("move")
def move_task(
    task_id: str,
    from_project_id: str = typer.Option(..., "--from-project-id", help="Source project ID."),
    to_project_id: str = typer.Option(..., "--to-project-id", help="Destination project ID."),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON."),
) -> None:
    try:
        result = TicktaskService().move_task(
            task_id=task_id,
            from_project_id=from_project_id,
            to_project_id=to_project_id,
        )
        if json_output:
            emit_json(ok(result))
        else:
            typer.echo(f"Moved {task_id} from {from_project_id} to {to_project_id}.")
    except Exception as exc:
        emit_error(exc, json_output)


@app.command("analytics")
def task_analytics(
    period: str | None = typer.Argument(None, help="Date preset: today, yesterday, or week."),
    from_date: str | None = typer.Option(None, "--from", help="Completed start date, YYYY-MM-DD."),
    to_date: str | None = typer.Option(None, "--to", help="Completed end date, YYYY-MM-DD."),
    project: str | None = typer.Option(None, "--project", help="Project name or ID."),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON."),
) -> None:
    try:
        report = TicktaskService().task_analytics(
            preset=period,
            start_date=from_date,
            end_date=to_date,
            project=project,
        )
        if json_output:
            emit_json(ok(report))
        else:
            summary = report["summary"]
            typer.echo(
                f"Open: {summary['open_count']} | Completed: {summary['completed_count']} | "
                f"Overdue: {summary['overdue_count']}"
            )
    except Exception as exc:
        emit_error(exc, json_output)


item_app = typer.Typer(help="Checklist item/subtask commands.")


@item_app.command("add")
def add_checklist_item(
    task_id: str,
    title: str,
    project_id: str = typer.Option(..., "--project-id", help="Exact project ID."),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON."),
) -> None:
    try:
        task = TicktaskService().add_checklist_item(task_id=task_id, project_id=project_id, title=title)
        if json_output:
            emit_json(ok(task))
        else:
            print_tasks([task])
    except Exception as exc:
        emit_error(exc, json_output)


@item_app.command("update")
def update_checklist_item(
    task_id: str,
    item_id: str,
    project_id: str = typer.Option(..., "--project-id", help="Exact project ID."),
    title: str | None = typer.Option(None, "--title", help="New checklist item title."),
    status: str | None = typer.Option(None, "--status", help="open or completed."),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON."),
) -> None:
    try:
        task = TicktaskService().update_checklist_item(
            task_id=task_id,
            project_id=project_id,
            item_id=item_id,
            title=title,
            status=status,
        )
        if json_output:
            emit_json(ok(task))
        else:
            print_tasks([task])
    except Exception as exc:
        emit_error(exc, json_output)


@item_app.command("complete")
def complete_checklist_item(
    task_id: str,
    item_id: str,
    project_id: str = typer.Option(..., "--project-id", help="Exact project ID."),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON."),
) -> None:
    try:
        task = TicktaskService().complete_checklist_item(
            task_id=task_id,
            project_id=project_id,
            item_id=item_id,
        )
        if json_output:
            emit_json(ok(task))
        else:
            print_tasks([task])
    except Exception as exc:
        emit_error(exc, json_output)


@item_app.command("delete")
def delete_checklist_item(
    task_id: str,
    item_id: str,
    project_id: str = typer.Option(..., "--project-id", help="Exact project ID."),
    yes: bool = typer.Option(False, "--yes", help="Confirm deletion."),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON."),
) -> None:
    try:
        task = TicktaskService().delete_checklist_item(
            task_id=task_id,
            project_id=project_id,
            item_id=item_id,
            confirmed=yes,
        )
        if json_output:
            emit_json(ok(task))
        else:
            print_tasks([task])
    except Exception as exc:
        emit_error(exc, json_output)



tag_app = typer.Typer(help="Task tag mutation commands.")


@tag_app.command("add")
def add_task_tag(
    task_id: str,
    tag: str,
    project_id: str = typer.Option(..., "--project-id", help="Exact project ID."),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON."),
) -> None:
    try:
        task = TicktaskService().add_task_tag(task_id=task_id, project_id=project_id, tag=tag)
        if json_output:
            emit_json(ok(task))
        else:
            print_tasks([task])
    except Exception as exc:
        emit_error(exc, json_output)


@tag_app.command("remove")
def remove_task_tag(
    task_id: str,
    tag: str,
    project_id: str = typer.Option(..., "--project-id", help="Exact project ID."),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON."),
) -> None:
    try:
        task = TicktaskService().remove_task_tag(task_id=task_id, project_id=project_id, tag=tag)
        if json_output:
            emit_json(ok(task))
        else:
            print_tasks([task])
    except Exception as exc:
        emit_error(exc, json_output)



reminder_app = typer.Typer(help="Task reminder commands.")


@reminder_app.command("set")
def set_task_reminders(
    task_id: str,
    project_id: str = typer.Option(..., "--project-id", help="Exact project ID."),
    reminders: list[str] = typer.Option(..., "--reminder", help="Reminder value; repeat for multiple reminders."),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON."),
) -> None:
    try:
        task = TicktaskService().set_task_reminders(task_id=task_id, project_id=project_id, reminders=reminders)
        if json_output:
            emit_json(ok(task))
        else:
            print_tasks([task])
    except Exception as exc:
        emit_error(exc, json_output)


@reminder_app.command("clear")
def clear_task_reminders(
    task_id: str,
    project_id: str = typer.Option(..., "--project-id", help="Exact project ID."),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON."),
) -> None:
    try:
        task = TicktaskService().clear_task_reminders(task_id=task_id, project_id=project_id)
        if json_output:
            emit_json(ok(task))
        else:
            print_tasks([task])
    except Exception as exc:
        emit_error(exc, json_output)


repeat_app = typer.Typer(help="Task repeat/RRULE commands.")


@repeat_app.command("set")
def set_task_repeat(
    task_id: str,
    project_id: str = typer.Option(..., "--project-id", help="Exact project ID."),
    preset: str | None = typer.Option(None, "--preset", help="daily, weekly, monthly, or yearly."),
    rrule: str | None = typer.Option(None, "--rrule", help="Raw RRULE, with or without RRULE: prefix."),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON."),
) -> None:
    try:
        task = TicktaskService().set_task_repeat(task_id=task_id, project_id=project_id, preset=preset, rrule=rrule)
        if json_output:
            emit_json(ok(task))
        else:
            print_tasks([task])
    except Exception as exc:
        emit_error(exc, json_output)


@repeat_app.command("clear")
def clear_task_repeat(
    task_id: str,
    project_id: str = typer.Option(..., "--project-id", help="Exact project ID."),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON."),
) -> None:
    try:
        task = TicktaskService().clear_task_repeat(task_id=task_id, project_id=project_id)
        if json_output:
            emit_json(ok(task))
        else:
            print_tasks([task])
    except Exception as exc:
        emit_error(exc, json_output)


batch_app = typer.Typer(help="Dry-run guarded batch task commands.")


def _batch_dry_run(execute: bool) -> bool:
    return not execute


@batch_app.command("complete")
def batch_complete_tasks(
    task_ids: list[str] = typer.Option(..., "--task-id", help="Exact task ID; repeat for multiple tasks."),
    project_id: str = typer.Option(..., "--project-id", help="Exact project ID."),
    execute: bool = typer.Option(False, "--execute", help="Execute mutations instead of dry-run preview."),
    yes: bool = typer.Option(False, "--yes", help="Confirm execution when --execute is used."),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON."),
) -> None:
    try:
        result = TicktaskService().batch_complete_tasks(
            task_ids=task_ids,
            project_id=project_id,
            dry_run=_batch_dry_run(execute),
            confirmed=yes,
        )
        if json_output:
            emit_json(ok(result))
        else:
            typer.echo(result)
    except Exception as exc:
        emit_error(exc, json_output)


@batch_app.command("delete")
def batch_delete_tasks(
    task_ids: list[str] = typer.Option(..., "--task-id", help="Exact task ID; repeat for multiple tasks."),
    project_id: str = typer.Option(..., "--project-id", help="Exact project ID."),
    execute: bool = typer.Option(False, "--execute", help="Execute mutations instead of dry-run preview."),
    yes: bool = typer.Option(False, "--yes", help="Confirm execution when --execute is used."),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON."),
) -> None:
    try:
        result = TicktaskService().batch_delete_tasks(
            task_ids=task_ids,
            project_id=project_id,
            dry_run=_batch_dry_run(execute),
            confirmed=yes,
        )
        if json_output:
            emit_json(ok(result))
        else:
            typer.echo(result)
    except Exception as exc:
        emit_error(exc, json_output)


@batch_app.command("move")
def batch_move_tasks(
    task_ids: list[str] = typer.Option(..., "--task-id", help="Exact task ID; repeat for multiple tasks."),
    from_project_id: str = typer.Option(..., "--from-project-id", help="Exact source project ID."),
    to_project_id: str = typer.Option(..., "--to-project-id", help="Exact destination project ID."),
    execute: bool = typer.Option(False, "--execute", help="Execute mutations instead of dry-run preview."),
    yes: bool = typer.Option(False, "--yes", help="Confirm execution when --execute is used."),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON."),
) -> None:
    try:
        result = TicktaskService().batch_move_tasks(
            task_ids=task_ids,
            from_project_id=from_project_id,
            to_project_id=to_project_id,
            dry_run=_batch_dry_run(execute),
            confirmed=yes,
        )
        if json_output:
            emit_json(ok(result))
        else:
            typer.echo(result)
    except Exception as exc:
        emit_error(exc, json_output)

app.add_typer(tag_app, name="tag")
app.add_typer(item_app, name="item")
app.add_typer(reminder_app, name="reminder")
app.add_typer(repeat_app, name="repeat")
app.add_typer(batch_app, name="batch")


