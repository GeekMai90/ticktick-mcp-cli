from __future__ import annotations

import csv
import io
import json
from typing import Any

from ticktask.core.errors import ValidationError


EXPORT_FORMATS = {"json", "jsonl", "csv", "markdown"}
TASK_EXPORT_FIELDS = ("id", "project_id", "title", "content", "due_date", "priority", "status")


def serialize_tasks(tasks: list[dict[str, Any]], output_format: str) -> str:
    normalized_format = output_format.casefold()
    if normalized_format not in EXPORT_FORMATS:
        raise ValidationError(
            f"Unsupported export format `{output_format}`.",
            hint="Use one of: json, jsonl, csv, markdown.",
        )
    rows = [_task_row(task) for task in tasks]
    if normalized_format == "json":
        return json.dumps(rows, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if normalized_format == "jsonl":
        return "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows)
    if normalized_format == "csv":
        return _to_csv(rows)
    return _to_markdown(rows)


def _task_row(task: dict[str, Any]) -> dict[str, Any]:
    return {field: task.get(field) for field in TASK_EXPORT_FIELDS}


def _to_csv(rows: list[dict[str, Any]]) -> str:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(TASK_EXPORT_FIELDS), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def _to_markdown(rows: list[dict[str, Any]]) -> str:
    lines = ["| ID | Project | Title | Due | Priority | Status |", "| --- | --- | --- | --- | --- | --- |"]
    for row in rows:
        lines.append(
            "| {id} | {project_id} | {title} | {due_date} | {priority} | {status} |".format(
                id=_markdown_cell(row.get("id")),
                project_id=_markdown_cell(row.get("project_id")),
                title=_markdown_cell(row.get("title")),
                due_date=_markdown_cell(row.get("due_date")),
                priority=_markdown_cell(row.get("priority")),
                status=_markdown_cell(row.get("status")),
            )
        )
    return "\n".join(lines) + "\n"


def _markdown_cell(value: Any) -> str:
    if value is None:
        return ""
    return str(value).replace("|", "\\|").replace("\n", " ")
