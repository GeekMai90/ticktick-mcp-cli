from ticktask.core.errors import (
    ApiError,
    AuthError,
    ConfirmationRequiredError,
    ConfigError,
    NotFoundError,
    TicktaskError,
    ValidationError,
)
from ticktask.core.results import err, normalize_error_payload


def test_ticktask_errors_include_taxonomy_fields() -> None:
    payload = ConfigError("missing config").to_dict()

    assert payload["code"] == "CONFIG_ERROR"
    assert payload["category"] == "configuration"
    assert payload["retryable"] is False
    assert payload["remediation"] == {
        "action": "configure_auth",
        "command": "ticktask auth init ...",
        "safe_to_retry": False,
    }


def test_api_error_retryability_comes_from_details() -> None:
    payload = ApiError(
        "rate limited",
        details={"status_code": 429, "path": "/open/v1/project", "retryable": True, "retry_after": 10},
    ).to_dict()

    assert payload["category"] == "api"
    assert payload["retryable"] is True
    assert payload["remediation"]["action"] == "retry_after_backoff"
    assert payload["remediation"]["safe_to_retry"] is True
    assert payload["details"]["retry_after"] == 10


def test_common_errors_have_agent_remediation_actions() -> None:
    examples = [
        (AuthError("missing token"), "authenticate"),
        (ValidationError("bad date"), "fix_arguments"),
        (NotFoundError("missing task"), "list_resources"),
        (ConfirmationRequiredError("confirm"), "verify_and_confirm"),
    ]

    for error, action in examples:
        payload = err(error)["error"]
        assert payload["remediation"]["action"] == action
        assert isinstance(payload["remediation"]["command"], str)
        assert payload["retryable"] is False


def test_unexpected_errors_get_unknown_taxonomy() -> None:
    payload = err(RuntimeError("boom"))["error"]

    assert payload["code"] == "UNEXPECTED_ERROR"
    assert payload["category"] == "unexpected"
    assert payload["retryable"] is False
    assert payload["remediation"]["action"] == "report_issue"


def test_normalize_error_payload_backfills_taxonomy_for_legacy_errors() -> None:
    payload = normalize_error_payload({"ok": False, "error": {"code": "VALIDATION_ERROR", "message": "bad"}})

    assert payload["error"]["hint"]
    assert payload["error"]["category"] == "validation"
    assert payload["error"]["retryable"] is False
    assert payload["error"]["remediation"]["action"] == "fix_arguments"
