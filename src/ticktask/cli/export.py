from __future__ import annotations

import typer

from ticktask.cli.formatters import emit_error
from ticktask.core.services import TicktaskService

app = typer.Typer(help="Export task and focus data.")


@app.command("tasks")
def export_tasks(
    output_format: str = typer.Option(..., "--format", help="json, jsonl, csv, or markdown."),
    project: str | None = typer.Option(None, "--project", help="Project name or ID."),
    status: str = typer.Option("open", "--status", help="open, completed, or all."),
    from_date: str | None = typer.Option(None, "--from", help="Start date, YYYY-MM-DD."),
    to_date: str | None = typer.Option(None, "--to", help="End date, YYYY-MM-DD."),
) -> None:
    try:
        typer.echo(
            TicktaskService().export_tasks(
                output_format=output_format,
                project=project,
                status=status,
                start_date=from_date,
                end_date=to_date,
            ),
            nl=False,
        )
    except Exception as exc:
        emit_error(exc, json_output=False)


@app.command("completed")
def export_completed(
    output_format: str = typer.Option(..., "--format", help="json, jsonl, csv, or markdown."),
    from_date: str | None = typer.Option(None, "--from", help="Start date, YYYY-MM-DD."),
    to_date: str | None = typer.Option(None, "--to", help="End date, YYYY-MM-DD."),
) -> None:
    try:
        typer.echo(
            TicktaskService().export_tasks(
                output_format=output_format,
                status="completed",
                start_date=from_date,
                end_date=to_date,
            ),
            nl=False,
        )
    except Exception as exc:
        emit_error(exc, json_output=False)


@app.command("focus")
def export_focus(
    output_format: str = typer.Option(..., "--format", help="json, jsonl, csv, or markdown."),
    from_time: str = typer.Option(..., "--from", help="Start time/date. Max 30-day range."),
    to_time: str = typer.Option(..., "--to", help="End time/date. Max 30-day range."),
    focus_type: int = typer.Option(0, "--type", help="0=Pomodoro, 1=Timing."),
) -> None:
    try:
        typer.echo(
            TicktaskService().export_focuses(
                output_format=output_format,
                from_time=from_time,
                to_time=to_time,
                focus_type=focus_type,
            ),
            nl=False,
        )
    except Exception as exc:
        emit_error(exc, json_output=False)
