import pytest

from ticktask.core.errors import ValidationError
from ticktask.core.natural_query import compile_task_query


def test_compile_task_query_maps_common_terms_to_filters() -> None:
    compiled = compile_task_query('completed high priority #agent project:"Inbox" from 2026-05-01 to 2026-05-17 milk')

    assert compiled == {
        "status": "completed",
        "filter_preset": "high-priority",
        "tag": "agent",
        "project": "Inbox",
        "start_date": "2026-05-01",
        "end_date": "2026-05-17",
        "search": "milk",
    }


def test_compile_task_query_supports_smart_filter_phrases() -> None:
    assert compile_task_query("overdue #work") == {
        "status": "open",
        "filter_preset": "overdue",
        "tag": "work",
    }
    assert compile_task_query("no date") == {"status": "open", "filter_preset": "no-date"}


def test_compile_task_query_rejects_empty_query() -> None:
    with pytest.raises(ValidationError):
        compile_task_query("  ")
