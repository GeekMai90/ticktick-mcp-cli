import json

from typer.testing import CliRunner

from ticktask.cli.app import app

runner = CliRunner()


def test_backup_tasks_cli_writes_json_manifest(monkeypatch, tmp_path) -> None:
    class FakeService:
        def backup_tasks(
            self,
            output_dir,
            output_formats,
            backup_date=None,
            project=None,
            status="all",
            start_date=None,
            end_date=None,
        ):
            assert output_dir == tmp_path
            assert output_formats == ["markdown", "jsonl"]
            assert backup_date == "2026-05-17"
            assert project == "Inbox"
            assert status == "all"
            assert start_date == "2026-05-01"
            assert end_date == "2026-05-17"
            return {
                "output_dir": str(tmp_path),
                "backup_date": backup_date,
                "project": project,
                "status": status,
                "count": 2,
                "files": [
                    {"format": "markdown", "path": "2026-05-17/inbox/tasks.md"},
                    {"format": "jsonl", "path": "2026-05-17/inbox/tasks.jsonl"},
                ],
                "manifest_path": "2026-05-17/manifest.json",
            }

    monkeypatch.setattr("ticktask.cli.backup.TicktaskService", lambda: FakeService())

    result = runner.invoke(
        app,
        [
            "backup",
            "tasks",
            "--output-dir",
            str(tmp_path),
            "--format",
            "markdown,jsonl",
            "--date",
            "2026-05-17",
            "--project",
            "Inbox",
            "--status",
            "all",
            "--from",
            "2026-05-01",
            "--to",
            "2026-05-17",
            "--json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["data"]["count"] == 2
    assert payload["data"]["manifest_path"] == "2026-05-17/manifest.json"
    assert payload["meta"]["file_count"] == 2
