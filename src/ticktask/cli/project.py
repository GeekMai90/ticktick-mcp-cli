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
