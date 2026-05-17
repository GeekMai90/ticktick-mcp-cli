from __future__ import annotations

from pathlib import Path

import typer

from ticktask.cli.formatters import emit_error, emit_json, emit_result
from ticktask.core.results import ok
from ticktask.core.services import TicktaskService

app = typer.Typer(help="Create local backup files for task data.")


def _parse_formats(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


@app.command("tasks")
def backup_tasks(
    output_dir: Path = typer.Option(..., "--output-dir", help="Directory that will receive date/project backup folders."),
    output_format: str = typer.Option("markdown,jsonl,csv", "--format", help="Comma-separated formats: json, jsonl, csv, markdown."),
    backup_date: str | None = typer.Option(None, "--date", help="Backup date folder, YYYY-MM-DD. Defaults to today."),
    project: str | None = typer.Option(None, "--project", help="Project name or ID."),
    status: str = typer.Option("all", "--status", help="open, completed, or all."),
    from_date: str | None = typer.Option(None, "--from", help="Start date, YYYY-MM-DD."),
    to_date: str | None = typer.Option(None, "--to", help="End date, YYYY-MM-DD."),
    json_output: bool = typer.Option(False, "--json", help="Emit stable JSON."),
) -> None:
    try:
        result = TicktaskService().backup_tasks(
            output_dir=output_dir,
            output_formats=_parse_formats(output_format),
            backup_date=backup_date,
            project=project,
            status=status,
            start_date=from_date,
            end_date=to_date,
        )
        if json_output:
            emit_json(ok(result, {"file_count": len(result.get("files", []))}))
        else:
            emit_result(result, {"file_count": len(result.get("files", []))}, json_output=False)
    except Exception as exc:
        emit_error(exc, json_output)
