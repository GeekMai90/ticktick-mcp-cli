from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, cast

from ticktask.core.errors import ConfigError

SECRET_FIELDS = ("client_secret", "access_token", "refresh_token")
SUPPORTED_TOKEN_STORAGES = ("file", "keyring")


class KeyringBackend(Protocol):
    def get_password(self, service_name: str, username: str) -> str | None: ...

    def set_password(self, service_name: str, username: str, password: str) -> None: ...

    def delete_password(self, service_name: str, username: str) -> None: ...


@dataclass(frozen=True)
class CredentialStoreStatus:
    storage: str
    available: bool
    hint: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {"storage": self.storage, "available": self.available, "hint": self.hint}


class CredentialStore:
    storage = "file"

    def load(self, service: str, field: str) -> str | None:
        return None

    def save(self, service: str, field: str, value: str | None) -> None:
        return None

    def configured(self, service: str, field: str) -> bool:
        return self.load(service, field) is not None

    def status(self) -> CredentialStoreStatus:
        return CredentialStoreStatus(storage=self.storage, available=True)


class FileCredentialStore(CredentialStore):
    storage = "file"


class KeyringCredentialStore(CredentialStore):
    storage = "keyring"
    service_namespace = "ticktask"

    def __init__(self, backend: KeyringBackend | None = None) -> None:
        self.backend = backend or self._load_backend()

    def load(self, service: str, field: str) -> str | None:
        return self.backend.get_password(self.service_namespace, self._username(service, field))

    def save(self, service: str, field: str, value: str | None) -> None:
        username = self._username(service, field)
        if value is None:
            try:
                self.backend.delete_password(self.service_namespace, username)
            except Exception:
                pass
            return
        self.backend.set_password(self.service_namespace, username, value)

    def configured(self, service: str, field: str) -> bool:
        return bool(self.load(service, field))

    def status(self) -> CredentialStoreStatus:
        try:
            # Probe read-only; some backends may still raise if unavailable.
            self.backend.get_password(self.service_namespace, "__probe__")
        except Exception as exc:
            return CredentialStoreStatus(
                storage=self.storage,
                available=False,
                hint=f"Keyring backend is unavailable: {exc}",
            )
        return CredentialStoreStatus(storage=self.storage, available=True)

    @staticmethod
    def _username(service: str, field: str) -> str:
        return f"{service}:{field}"

    @staticmethod
    def _load_backend() -> KeyringBackend:
        try:
            import keyring  # type: ignore[import-not-found]
        except ImportError as exc:
            raise ConfigError(
                "Keyring token storage requires the optional `keyring` package.",
                hint="Install with `pip install 'ticktick-mcp-cli[keyring]'` or use `--token-storage file`.",
            ) from exc
        return cast(KeyringBackend, keyring)


def credential_store_for(storage: str | None) -> CredentialStore:
    storage_name = storage or "file"
    if storage_name == "file":
        return FileCredentialStore()
    if storage_name == "keyring":
        return KeyringCredentialStore()
    raise ConfigError(
        f"Unsupported token storage `{storage_name}`.",
        hint="Use `file` or `keyring`.",
    )
