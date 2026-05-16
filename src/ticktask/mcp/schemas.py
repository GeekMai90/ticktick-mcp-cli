from __future__ import annotations

from typing import Any, TypedDict


class ErrorPayload(TypedDict):
    code: str
    message: str
    hint: str


class ResultPayload(TypedDict, total=False):
    ok: bool
    data: Any
    meta: dict[str, Any]
    error: ErrorPayload
