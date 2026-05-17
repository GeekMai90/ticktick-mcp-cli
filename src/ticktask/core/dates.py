from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from ticktask.core.errors import ValidationError


@dataclass(frozen=True)
class DateRange:
    start: str
    end: str

    def to_dict(self) -> dict[str, str]:
        return {"from": self.start, "to": self.end}


def parse_date_range(
    preset: str | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
    *,
    today: date | None = None,
) -> DateRange:
    current = today or date.today()
    if preset and (from_date or to_date):
        raise ValidationError("Use either a preset or --from/--to, not both.")

    if preset:
        normalized = preset.casefold()
        if normalized == "today":
            return DateRange(current.isoformat(), current.isoformat())
        if normalized == "yesterday":
            value = current - timedelta(days=1)
            return DateRange(value.isoformat(), value.isoformat())
        if normalized == "week":
            start = current - timedelta(days=current.weekday())
            return DateRange(start.isoformat(), current.isoformat())
        raise ValidationError(
            f"Unknown date range `{preset}`.",
            hint="Use today, yesterday, week, or explicit --from/--to dates.",
        )

    if from_date or to_date:
        start = _parse_iso_date(from_date or to_date or current.isoformat())
        end = _parse_iso_date(to_date or from_date or current.isoformat())
        if start > end:
            raise ValidationError("--from must be on or before --to.")
        return DateRange(start.isoformat(), end.isoformat())

    return DateRange("1970-01-01", current.isoformat())


def _parse_iso_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValidationError(
            f"Invalid date `{value}`.",
            hint="Use ISO dates in YYYY-MM-DD format.",
        ) from exc
