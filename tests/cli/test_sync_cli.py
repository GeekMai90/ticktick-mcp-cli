import json

from typer.testing import CliRunner

from ticktask.cli.app import app

runner = CliRunner()


def test_sync_state_and_mark_cli_json(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("TICKTASK_CONFIG_DIR", str(tmp_path))

    marked = runner.invoke(
        app,
        ["sync", "mark", "tasks:all", "--timestamp", "2026-05-17T00:00:00Z", "--json"],
    )
    assert marked.exit_code == 0
    marked_payload = json.loads(marked.stdout)
    assert marked_payload["data"]["state_key"] == "tasks:all"
    assert marked_payload["data"]["last_synced_at"] == "2026-05-17T00:00:00Z"

    state = runner.invoke(app, ["sync", "state", "--json"])
    assert state.exit_code == 0
    state_payload = json.loads(state.stdout)
    assert state_payload["data"]["states"]["tasks:all"]["last_synced_at"] == "2026-05-17T00:00:00Z"


def test_sync_export_tasks_uses_state_and_can_save_next_state(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("TICKTASK_CONFIG_DIR", str(tmp_path))

    class FakeService:
        def sync_export_tasks(self, output_format, state_key, project=None, status="all", since=None, save_state=False):
            assert output_format == "jsonl"
            assert state_key == "tasks:all"
            assert status == "all"
            assert save_state is True
            return {
                "state_key": state_key,
                "since": since or "2026-05-01T00:00:00Z",
                "content": '{"id":"t1"}\n',
                "state": {"state_key": state_key, "last_synced_at": "2026-05-17T00:00:00Z"},
            }

    monkeypatch.setattr("ticktask.cli.sync.TicktaskService", lambda: FakeService())
    runner.invoke(app, ["sync", "mark", "tasks:all", "--timestamp", "2026-05-01T00:00:00Z", "--json"])

    result = runner.invoke(
        app,
        ["sync", "export", "tasks", "--format", "jsonl", "--state-key", "tasks:all", "--save-state", "--json"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["data"]["since"] == "2026-05-01T00:00:00Z"
    assert payload["data"]["content"] == '{"id":"t1"}\n'
    assert payload["data"]["state"]["state_key"] == "tasks:all"
