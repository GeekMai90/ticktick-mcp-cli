from __future__ import annotations

import os

import typer

from ticktask.cli.formatters import emit_error, emit_json, emit_result
from ticktask.core.results import ok
from ticktask.core.services import TicktaskService

app = typer.Typer(help="Explicit real-API integration checks.")


@app.command("smoke")
def smoke(
    service: str | None = typer.Option(None, "--service", help="Service profile to use."),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON."),
) -> None:
    """Run a read-only real API smoke check when explicitly enabled."""
    try:
        if os.environ.get("TICKTASK_INTEGRATION") != "1":
            data = {"enabled": False, "skipped": True, "project_count": None}
            if json_output:
                emit_json(ok(data))
            else:
                typer.echo("Integration smoke skipped. Set TICKTASK_INTEGRATION=1 to run.")
            return

        projects = TicktaskService(service=service).list_projects()
        data = {
            "enabled": True,
            "skipped": False,
            "service": service,
            "project_count": len(projects),
        }
        emit_result(data, json_output=json_output)
    except Exception as exc:
        emit_error(exc, json_output)
