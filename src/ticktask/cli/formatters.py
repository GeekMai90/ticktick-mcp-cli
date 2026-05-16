from __future__ import annotations

import json
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

from ticktask.core.errors import TicktaskError
from ticktask.core.results import err, ok

console = Console()


def emit_json(payload: dict[str, Any]) -> None:
    typer.echo(json.dumps(payload, ensure_ascii=False, sort_keys=True))


def emit_result(data: Any = None, meta: dict[str, Any] | None = None, json_output: bool = False) -> None:
    payload = ok(data, meta)
    if json_output:
        emit_json(payload)
    else:
        console.print(data if data is not None else "OK")


def emit_error(error: TicktaskError | Exception, json_output: bool = False) -> None:
    payload = err(error)
    if json_output:
        emit_json(payload)
    else:
        error_payload = payload["error"]
        console.print(f"[red]{error_payload['code']}[/red]: {error_payload['message']}")
        if error_payload.get("hint"):
            console.print(f"[dim]{error_payload['hint']}[/dim]")
    raise typer.Exit(1)


def print_projects(projects: list[dict[str, Any]]) -> None:
    table = Table("ID", "Name")
    for project in projects:
        table.add_row(str(project.get("id", "")), str(project.get("name", "")))
    console.print(table)


def print_tasks(tasks: list[dict[str, Any]]) -> None:
    table = Table("ID", "Project", "Title", "Due", "Status")
    for task in tasks:
        table.add_row(
            str(task.get("id", "")),
            str(task.get("project_id") or ""),
            str(task.get("title", "")),
            str(task.get("due_date") or ""),
            str(task.get("status") or ""),
        )
    console.print(table)
