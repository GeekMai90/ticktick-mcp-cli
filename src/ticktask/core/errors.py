from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ErrorSpec:
    category: str
    hint: str
    retryable: bool
    remediation: dict[str, Any]


_ERROR_SPECS: dict[str, ErrorSpec] = {
    "CONFIG_ERROR": ErrorSpec(
        category="configuration",
        hint="Run `ticktask auth init ...` to create local config.",
        retryable=False,
        remediation={"action": "configure_auth", "command": "ticktask auth init ...", "safe_to_retry": False},
    ),
    "AUTH_ERROR": ErrorSpec(
        category="auth",
        hint="Run `ticktask auth login --service <service> --json` to authenticate.",
        retryable=False,
        remediation={"action": "authenticate", "command": "ticktask auth login --json", "safe_to_retry": False},
    ),
    "API_ERROR": ErrorSpec(
        category="api",
        hint="Check your network, service profile, and authentication token.",
        retryable=False,
        remediation={"action": "check_api_status", "command": "ticktask doctor --json", "safe_to_retry": False},
    ),
    "NOT_FOUND": ErrorSpec(
        category="lookup",
        hint="Use an exact ID or list resources first.",
        retryable=False,
        remediation={"action": "list_resources", "command": "ticktask project list --json", "safe_to_retry": False},
    ),
    "AMBIGUOUS_OPERATION": ErrorSpec(
        category="lookup",
        hint="Use an exact task ID and project ID for mutations.",
        retryable=False,
        remediation={"action": "use_exact_ids", "command": "ticktask project list --json", "safe_to_retry": False},
    ),
    "CONFIRMATION_REQUIRED": ErrorSpec(
        category="safety",
        hint="Pass `--yes` only after verifying the target ID.",
        retryable=False,
        remediation={"action": "verify_and_confirm", "command": "rerun with --yes after exact-ID verification", "safe_to_retry": False},
    ),
    "VALIDATION_ERROR": ErrorSpec(
        category="validation",
        hint="Check the command arguments and try again.",
        retryable=False,
        remediation={"action": "fix_arguments", "command": "rerun with valid arguments", "safe_to_retry": False},
    ),
    "UNEXPECTED_ERROR": ErrorSpec(
        category="unexpected",
        hint="Run `ticktask doctor bundle` and report this issue.",
        retryable=False,
        remediation={"action": "report_issue", "command": "ticktask doctor bundle --output ./ticktask-diagnostics.zip", "safe_to_retry": False},
    ),
}


def error_spec(code: str) -> ErrorSpec:
    return _ERROR_SPECS.get(code, _ERROR_SPECS["UNEXPECTED_ERROR"])


def enrich_error_payload(payload: dict[str, Any]) -> dict[str, Any]:
    enriched = dict(payload)
    code = str(enriched.get("code") or "UNEXPECTED_ERROR")
    spec = error_spec(code)
    raw_details = enriched.get("details")
    details: dict[str, Any] = raw_details if isinstance(raw_details, dict) else {}
    retryable = bool(details.get("retryable", spec.retryable))
    remediation = dict(spec.remediation)
    if code == "API_ERROR" and retryable:
        remediation.update(
            {
                "action": "retry_after_backoff" if details.get("retry_after") else "retry_with_backoff",
                "command": "retry the same read-only command after the suggested delay",
                "safe_to_retry": True,
            }
        )
    enriched.setdefault("message", "")
    enriched["hint"] = enriched.get("hint") or spec.hint
    enriched["category"] = enriched.get("category") or spec.category
    enriched["retryable"] = retryable
    enriched["remediation"] = enriched.get("remediation") or remediation
    return enriched


@dataclass
class TicktaskError(Exception):
    code: str
    message: str
    hint: str | None = None
    details: dict[str, Any] | None = None

    def __str__(self) -> str:
        return self.message

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "code": self.code,
            "message": self.message,
            "hint": self.hint or "",
        }
        if self.details:
            payload["details"] = self.details
        return enrich_error_payload(payload)


class ConfigError(TicktaskError):
    def __init__(
        self,
        message: str,
        hint: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__("CONFIG_ERROR", message, hint, details)

class AuthError(TicktaskError):
    def __init__(
        self,
        message: str,
        hint: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__("AUTH_ERROR", message, hint, details)


class ApiError(TicktaskError):
    def __init__(
        self,
        message: str,
        hint: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__("API_ERROR", message, hint, details)


class NotFoundError(TicktaskError):
    def __init__(self, message: str, hint: str | None = None) -> None:
        super().__init__("NOT_FOUND", message, hint)


class AmbiguousOperationError(TicktaskError):
    def __init__(self, message: str, hint: str | None = None) -> None:
        super().__init__("AMBIGUOUS_OPERATION", message, hint)


class ConfirmationRequiredError(TicktaskError):
    def __init__(self, message: str, hint: str | None = None) -> None:
        super().__init__("CONFIRMATION_REQUIRED", message, hint)


class ValidationError(TicktaskError):
    def __init__(self, message: str, hint: str | None = None) -> None:
        super().__init__("VALIDATION_ERROR", message, hint)
