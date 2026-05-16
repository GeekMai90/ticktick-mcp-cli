from ticktask.core.errors import ConfigError
from ticktask.core.results import err, ok


def test_success_shape() -> None:
    assert ok({"x": 1}) == {"ok": True, "data": {"x": 1}, "meta": {}}


def test_error_shape() -> None:
    payload = err(ConfigError("missing"))
    assert payload["ok"] is False
    assert payload["error"]["code"] == "CONFIG_ERROR"
    assert payload["error"]["message"] == "missing"
    assert "hint" in payload["error"]
