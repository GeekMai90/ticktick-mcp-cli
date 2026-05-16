from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from ticktask.core.config import ConfigStore, ProfileConfig
from ticktask.core.errors import AuthError, ConfigError


@dataclass
class AuthStatus:
    service: str
    base_url: str
    config_path: str
    configured: bool
    authenticated: bool
    has_refresh_token: bool
    client_id: str | None
    redirect_uri: str | None
    expires_at: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class AuthManager:
    def __init__(self, store: ConfigStore | None = None) -> None:
        self.store = store or ConfigStore()

    def init(
        self,
        service: str,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        access_token: str | None = None,
        refresh_token: str | None = None,
        expires_at: str | None = None,
    ) -> ProfileConfig:
        profile = ProfileConfig.for_service(
            service=service,
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
        )
        profile.access_token = access_token
        profile.refresh_token = refresh_token
        profile.expires_at = expires_at
        config = self.store.load()
        config.set_profile(profile)
        self.store.save(config)
        return profile

    def status(self, service: str | None = None) -> AuthStatus:
        config = self.store.load()
        try:
            profile = config.get_profile(service)
        except ConfigError:
            service_name = service or config.active_service
            from ticktask.core.constants import get_service_profile

            service_profile = get_service_profile(service_name)
            return AuthStatus(
                service=service_profile.name,
                base_url=service_profile.base_url,
                config_path=self.store.path_string(),
                configured=False,
                authenticated=False,
                has_refresh_token=False,
                client_id=None,
                redirect_uri=None,
                expires_at=None,
            )
        return AuthStatus(
            service=profile.service,
            base_url=profile.base_url,
            config_path=self.store.path_string(),
            configured=profile.is_configured(),
            authenticated=profile.has_token(),
            has_refresh_token=bool(profile.refresh_token),
            client_id=profile.client_id,
            redirect_uri=profile.redirect_uri,
            expires_at=profile.expires_at,
        )

    def require_token(self, service: str | None = None) -> ProfileConfig:
        config = self.store.load()
        profile = config.get_profile(service)
        if not profile.access_token:
            raise AuthError(
                f"Service profile `{profile.service}` has no access token.",
                hint=(
                    "Run `ticktask auth init ... --access-token TOKEN` for testing or complete "
                    "the OAuth browser flow when it is configured."
                ),
            )
        return profile
