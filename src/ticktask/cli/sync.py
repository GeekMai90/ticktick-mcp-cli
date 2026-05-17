from __future__ import annotations

import typer

from ticktask.cli.formatters import emit_error, emit_json
from ticktask.core.results import ok
from ticktask.core.services import TicktaskService

app = typer.Typer(help="Incremental sync/export state commands.")


@app.command("state")
def sync_state(json_output: bool = typer.Option(False, "--json", help="Emit stable JSON.")) -> None:
    try:
        state = TicktaskService().sync_state()
        if json_output:
            emit_json(ok(state))
        else:
            typer.echo(state["state_path"])
            for key, value in state.get("states", {}).items():
                typer.echo(f"{key}: {value.get('last_synced_at', '')}")
    except Exception as exc:
        emit_error(exc, json_output)


@app.command("mark")
def mark_sync_state(
    state_key: str,
    timestamp: str | None = typer.Option(None, "--timestamp", help="ISO timestamp. Defaults to current UTC time."),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON."),
) -> None:
    try:
        state = TicktaskService().mark_sync_state(state_key, timestamp=timestamp)
        if json_output:
            emit_json(ok(state))
        else:
            typer.echo(f"{state['state_key']}: {state['last_synced_at']}")
    except Exception as exc:
        emit_error(exc, json_output)


@app.command("export")
def sync_export(
    resource: str = typer.Argument(..., help="Resource to export incrementally. Currently: tasks."),
    output_format: str = typer.Option("jsonl", "--format", help="json, jsonl, csv, or markdown."),
    state_key: str = typer.Option(..., "--state-key", help="State key to read/update, e.g. tasks:all."),
    project: str | None = typer.Option(None, "--project", help="Project name or ID."),
    status: str = typer.Option("all", "--status", help="open, completed, or all."),
    since: str | None = typer.Option(None, "--since", help="Override stored ISO timestamp."),
    save_state: bool = typer.Option(False, "--save-state", help="Persist current UTC timestamp after export."),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON."),
) -> None:
    try:
        if resource != "tasks":
            raise ValueError("sync export currently supports only the `tasks` resource")
        result = TicktaskService().sync_export_tasks(
            output_format=output_format,
            state_key=state_key,
            project=project,
            status=status,
            since=since,
            save_state=save_state,
        )
        if json_output:
            emit_json(ok(result))
        else:
            typer.echo(result["content"])
    except Exception as exc:
        emit_error(exc, json_output)
