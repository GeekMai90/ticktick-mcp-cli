from __future__ import annotations

import typer

from ticktask.cli.formatters import emit_error, emit_json
from ticktask.core.results import ok
from ticktask.core.services import TicktaskService

app = typer.Typer(help="Focus session commands.")


@app.command("list")
def list_focuses(
    from_time: str = typer.Option(..., "--from", help="Start time/date. Max 30-day range."),
    to_time: str = typer.Option(..., "--to", help="End time/date. Max 30-day range."),
    focus_type: int = typer.Option(0, "--type", help="0=Pomodoro, 1=Timing."),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON."),
) -> None:
    try:
        focuses = TicktaskService().list_focuses(from_time=from_time, to_time=to_time, focus_type=focus_type)
        if json_output:
            emit_json(ok(focuses, {"count": len(focuses)}))
        else:
            for focus in focuses:
                typer.echo(f"{focus['id']}\t{focus.get('focus_type')}")
    except Exception as exc:
        emit_error(exc, json_output)


@app.command("get")
def get_focus(
    focus_id: str,
    focus_type: int = typer.Option(0, "--type", help="0=Pomodoro, 1=Timing."),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON."),
) -> None:
    try:
        focus = TicktaskService().get_focus(focus_id=focus_id, focus_type=focus_type)
        if json_output:
            emit_json(ok(focus))
        else:
            typer.echo(f"{focus['id']}\t{focus.get('focus_type')}")
    except Exception as exc:
        emit_error(exc, json_output)


@app.command("delete")
def delete_focus(
    focus_id: str,
    focus_type: int = typer.Option(0, "--type", help="0=Pomodoro, 1=Timing."),
    yes: bool = typer.Option(False, "--yes", help="Confirm deletion."),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON."),
) -> None:
    try:
        result = TicktaskService().delete_focus(focus_id=focus_id, focus_type=focus_type, confirmed=yes)
        if json_output:
            emit_json(ok(result))
        else:
            typer.echo(f"Deleted focus session {focus_id}.")
    except Exception as exc:
        emit_error(exc, json_output)
