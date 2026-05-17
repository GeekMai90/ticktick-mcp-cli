from __future__ import annotations

from dataclasses import dataclass
from typing import Any


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
        return payload


class ConfigError(TicktaskError):
    def __init__(
        self,
        message: str,
        hint: str | None = "Run `ticktask auth init ...` to create local config.",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__("CONFIG_ERROR", message, hint, details)


class AuthError(TicktaskError):
    def __init__(
        self,
        message: str,
        hint: str | None = "Run `ticktask auth init ...` and configure OAuth tokens.",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__("AUTH_ERROR", message, hint, details)


class ApiError(TicktaskError):
    def __init__(
        self,
        message: str,
        hint: str | None = "Check your network, service profile, and authentication token.",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__("API_ERROR", message, hint, details)


class NotFoundError(TicktaskError):
    def __init__(self, message: str, hint: str | None = None) -> None:
        super().__init__("NOT_FOUND", message, hint or "Use an exact ID or list resources first.")


class AmbiguousOperationError(TicktaskError):
    def __init__(self, message: str, hint: str | None = None) -> None:
        super().__init__(
            "AMBIGUOUS_OPERATION",
            message,
            hint or "Use an exact task ID and project ID for mutations.",
        )


class ConfirmationRequiredError(TicktaskError):
    def __init__(self, message: str, hint: str | None = None) -> None:
        super().__init__(
            "CONFIRMATION_REQUIRED",
            message,
            hint or "Pass `--yes` only after verifying the target ID.",
        )


class ValidationError(TicktaskError):
    def __init__(self, message: str, hint: str | None = None) -> None:
        super().__init__(
            "VALIDATION_ERROR",
            message,
            hint or "Check the command arguments and try again.",
        )
