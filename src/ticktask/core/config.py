from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from ticktask.core.constants import CONFIG_FILENAME, DEFAULT_SERVICE, get_service_profile
from ticktask.core.credentials import SECRET_FIELDS, SUPPORTED_TOKEN_STORAGES, credential_store_for
from ticktask.core.errors import ConfigError


@dataclass
class ProfileConfig:
    service: str
    base_url: str
    oauth_authorize_base_url: str
    oauth_token_base_url: str
    client_id: str | None = None
    client_secret: str | None = None
    redirect_uri: str | None = None
    access_token: str | None = None
    refresh_token: str | None = None
    token_storage: str = "file"
    expires_at: str | None = None
    oauth_state: str | None = None
    code_verifier: str | None = None

    @classmethod
    def for_service(
        cls,
        service: str,
        client_id: str | None = None,
        client_secret: str | None = None,
        redirect_uri: str | None = None,
        token_storage: str = "file",
    ) -> ProfileConfig:
        profile = get_service_profile(service)
        _validate_token_storage(token_storage)
        return cls(
            service=profile.name,
            base_url=profile.base_url,
            oauth_authorize_base_url=profile.oauth_authorize_base_url,
            oauth_token_base_url=profile.oauth_token_base_url,
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            token_storage=token_storage,
        )

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> ProfileConfig:
        service = raw.get("service") or DEFAULT_SERVICE
        profile = get_service_profile(service)
        token_storage = raw.get("token_storage") or "file"
        _validate_token_storage(token_storage)
        return cls(
            service=profile.name,
            base_url=raw.get("base_url") or profile.base_url,
            oauth_authorize_base_url=(
                raw.get("oauth_authorize_base_url") or profile.oauth_authorize_base_url
            ),
            oauth_token_base_url=raw.get("oauth_token_base_url") or profile.oauth_token_base_url,
            client_id=raw.get("client_id"),
            client_secret=raw.get("client_secret"),
            redirect_uri=raw.get("redirect_uri"),
            access_token=raw.get("access_token"),
            refresh_token=raw.get("refresh_token"),
            token_storage=token_storage,
            expires_at=raw.get("expires_at"),
            oauth_state=raw.get("oauth_state"),
            code_verifier=raw.get("code_verifier"),
        )

    def is_configured(self) -> bool:
        return bool(self.client_id and self.client_secret and self.redirect_uri)

    def has_token(self) -> bool:
        return bool(self.access_token)

    def hydrate_credentials(self) -> ProfileConfig:
        if self.token_storage != "keyring":
            return self
        store = credential_store_for(self.token_storage)
        for field in SECRET_FIELDS:
            if getattr(self, field) is None:
                setattr(self, field, store.load(self.service, field))
        return self

    def save_external_credentials(self) -> None:
        if self.token_storage != "keyring":
            return
        store = credential_store_for(self.token_storage)
        for field in SECRET_FIELDS:
            store.save(self.service, field, getattr(self, field))

    def credential_configured(self, field: str) -> bool:
        value = getattr(self, field)
        if value:
            return True
        if self.token_storage != "keyring":
            return False
        try:
            return credential_store_for(self.token_storage).configured(self.service, field)
        except Exception:
            return False


@dataclass
class TicktaskConfig:
    active_service: str = DEFAULT_SERVICE
    profiles: dict[str, ProfileConfig] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> TicktaskConfig:
        profiles = {
            name: ProfileConfig.from_dict(value)
            for name, value in (raw.get("profiles") or {}).items()
            if isinstance(value, dict)
        }
        active_service = raw.get("active_service") or raw.get("service") or DEFAULT_SERVICE
        get_service_profile(active_service)
        return cls(active_service=active_service, profiles=profiles)

    def to_dict(self) -> dict[str, Any]:
        profiles: dict[str, dict[str, Any]] = {}
        for name, profile in self.profiles.items():
            raw = asdict(profile)
            if profile.token_storage == "keyring":
                for field in SECRET_FIELDS:
                    raw.pop(field, None)
            profiles[name] = raw
        return {
            "active_service": self.active_service,
            "profiles": profiles,
        }

    def get_profile(self, service: str | None = None) -> ProfileConfig:
        service_name = service or self.active_service
        get_service_profile(service_name)
        profile = self.profiles.get(service_name)
        if profile is None:
            raise ConfigError(f"No local config found for service profile `{service_name}`.")
        return profile

    def set_profile(self, profile: ProfileConfig, active: bool = True) -> None:
        get_service_profile(profile.service)
        _validate_token_storage(profile.token_storage)
        self.profiles[profile.service] = profile
        if active:
            self.active_service = profile.service


def _validate_token_storage(token_storage: str) -> None:
    if token_storage not in SUPPORTED_TOKEN_STORAGES:
        raise ConfigError(
            f"Unsupported token storage `{token_storage}`.",
            hint="Use `file` or `keyring`.",
        )


def config_dir() -> Path:
    explicit = os.environ.get("TICKTASK_CONFIG_DIR")
    if explicit:
        return Path(explicit).expanduser()
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        return Path(xdg).expanduser() / "ticktask"
    return Path.home() / ".config" / "ticktask"


def config_path() -> Path:
    return config_dir() / CONFIG_FILENAME


class ConfigStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or config_path()

    def load(self) -> TicktaskConfig:
        if not self.path.exists():
            return TicktaskConfig()
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ConfigError(f"Config file is not valid JSON: {self.path}") from exc
        if not isinstance(raw, dict):
            raise ConfigError(f"Config file root must be a JSON object: {self.path}")
        return TicktaskConfig.from_dict(raw)

    def save(self, config: TicktaskConfig) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(config.to_dict(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        try:
            self.path.chmod(0o600)
        except OSError:
            pass

    def path_string(self) -> str:
        return str(self.path)
