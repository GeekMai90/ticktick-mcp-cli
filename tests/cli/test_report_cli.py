import json

from typer.testing import CliRunner

from ticktask.cli.app import app

runner = CliRunner()


def test_report_progress_cli_json(monkeypatch) -> None:
    class FakeService:
        def progress_report(self, period=None, start_date=None, end_date=None, project=None, focus_type=0):
            assert period == "week"
            assert start_date == "2026-05-01"
            assert end_date == "2026-05-17"
            assert project == "Inbox"
            assert focus_type == 1
            return {
                "period": {"preset": period, "start": start_date, "end": end_date},
                "scope": {"project": project, "focus_type": focus_type},
                "tasks": {"completed_count": 2, "open_count": 3, "completion_rate": 0.4},
                "habits": {"habit_count": 1, "checkin_count": 4},
                "focus": {"session_count": 2, "duration_minutes": 50},
                "scorecard": {"completed_tasks": 2, "habit_checkins": 4, "focus_minutes": 50, "overdue_tasks": 1},
            }

    monkeypatch.setattr("ticktask.cli.report.TicktaskService", lambda: FakeService())

    result = runner.invoke(
        app,
        [
            "report",
            "progress",
            "week",
            "--from",
            "2026-05-01",
            "--to",
            "2026-05-17",
            "--project",
            "Inbox",
            "--focus-type",
            "1",
            "--json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["data"]["scorecard"]["focus_minutes"] == 50
    assert payload["meta"] == {"report": "progress"}
