from datetime import date

import pytest

from ticktask.core.errors import ValidationError
from ticktask.core.validation import (
    normalize_priority,
    normalize_project_kind,
    normalize_task_status,
    normalize_task_date,
    normalize_view_mode,
)


def test_normalize_task_date_accepts_iso_and_relative_words() -> None:
    today = date(2026, 5, 17)

    assert normalize_task_date("2026-05-20", today=today) == "2026-05-20"
    assert normalize_task_date("today", today=today) == "2026-05-17"
    assert normalize_task_date("tomorrow", today=today) == "2026-05-18"
    assert normalize_task_date("next monday", today=today) == "2026-05-18"


def test_normalize_task_date_rejects_ambiguous_or_invalid_values() -> None:
    with pytest.raises(ValidationError) as exc:
        normalize_task_date("05/20/2026", today=date(2026, 5, 17))

    assert "YYYY-MM-DD" in (exc.value.hint or "")


def test_enum_normalizers_accept_aliases_and_canonicalize_case() -> None:
    assert normalize_priority("HIGH") == "high"
    assert normalize_priority("p1") == "high"
    assert normalize_priority("normal") == "none"
    assert normalize_task_status("done") == "completed"
    assert normalize_task_status("ALL") == "all"
    assert normalize_project_kind("task") == "TASK"
    assert normalize_view_mode("KANBAN") == "kanban"


def test_enum_normalizers_reject_unknown_values_with_hints() -> None:
    with pytest.raises(ValidationError) as exc:
        normalize_priority("urgent")
    assert "none, low, medium, high" in (exc.value.hint or "")

    with pytest.raises(ValidationError) as exc:
        normalize_project_kind("folder")
    assert "TASK, NOTE" in (exc.value.hint or "")
