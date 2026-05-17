from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from ticktask.core.config import config_dir
from ticktask.core.errors import ValidationError


def idempotency_path() -> Path:
    return config_dir() / "idempotency.json"


class IdempotencyStore:
    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path).expanduser() if path is not None else idempotency_path()

    def get(self, operation: str, key: str | None, payload: dict[str, Any]) -> dict[str, Any] | None:
        if not key:
            return None
        data = self._load()
        entry = data.get(self._entry_key(operation, key))
        if entry is None:
            return None
        fingerprint = self._fingerprint(operation, payload)
        if entry.get("fingerprint") != fingerprint:
            raise ValidationError(
                f"Idempotency key `{key}` was already used with a different payload.",
                hint="Use a new --idempotency-key when changing task creation arguments.",
            )
        result = entry.get("result")
        return result if isinstance(result, dict) else None

    def record(self, operation: str, key: str | None, payload: dict[str, Any], result: dict[str, Any]) -> None:
        if not key:
            return
        data = self._load()
        data[self._entry_key(operation, key)] = {
            "operation": operation,
            "key": key,
            "fingerprint": self._fingerprint(operation, payload),
            "result": result,
        }
        self._save(data)

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {}
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValidationError(f"Idempotency store is not valid JSON: {self.path}") from exc
        if not isinstance(raw, dict):
            raise ValidationError(f"Idempotency store root must be a JSON object: {self.path}")
        return raw

    def _save(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        try:
            self.path.chmod(0o600)
        except OSError:
            pass

    @staticmethod
    def _entry_key(operation: str, key: str) -> str:
        return f"{operation}:{key}"

    @staticmethod
    def _fingerprint(operation: str, payload: dict[str, Any]) -> str:
        encoded = json.dumps({"operation": operation, "payload": payload}, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()
