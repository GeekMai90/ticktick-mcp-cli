from __future__ import annotations

import csv
import io
import json
from typing import Any

from ticktask.core.errors import ValidationError


EXPORT_FORMATS = {"json", "jsonl", "csv", "markdown"}
TASK_EXPORT_FIELDS = ("id", "project_id", "title", "content", "due_date", "priority", "status")
TASK_MARKDOWN_FIELDS = ("id", "project_id", "title", "due_date", "priority", "status")
FOCUS_EXPORT_FIELDS = (
    "id",
    "focus_type",
    "task_id",
    "start_time",
    "end_time",
    "duration_seconds",
    "duration_minutes",
)


def serialize_tasks(tasks: list[dict[str, Any]], output_format: str) -> str:
    return _serialize_rows(
        rows=[_task_row(task) for task in tasks],
        output_format=output_format,
        fields=TASK_EXPORT_FIELDS,
        markdown_header=("ID", "Project", "Title", "Due", "Priority", "Status"),
        markdown_fields=TASK_MARKDOWN_FIELDS,
    )


def serialize_focuses(focuses: list[dict[str, Any]], output_format: str) -> str:
    return _serialize_rows(
        rows=[_focus_row(focus) for focus in focuses],
        output_format=output_format,
        fields=FOCUS_EXPORT_FIELDS,
        markdown_header=("ID", "Type", "Task", "Start", "End", "Seconds", "Minutes"),
        markdown_fields=FOCUS_EXPORT_FIELDS,
    )


def _serialize_rows(
    rows: list[dict[str, Any]],
    output_format: str,
    fields: tuple[str, ...],
    markdown_header: tuple[str, ...],
    markdown_fields: tuple[str, ...],
) -> str:
    normalized_format = output_format.casefold()
    if normalized_format not in EXPORT_FORMATS:
        raise ValidationError(
            f"Unsupported export format `{output_format}`.",
            hint="Use one of: json, jsonl, csv, markdown.",
        )
    if normalized_format == "json":
        return json.dumps(rows, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if normalized_format == "jsonl":
        return "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows)
    if normalized_format == "csv":
        return _to_csv(rows, fields)
    return _to_markdown(rows, markdown_fields, markdown_header)


def _task_row(task: dict[str, Any]) -> dict[str, Any]:
    return {field: task.get(field) for field in TASK_EXPORT_FIELDS}


def _focus_row(focus: dict[str, Any]) -> dict[str, Any]:
    duration_seconds = focus.get("duration")
    if duration_seconds is None:
        duration_seconds = focus.get("duration_seconds")
    duration_minutes = None
    if duration_seconds is not None:
        duration_minutes = round(int(duration_seconds) / 60, 2)
        if duration_minutes == int(duration_minutes):
            duration_minutes = int(duration_minutes)
    return {
        "id": focus.get("id"),
        "focus_type": focus.get("focus_type"),
        "task_id": focus.get("task_id"),
        "start_time": focus.get("start_time"),
        "end_time": focus.get("end_time"),
        "duration_seconds": duration_seconds,
        "duration_minutes": duration_minutes,
    }


def _to_csv(rows: list[dict[str, Any]], fields: tuple[str, ...]) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(fields), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def _to_markdown(rows: list[dict[str, Any]], fields: tuple[str, ...], header: tuple[str, ...]) -> str:
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join("---" for _ in header) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(_markdown_cell(row.get(field)) for field in fields) + " |")
    return "\n".join(lines) + "\n"


def _markdown_cell(value: Any) -> str:
    if value is None:
        return ""
    return str(value).replace("|", "\\|").replace("\n", " ")
