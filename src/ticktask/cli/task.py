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
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON."),
) -> None:
    try:
        tasks = TicktaskService().list_tasks(project=project, status=status)
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
