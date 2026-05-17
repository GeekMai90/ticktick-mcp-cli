import json

from typer.testing import CliRunner

from ticktask.cli.app import app
from ticktask.core.errors import ValidationError

runner = CliRunner()


def test_cli_json_error_includes_taxonomy(monkeypatch) -> None:
    class FakeService:
        def list_tasks(self, **kwargs):
            raise ValidationError("bad filter")

    monkeypatch.setattr("ticktask.cli.task.TicktaskService", lambda: FakeService())

    result = runner.invoke(app, ["task", "list", "--json"])

    assert result.exit_code == 1
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert payload["error"]["code"] == "VALIDATION_ERROR"
    assert payload["error"]["category"] == "validation"
    assert payload["error"]["retryable"] is False
    assert payload["error"]["remediation"]["action"] == "fix_arguments"
