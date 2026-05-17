from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from typing import Any
from urllib.parse import urlencode

import httpx

from ticktask.core.client import request_json_without_auth
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

    def authorization_url(self, service: str | None = None, scope: str | None = None) -> str:
        profile = self._require_configured_profile(service)
        params = {
            "client_id": profile.client_id or "",
            "redirect_uri": profile.redirect_uri or "",
            "response_type": "code",
        }
        if scope:
            params["scope"] = scope
        authorize_base_url = profile.oauth_authorize_base_url.rstrip("/")
        return f"{authorize_base_url}/oauth/authorize?{urlencode(params)}"

    def login_with_code(
        self,
        code: str,
        service: str | None = None,
        http_client: httpx.Client | None = None,
    ) -> ProfileConfig:
        profile = self._require_configured_profile(service)
        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": profile.client_id,
            "client_secret": profile.client_secret,
            "redirect_uri": profile.redirect_uri,
        }
        token_payload = request_json_without_auth(
            profile.oauth_token_base_url,
            "POST",
            "/oauth/token",
            data=payload,
            http_client=http_client,
        )
        return self._store_tokens(profile, token_payload)

    def refresh(
        self,
        service: str | None = None,
        http_client: httpx.Client | None = None,
    ) -> ProfileConfig:
        profile = self._require_configured_profile(service)
        if not profile.refresh_token:
            raise AuthError(
                f"Service profile `{profile.service}` has no refresh token.",
                hint="Run `ticktask auth login` to obtain a refresh token first.",
            )
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": profile.refresh_token,
            "client_id": profile.client_id,
            "client_secret": profile.client_secret,
        }
        token_payload = request_json_without_auth(
            profile.oauth_token_base_url,
            "POST",
            "/oauth/token",
            data=payload,
            http_client=http_client,
        )
        return self._store_tokens(profile, token_payload)

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

    def _require_configured_profile(self, service: str | None = None) -> ProfileConfig:
        config = self.store.load()
        profile = config.get_profile(service)
        if not profile.is_configured():
            raise AuthError(
                f"Service profile `{profile.service}` is missing OAuth client config.",
                hint="Run `ticktask auth init --service SERVICE --client-id ... --client-secret ... --redirect-uri ...`.",
            )
        return profile

    def _store_tokens(self, profile: ProfileConfig, token_payload: dict[str, Any]) -> ProfileConfig:
        access_token = token_payload.get("access_token")
        if not access_token:
            raise AuthError("OAuth token response did not include an access_token.")
        profile.access_token = str(access_token)
        refresh_token = token_payload.get("refresh_token")
        if refresh_token:
            profile.refresh_token = str(refresh_token)
        expires_in = token_payload.get("expires_in")
        if expires_in is not None:
            try:
                expires_at = datetime.now(UTC) + timedelta(seconds=int(expires_in))
            except (TypeError, ValueError) as exc:
                raise AuthError("OAuth token response included an invalid expires_in value.") from exc
            profile.expires_at = expires_at.isoformat()
        config = self.store.load()
        config.set_profile(profile)
        self.store.save(config)
        return profile
