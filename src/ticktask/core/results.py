from __future__ import annotations

from typing import Any

from ticktask.core.errors import TicktaskError, enrich_error_payload


def ok(data: Any = None, meta: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"ok": True, "data": data if data is not None else {}, "meta": meta or {}}


def err(error: TicktaskError | Exception) -> dict[str, Any]:
    if isinstance(error, TicktaskError):
        payload = error.to_dict()
    else:
        payload = enrich_error_payload(
            {
                "code": "UNEXPECTED_ERROR",
                "message": str(error),
                "hint": "Run `ticktask doctor bundle` and report this issue.",
            }
        )
    return {"ok": False, "error": payload}


def normalize_error_payload(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("ok") is False and "error" in payload:
        error = enrich_error_payload(dict(payload["error"]))
        return {"ok": False, "error": error}
    return payload
