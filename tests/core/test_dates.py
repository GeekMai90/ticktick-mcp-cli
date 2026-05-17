from datetime import date

import pytest

from ticktask.core.dates import parse_date_range
from ticktask.core.errors import ValidationError


def test_parse_date_range_presets() -> None:
    today = date(2026, 5, 17)
    assert parse_date_range("today", today=today).to_dict() == {
        "from": "2026-05-17",
        "to": "2026-05-17",
    }
    assert parse_date_range("yesterday", today=today).to_dict() == {
        "from": "2026-05-16",
        "to": "2026-05-16",
    }
    assert parse_date_range("week", today=today).to_dict() == {
        "from": "2026-05-11",
        "to": "2026-05-17",
    }


def test_parse_date_range_explicit_dates() -> None:
    assert parse_date_range(from_date="2026-01-01", to_date="2026-01-31").to_dict() == {
        "from": "2026-01-01",
        "to": "2026-01-31",
    }


def test_parse_date_range_rejects_invalid_date() -> None:
    with pytest.raises(ValidationError):
        parse_date_range(from_date="2026-99-99")
