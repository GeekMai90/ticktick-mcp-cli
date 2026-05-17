from __future__ import annotations

import re
from typing import Any

from ticktask.core.errors import ValidationError

_STATUS_TERMS = {
    "completed": "completed",
    "complete": "completed",
    "done": "completed",
    "finished": "completed",
    "open": "open",
    "todo": "open",
    "active": "open",
    "all": "all",
}

_FILTER_PHRASES = [
    (re.compile(r"\bhigh\s+priority\b", re.IGNORECASE), "high-priority"),
    (re.compile(r"\bno\s+date\b", re.IGNORECASE), "no-date"),
    (re.compile(r"\btoday\b", re.IGNORECASE), "today"),
    (re.compile(r"\boverdue\b", re.IGNORECASE), "overdue"),
    (re.compile(r"\bupcoming\b", re.IGNORECASE), "upcoming"),
]


def compile_task_query(query: str) -> dict[str, Any]:
    """Compile a small deterministic natural-language task query to filters.

    Supported hints are intentionally conservative and transparent:
    - status words: open/todo/active, completed/done/finished, all
    - smart filters: today, overdue, upcoming, high priority, no date
    - tag tokens: #agent or tag:agent
    - project tokens: project:Inbox or project:"Deep Work"
    - date range tokens: from YYYY-MM-DD, to YYYY-MM-DD
    - any remaining words become a local search string
    """

    original = query.strip()
    if not original:
        raise ValidationError("Natural task query cannot be empty.")

    remaining = original
    compiled: dict[str, Any] = {}

    for pattern, filter_preset in _FILTER_PHRASES:
        if pattern.search(remaining):
            compiled["filter_preset"] = filter_preset
            remaining = pattern.sub(" ", remaining, count=1)
            break

    for status_word, status in _STATUS_TERMS.items():
        pattern = re.compile(rf"\b{re.escape(status_word)}\b", re.IGNORECASE)
        if pattern.search(remaining):
            compiled["status"] = status
            remaining = pattern.sub(" ", remaining, count=1)
            break
    if "status" not in compiled:
        compiled["status"] = "open"

    tag_match = re.search(r"(?:^|\s)(?:#|tag:)([\w.-]+)", remaining, re.IGNORECASE)
    if tag_match:
        compiled["tag"] = tag_match.group(1)
        remaining = remaining[: tag_match.start()] + " " + remaining[tag_match.end() :]

    project_match = re.search(
        r"(?:^|\s)project:(?:\"([^\"]+)\"|'([^']+)'|([^\s]+))",
        remaining,
        re.IGNORECASE,
    )
    if project_match:
        compiled["project"] = next(group for group in project_match.groups() if group)
        remaining = remaining[: project_match.start()] + " " + remaining[project_match.end() :]

    for key, output_key in (("from", "start_date"), ("to", "end_date")):
        date_match = re.search(rf"(?:^|\s){key}\s+(\d{{4}}-\d{{2}}-\d{{2}})", remaining, re.IGNORECASE)
        if date_match:
            compiled[output_key] = date_match.group(1)
            remaining = remaining[: date_match.start()] + " " + remaining[date_match.end() :]

    search = " ".join(remaining.split()).strip()
    if search:
        compiled["search"] = search

    return compiled
