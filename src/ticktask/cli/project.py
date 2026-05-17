from __future__ import annotations

import typer

from ticktask.cli.formatters import emit_error, emit_json, print_projects
from ticktask.core.results import ok
from ticktask.core.services import TicktaskService

app = typer.Typer(help="Project commands.")


@app.command("list")
def list_projects(
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON."),
) -> None:
    try:
        projects = TicktaskService().list_projects()
        if json_output:
            emit_json(ok(projects, {"count": len(projects)}))
        else:
            print_projects(projects)
    except Exception as exc:
        emit_error(exc, json_output)


@app.command("get")
def get_project(
    project: str,
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON."),
) -> None:
    try:
        projects = TicktaskService().list_projects()
        matches = [item for item in projects if item["id"] == project or item["name"] == project]
        if not matches:
            from ticktask.core.errors import NotFoundError

            raise NotFoundError(f"Project `{project}` was not found.")
        data = matches[0]
        if json_output:
            emit_json(ok(data))
        else:
            print_projects([data])
    except Exception as exc:
        emit_error(exc, json_output)


@app.command("data")
def project_data(
    project_id: str,
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON."),
) -> None:
    try:
        data = TicktaskService().get_project_data(project_id)
        if json_output:
            emit_json(ok(data))
        else:
            from rich.console import Console

            Console().print(data)
    except Exception as exc:
        emit_error(exc, json_output)


@app.command("create")
def create_project(
    name: str,
    color: str | None = typer.Option(None, "--color", help="Project color, e.g. #00aa00."),
    sort_order: int | None = typer.Option(None, "--sort-order", help="Project sort order."),
    view_mode: str | None = typer.Option(None, "--view-mode", help="list, kanban, or timeline."),
    kind: str | None = typer.Option(None, "--kind", help="TASK or NOTE."),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON."),
) -> None:
    try:
        project = TicktaskService().create_project(
            name=name,
            color=color,
            sort_order=sort_order,
            view_mode=view_mode,
            kind=kind,
        )
        if json_output:
            emit_json(ok(project))
        else:
            print_projects([project])
    except Exception as exc:
        emit_error(exc, json_output)


@app.command("update")
def update_project(
    project_id: str,
    name: str | None = typer.Option(None, "--name", help="New project name."),
    color: str | None = typer.Option(None, "--color", help="Project color, e.g. #00aa00."),
    sort_order: int | None = typer.Option(None, "--sort-order", help="Project sort order."),
    view_mode: str | None = typer.Option(None, "--view-mode", help="list, kanban, or timeline."),
    kind: str | None = typer.Option(None, "--kind", help="TASK or NOTE."),
    closed: bool | None = typer.Option(None, "--closed/--not-closed", help="Archive or restore."),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON."),
) -> None:
    try:
        project = TicktaskService().update_project(
            project_id=project_id,
            name=name,
            color=color,
            sort_order=sort_order,
            view_mode=view_mode,
            kind=kind,
            closed=closed,
        )
        if json_output:
            emit_json(ok(project))
        else:
            print_projects([project])
    except Exception as exc:
        emit_error(exc, json_output)


@app.command("delete")
def delete_project(
    project_id: str,
    yes: bool = typer.Option(False, "--yes", help="Confirm deletion."),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON."),
) -> None:
    try:
        result = TicktaskService().delete_project(project_id=project_id, confirmed=yes)
        if json_output:
            emit_json(ok(result))
        else:
            typer.echo(f"deleted project {project_id}")
    except Exception as exc:
        emit_error(exc, json_output)
