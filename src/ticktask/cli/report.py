from __future__ import annotations

import typer

from ticktask.cli.formatters import emit_error, emit_json
from ticktask.core.results import ok
from ticktask.core.services import TicktaskService

app = typer.Typer(help="Derived reports across tasks, habits, and focus sessions.")


@app.command("progress")
def progress_report(
    period: str | None = typer.Argument(None, help="Date preset: today, yesterday, or week."),
    from_date: str | None = typer.Option(None, "--from", help="Start date, YYYY-MM-DD."),
    to_date: str | None = typer.Option(None, "--to", help="End date, YYYY-MM-DD."),
    project: str | None = typer.Option(None, "--project", help="Project name or ID."),
    focus_type: int = typer.Option(0, "--focus-type", help="0=Pomodoro, 1=Timing."),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON."),
) -> None:
    try:
        report = TicktaskService().progress_report(
            period=period,
            start_date=from_date,
            end_date=to_date,
            project=project,
            focus_type=focus_type,
        )
        if json_output:
            emit_json(ok(report, {"report": "progress"}))
        else:
            scorecard = report["scorecard"]
            typer.echo(
                f"Completed: {scorecard['completed_tasks']} | "
                f"Habit check-ins: {scorecard['habit_checkins']} | "
                f"Focus minutes: {scorecard['focus_minutes']} | "
                f"Overdue: {scorecard['overdue_tasks']}"
            )
    except Exception as exc:
        emit_error(exc, json_output)
