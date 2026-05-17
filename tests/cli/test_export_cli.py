from typer.testing import CliRunner

from ticktask.cli.app import app

runner = CliRunner()


def test_export_tasks_outputs_raw_format(monkeypatch) -> None:
    class FakeService:
        def export_tasks(self, output_format, project=None, status="open", start_date=None, end_date=None):
            assert output_format == "jsonl"
            assert status == "completed"
            assert start_date == "2026-01-01"
            return '{"id":"t1"}\n'

    monkeypatch.setattr("ticktask.cli.export.TicktaskService", lambda: FakeService())
    result = runner.invoke(
        app,
        [
            "export",
            "tasks",
            "--format",
            "jsonl",
            "--status",
            "completed",
            "--from",
            "2026-01-01",
        ],
    )
    assert result.exit_code == 0
    assert result.stdout == '{"id":"t1"}\n'


def test_export_focus_outputs_raw_format(monkeypatch) -> None:
    class FakeService:
        def export_focuses(self, output_format, from_time, to_time, focus_type=0):
            assert output_format == "csv"
            assert from_time == "2026-01-01"
            assert to_time == "2026-01-30"
            assert focus_type == 1
            return "id,duration_minutes\nf1,25\n"

    monkeypatch.setattr("ticktask.cli.export.TicktaskService", lambda: FakeService())
    result = runner.invoke(
        app,
        [
            "export",
            "focus",
            "--format",
            "csv",
            "--from",
            "2026-01-01",
            "--to",
            "2026-01-30",
            "--type",
            "1",
        ],
    )
    assert result.exit_code == 0
    assert result.stdout == "id,duration_minutes\nf1,25\n"
